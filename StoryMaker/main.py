# -*- coding: utf-8 -*-

import logging
import sys
import io
import json
import argparse
import os
from PIL import Image  # For image processing

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QAction, QFileDialog, QMessageBox, QToolBar,
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QGraphicsView, QStyle
)
from PyQt5.QtGui import QPainter, QImage, QKeySequence
from PyQt5.QtCore import Qt, QObject, pyqtSignal, QThread

from dialogs import EinstellungenDialog, LoadingDialog  # Removed EigenschaftenDialog
from elements import VerschiebbaresTextElement, VerschiebbaresBildElement, HintergrundElement
from scenes import SeitenSzene, CoverSzene

# 1. Remove all existing logger handlers to prevent duplicate logs
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

# 2. Set sys.stdout encoding to UTF-8 to support Unicode characters in console output
if sys.stdout:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
# 3. Manual logger configuration
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 3.1. StreamHandler for console output
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

# 3.2. FileHandler for log file with UTF-8 encoding
file_handler = logging.FileHandler('JSONBuchEditor.log', encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(console_formatter)
logger.addHandler(file_handler)

# 4. Test log entry to verify logging setup
logging.info("Logging configuration successfully set up.")

class JSONLoaderWorker(QObject):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, json_path):
        super().__init__()
        self.json_path = json_path
        self.base_path = os.path.dirname(json_path)  # Basispfad speichern

    def run(self):
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)

            # Auflösen der relativen Pfade
            json_data = self.resolve_relative_paths(json_data)

            self.finished.emit(json_data)
        except Exception as e:
            self.error.emit(str(e))

    def resolve_relative_paths(self, json_data):
        """
        Löst alle relativen Pfade in den JSON-Daten auf.
        """
        if 'coverImage' in json_data and json_data['coverImage']:
            json_data['coverImage'] = self.resolve_path(json_data['coverImage'])

        for scene in json_data.get('scenes', []):
            if 'background' in scene and scene['background']:
                scene['background'] = self.resolve_path(scene['background'])

            for image_element in scene.get('imageElements', []):
                if 'imageUrl' in image_element and image_element['imageUrl']:
                    image_element['imageUrl'] = self.resolve_path(image_element['imageUrl'])

        return json_data

    def resolve_path(self, path):
        """
        Löst einen relativen Pfad relativ zum Basispfad der JSON-Datei auf.
        """
        if not path.startswith(('http://', 'https://', '/')):  # Relativer Pfad
            return os.path.join(self.base_path, path)
        return path



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JSON Book Editor")
        self.json_data = None
        self.current_page_index = 0
        self.page_size = (800, 600)  # Default size
        self.show_invisible_elements = False  # Default to not show invisible elements

        # Create actions with icons and connect them to methods
        open_icon = QApplication.style().standardIcon(QStyle.SP_DialogOpenButton)
        save_icon = QApplication.style().standardIcon(QStyle.SP_DialogSaveButton)
        exit_icon = QApplication.style().standardIcon(QStyle.SP_DialogCloseButton)
        new_text_icon = QApplication.style().standardIcon(QStyle.SP_FileIcon)
        new_image_icon = QApplication.style().standardIcon(QStyle.SP_FileDialogContentsView)
        add_page_icon = QApplication.style().standardIcon(QStyle.SP_FileDialogNewFolder)
        delete_page_icon = QApplication.style().standardIcon(QStyle.SP_TrashIcon)
        settings_icon = QApplication.style().standardIcon(QStyle.SP_FileDialogDetailedView)
        delete_icon = QApplication.style().standardIcon(QStyle.SP_TrashIcon)

        open_action = QAction(open_icon, 'Open JSON', self)
        open_action.triggered.connect(self.open_json_file)
        save_action = QAction(save_icon, 'Save JSON', self)
        save_action.triggered.connect(self.save_json_file)
        exit_action = QAction(exit_icon, 'Exit', self)
        exit_action.triggered.connect(self.close)
        new_text_action = QAction(new_text_icon, 'New Text', self)
        new_text_action.triggered.connect(self.add_new_text)
        new_image_action = QAction(new_image_icon, 'New Image', self)
        new_image_action.triggered.connect(self.add_new_image)
        add_page_action = QAction(add_page_icon, 'Add New Page', self)
        add_page_action.triggered.connect(self.add_new_page)
        delete_page_action = QAction(delete_page_icon, 'Delete Current Page', self)
        delete_page_action.triggered.connect(self.delete_current_page)
        show_invisible_elements_action = QAction('Show Invisible Elements', self, checkable=True)
        show_invisible_elements_action.triggered.connect(self.toggle_show_invisible_elements)
        settings_action = QAction(settings_icon, 'Book Settings', self)
        settings_action.triggered.connect(self.book_settings)
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about_dialog)
        delete_action = QAction(delete_icon, 'Delete', self)
        delete_action.setShortcut(QKeySequence.Delete)
        delete_action.triggered.connect(self.delete_selected_elements)

        # Create menu bar and add menus with actions
        menu = self.menuBar()
        file_menu = menu.addMenu('File')
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        edit_menu = menu.addMenu('Edit')
        edit_menu.addAction(add_page_action)
        edit_menu.addAction(delete_page_action)
        edit_menu.addSeparator()
        edit_menu.addAction(settings_action)

        view_menu = menu.addMenu('View')
        view_menu.addAction(show_invisible_elements_action)

        help_menu = menu.addMenu('Help')
        help_menu.addAction(about_action)

        # Create toolbar and add actions
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        toolbar.addAction(open_action)
        toolbar.addAction(save_action)
        toolbar.addSeparator()
        toolbar.addAction(add_page_action)
        toolbar.addAction(delete_page_action)
        toolbar.addSeparator()
        toolbar.addAction(new_text_action)
        toolbar.addAction(new_image_action)
        toolbar.addSeparator()
        toolbar.addAction(settings_action)
        toolbar.addAction(delete_action)  # Add Delete action to toolbar

        # Show both icon and text in the toolbar
        toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        # Create main layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Create navigation layout with previous and next buttons
        navigation_layout = QHBoxLayout()
        self.previous_page_button = QPushButton("◀ Previous Page")
        self.previous_page_button.clicked.connect(self.previous_page)
        self.page_info_label = QLabel("Page 0 of 0")
        self.next_page_button = QPushButton("Next Page ▶")
        self.next_page_button.clicked.connect(self.next_page)

        navigation_layout.addWidget(self.previous_page_button)
        navigation_layout.addWidget(self.page_info_label)
        navigation_layout.addWidget(self.next_page_button)
        navigation_layout.addStretch()

        # Add navigation to main layout
        main_layout.addLayout(navigation_layout)

        # Create GraphicsView for displaying scenes
        self.view = QGraphicsView()
        self.view.setRenderHint(QPainter.Antialiasing)
        main_layout.addWidget(self.view)

        # Store the action for later access
        self.show_invisible_elements_action = show_invisible_elements_action

        logging.info("GUI initialized and MainWindow displayed.")

    def toggle_show_invisible_elements(self, checked):
        self.show_invisible_elements = checked
        # Update the scene to reflect the change
        if self.view.scene():
            if hasattr(self.view.scene(), 'show_invisible_elements'):
                self.view.scene().show_invisible_elements = self.show_invisible_elements
                for item in self.view.scene().items():
                    if isinstance(item, (VerschiebbaresTextElement, VerschiebbaresBildElement)):
                        item.update_visibility()
                self.view.scene().update()
        logging.info(f"Show invisible elements set to {'enabled' if self.show_invisible_elements else 'disabled'}.")

    def update_page_info(self):
        if self.json_data:
            has_cover = bool(self.json_data.get('coverImage'))
            total_pages = len(self.json_data.get('scenes', [])) + (1 if has_cover else 0)
            current_page = self.current_page_index + 1
            self.page_info_label.setText(f"Page {current_page} of {total_pages}")
        else:
            self.page_info_label.setText("Page 0 of 0")

    def open_json_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open JSON File", "", "JSON Files (*.json);;All Files (*)")
        if file_path:
            # Show loading dialog
            self.loading_dialog = LoadingDialog(self)
            self.loading_dialog.show()

            # Set up worker and thread
            self.thread = QThread()
            self.worker = JSONLoaderWorker(file_path)
            self.worker.moveToThread(self.thread)

            # Connect signals
            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.on_json_loaded)
            self.worker.error.connect(self.on_json_load_error)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            self.worker.error.connect(self.thread.quit)
            self.worker.error.connect(self.worker.deleteLater)

            # Start thread
            self.thread.start()

    def on_json_loaded(self, json_data):
        self.loading_dialog.close()
        self.json_data = json_data
        if not validate_json(self.json_data):
            QMessageBox.critical(self, "Invalid JSON", "The selected JSON file is invalid.")
            self.json_data = None
            self.view.setScene(None)
            self.update_page_info()
            return
        self.current_page_index = 0
        # Read page size
        page_size = self.json_data.get('pageSize', {'width': 800, 'height': 600})
        self.page_size = (page_size.get('width', 800), page_size.get('height', 600))
        self.load_page()
        self.update_page_info()
        logging.info("JSON data successfully loaded.")

    def on_json_load_error(self, error_message):
        self.loading_dialog.close()
        QMessageBox.critical(self, "Error", f"Error loading JSON file: {error_message}")
        logging.error(f"Error loading JSON file: {error_message}")

    def save_json_file(self):
        if not self.json_data:
            QMessageBox.warning(self, "No Data", "No JSON data available to save.")
            return
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save JSON File", "", "JSON Files (*.json);;All Files (*)")
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.json_data, f, ensure_ascii=False, indent=2)
                QMessageBox.information(self, "Saved", "JSON data successfully saved.")
                logging.info(f"JSON data successfully saved: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error saving JSON file: {e}")
                logging.error(f"Error saving JSON file: {e}")

    def load_page(self):
        if not self.json_data:
            return
        total_pages = len(self.json_data.get('scenes', []))
        has_cover = bool(self.json_data.get('coverImage'))
        if has_cover:
            total_pages += 1

        if self.current_page_index < 0 or self.current_page_index >= total_pages:
            QMessageBox.warning(self, "Range Error", "No more pages available.")
            return

        # Update page size
        page_size = self.json_data.get('pageSize', {'width': 800, 'height': 600})
        self.page_size = (page_size.get('width', 800), page_size.get('height', 600))

        if has_cover and self.current_page_index == 0:
            # Load cover page
            cover_image_path = self.json_data.get('coverImage', '')
            scene = CoverSzene(cover_image_path, self.page_size, self.show_invisible_elements)
        else:
            # Load scene page
            scene_index = self.current_page_index - (1 if has_cover else 0)
            scenes = self.json_data.get('scenes', [])
            if 0 <= scene_index < len(scenes):
                scene_data = scenes[scene_index]
                scene = SeitenSzene(scene_data, self.page_size, self.show_invisible_elements)
            else:
                QMessageBox.warning(self, "Range Error", "No more pages available.")
                return

        self.view.setScene(scene)
        self.view.setSceneRect(0, 0, self.page_size[0], self.page_size[1])  # Set scene size
        self.view.fitInView(scene.sceneRect(), Qt.KeepAspectRatio)
        self.update_page_info()
        logging.info(f"Page {self.current_page_index + 1} loaded.")

    def next_page(self):
        if not self.json_data:
            return
        total_pages = len(self.json_data.get('scenes', []))
        has_cover = bool(self.json_data.get('coverImage'))
        if has_cover:
            total_pages += 1
        if self.current_page_index < total_pages - 1:
            self.current_page_index += 1
            self.load_page()
        else:
            QMessageBox.information(self, "End", "This is the last page.")
            logging.info("Attempted to navigate beyond the last page.")

    def previous_page(self):
        if self.current_page_index > 0:
            self.current_page_index -= 1
            self.load_page()
        else:
            QMessageBox.information(self, "Start", "This is the first page.")
            logging.info("Attempted to navigate before the first page.")

    def add_new_text(self):
        if not self.json_data:
            QMessageBox.warning(self, "No Data", "Please open a JSON file first.")
            return
        if self.view.scene() and isinstance(self.view.scene(), SeitenSzene):
            # Create new text element
            new_text_element = {
                "content": "New Text",
                "position": {"x": 100, "y": 100},
                "fontFamily": "Arial",
                "fontSize": 24,
                "color": "#000000",
                "width": 300,
                "layer": 1,
                "rotation": 0,
                "opacity": 1.0,
                "fontStyle": "normal",
                "visible": True
            }
            # Add to scene and JSON
            scene_index = self.current_page_index - (1 if self.json_data.get('coverImage') else 0)
            current_scene = self.json_data['scenes'][scene_index]
            current_scene.setdefault('textElements', []).append(new_text_element)
            item = VerschiebbaresTextElement(new_text_element)
            self.view.scene().addItem(item)
            logging.info("New text element added.")
        else:
            QMessageBox.warning(self, "Action Not Possible", "Cannot add text element on this page.")

    def add_new_image(self):
        if not self.json_data:
            QMessageBox.warning(self, "No Data", "Please open a JSON file first.")
            return
        if self.view.scene() and isinstance(self.view.scene(), SeitenSzene):
            # Select image file
            file_name, _ = QFileDialog.getOpenFileName(
                self, "Select Image File", "", "Images (*.png *.jpg *.jpeg *.bmp);;All Files (*)")
            if file_name:
                new_image_element = {
                    "imageUrl": file_name,
                    "position": {"x": 100, "y": 100},
                    "width": 200,
                    "height": 150,
                    "imagePrompt": "",
                    "layer": 0,
                    "rotation": 0,
                    "opacity": 1.0,
                    "visible": True,
                    "userProvided": False
                }
                # Add to scene and JSON
                scene_index = self.current_page_index - (1 if self.json_data.get('coverImage') else 0)
                current_scene = self.json_data['scenes'][scene_index]
                current_scene.setdefault('imageElements', []).append(new_image_element)
                item = VerschiebbaresBildElement(new_image_element)
                self.view.scene().addItem(item)
                logging.info(f"New image element added: {file_name}")
        else:
            QMessageBox.warning(self, "Action Not Possible", "Cannot add image element on this page.")

    def add_new_page(self):
        if not self.json_data:
            QMessageBox.warning(self, "No Data", "Please open a JSON file first or create a new one.")
            return
        # Create new page
        new_scene = {
            "pageNumber": len(self.json_data['scenes']) + 1,
            "background": "",
            "textElements": [],
            "imageElements": []
        }
        self.json_data['scenes'].append(new_scene)
        self.current_page_index = len(self.json_data['scenes']) - 1 + (1 if self.json_data.get('coverImage') else 0)
        self.load_page()
        self.update_page_info()
        logging.info("New page added.")

    def delete_current_page(self):
        if not self.json_data:
            QMessageBox.warning(self, "No Data", "No page available to delete.")
            return
        total_pages = len(self.json_data.get('scenes', []))
        has_cover = bool(self.json_data.get('coverImage'))

        if has_cover and self.current_page_index == 0:
            reply = QMessageBox.question(
                self, 'Delete Cover Image',
                'Are you sure you want to remove the cover image?',
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.json_data['coverImage'] = ''
                self.load_page()
                self.update_page_info()
                logging.info("Cover image removed.")
            return

        if total_pages == 1 and not has_cover:
            QMessageBox.warning(self, "Last Page", "Cannot delete the last remaining page.")
            logging.warning("Attempted to delete the last page.")
            return

        reply = QMessageBox.question(
            self, 'Delete Page',
            'Are you sure you want to delete the current page?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            scene_index = self.current_page_index - (1 if has_cover else 0)
            del self.json_data['scenes'][scene_index]
            if self.current_page_index >= len(self.json_data['scenes']) + (1 if has_cover else 0):
                self.current_page_index = len(self.json_data['scenes']) - 1 + (1 if has_cover else 0)
            self.load_page()
            self.update_page_info()
            logging.info(f"Page {scene_index + 1} deleted.")

    def book_settings(self):
        if not self.json_data:
            QMessageBox.warning(self, "No Data", "Please open a JSON file first or create a new one.")
            return
        dialog = EinstellungenDialog(self.json_data, self)
        if dialog.exec_():
            data = dialog.get_data()
            # Update json_data
            self.json_data['title'] = data['title']
            self.json_data['description'] = data['description']
            self.json_data['author'] = data.get('author', '')
            self.json_data['illustrator'] = data.get('illustrator', '')
            self.json_data['pageSize'] = data['pageSize']
            self.json_data['coverImage'] = data.get('coverImage', '')
            # Update page size
            self.page_size = (data['pageSize']['width'], data['pageSize']['height'])
            self.load_page()
            QMessageBox.information(self, "Settings Saved", "Book settings have been updated.")
            logging.info("Book settings updated.")

    def show_about_dialog(self):
        QMessageBox.about(self, "About JSON Book Editor",
                          "JSON Book Editor\nVersion 1.0\nCreated by Your Name")

    def delete_selected_elements(self):
        selected_elements = self.view.scene().selectedItems()
        if selected_elements:
            reply = QMessageBox.question(
                self, 
                'Bestätigung', 
                f'Möchten Sie {len(selected_elements)} ausgewählte(s) Element(e) wirklich löschen?', 
                QMessageBox.Yes | QMessageBox.No, 
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                for element in selected_elements:
                    if hasattr(element, 'text_element'):
                        # Entferne das Textelement aus der Szene und aus den JSON-Daten
                        scene_index = self.current_page_index - (1 if self.json_data.get('coverImage') else 0)
                        current_scene = self.json_data['scenes'][scene_index]
                        text_elements = current_scene.get('textElements', [])
                        text_elements = [te for te in text_elements if te != element.text_element]  # Filtere das gelöschte Element aus der Liste
                        current_scene['textElements'] = text_elements
                        element_name = element.text_element.get('content', 'Unbekannt')
                        self.view.scene().removeItem(element)
                        logging.info(f"Textelement gelöscht: {element_name}")

                    elif hasattr(element, 'image_element'):
                        # Entferne das Bildelement aus der Szene und aus den JSON-Daten
                        scene_index = self.current_page_index - (1 if self.json_data.get('coverImage') else 0)
                        current_scene = self.json_data['scenes'][scene_index]
                        image_elements = current_scene.get('imageElements', [])
                        image_elements = [ie for ie in image_elements if ie != element.image_element]  # Filtere das gelöschte Element aus der Liste
                        current_scene['imageElements'] = image_elements
                        element_name = element.image_element.get('imageUrl', 'Unbekannt')
                        self.view.scene().removeItem(element)
                        logging.info(f"Bildelement gelöscht: {element_name}")

                logging.info(f"{len(selected_elements)} Element(e) erfolgreich gelöscht.")
        else:
            QMessageBox.information(self, "Info", "Keine Elemente ausgewählt zum Löschen.")



def combine_jpgs_vertically(jpg_files, output_path):
    """
    Combines multiple JPG images vertically into a single image.

    :param jpg_files: List of paths to individual JPG files.
    :param output_path: Path to the combined output file.
    :return: Path to the combined output file.
    """
    try:
        images = [Image.open(jpg) for jpg in jpg_files]
        widths, heights = zip(*(i.size for i in images))

        max_width = max(widths)
        total_height = sum(heights)

        combined_image = Image.new('RGB', (max_width, total_height), color='white')

        y_offset = 0
        for im in images:
            combined_image.paste(im, (0, y_offset))
            y_offset += im.height

        combined_image.save(output_path, "JPEG")
        logging.info(f"Combined image saved as {output_path}")
        return output_path
    except Exception as e:
        logging.error(f"Error combining images: {e}")
        sys.exit(1)


def render_json_to_jpg(json_path, output_path):
    try:
        # Initialize the Qt application
        app = QApplication(sys.argv)
        logging.info("Qt application initialized for headless mode.")

        # Load JSON data
        with open(json_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        logging.info(f"JSON data loaded from {json_path}")

        # Validate JSON data
        if not validate_json(json_data):
            logging.error("Invalid JSON data. Process will terminate.")
            sys.exit(1)

        # Determine if a cover is present
        has_cover = bool(json_data.get('coverImage'))
        total_pages = len(json_data.get('scenes', [])) + (1 if has_cover else 0)
        logging.info(f"Total pages: {total_pages} (Cover: {has_cover})")

        # Get page size from JSON or use default values
        page_size = json_data.get('pageSize', {'width': 800, 'height': 600})

        # Ensure width and height are integers
        try:
            page_width = int(page_size.get('width', 800))
            page_height = int(page_size.get('height', 600))
            logging.info(f"Page resolution: {page_width}x{page_height}")
        except ValueError as ve:
            logging.error(f"Invalid page resolution in JSON: {ve}")
            sys.exit(1)

        # Use a local variable instead of 'self.page_size'
        page_size_tuple = (page_width, page_height)

        # List to store paths of generated JPGs
        jpg_files = []

        # Iterate through all pages
        for index in range(total_pages):
            if has_cover and index == 0:
                # Load cover page
                cover_image_path = json_data.get('coverImage', '')
                scene = CoverSzene(cover_image_path, page_size_tuple, False)
                logging.info(f"Loading cover page: {cover_image_path}")
            else:
                # Load scene page
                scene_index = index - 1 if has_cover else index
                scene_data = json_data['scenes'][scene_index]
                scene = SeitenSzene(scene_data, page_size_tuple, False)
                logging.info(f"Loading scene page {scene_index + 1}")

            # Create a QImage and QPainter to render
            image = QImage(page_width, page_height, QImage.Format_ARGB32)
            image.fill(Qt.white)  # Set background color

            painter = QPainter(image)
            scene.render(painter)
            painter.end()

            # Save the image as JPG
            jpg_filename = f"page_{index + 1}.jpg"
            image.save(jpg_filename, "JPG")
            jpg_files.append(jpg_filename)
            logging.info(f"Generated {jpg_filename}")

        # Combine all JPGs vertically
        combined_image = combine_jpgs_vertically(jpg_files, output_path)
        logging.info(f"Combined image saved as {output_path}")

        # Delete temporary JPGs
        for jpg in jpg_files:
            os.remove(jpg)
            logging.info(f"Temporary file deleted: {jpg}")

        # Exit the Qt application
        sys.exit()
    except Exception as e:
        logging.exception("Error in headless mode:")
        sys.exit(1)


def validate_json(json_data):
    required_fields = ['pageSize', 'scenes']
    for field in required_fields:
        if field not in json_data:
            logging.error(f"Missing required field in JSON: {field}")
            return False

    # Additional validations can be added here
    return True


def main():
    parser = argparse.ArgumentParser(description="JSON Book Editor and Converter")
    parser.add_argument('--headless', action='store_true', help='Run in headless mode')
    parser.add_argument('json_file', nargs='?', help='Path to the JSON file')
    parser.add_argument('--output', '-o', default='combined_image.jpg', help='Output JPG file name')

    args = parser.parse_args()

    if args.headless:
        if not args.json_file:
            print("Error: JSON file path is required in headless mode.")
            sys.exit(1)
        render_json_to_jpg(args.json_file, args.output)
    else:
        try:
            # Start GUI mode
            app = QApplication(sys.argv)
            app.setStyle("Fusion")

            # Optional: Load stylesheet
            stylesheet = """
            QMainWindow {
                background-color: #f0f0f0;
            }
            QPushButton {
                padding: 5px;
            }
            QLabel {
                font-size: 14px;
            }
            QGraphicsView {
                background-color: white;
                border: 1px solid #ccc;
            }
            QToolBar {
                background: #e0e0e0;
            }
            """
            app.setStyleSheet(stylesheet)

            window = MainWindow()
            window.resize(1024, 768)
            window.show()
            logging.info("Starting GUI mode.")
            sys.exit(app.exec_())
        except Exception as e:
            logging.exception("Error in GUI mode:")
            sys.exit(1)


if __name__ == '__main__':
    main()
