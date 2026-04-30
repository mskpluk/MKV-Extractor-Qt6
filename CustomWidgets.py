#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Widgets Qt personnalisés utilisés par l'application."""

from PySide6.QtWidgets import QMenu, QPushButton, QTextEdit, QToolButton
from PySide6.QtCore import Signal, QCoreApplication, QDir, Qt
from PySide6.QtGui import QAction, QCursor, QIcon, QKeySequence, QShortcut


#############################################################################
def MultiVar(*Values):
    """Retourne la première valeur valide d'une liste, ou "" si toutes sont falsy."""
    for Value in Values:
        if Value:
            return Value
    return ""


#############################################################################
class QuitButton(QPushButton):
    """QPushButton gérant le clic droit pour déclencher un redémarrage."""

    signalReboot = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.handleContextMenu)

    def handleContextMenu(self, pos):
        """Affiche un menu contextuel proposant le redémarrage."""
        menu = QMenu(self)
        reboot_action = menu.addAction(
            QCoreApplication.translate("QuitButton", "Reboot")
        )
        action = menu.exec(self.mapToGlobal(pos))
        if action == reboot_action:
            self.signalReboot.emit()

    def mousePressEvent(self, event):
        """Émet signalReboot sur clic droit."""
        if event.button() == Qt.RightButton:
            self.signalReboot.emit()
            event.accept()
            return
        super().mousePressEvent(event)


#############################################################################
class QActionCustom(QAction):
    """QAction affichant l'info-bulle uniquement quand l'action est désactivée."""

    def __init__(self, Parent=None):
        super().__init__(Parent)
        self._default_tooltip = ""
        self._is_enabled = self.isEnabled()

    def setEnabled(self, State):
        self._is_enabled = State
        self.setToolTip("" if State else self._default_tooltip)
        super().setEnabled(State)

    def setToolTip(self, ToolTip):
        self._default_tooltip = ToolTip
        super().setToolTip("" if self._is_enabled else ToolTip)


#############################################################################
class QActionMenuCustom(QAction):
    """QAction cochant automatiquement son QToolButton parent lors du déclenchement."""

    def __init__(self, Parent=None, *args, **kwargs):
        super().__init__(Parent, *args, **kwargs)
        self.ToolButton = None
        self.triggered.connect(self.toolButtonCheck)

    def toolButtonCheck(self, value):
        """Coche le QToolButton parent si l'action vient d'être activée."""
        if not value:
            return
        if not self.ToolButton:
            parent = self.parent()
            if not isinstance(parent, QMenu):
                return
            grand_parent = parent.parent()
            if not isinstance(grand_parent, QToolButton):
                return
            self.ToolButton = grand_parent
        if self.ToolButton.isEnabled() and not self.ToolButton.isChecked():
            self.ToolButton.setChecked(True)


#############################################################################
class QTextEditCustom(QTextEdit):
    """QTextEdit avec menu contextuel enrichi (nettoyage + export)."""

    def __init__(self, Parent=None):
        super().__init__(Parent)

        self.export_shortcut = QShortcut("ctrl+e", self)
        self.export_shortcut.activated.connect(self.export_action)

        self.clean_shortcut = QShortcut("ctrl+d", self)
        self.clean_shortcut.activated.connect(self.clean_action)

        # Textes initialisés en anglais, mis à jour par retranslate() à chaque changement de langue
        self._text_clean = "Clean the information fee&dback box"
        self._text_export = "&Export info to ~/InfoMKVExtractorQt6.txt"

    def retranslate(self):
        """Met à jour les textes du menu contextuel dans la langue courante."""
        self._text_clean = QCoreApplication.translate(
            "QTextEditCustom", "Clean the information fee&dback box"
        )
        self._text_export = QCoreApplication.translate(
            "QTextEditCustom", "&Export info to ~/InfoMKVExtractorQt6.txt"
        )

    def contextMenuEvent(self, event):
        """Menu contextuel avec actions Nettoyer et Exporter."""
        menu = self.createStandardContextMenu()
        menu.addSeparator()

        clean_action = QAction(
            QIcon.fromTheme("edit-clear", QIcon(":/img/edit-clear.png")),
            self._text_clean,
            menu,
        )
        clean_action.setShortcut(QKeySequence("ctrl+d"))
        clean_action.triggered.connect(self.clean_action)

        export_action = QAction(
            QIcon.fromTheme("document-export", QIcon(":/img/document-export.png")),
            self._text_export,
            menu,
        )
        export_action.setShortcut(QKeySequence("ctrl+e"))
        export_action.triggered.connect(self.export_action)

        if not self.toPlainText():
            export_action.setEnabled(False)
            clean_action.setEnabled(False)

        menu.addAction(clean_action)
        menu.addAction(export_action)
        menu.exec(QCursor.pos())
        event.accept()

    def clean_action(self, *args):
        """Vide le contenu du QTextEdit."""
        self.clear()

    def export_action(self, *args):
        """Exporte le contenu vers ~/InfoMKVExtractorQt6.txt."""
        text = self.toPlainText()
        if not text:
            return
        export_path = f"{QDir.homePath()}/InfoMKVExtractorQt6.txt"
        try:
            with open(export_path, "w", encoding="utf-8") as file:
                file.write(text)
        except IOError as e:
            print(f"Erreur lors de l'exportation: {e}")
