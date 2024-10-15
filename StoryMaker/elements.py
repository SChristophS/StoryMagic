# elements.py

from PyQt5.QtWidgets import QGraphicsTextItem, QGraphicsPixmapItem, QGraphicsItem, QMenu, QMessageBox
from PyQt5.QtGui import QFont, QColor, QPainter, QPixmap
from PyQt5.QtCore import Qt, QPointF
import requests
import os
import logging


class VerschiebbaresTextElement(QGraphicsTextItem):
    def __init__(self, text_element, parent=None):
        super().__init__(parent)
        self.text_element = text_element
        self.setPlainText(text_element['content'])
        font = QFont(text_element.get('fontFamily', 'Arial'), text_element.get('fontSize', 12))

        # Schriftstil anwenden
        font_style = text_element.get('fontStyle', 'normal')
        font.setBold('bold' in font_style)
        font.setItalic('italic' in font_style)
        font.setUnderline('underline' in font_style)

        self.setFont(font)
        color = QColor(text_element.get('color', '#000000'))
        self.setDefaultTextColor(color)
        self.setTextWidth(text_element.get('width', 300))
        self.setFlags(
            QGraphicsItem.ItemIsMovable |
            QGraphicsItem.ItemIsSelectable |
            QGraphicsItem.ItemIsFocusable
        )
        self.setPos(text_element['position']['x'], text_element['position']['y'])
        self.setAcceptHoverEvents(True)
        self.setZValue(text_element.get('layer', 0))
        self.setRotation(text_element.get('rotation', 0))
        # Opacity wird in update_visibility gehandhabt
        self.user_visible = text_element.get('visible', True)
        self.update_visibility()

    def update_visibility(self):
        if self.scene() and hasattr(self.scene(), 'show_invisible_elements'):
            show_invisible = self.scene().show_invisible_elements
        else:
            show_invisible = False

        if self.user_visible:
            self.setOpacity(self.text_element.get('opacity', 1.0))
            self.setEnabled(True)
        else:
            if show_invisible:
                self.setOpacity(0.3)
                self.setEnabled(True)
            else:
                self.setOpacity(0)
                self.setEnabled(False)

    def paint(self, painter, option, widget):
        self.update_visibility()
        super().paint(painter, option, widget)

    def focusOutEvent(self, event):
        # Aktualisieren des Textinhalts im JSON-Daten
        self.text_element['content'] = self.toPlainText()
        super().focusOutEvent(event)

    def mouseDoubleClickEvent(self, event):
        self.setTextInteractionFlags(Qt.TextEditorInteraction)
        self.setFocus()
        super().mouseDoubleClickEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self.show_context_menu(event.pos())
        else:
            self.setTextInteractionFlags(Qt.NoTextInteraction)
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        # Aktualisieren der Position im JSON-Daten
        self.text_element['position']['x'] = int(self.pos().x())
        self.text_element['position']['y'] = int(self.pos().y())
        super().mouseReleaseEvent(event)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange and self.scene():
            new_pos = value.toPointF()
            # Begrenzen der Position auf die Szenegrenzen
            rect = self.scene().sceneRect()
            item_rect = self.boundingRect()
            new_rect = item_rect.translated(new_pos)
            if not rect.contains(new_rect):
                # Anpassung der X-Position
                if new_rect.left() < rect.left():
                    new_pos.setX(rect.left() - item_rect.left())
                elif new_rect.right() > rect.right():
                    new_pos.setX(rect.right() - item_rect.right())
                # Anpassung der Y-Position
                if new_rect.top() < rect.top():
                    new_pos.setY(rect.top() - item_rect.top())
                elif new_rect.bottom() > rect.bottom():
                    new_pos.setY(rect.bottom() - item_rect.bottom())
                return QPointF(new_pos)
        return super().itemChange(change, value)

    def show_context_menu(self, pos):
        menu = QMenu()
        delete_action = menu.addAction("Löschen")
        properties_action = menu.addAction("Eigenschaften")
        
        # Zugriff auf den View und Konvertierung der Position
        views = self.scene().views()
        if views:
            view = views[0]
            global_pos = view.mapToGlobal(view.mapFromScene(self.mapToScene(pos).toPoint()))
            action = menu.exec_(global_pos)
        else:
            action = menu.exec_(pos.toPoint())
        
        if action == delete_action:
            reply = QMessageBox.question(
                None, 
                'Bestätigung', 
                'Möchten Sie dieses Textelement wirklich löschen?', 
                QMessageBox.Yes | QMessageBox.No, 
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.scene().removeItem(self)
                logging.info(f"Textelement gelöscht: {self.text_element['content']}")
        elif action == properties_action:
            self.show_properties()

    def show_properties(self):
        try:
            from dialogs import EigenschaftenDialog  # Import innerhalb der Methode
            dialog = EigenschaftenDialog(self)
            if dialog.exec_():
                pass  # Änderungen wurden bereits angewendet
        except ImportError as e:
            logging.error(f"Fehler beim Importieren von EigenschaftenDialog: {e}")


class VerschiebbaresBildElement(QGraphicsPixmapItem):
    def __init__(self, image_element, parent=None):
        super().__init__(parent)
        self.image_element = image_element
        self.setFlags(
            QGraphicsItem.ItemIsMovable |
            QGraphicsItem.ItemIsSelectable
        )
        self.setPos(image_element['position']['x'], image_element['position']['y'])
        self.setAcceptHoverEvents(True)
        self.setZValue(image_element.get('layer', 0))
        self.setRotation(image_element.get('rotation', 0))
        # Opacity wird in update_visibility gehandhabt
        self.user_visible = image_element.get('visible', True)
        self.bild_laden()
        self.update_visibility()

    def update_visibility(self):
        if self.scene() and hasattr(self.scene(), 'show_invisible_elements'):
            show_invisible = self.scene().show_invisible_elements
        else:
            show_invisible = False

        if self.user_visible:
            self.setOpacity(self.image_element.get('opacity', 1.0))
            self.setEnabled(True)
        else:
            if show_invisible:
                self.setOpacity(0.3)
                self.setEnabled(True)
            else:
                self.setOpacity(0)
                self.setEnabled(False)

    def paint(self, painter, option, widget):
        self.update_visibility()
        super().paint(painter, option, widget)

    def bild_laden(self):
        try:
            if self.image_element.get('userProvided', False):
                # Benutzer soll dieses Bild bereitstellen
                # Placeholder-Bild erstellen
                breite = self.image_element.get('width', 200)
                hoehe = self.image_element.get('height', 150)
                image = QPixmap(int(breite), int(hoehe))
                image.fill(QColor('lightgray'))
                painter = QPainter(image)
                painter.setPen(Qt.black)
                painter.drawText(image.rect(), Qt.AlignCenter, "Benutzerbild")
                painter.end()
                self.setPixmap(image)
            else:
                image_url = self.image_element['imageUrl']
                if image_url.startswith('http://') or image_url.startswith('https://'):
                    response = requests.get(image_url)
                    image = QPixmap()
                    image.loadFromData(response.content)
                else:
                    if os.path.isfile(image_url):
                        image = QPixmap(image_url)
                    else:
                        raise FileNotFoundError(f"Datei nicht gefunden: {image_url}")
                breite = self.image_element.get('width', image.width())
                hoehe = self.image_element.get('height', image.height())
                self.setPixmap(image.scaled(int(breite), int(hoehe), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        except Exception as e:
            logging.error(f"Fehler beim Laden des Bildes: {e}")
            # Fallback: Platzhalter-Bild anzeigen
            breite = self.image_element.get('width', 200)
            hoehe = self.image_element.get('height', 150)
            image = QPixmap(int(breite), int(hoehe))
            image.fill(QColor('red'))
            painter = QPainter(image)
            painter.setPen(Qt.white)
            painter.drawText(image.rect(), Qt.AlignCenter, "Fehler")
            painter.end()
            self.setPixmap(image)

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self.show_context_menu(event.pos())
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        # Aktualisieren der Position im JSON-Daten
        self.image_element['position']['x'] = int(self.pos().x())
        self.image_element['position']['y'] = int(self.pos().y())
        super().mouseReleaseEvent(event)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange and self.scene():
            new_pos = value.toPointF()
            # Begrenzen der Position auf die Szenegrenzen
            rect = self.scene().sceneRect()
            item_rect = self.boundingRect()
            new_rect = item_rect.translated(new_pos)
            if not rect.contains(new_rect):
                # Anpassung der X-Position
                if new_rect.left() < rect.left():
                    new_pos.setX(rect.left() - item_rect.left())
                elif new_rect.right() > rect.right():
                    new_pos.setX(rect.right() - item_rect.right())
                # Anpassung der Y-Position
                if new_rect.top() < rect.top():
                    new_pos.setY(rect.top() - item_rect.top())
                elif new_rect.bottom() > rect.bottom():
                    new_pos.setY(rect.bottom() - item_rect.bottom())
                return QPointF(new_pos)
        return super().itemChange(change, value)

    def show_context_menu(self, pos):
        menu = QMenu()
        delete_action = menu.addAction("Löschen")
        properties_action = menu.addAction("Eigenschaften")
        
        # Zugriff auf den View und Konvertierung der Position
        views = self.scene().views()
        if views:
            view = views[0]
            global_pos = view.mapToGlobal(view.mapFromScene(self.mapToScene(pos).toPoint()))
            action = menu.exec_(global_pos)
        else:
            action = menu.exec_(pos.toPoint())
        
        if action == delete_action:
            reply = QMessageBox.question(
                None, 
                'Bestätigung', 
                'Möchten Sie dieses Bildelement wirklich löschen?', 
                QMessageBox.Yes | QMessageBox.No, 
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.scene().removeItem(self)
                logging.info(f"Bildelement gelöscht: {self.image_element['imageUrl']}")
        elif action == properties_action:
            self.show_properties()

    def show_properties(self):
        try:
            from dialogs import EigenschaftenDialog  # Import innerhalb der Methode
            dialog = EigenschaftenDialog(self)
            if dialog.exec_():
                pass  # Änderungen wurden bereits angewendet
        except ImportError as e:
            logging.error(f"Fehler beim Importieren von EigenschaftenDialog: {e}")


class HintergrundElement(QGraphicsPixmapItem):
    def __init__(self, background_url, page_size, parent=None):
        super().__init__(parent)
        self.setZValue(-1000)  # Hintergrund weit nach hinten setzen
        self.setPos(0, 0)
        self.page_size = page_size
        self.lade_hintergrund(background_url)

    def lade_hintergrund(self, background_url):
        try:
            if background_url.startswith('http://') or background_url.startswith('https://'):
                response = requests.get(background_url)
                image = QPixmap()
                image.loadFromData(response.content)
            else:
                if os.path.isfile(background_url):
                    image = QPixmap(background_url)
                else:
                    raise FileNotFoundError(f"Datei nicht gefunden: {background_url}")
            self.setPixmap(image.scaled(
                self.page_size[0], self.page_size[1], Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
        except Exception as e:
            logging.error(f"Fehler beim Laden des Hintergrundbildes: {e}")
            # Fallback: Weißes Hintergrundbild
            pixmap = QPixmap(self.page_size[0], self.page_size[1])
            pixmap.fill(Qt.white)
            self.setPixmap(pixmap)

    # Hintergrund soll nicht interaktiv sein
    def mousePressEvent(self, event):
        pass

    def mouseReleaseEvent(self, event):
        pass

    def mouseDoubleClickEvent(self, event):
        pass
