# dialogs.py

from PyQt5.QtWidgets import (
    QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, 
    QFileDialog, QColorDialog, QFontDialog, QDoubleSpinBox, QSpinBox, QCheckBox, QProgressBar,
    QGraphicsTextItem, QGraphicsPixmapItem, QMessageBox
)
from PyQt5.QtGui import QPixmap, QFont, QColor, QMovie
from PyQt5.QtCore import Qt
import os
import logging

# Eigenschaftseditor importiert nicht mehr direkt Elemente
# from elements import VerschiebbaresTextElement, VerschiebbaresBildElement  # Entfernt

class EinstellungenDialog(QDialog):
    def __init__(self, json_daten, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Buch-Einstellungen")
        self.json_daten = json_daten
        self.cover_image_path = json_daten.get('coverImage', '')
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Titel
        self.title_label = QLabel("Titel:")
        self.title_edit = QLineEdit(self.json_daten.get('title', ''))
        layout.addWidget(self.title_label)
        layout.addWidget(self.title_edit)

        # Beschreibung
        self.description_label = QLabel("Beschreibung:")
        self.description_edit = QLineEdit(self.json_daten.get('description', ''))
        layout.addWidget(self.description_label)
        layout.addWidget(self.description_edit)

        # Seitenbreite
        self.width_label = QLabel("Seitenbreite:")
        self.width_spin = QSpinBox()
        self.width_spin.setRange(100, 10000)
        self.width_spin.setValue(self.json_daten.get('pageSize', {}).get('width', 800))
        layout.addWidget(self.width_label)
        layout.addWidget(self.width_spin)

        # Seitenhöhe
        self.height_label = QLabel("Seitenhöhe:")
        self.height_spin = QSpinBox()
        self.height_spin.setRange(100, 10000)
        self.height_spin.setValue(self.json_daten.get('pageSize', {}).get('height', 600))
        layout.addWidget(self.height_label)
        layout.addWidget(self.height_spin)

        # Coverbild
        self.cover_image_label = QLabel("Coverbild:")
        self.cover_image_preview = QLabel()
        self.cover_image_preview.setFixedSize(200, 150)
        self.cover_image_preview.setStyleSheet("border: 1px solid #ccc;")
        self.update_cover_image_preview()

        self.select_cover_button = QPushButton("Coverbild auswählen")
        self.select_cover_button.clicked.connect(self.select_cover_image)

        cover_layout = QHBoxLayout()
        cover_layout.addWidget(self.cover_image_preview)
        cover_layout.addWidget(self.select_cover_button)

        layout.addWidget(self.cover_image_label)
        layout.addLayout(cover_layout)

        # Optional: Weitere Metadaten
        # Autor
        self.author_label = QLabel("Autor:")
        self.author_edit = QLineEdit(self.json_daten.get('author', ''))
        layout.addWidget(self.author_label)
        layout.addWidget(self.author_edit)

        # Illustrator
        self.illustrator_label = QLabel("Illustrator:")
        self.illustrator_edit = QLineEdit(self.json_daten.get('illustrator', ''))
        layout.addWidget(self.illustrator_label)
        layout.addWidget(self.illustrator_edit)

        # Buttons
        buttons_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Abbrechen")
        self.cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(self.ok_button)
        buttons_layout.addWidget(self.cancel_button)

        layout.addLayout(buttons_layout)
        self.setLayout(layout)

    def select_cover_image(self):
        dateiname, _ = QFileDialog.getOpenFileName(
            self, "Coverbild auswählen", "", "Bilder (*.png *.jpg *.jpeg *.bmp);;Alle Dateien (*)")
        if dateiname:
            self.cover_image_path = dateiname
            self.update_cover_image_preview()

    def update_cover_image_preview(self):
        if self.cover_image_path and os.path.isfile(self.cover_image_path):
            pixmap = QPixmap(self.cover_image_path)
            pixmap = pixmap.scaled(self.cover_image_preview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.cover_image_preview.setPixmap(pixmap)
        else:
            self.cover_image_preview.clear()
            self.cover_image_preview.setText("Kein Coverbild")

    def get_data(self):
        return {
            'title': self.title_edit.text(),
            'description': self.description_edit.text(),
            'pageSize': {
                'width': self.width_spin.value(),
                'height': self.height_spin.value()
            },
            'coverImage': self.cover_image_path,
            'author': self.author_edit.text(),
            'illustrator': self.illustrator_edit.text()
        }


class EigenschaftenDialog(QDialog):
    def __init__(self, element, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Eigenschaften bearbeiten")
        self.element = element
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Prüfen, ob das Element ein Textelement oder Bildelement ist
        if isinstance(self.element, QGraphicsTextItem):
            # Text-Eigenschaften bearbeiten
            self.content_label = QLabel("Text:")
            self.content_edit = QLineEdit(self.element.toPlainText())

            self.font_button = QPushButton("Schriftart wählen")
            self.font_button.clicked.connect(self.choose_font)

            self.color_button = QPushButton("Textfarbe wählen")
            self.color_button.clicked.connect(self.choose_color)

            self.width_label = QLabel("Breite:")
            self.width_edit = QDoubleSpinBox()
            self.width_edit.setMaximum(10000)
            self.width_edit.setValue(getattr(self.element, 'text_element', {}).get('width', 300))

            self.layer_label = QLabel("Ebene (layer):")
            self.layer_spin = QSpinBox()
            self.layer_spin.setValue(getattr(self.element, 'text_element', {}).get('layer', 0))

            self.rotation_label = QLabel("Rotation:")
            self.rotation_spin = QDoubleSpinBox()
            self.rotation_spin.setRange(0, 360)
            self.rotation_spin.setValue(getattr(self.element, 'text_element', {}).get('rotation', 0))

            self.opacity_label = QLabel("Deckkraft (opacity):")
            self.opacity_spin = QDoubleSpinBox()
            self.opacity_spin.setRange(0, 1)
            self.opacity_spin.setSingleStep(0.1)
            self.opacity_spin.setValue(getattr(self.element, 'text_element', {}).get('opacity', 1.0))

            self.visible_checkbox = QCheckBox("Sichtbar")
            self.visible_checkbox.setChecked(getattr(self.element, 'text_element', {}).get('visible', True))

            layout.addWidget(self.content_label)
            layout.addWidget(self.content_edit)
            layout.addWidget(self.font_button)
            layout.addWidget(self.color_button)
            layout.addWidget(self.width_label)
            layout.addWidget(self.width_edit)
            layout.addWidget(self.layer_label)
            layout.addWidget(self.layer_spin)
            layout.addWidget(self.rotation_label)
            layout.addWidget(self.rotation_spin)
            layout.addWidget(self.opacity_label)
            layout.addWidget(self.opacity_spin)
            layout.addWidget(self.visible_checkbox)

        elif isinstance(self.element, QGraphicsPixmapItem):
            # Bild-Eigenschaften bearbeiten
            self.width_label = QLabel("Breite:")
            self.width_edit = QDoubleSpinBox()
            self.width_edit.setMaximum(10000)
            self.width_edit.setValue(getattr(self.element, 'image_element', {}).get('width', self.element.pixmap().width()))

            self.height_label = QLabel("Höhe:")
            self.height_edit = QDoubleSpinBox()
            self.height_edit.setMaximum(10000)
            self.height_edit.setValue(getattr(self.element, 'image_element', {}).get('height', self.element.pixmap().height()))

            self.prompt_label = QLabel("Image Prompt:")
            self.prompt_edit = QLineEdit(getattr(self.element, 'image_element', {}).get('imagePrompt', ''))

            self.layer_label = QLabel("Ebene (layer):")
            self.layer_spin = QSpinBox()
            self.layer_spin.setValue(getattr(self.element, 'image_element', {}).get('layer', 0))

            self.rotation_label = QLabel("Rotation:")
            self.rotation_spin = QDoubleSpinBox()
            self.rotation_spin.setRange(0, 360)
            self.rotation_spin.setValue(getattr(self.element, 'image_element', {}).get('rotation', 0))

            self.opacity_label = QLabel("Deckkraft (opacity):")
            self.opacity_spin = QDoubleSpinBox()
            self.opacity_spin.setRange(0, 1)
            self.opacity_spin.setSingleStep(0.1)
            self.opacity_spin.setValue(getattr(self.element, 'image_element', {}).get('opacity', 1.0))

            self.visible_checkbox = QCheckBox("Sichtbar")
            self.visible_checkbox.setChecked(getattr(self.element, 'image_element', {}).get('visible', True))

            self.user_provided_checkbox = QCheckBox("Vom Benutzer bereitgestellt")
            self.user_provided_checkbox.setChecked(getattr(self.element, 'image_element', {}).get('userProvided', False))

            layout.addWidget(self.width_label)
            layout.addWidget(self.width_edit)
            layout.addWidget(self.height_label)
            layout.addWidget(self.height_edit)
            layout.addWidget(self.prompt_label)
            layout.addWidget(self.prompt_edit)
            layout.addWidget(self.layer_label)
            layout.addWidget(self.layer_spin)
            layout.addWidget(self.rotation_label)
            layout.addWidget(self.rotation_spin)
            layout.addWidget(self.opacity_label)
            layout.addWidget(self.opacity_spin)
            layout.addWidget(self.visible_checkbox)
            layout.addWidget(self.user_provided_checkbox)

        buttons_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.apply_changes)
        self.cancel_button = QPushButton("Abbrechen")
        self.cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(self.ok_button)
        buttons_layout.addWidget(self.cancel_button)

        layout.addLayout(buttons_layout)
        self.setLayout(layout)

    def choose_color(self):
        if isinstance(self.element, QGraphicsTextItem):
            color = QColorDialog.getColor(Qt.black, self, "Textfarbe wählen")
            if color.isValid():
                # Dynamisch das Attribut 'text_element' aktualisieren
                if hasattr(self.element, 'text_element'):
                    self.element.text_element['color'] = color.name()
                self.element.setDefaultTextColor(color)

    def choose_font(self):
        if isinstance(self.element, QGraphicsTextItem):
            font, ok = QFontDialog.getFont(self.element.font(), self, "Schriftart wählen")
            if ok:
                self.element.setFont(font)
                # Dynamisch das Attribut 'text_element' aktualisieren
                if hasattr(self.element, 'text_element'):
                    self.element.text_element['fontFamily'] = font.family()
                    self.element.text_element['fontSize'] = font.pointSize()
                    # Schriftstil speichern
                    styles = []
                    if font.bold():
                        styles.append('bold')
                    if font.italic():
                        styles.append('italic')
                    if font.underline():
                        styles.append('underline')
                    self.element.text_element['fontStyle'] = ' '.join(styles) if styles else 'normal'

    def apply_changes(self):
        if isinstance(self.element, QGraphicsTextItem):
            # Dynamisch das Attribut 'text_element' aktualisieren
            if hasattr(self.element, 'text_element'):
                self.element.text_element['content'] = self.content_edit.text()
                self.element.setPlainText(self.content_edit.text())

                self.element.text_element['width'] = self.width_edit.value()
                self.element.setTextWidth(self.width_edit.value())

                self.element.text_element['layer'] = self.layer_spin.value()
                self.element.setZValue(self.layer_spin.value())

                self.element.text_element['rotation'] = self.rotation_spin.value()
                self.element.setRotation(self.rotation_spin.value())

                self.element.text_element['opacity'] = self.opacity_spin.value()
                self.element.setOpacity(self.opacity_spin.value())

                self.element.text_element['visible'] = self.visible_checkbox.isChecked()
                self.element.user_visible = self.visible_checkbox.isChecked()
                self.element.update_visibility()

        elif isinstance(self.element, QGraphicsPixmapItem):
            # Dynamisch das Attribut 'image_element' aktualisieren
            if hasattr(self.element, 'image_element'):
                self.element.image_element['width'] = self.width_edit.value()
                self.element.image_element['height'] = self.height_edit.value()
                self.element.image_element['imagePrompt'] = self.prompt_edit.text()
                self.element.image_element['layer'] = self.layer_spin.value()
                self.element.image_element['rotation'] = self.rotation_spin.value()
                self.element.image_element['opacity'] = self.opacity_spin.value()
                self.element.image_element['visible'] = self.visible_checkbox.isChecked()
                self.element.image_element['userProvided'] = self.user_provided_checkbox.isChecked()

                self.element.setZValue(self.layer_spin.value())
                self.element.setRotation(self.rotation_spin.value())
                self.element.setOpacity(self.opacity_spin.value())
                self.element.update_visibility()

                # Bild neu laden und skalieren
                self.element.bild_laden()

        self.accept()


class DatabaseSettingsDialog(QDialog):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Datenbank-Einstellungen")
        self.db_manager = db_manager
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Host
        host_layout = QHBoxLayout()
        host_label = QLabel("Host:")
        self.host_input = QLineEdit(self.db_manager.host)
        host_layout.addWidget(host_label)
        host_layout.addWidget(self.host_input)
        layout.addLayout(host_layout)
        
        # Port
        port_layout = QHBoxLayout()
        port_label = QLabel("Port:")
        self.port_input = QLineEdit(str(self.db_manager.port))
        port_layout.addWidget(port_label)
        port_layout.addWidget(self.port_input)
        layout.addLayout(port_layout)
        
        # Datenbankname
        db_name_layout = QHBoxLayout()
        db_name_label = QLabel("Datenbankname:")
        self.db_name_input = QLineEdit(self.db_manager.db_name)
        db_name_layout.addWidget(db_name_label)
        db_name_layout.addWidget(self.db_name_input)
        layout.addLayout(db_name_layout)
        
        # Sammlung
        collection_layout = QHBoxLayout()
        collection_label = QLabel("Sammlung:")
        self.collection_input = QLineEdit(self.db_manager.collection_name)
        collection_layout.addWidget(collection_label)
        collection_layout.addWidget(self.collection_input)
        layout.addLayout(collection_layout)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        save_button = QPushButton("Speichern")
        save_button.clicked.connect(self.save_settings)
        cancel_button = QPushButton("Abbrechen")
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addStretch()
        buttons_layout.addWidget(save_button)
        buttons_layout.addWidget(cancel_button)
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)

    def save_settings(self):
        host = self.host_input.text().strip()
        port_text = self.port_input.text().strip()
        db_name = self.db_name_input.text().strip()
        collection_name = self.collection_input.text().strip()
        
        # Validierung der Eingaben
        if not host or not port_text or not db_name or not collection_name:
            QMessageBox.warning(self, "Ungültige Eingaben", "Alle Felder müssen ausgefüllt sein.")
            return
        
        try:
            port = int(port_text)
        except ValueError:
            QMessageBox.warning(self, "Ungültige Eingabe", "Der Port muss eine Zahl sein.")
            return
        
        # Aktualisieren der Datenbank-Einstellungen
        self.db_manager.update_settings(host, port, db_name, collection_name)
        QMessageBox.information(self, "Einstellungen gespeichert", "Datenbank-Einstellungen wurden aktualisiert.")
        self.accept()


class LoadingDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Lade Daten...")
        self.setModal(True)
        self.setFixedSize(300, 150)
        
        layout = QVBoxLayout()
        
        label = QLabel("Bitte warten, die Daten werden geladen...")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        
        # Verwenden Sie einen unendlichen Fortschrittsbalken als Fallback
        self.progress = QProgressBar(self)
        self.progress.setRange(0, 0)  # Unendlicher Fortschrittsbalken
        layout.addWidget(self.progress)
        
        # Optional: Spinner-GIF hinzufügen, falls vorhanden
        if os.path.exists("spinner.gif"):
            self.spinner = QLabel(self)
            self.movie = QMovie("spinner.gif")
            self.spinner.setMovie(self.movie)
            self.spinner.setAlignment(Qt.AlignCenter)
            layout.addWidget(self.spinner)
            self.movie.start()
        
        self.setLayout(layout)
