#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Mixin de gestion des outils MKV (MKVInfo, MKVMerge, MKVView, MKClean, MKValidator, MKVConvert)."""

import state
from PySide6.QtWidgets import QCheckBox, QMessageBox
from PySide6.QtCore import QFileInfo, QProcess, Qt, QUrl
from PySide6.QtGui import QDesktopServices, QIcon, QPixmap
from QFileDialogCustom.QFileDialogCustom import QFileDialogCustom


class MKVToolsMixin:
    # ========================================================================
    def _startDetached(self, executable, arguments):
        """Lance un processus détaché en silence (stdout/stderr redirigés vers /dev/null)."""
        p = QProcess()
        p.setStandardOutputFile(QProcess.nullDevice())
        p.setStandardErrorFile(QProcess.nullDevice())
        p.setProgram(executable)
        p.setArguments(arguments)
        p.startDetached()

    def MKVInfoGui(self):
        """Fonction ouvrant le fichier MKV avec le logiciel MKVInfo en mode détaché."""
        self._startDetached(
            state.Configs.value("Location/MKVToolNix"),
            ["--info", state.Configs.value("InputFile")],
        )

    # ========================================================================
    def MKVMergeGui(self):
        """Fonction ouvrant le fichier MKV avec le logiciel MKVToolNix-Gui en mode détaché."""
        self._startDetached(
            state.Configs.value("Location/MKVToolNix"),
            [state.Configs.value("InputFile")],
        )

    # ========================================================================
    def MKVView(self):
        """Fonction ouvrant le fichier MKV avec le logiciel de lecture par défaut."""
        QDesktopServices.openUrl(QUrl.fromLocalFile(state.Configs.value("InputFile")))

    # ========================================================================
    def MKClean(self):
        """Fonction lançant MKClean sur le fichier MKV."""
        InputFileName = QFileInfo(state.Configs.value("InputFile")).fileName()

        ### On crée automatiquement l'adresse de sortie
        if state.Configs.value("MKCleanRename") and (
            state.Configs.value("MKCleanSameFolder") or state.Configs.value("MKCleanThisFolder")
        ):
            ## Utilisation du même dossier en entré et sorti ou du dossier choisi
            MKCleanTemp = "{}/Clean_{}".format(
                state.Configs.value("OutputFolder", state.Configs.value("MKCleanThisFolder")),
                InputFileName,
            )

        ### Fenêtre de sélection de sortie du fichier MKV
        else:
            ## Création de la fenêtre
            FileDialogCustom = QFileDialogCustom(
                self,
                self.Trad["SelectFileOut"],
                state.Configs.value("OutputFolder"),
                "Matroska file (*.mkv *.mks *.mka *.mk3d *.webm *.webmv *.webma)",
            )

            MKCleanTemp = FileDialogCustom.createWindow(
                "File",
                "Save",
                None,
                Qt.Tool,
                FileName="Clean_{}".format(InputFileName),
                AlreadyExistsTest=state.Configs.value("AlreadyExistsTest", False),
                Language=state.Configs.value("Language"),
            )

        ### Arrêt de la fonction s'il n'y a pas de fichier de choisi
        if not MKCleanTemp:
            return

        ### Ajout du fichier de sortie dans le listing des fichiers
        TempFiles = [MKCleanTemp]

        ### Commande finale
        state.TempValues.setValue(
            "Command",
            [
                "MKClean",
                state.Configs.value("Location/MKClean"),
                ["--optimize", state.Configs.value("InputFile"), MKCleanTemp],
                [state.Configs.value("InputFile")],
            ],
        )

        ### Affichage des retours
        self.SetInfo(
            self.Trad["WorkProgress"].format(state.TempValues.value("Command")[0]),
            "800080",
            True,
            True,
        )
        self.SetInfo(
            self.Trad["WorkCmd"].format(
                state.TempValues.value("Command")[1]
                + " "
                + " ".join(state.TempValues.value("Command")[2])
            )
        )

        ### Lancement de la commande après blocage des widgets
        self.WorkInProgress(True)
        self.WorkStart()

    # ========================================================================
    def MKValidator(self):
        """Fonction lançant MKValidator sur le fichier MKV."""
        ### Code à exécuter
        state.TempValues.setValue(
            "Command",
            [
                "MKValidator",
                state.Configs.value("Location/MKValidator"),
                [state.Configs.value("InputFile")],
                [state.Configs.value("InputFile")],
            ],
        )

        ### Affichage des retours
        self.SetInfo(
            self.Trad["WorkProgress"].format(state.TempValues.value("Command")[0]),
            "800080",
            True,
            True,
        )  # Nom de la commande
        self.SetInfo(
            self.Trad["WorkCmd"].format(
                state.TempValues.value("Command")[1]
                + " "
                + " ".join(state.TempValues.value("Command")[2])
            )
        )  # Envoie d'informations

        ### Lancement de la commande après blocage des widgets
        self.WorkInProgress(True)
        self.ui.progressBar.setMaximum(0)  # Mode pulsation de la barre de progression
        self.WorkStart()

    # ========================================================================
    def MKVConvert(self, File):
        """Fonction de conversion d'une vidéo en fichier MKV."""
        # File : URL du fichier au format QFileInfo

        ### Proposition de conversion de la vidéo
        if not state.Configs.value("ConfirmConvert"):
            ## Création d'une fenêtre de confirmation avec case à cocher pour se souvenir du choix
            dialog = QMessageBox(
                QMessageBox.Warning,
                self.Trad["Convert1"],
                self.Trad["Convert2"],
                QMessageBox.NoButton,
                self,
            )
            CheckBox = QCheckBox(self.Trad["Convert0"])
            dialog.setCheckBox(CheckBox)
            dialog.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            dialog.setDefaultButton(QMessageBox.Ok)
            dialog.setIconPixmap(
                QPixmap(
                    QIcon()
                    .fromTheme("dialog-warning", QIcon(":/img/dialog-warning.png"))
                    .pixmap(64)
                )
            )
            Confirmation = dialog.exec()

            ## Mise en mémoire de la case à cocher
            state.Configs.setValue("ConfirmConvert", CheckBox.isChecked())

            ## Arrêt de la fonction en cas de refus
            if Confirmation != 1024:
                return

        ### Choix du dossier de sortie
        FileDialogCustom = QFileDialogCustom(
            self, self.Trad["Convert6"], File.absolutePath()
        )
        OutputFile = FileDialogCustom.createWindow(
            "File",
            "Save",
            None,
            Qt.Tool,
            FileName="{}.mkv".format(File.completeBaseName()),
            AlreadyExistsTest=state.Configs.value("AlreadyExistsTest", False),
            Language=state.Configs.value("Language"),
        )

        ### En cas d'annulation
        if not OutputFile:
            return

        ### Nettoyage graphique ici aussi afin de tout nettoyer avant la conversion pour un visuel plus joli
        ## Désactivation des différentes options qui pourraient être activées
        for widget in [
            self.ui.option_reencapsulate,
            self.ui.option_subtitles,
            self.ui.option_audio,
        ]:
            widget.setChecked(False)
            widget.setEnabled(False)

        ## Désactivation des widgets
        for Widget in [
            self.mkv_info,
            self.mkv_mkvtoolnix,
            self.mk_validator,
            self.mk_clean,
            self.mkv_view,
            self.mkv_execute_2,
        ]:
            Widget.setEnabled(False)

        ## Affichage et nettoyage du tableau des pistes
        if self.ui.stackedMiddle.currentIndex() != 0:
            self.ui.stackedMiddle.setCurrentIndex(0)

        while self.ui.mkv_tracks.rowCount() != 0:
            self.ui.mkv_tracks.removeRow(0)

        ## Suppression du titre
        self.ui.mkv_title.setText("")

        ### Mise à jour des variables
        state.WarningReply.clear()  # Réinitialisation des retours de warning de mkvmerge
        state.AllTempFiles.clear()
        state.AllTempFiles.append(OutputFile)  # Ajout du fichier dans la liste en cas d'arrêt
        state.TempValues.setValue(
            "Command",
            [
                "FileToMKV",
                state.Configs.value("Location/MKVMerge"),
                ["-o", OutputFile, File.absoluteFilePath()],
                [File.absoluteFilePath()],
            ],
        )  # Commande de conversion

        ### Affichage des retours
        self.SetInfo(
            self.Trad["WorkProgress"].format(state.TempValues.value("Command")[0]),
            "800080",
            True,
            True,
        )  # Nom de la commande
        self.SetInfo(
            self.Trad["WorkCmd"].format(
                state.TempValues.value("Command")[1]
                + " "
                + " ".join(state.TempValues.value("Command")[2])
            )
        )  # Envoie d'informations

        ### Lancement de la commande après blocage des widgets
        self.WorkInProgress(True)
        self.WorkStart()
