# scenes.py

import logging
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem, QGraphicsPixmapItem
from PyQt5.QtGui import QFont, QBrush, QPen, QColor
from PyQt5.QtCore import Qt
import os

from elements import VerschiebbaresTextElement, VerschiebbaresBildElement, HintergrundElement


class SeitenSzene(QGraphicsScene):
    def __init__(self, scene_data, page_size, show_invisible_elements=False, parent=None):
        super().__init__(parent)
        self.scene_data = scene_data
        try:
            self.page_width = int(page_size[0])
            self.page_height = int(page_size[1])
            logging.info(f"SeitenSzene initialisiert mit Größe: {self.page_width}x{self.page_height}")
        except (ValueError, TypeError) as e:
            logging.error(f"Ungültige Seitenauflösung: {e}")
            self.page_width, self.page_height = 800, 600  # Fallback auf Standardwerte

        self.setSceneRect(0, 0, self.page_width, self.page_height)
        self.show_invisible_elements = show_invisible_elements
        self.szene_initialisieren()

    def szene_initialisieren(self):
        # Zeichne ein Rechteck, das die Seitengröße darstellt
        border_rect = QGraphicsRectItem(0, 0, self.page_width, self.page_height)
        border_pen = QPen(QColor(255, 0, 0), 2)  # Roter Rand, 2px breit
        border_rect.setPen(QPen(border_pen))
        border_rect.setBrush(QBrush(Qt.NoBrush))  # Transparente Füllung
        border_rect.setZValue(-1)  # Hinter anderen Elementen
        self.addItem(border_rect)
        logging.info("Seitenbegrenzung hinzugefügt.")

        # Hintergrund hinzufügen
        background_url = self.scene_data.get('background')
        if background_url and os.path.isfile(background_url):
            hintergrund = HintergrundElement(background_url, (self.page_width, self.page_height))
            self.addItem(hintergrund)

        # Hinzufügen von Bildelementen
        for image_element in self.scene_data.get('imageElements', []):
            item = VerschiebbaresBildElement(image_element)
            self.addItem(item)

        # Hinzufügen von Textelementen
        for text_element in self.scene_data.get('textElements', []):
            item = VerschiebbaresTextElement(text_element)
            self.addItem(item)

        # Auswahl zurücksetzen
        self.clearSelection()

    def render(self, painter):
        super().render(painter)


class CoverSzene(QGraphicsScene):
    def __init__(self, cover_image_path, page_size, show_invisible_elements=False, parent=None):
        super().__init__(parent)
        self.cover_image_path = cover_image_path
        try:
            self.page_width = int(page_size[0])
            self.page_height = int(page_size[1])
            logging.info(f"CoverSzene initialisiert mit Größe: {self.page_width}x{self.page_height}")
        except (ValueError, TypeError) as e:
            logging.error(f"Ungültige Seitenauflösung für Cover: {e}")
            self.page_width, self.page_height = 800, 600  # Fallback auf Standardwerte

        self.setSceneRect(0, 0, self.page_width, self.page_height)
        self.show_invisible_elements = show_invisible_elements
        self.szene_initialisieren()

    def szene_initialisieren(self):
        # Zeichne ein Rechteck, das die Seitengröße darstellt
        border_rect = QGraphicsRectItem(0, 0, self.page_width, self.page_height)
        border_pen = QPen(QColor(255, 0, 0), 2)  # Roter Rand, 2px breit
        border_rect.setPen(QPen(border_pen))
        border_rect.setBrush(QBrush(Qt.NoBrush))  # Transparente Füllung
        border_rect.setZValue(-1)  # Hinter anderen Elementen
        self.addItem(border_rect)
        logging.info("Cover-Seitenbegrenzung hinzugefügt.")

        # Hintergrund hinzufügen
        if self.cover_image_path and os.path.isfile(self.cover_image_path):
            hintergrund = HintergrundElement(self.cover_image_path, (self.page_width, self.page_height))
            self.addItem(hintergrund)
        else:
            # Falls kein Coverbild vorhanden ist, leere Seite anzeigen
            rect_item = QGraphicsRectItem(0, 0, self.page_width, self.page_height)
            rect_item.setBrush(QBrush(Qt.white))
            pen = QPen()
            pen.setStyle(Qt.NoPen)
            rect_item.setPen(pen)
            self.addItem(rect_item)
            # Text anzeigen, dass kein Coverbild vorhanden ist
            text_item = QGraphicsTextItem("Kein Coverbild vorhanden")
            font = QFont("Arial", 24)
            text_item.setFont(font)
            text_item.setDefaultTextColor(Qt.gray)
            text_item.setTextWidth(self.page_width)
            text_item.setPos(0, self.page_height / 2 - 50)
            text_item.setTextInteractionFlags(Qt.NoTextInteraction)
            self.addItem(text_item)

    def render(self, painter):
        super().render(painter)
