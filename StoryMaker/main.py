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
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QGraphicsView, QStyle,
    QInputDialog
)
from PyQt5.QtGui import QPainter, QImage, QKeySequence
from PyQt5.QtCore import Qt, QObject, pyqtSignal, QThread

from dialogs import EinstellungenDialog, EigenschaftenDialog, LoadingDialog, DatabaseSettingsDialog  # Inklusive DatabaseSettingsDialog
from elements import VerschiebbaresTextElement, VerschiebbaresBildElement, HintergrundElement
from scenes import SeitenSzene, CoverSzene
from database import DatabaseManager

# 1. Entfernen aller bestehenden Logger-Handler, um doppelte Logs zu vermeiden
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

# 2. Setzen der sys.stdout-Kodierung auf UTF-8, um Unicode-Zeichen in der Konsole zu unterstützen
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 3. Manuelle Logger-Konfiguration
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 3.1. StreamHandler für die Konsolenausgabe
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

# 3.2. FileHandler für die Log-Datei mit UTF-8-Kodierung
file_handler = logging.FileHandler('JSONBuchEditor.log', encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(console_formatter)
logger.addHandler(file_handler)

# 4. Test-Log-Eintrag zur Überprüfung der Logger-Konfiguration
logging.info("Logging configuration successfully set up.")

class JSONLoaderWorker(QObject):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, json_path):
        super().__init__()
        self.json_path = json_path

    def run(self):
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            self.finished.emit(json_data)
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JSON Book Editor")
        self.json_data = None
        self.current_page_index = 0
        self.page_size = (800, 600)  # Standardgröße
        self.show_invisible_elements = False  # Standardmäßig unsichtbare Elemente nicht anzeigen

        # Aktionen mit Icons erstellen und mit Methoden verbinden
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

        # Menüleiste erstellen und Menüs mit Aktionen hinzufügen
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

        # Toolbar erstellen und Aktionen hinzufügen
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
        toolbar.addAction(delete_action)  # Delete-Aktion zur Toolbar hinzufügen

        # Anzeigen sowohl von Icon als auch Text in der Toolbar
        toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        # Hauptlayout erstellen
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Navigationslayout mit vorherigen und nächsten Buttons erstellen
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

        # Datenbankmanager initialisieren
        self.db_manager = DatabaseManager()

        # Neue Menüpunkte für die Datenbank hinzufügen
        self.add_database_menu()

        # Navigation zum Hauptlayout hinzufügen
        main_layout.addLayout(navigation_layout)

        # QGraphicsView für die Anzeige der Szenen erstellen
        self.view = QGraphicsView()
        self.view.setRenderHint(QPainter.Antialiasing)
        main_layout.addWidget(self.view)

        # Aktion für das Anzeigen unsichtbarer Elemente speichern
        self.show_invisible_elements_action = show_invisible_elements_action

        logging.info("GUI initialized and MainWindow displayed.")

    def add_database_menu(self):
        menu = self.menuBar()
        db_menu = menu.addMenu('Datenbank')  # Neues Menü

        load_db_action = QAction('Laden aus Datenbank', self)
        load_db_action.triggered.connect(self.load_from_database)
        save_db_action = QAction('Speichern in Datenbank', self)
        save_db_action.triggered.connect(self.save_to_database)
        delete_db_action = QAction('Löschen aus Datenbank', self)
        delete_db_action.triggered.connect(self.delete_from_database)
        synchronize_action = QAction('Synchronisieren mit Datenbank', self)
        synchronize_action.triggered.connect(self.synchronize_with_database)
        settings_db_action = QAction('Datenbank-Einstellungen', self)
        settings_db_action.triggered.connect(self.database_settings)

        db_menu.addAction(load_db_action)
        db_menu.addAction(save_db_action)
        db_menu.addAction(delete_db_action)
        db_menu.addAction(synchronize_action)  # Neuer Menüpunkt
        db_menu.addSeparator()
        db_menu.addAction(settings_db_action)

    def database_settings(self):
        dialog = DatabaseSettingsDialog(self.db_manager, self)
        if dialog.exec_():
            # Nach dem Speichern der Einstellungen neu verbinden
            self.db_manager.connect()
            QMessageBox.information(self, "Einstellungen gespeichert", "Datenbank-Einstellungen wurden aktualisiert.")

    def load_from_database(self):
        if self.db_manager.collection is None:
            QMessageBox.critical(self, "Verbindungsfehler", "Keine Verbindung zur MongoDB. Bitte überprüfen Sie die Einstellungen.")
            return

        stories = self.db_manager.get_all_stories()
        if not stories:
            QMessageBox.information(self, "Keine Geschichten", "Es wurden keine Geschichten in der Datenbank gefunden.")
            return

        # Dialog zur Auswahl der Geschichte
        story_titles = [story.get('title', f"Geschichte {i+1}") for i, story in enumerate(stories)]
        story, ok = QInputDialog.getItem(self, "Geschichte auswählen", "Wählen Sie eine Geschichte zum Laden:", story_titles, 0, False)
        if ok and story:
            selected_story = next((s for s in stories if s.get('title') == story), None)
            if selected_story:
                self.json_data = selected_story
                self.current_page_index = 0
                # Lesen der Seitengröße
                page_size = self.json_data.get('pageSize', {'width': 800, 'height': 600})
                self.page_size = (page_size.get('width', 800), page_size.get('height', 600))
                self.load_page()
                self.update_page_info()
                logging.info("Geschichte erfolgreich aus der Datenbank geladen.")
                QMessageBox.information(self, "Erfolgreich geladen", f"Geschichte '{story}' wurde aus der Datenbank geladen.")
            else:
                QMessageBox.warning(self, "Nicht gefunden", "Die ausgewählte Geschichte wurde nicht gefunden.")

    def save_to_database(self):
        if not self.json_data:
            QMessageBox.warning(self, "Keine Daten", "Keine Daten vorhanden, die gespeichert werden können.")
            return

        # JSON-Daten validieren, bevor gespeichert wird
        if "title" not in self.json_data or not self.json_data.get("scenes"):
            QMessageBox.critical(self, "Ungültige Daten", "Die Geschichte hat keinen Titel oder enthält keine Szenen.")
            return

        # Bestimmen, ob es sich um eine neue Geschichte handelt oder um eine Aktualisierung
        if "_id" in self.json_data:
            confirmation = QMessageBox.question(
                self, 'Bestätigung', 
                f"Möchten Sie die Geschichte '{self.json_data.get('title', 'Unbekannt')}' in der Datenbank aktualisieren?",
                QMessageBox.Yes | QMessageBox.No, 
                QMessageBox.No
            )
            if confirmation != QMessageBox.Yes:
                return
        else:
            confirmation = QMessageBox.question(
                self, 'Bestätigung', 
                f"Möchten Sie die aktuelle Geschichte '{self.json_data.get('title', 'Unbekannt')}' in die Datenbank speichern?",
                QMessageBox.Yes | QMessageBox.No, 
                QMessageBox.No
            )
            if confirmation != QMessageBox.Yes:
                return

        success = self.db_manager.save_story(self.json_data)
        if success:
            QMessageBox.information(self, "Erfolgreich gespeichert", "Die Geschichte wurde erfolgreich in der Datenbank gespeichert.")
        else:
            QMessageBox.critical(self, "Speicherfehler", "Beim Speichern der Geschichte in der Datenbank ist ein Fehler aufgetreten.")


    def delete_from_database(self):
        if not self.json_data or "_id" not in self.json_data:
            QMessageBox.warning(self, "Keine Daten", "Keine gespeicherte Geschichte vorhanden, die gelöscht werden kann.")
            return

        confirmation = QMessageBox.question(
            self, 'Bestätigung', 
            f"Möchten Sie die Geschichte '{self.json_data.get('title', 'Unbekannt')}' wirklich aus der Datenbank löschen?",
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        if confirmation != QMessageBox.Yes:
            return

        story_id = self.json_data["_id"]
        success = self.db_manager.delete_story(story_id)
        if success:
            QMessageBox.information(self, "Erfolgreich gelöscht", "Die Geschichte wurde erfolgreich aus der Datenbank gelöscht.")
            self.json_data = None
            self.view.setScene(None)
            self.update_page_info()
            logging.info(f"Geschichte mit ID {story_id} gelöscht.")
        else:
            QMessageBox.critical(self, "Löschfehler", "Beim Löschen der Geschichte aus der Datenbank ist ein Fehler aufgetreten.")

    def synchronize_with_database(self):
        if self.db_manager.collection is None:
            QMessageBox.critical(self, "Verbindungsfehler", "Keine Verbindung zur MongoDB. Bitte überprüfen Sie die Einstellungen.")
            return

        confirmation = QMessageBox.question(
            self, 'Synchronisation bestätigen', 
            "Möchten Sie die aktuellen Daten mit der Datenbank synchronisieren? (Speichern Sie zuerst alle Änderungen)",
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        if confirmation != QMessageBox.Yes:
            return

        # Speichern in die Datenbank
        success = self.db_manager.save_story(self.json_data)
        if success:
            QMessageBox.information(self, "Erfolgreich synchronisiert", "Die Daten wurden erfolgreich mit der Datenbank synchronisiert.")
            logging.info("Daten erfolgreich mit der Datenbank synchronisiert.")
        else:
            QMessageBox.critical(self, "Synchronisationsfehler", "Beim Synchronisieren der Daten mit der Datenbank ist ein Fehler aufgetreten.")
            logging.error("Fehler beim Synchronisieren der Daten mit der Datenbank.")

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
            # Lade-Dialog anzeigen
            self.loading_dialog = LoadingDialog(self)
            self.loading_dialog.show()

            # Worker und Thread einrichten
            self.thread = QThread()
            self.worker = JSONLoaderWorker(file_path)
            self.worker.moveToThread(self.thread)

            # Signale verbinden
            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.on_json_loaded)
            self.worker.error.connect(self.on_json_load_error)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            self.worker.error.connect(self.thread.quit)
            self.worker.error.connect(self.worker.deleteLater)

            # Thread starten
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
        # Seitengröße lesen
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

        if self.current_page_index < 0 or self.current_page_index >= total_pages + (1 if has_cover else 0):
            QMessageBox.warning(self, "Range Error", "No more pages available.")
            return

        # Seitengröße aktualisieren
        page_size = self.json_data.get('pageSize', {'width': 800, 'height': 600})
        self.page_size = (page_size.get('width', 800), page_size.get('height', 600))

        if has_cover and self.current_page_index == 0:
            # Cover-Seite laden
            cover_image_path = self.json_data.get('coverImage', '')
            scene = CoverSzene(cover_image_path, self.page_size, self.show_invisible_elements)
        else:
            # Szenen-Seite laden
            scene_index = self.current_page_index - (1 if has_cover else 0)
            scenes = self.json_data.get('scenes', [])
            if 0 <= scene_index < len(scenes):
                scene_data = scenes[scene_index]
                scene = SeitenSzene(scene_data, self.page_size, self.show_invisible_elements)
            else:
                QMessageBox.warning(self, "Range Error", "No more pages available.")
                return

        self.view.setScene(scene)
        self.view.setSceneRect(0, 0, self.page_size[0], self.page_size[1])  # Szenengröße setzen
        self.view.fitInView(scene.sceneRect(), Qt.KeepAspectRatio)
        self.update_page_info()
        logging.info(f"Page {self.current_page_index + 1} loaded.")

    def next_page(self):
        if not self.json_data:
            return
        total_pages = len(self.json_data.get('scenes', []))
        has_cover = bool(self.json_data.get('coverImage'))
        total_pages += 1 if has_cover else 0
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
            # Neues Textelement erstellen
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
            # Zum JSON und zur Szene hinzufügen
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
            # Bilddatei auswählen
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
                # Zum JSON und zur Szene hinzufügen
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
        # Neue Seite erstellen
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
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
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
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
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
            # JSON-Daten aktualisieren
            self.json_data['title'] = data['title']
            self.json_data['description'] = data['description']
            self.json_data['author'] = data.get('author', '')
            self.json_data['illustrator'] = data.get('illustrator', '')
            self.json_data['pageSize'] = data['pageSize']
            self.json_data['coverImage'] = data.get('coverImage', '')
            # Seitengröße aktualisieren
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
                'Confirm Deletion', 
                f'Do you want to delete {len(selected_elements)} selected element(s)?', 
                QMessageBox.Yes | QMessageBox.No, 
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                for element in selected_elements:
                    if hasattr(element, 'text_element'):
                        element_name = element.text_element.get('content', 'Unknown')
                        # Entfernen aus JSON-Daten
                        scene_index = self.current_page_index - (1 if self.json_data.get('coverImage') else 0)
                        current_scene = self.json_data['scenes'][scene_index]
                        current_scene['textElements'] = [
                            te for te in current_scene.get('textElements', []) if te != element.text_element
                        ]
                    elif hasattr(element, 'image_element'):
                        element_name = element.image_element.get('imageUrl', 'Unknown')
                        # Entfernen aus JSON-Daten
                        scene_index = self.current_page_index - (1 if self.json_data.get('coverImage') else 0)
                        current_scene = self.json_data['scenes'][scene_index]
                        current_scene['imageElements'] = [
                            ie for ie in current_scene.get('imageElements', []) if ie != element.image_element
                        ]
                    else:
                        element_name = 'Unknown'
                    self.view.scene().removeItem(element)
                    logging.info(f"Element deleted: {element_name}")
                QMessageBox.information(self, "Deleted", f"{len(selected_elements)} element(s) deleted successfully.")
        else:
            QMessageBox.information(self, "Info", "No elements selected for deletion.")


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
        # Qt-Anwendung initialisieren
        app = QApplication(sys.argv)
        logging.info("Qt application initialized for headless mode.")

        # JSON-Daten laden
        with open(json_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        logging.info(f"JSON data loaded from {json_path}")

        # JSON-Daten validieren
        if not validate_json(json_data):
            logging.error("Invalid JSON data. Process will terminate.")
            sys.exit(1)

        # Überprüfen, ob ein Cover vorhanden ist
        has_cover = bool(json_data.get('coverImage'))
        total_pages = len(json_data.get('scenes', [])) + (1 if has_cover else 0)
        logging.info(f"Total pages: {total_pages} (Cover: {has_cover})")

        # Seitengröße aus JSON oder Standardwerte verwenden
        page_size = json_data.get('pageSize', {'width': 800, 'height': 600})

        # Sicherstellen, dass Breite und Höhe Ganzzahlen sind
        try:
            page_width = int(page_size.get('width', 800))
            page_height = int(page_size.get('height', 600))
            logging.info(f"Page resolution: {page_width}x{page_height}")
        except ValueError as ve:
            logging.error(f"Invalid page resolution in JSON: {ve}")
            sys.exit(1)

        # Lokale Variable statt 'self.page_size' verwenden
        page_size_tuple = (page_width, page_height)

        # Liste zur Speicherung der Pfade der generierten JPGs
        jpg_files = []

        # Durch alle Seiten iterieren
        for index in range(total_pages):
            if has_cover and index == 0:
                # Cover-Seite laden
                cover_image_path = json_data.get('coverImage', '')
                scene = CoverSzene(cover_image_path, page_size_tuple, False)
                logging.info(f"Loading cover page: {cover_image_path}")
            else:
                # Szenen-Seite laden
                scene_index = index - 1 if has_cover else index
                scene_data = json_data['scenes'][scene_index]
                scene = SeitenSzene(scene_data, page_size_tuple, False)
                logging.info(f"Loading scene page {scene_index + 1}")

            # QImage und QPainter zum Rendern erstellen
            image = QImage(page_width, page_height, QImage.Format_ARGB32)
            image.fill(Qt.white)  # Hintergrundfarbe setzen

            painter = QPainter(image)
            scene.render(painter)
            painter.end()

            # Bild als JPG speichern
            jpg_filename = f"page_{index + 1}.jpg"
            image.save(jpg_filename, "JPG")
            jpg_files.append(jpg_filename)
            logging.info(f"Generated {jpg_filename}")

        # Alle JPGs vertikal kombinieren
        combined_image = combine_jpgs_vertically(jpg_files, output_path)
        logging.info(f"Combined image saved as {output_path}")

        # Temporäre JPGs löschen
        for jpg in jpg_files:
            os.remove(jpg)
            logging.info(f"Temporary file deleted: {jpg}")

        # Qt-Anwendung beenden
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

    # Weitere Validierungen können hier hinzugefügt werden
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
            # GUI-Modus starten
            app = QApplication(sys.argv)
            app.setStyle("Fusion")

            # Optional: Stylesheet laden
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
