#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Mixin de gestion des logiciels externes (détection, sélection, validation)."""

import state

from PySide6.QtWidgets import QFileDialog, QLineEdit, QMessageBox
from PySide6.QtCore import QDir, QFileInfo, QStandardPaths
from PySide6.QtGui import QAction, QIcon

from CustomWidgets import MultiVar


class SoftwareMixin:
    # ========================================================================
    def SoftwareFinding(self, Reset=False):
        """Fonction vérifiant les adresses des exécutables et les affichant dans la page des exécutables."""
        ### Si demande de réinitialisation
        if Reset:
            for Location in self.WidgetsLocation.keys():
                state.Configs.setValue(Location, "")

        ### Traitement de tous les exécutables
        for Location, Executable, Widget in (
            ("Location/AvConv", "avconv", self.ui.location_avconv),
            ("Location/BDSup2Sub", "bdsup2sub", self.ui.location_bdsup2sub),
            ("Location/FFMpeg", "ffmpeg", self.ui.location_ffmpeg),
            ("Location/MKClean", "mkclean", self.ui.location_mkclean),
            ("Location/MKVExtract", "mkvextract", self.ui.location_mkvextract),
            ("Location/MKVInfo", "mkvinfo-gui", self.ui.location_mkvinfo),
            ("Location/MKVMerge", "mkvmerge", self.ui.location_mkvmerge),
            ("Location/MKVToolNix", "mkvtoolnix-gui", self.ui.location_mkvtoolnix),
            ("Location/MKValidator", "mkvalidator", self.ui.location_mkvalidator),
            ("Location/Qtesseract5", "qtesseract5", self.ui.location_qtesseract5),
        ):

            ## Sauvegarde de la valeur initiale
            InitialValue = state.Configs.value(Location)

            ## Si la variable est vide, on recherche le logiciel
            if not state.Configs.value(Location):
                # Recherche le fichier dans le PATH
                if QStandardPaths.findExecutable(Executable):
                    state.Configs.setValue(
                        Location, QStandardPaths.findExecutable(Executable)
                    )

                # Recherche le fichier à la base du logiciel
                elif QStandardPaths.findExecutable(
                    Executable, [QFileInfo(Executable).absoluteFilePath()]
                ):
                    state.Configs.setValue(
                        Location,
                        QStandardPaths.findExecutable(
                            Executable, [QFileInfo(Executable).absoluteFilePath()]
                        ),
                    )

                # Cas spécifique à BDSup2Sub
                elif Location == "Location/BDSup2Sub":
                    if QStandardPaths.findExecutable("BDSup2Sub.jar"):
                        state.Configs.setValue(
                            "Location/BDSup2Sub",
                            QStandardPaths.findExecutable("BDSup2Sub.jar"),
                        )

                    elif QStandardPaths.findExecutable("bdsup2sub.jar"):
                        state.Configs.setValue(
                            "Location/BDSup2Sub",
                            QStandardPaths.findExecutable("bdsup2sub.jar"),
                        )

                    elif QStandardPaths.findExecutable(
                        "bdsup2sub", [QFileInfo("BDSup2Sub.jar").absoluteFilePath()]
                    ):
                        state.Configs.setValue(
                            "Location/BDSup2Sub",
                            QStandardPaths.findExecutable(
                                "bdsup2sub",
                                [QFileInfo("BDSup2Sub.jar").absoluteFilePath()],
                            ),
                        )

                    elif QStandardPaths.findExecutable(
                        "bdsup2sub", [QFileInfo("bdsup2sub.jar").absoluteFilePath()]
                    ):
                        state.Configs.setValue(
                            "Location/BDSup2Sub",
                            QStandardPaths.findExecutable(
                                "bdsup2sub",
                                [QFileInfo("bdsup2sub.jar").absoluteFilePath()],
                            ),
                        )

                # Cas spécifique à MKVToolNix
                elif Location == "Location/MKVToolNix":
                    if QStandardPaths.findExecutable("mmg"):
                        state.Configs.setValue(
                            "Location/MKVToolNix", QStandardPaths.findExecutable("mmg")
                        )

                    elif QStandardPaths.findExecutable(
                        "mmg", [QFileInfo("mmg").absoluteFilePath()]
                    ):
                        state.Configs.setValue(
                            "Location/MKVToolNix",
                            "{} --info".format(
                                QStandardPaths.findExecutable(
                                    "mmg", [QFileInfo("mmg").absoluteFilePath()]
                                )
                            ),
                        )

                    elif QStandardPaths.findExecutable("mkvtoolnix-gui"):
                        state.Configs.setValue(
                            "Location/MKVToolNix",
                            QStandardPaths.findExecutable("mkvtoolnix-gui"),
                        )

                    elif QStandardPaths.findExecutable(
                        "mkvtoolnix-gui",
                        [QFileInfo("mkvtoolnix-gui").absoluteFilePath()],
                    ):
                        state.Configs.setValue(
                            "Location/MKVToolNix",
                            "{} --info".format(
                                QStandardPaths.findExecutable(
                                    "mkvtoolnix-gui",
                                    [QFileInfo("mkvtoolnix-gui").absoluteFilePath()],
                                )
                            ),
                        )

                # Cas spécifique à MKVInfo
                elif Location == "Location/MKVInfo":
                    if QStandardPaths.findExecutable("mkvtoolnix-gui"):
                        state.Configs.setValue(
                            "Location/MKVInfo",
                            "{} --info".format(
                                QStandardPaths.findExecutable("mkvtoolnix-gui")
                            ),
                        )

                    elif QStandardPaths.findExecutable(
                        "mkvtoolnix-gui",
                        [QFileInfo("mkvtoolnix-gui").absoluteFilePath()],
                    ):
                        state.Configs.setValue(
                            "Location/MKVInfo",
                            "{} --info".format(
                                QStandardPaths.findExecutable(
                                    "mkvtoolnix-gui",
                                    [QFileInfo("mkvtoolnix-gui").absoluteFilePath()],
                                )
                            ),
                        )

                    elif QStandardPaths.findExecutable("mkvinfo"):
                        state.Configs.setValue(
                            "Location/MKVInfo",
                            "{} -g".format(QStandardPaths.findExecutable("mkvinfo")),
                        )

                    elif QStandardPaths.findExecutable(
                        "mkvinfo", [QFileInfo("mkvinfo").absoluteFilePath()]
                    ):
                        state.Configs.setValue(
                            "Location/MKVInfo",
                            "{} --info".format(
                                QStandardPaths.findExecutable(
                                    "mkvinfo", [QFileInfo("mkvinfo").absoluteFilePath()]
                                )
                            ),
                        )

            ## Si la valeur n'a pas évoluée, au démarrage, le setText ne sera pas "fonctionnel", on l'appelle manuellement
            if InitialValue == state.Configs.value(Location):
                self.SoftwareChanged(Location, InitialValue, Widget)

            ## Envoie de l'adresse dans le line edit
            Widget.setText(state.Configs.value(Location))

    # ========================================================================
    def SoftwareSelector(self, Location, Widget):
        """Fonction de sélection des exécutables."""
        ### Affichage de la fenêtre avec le bon dossier par défaut
        FileDialog = QFileDialog.getOpenFileName(
            self,
            self.Trad["LocationTitle"],
            MultiVar(state.Configs.value(Location), QDir.homePath()),
        )

        ### En cas d'annulation, on arrête là
        if not FileDialog[0]:
            return

        ### Mise à jour du widget
        Widget.setText(FileDialog[0])

    # ========================================================================
    def SoftIsExec(self, Name):
        """Mini fonction pour simplifier les tests d'executabilité (et du coup son existence) des commandes."""
        ### Si utilisation de | pour tester plusieurs commandes
        # not self.SoftIsExec("FFMpeg|AvConv") : Si on veut que tous les tests soient négatifs
        # self.SoftIsExec("BDSup2Sub|FFMpeg") : Si on veut au moins 1 résultat positif
        if "|" in Name:
            ## Boucles sur tous les noms
            for SubName in Name.split("|"):
                # Ajout de Location/
                SubName = "Location/" + SubName.replace("Location/", "")

                # Si le fichier est exécutable (et du coup existant)
                if QFileInfo(state.Configs.value(SubName).split(" -")[0]).isExecutable():
                    return True

            ## Si tous les tests ont échoués
            return False

        ### Mode simple
        else:
            ## Ajout de Location/
            Name = "Location/" + Name.replace("Location/", "")

            ## Renvoi de l'état de la commande
            Retour = QFileInfo(state.Configs.value(Name).split(" -")[0]).isExecutable()

            ## Cas spécifique à MKVExtract et MKVMerge
            if not Retour and Name in ("Location/MKVExtract", "Location/MKVMerge"):
                QMessageBox.critical(
                    self,
                    self.Trad["WorkTestTitle"].format(Name.replace("Location/", "")),
                    self.Trad["WorkTestText"].format(Name.replace("Location/", "")),
                )

                self.SetInfo(
                    self.Trad["WorkTestTitle"].format(Name.replace("Location/", ""))
                    + " : "
                    + self.Trad["WorkTestText"].format(Name.replace("Location/", "")),
                    "FF0000",
                    True,
                )  # Erreur pendant le travail

                # Blocage du chargement de fichier mkv
                if Name == "Location/MKVMerge":
                    self.ui.input_file.setEnabled(False)

                # Blocage des boutons d'exécution dans le cas où l'adresse du soft serait modifiée une fois les lignes cochées
                elif Name == "Location/MKVExtract":
                    self.ui.mkv_execute.setEnabled(False)
                    self.mkv_execute_2.setEnabled(False)

                # Si on n'est pas dans la gestion des adresses, on y va
                # Donc au démarrage on y va, dans le cas d'une modif à la main, on y est déjà
                if self.ui.stackedMiddle.currentIndex() != 2:
                    self.ui.stackedMiddle.setCurrentIndex(2)

                self.WorkStop("Error")

            elif Name == "Location/MKVMerge":
                # Déblocage du chargement de fichier mkv
                self.ui.input_file.setEnabled(True)

            ## Renvoi de la valeur
            return Retour

    # ========================================================================
    def SoftwareChanged(self, Location, NewText, Widget=None):
        """Fonction vérifiant que l'adresse de l'exécutable est valide."""
        ### Mise à jour de la variable
        state.Configs.setValue(Location, NewText)

        ### Fait sauter les arguments afin de pouvoir tester uniquement l'exécutable
        NewText = NewText.split(" -")[0]

        ### Nom du widget appelant la fonction
        if not Widget:
            Widget = self.sender()

            if not Widget:
                return

        ### Variable servant au (dé)grisement des options
        OptionActive = False

        ### Suppression des actions (icônes) du widget
        for Action in Widget.actions():
            Widget.removeAction(Action)

        ### Teste l'adresse et attribut une icône
        # Si l'adresse est vide, envoi d'une icône question dans le line edit
        if not NewText:
            Action = QAction(
                QIcon.fromTheme("emblem-question", QIcon(":/img/emblem-question.svg")),
                "",
                Widget,
            )
            Action.setStatusTip(self.Trad["LocationNo"])

        # Si l'adresse est introuvable, envoi d'une icône d'erreur dans le line edit
        elif not QFileInfo(NewText.split(" -")[0]).exists():
            Action = QAction(
                QIcon.fromTheme("emblem-error", QIcon(":/img/emblem-error.svg")),
                "",
                Widget,
            )
            Action.setStatusTip(self.Trad["LocationKO"])

        # Si l'adresse n'est pas exécutable, envoi d'une icône de point d'exclamation dans le line edit
        elif not QFileInfo(NewText.split(" -")[0]).isExecutable():
            Action = QAction(
                QIcon.fromTheme(
                    "emblem-important", QIcon(":/img/emblem-important.svg")
                ),
                "",
                Widget,
            )
            Action.setStatusTip(self.Trad["LocationOKO"])

        # Sinon, icône OK
        else:
            Action = QAction(
                QIcon.fromTheme("emblem-succed", QIcon(":/img/emblem-succed.svg")),
                "",
                Widget,
            )
            Action.setStatusTip(self.Trad["LocationOK"])
            OptionActive = True

        ### Envoi de l'icône dans le line edit
        Widget.addAction(Action, QLineEdit.LeadingPosition)

        ### Mise à jour de l'état du logiciel
        state.SoftExec[Location.replace("Location/", "")] = self.SoftIsExec(Location)

        ### Récupération du widget de l'option
        # Avconv n'a pas de widget
        try:
            OptionWidget = self.WidgetsLocation[Location]

        except KeyError:
            # [Claude] AMÉLIORATION : bare except remplacé par KeyError, la seule exception
            # attendue lors d'un accès à un dictionnaire avec une clé absente (ex: AvConv).
            OptionWidget = None

        ### Si un widget a été donné
        if OptionWidget:
            ## Fait disparaître si besoin l'option
            if state.Configs.value("HideOptions") and not OptionActive:
                OptionWidget.setVisible(False)

            ## Fait apparaître l'option
            else:
                OptionWidget.setVisible(True)

            ## Activation du widget si un fichier est chargé ne concernant pas Qtesseract et BDSup2Sub
            if state.TempValues.value("MKVLoaded") and Location not in (
                "Location/Qtesseract5",
                "Location/FFMpeg",
                "Location/BDSup2Sub",
            ):
                if state.SoftExec[Location.replace("Location/", "")] and OptionActive:
                    OptionWidget.setEnabled(True)

                else:
                    OptionWidget.setEnabled(False)

            ## Pour Qtesseract / BDSup2Sub / FFMpeg, self.StartInProgress évite d'appeler 3 fois la fonction au démarrage
            if (
                Location
                in ("Location/Qtesseract5", "Location/FFMpeg", "Location/BDSup2Sub")
                and not self.StartInProgress
            ):
                self.SubtitlesSoftwareUpdate()

        ### Recherche ffmpeg et avconv qui font la même chose
        if Location in ("Location/FFMpeg", "Location/AvConv"):
            # Décoche le bouton de conversion audio
            self.ui.option_audio.setChecked(False)

            # Décoche les sous options
            self.option_stereo.setChecked(False)
            self.option_to_ac3.setChecked(False)

            for nb in [128, 192, 224, 256, 320, 384, 448, 512, 576, 640]:
                state.QualityList[nb].setChecked(False)

            for nb in [2, 3, 4, 5]:
                state.PowerList[nb].setChecked(False)

            # S'il n'y a ni FFMpeg ni AvConv
            if not state.SoftExec["FFMpeg"] and not state.SoftExec["AvConv"]:
                # On désactive les options et le bouton de conversion audio
                state.TempValues.setValue("FFMpeg", False)
                self.option_ffmpeg.setEnabled(False)
                self.option_ffmpeg.setChecked(False)
                self.ui.option_audio.setEnabled(False)

                # Si besoin, on cache aussi le bouton de conversion audio
                if state.Configs.value("HideOptions"):
                    self.ui.option_audio.setVisible(False)

            else:
                # Affichage du bouton de conversion audio
                self.ui.option_audio.setVisible(True)

                # Activation du bouton de conversion audio s'il y a de l'audio coché
                for valeurs in state.MKVDicoSelect.values():
                    if valeurs[2] == "audio-x-generic":
                        self.ui.option_audio.setEnabled(True)

                # Si FFMPEG existe, c'est toujours lui qu'on utilise par défaut
                if state.SoftExec["FFMpeg"]:
                    state.TempValues.setValue("FFMpeg", True)

                # Sinon utilisation de AvConv
                elif state.SoftExec["AvConv"]:
                    state.TempValues.setValue("FFMpeg", False)

                # S'il y a FFMPEG et AvConv, activation de l'option
                if state.SoftExec["FFMpeg"] and state.SoftExec["AvConv"]:
                    self.option_ffmpeg.setEnabled(True)
                    self.option_ffmpeg.setChecked(True)

                # Sinon, on désactive l'option
                else:
                    self.option_ffmpeg.setChecked(False)
                    self.option_ffmpeg.setEnabled(False)

    # ========================================================================
    def SubtitlesSoftwareUpdate(self):
        """Gestion spécifique des actions de conversion des sous-titres."""
        # Bouton d'activation des conversions de sous titres
        option_subtitlesEnabled = False
        option_subtitlesChecked = False

        # Décoche et désactive les actions de Qtesseract
        Qtesseract5ConvertChecked = False
        Qtesseract5ConvertEnabled = False
        Qtesseract5OpenChecked = False
        Qtesseract5OpenEnabled = False

        # Décoche et désactive les actions de BDSup2Sub
        BDSup2SubConvertChecked = False
        BDSup2SubConvertEnabled = False
        BDSup2SubOpenEnabled = False
        BDSup2SubOpenChecked = False

        # Décoche et désactive les actions de FFMpeg
        FFMpegConvertChecked = False
        FFMpegConvertEnabled = False

        # Dans le cas où il faut cacher les actions indisponibles
        if state.Configs.value("HideOptions"):
            Qtesseract5ConvertVisible = False
            Qtesseract5OpenVisible = False
            BDSup2SubOpenVisible = False
            BDSup2SubConvertVisible = False
            FFMpegConvertVisible = False

        else:
            Qtesseract5ConvertVisible = True
            Qtesseract5OpenVisible = True
            BDSup2SubOpenVisible = True
            BDSup2SubConvertVisible = True
            FFMpegConvertVisible = True

        # Si BDSup2Sub/FFMpeg et Qtesseract sont fonctionnels
        if (state.SoftExec["BDSup2Sub"] or state.SoftExec["FFMpeg"]) and state.SoftExec["Qtesseract5"]:
            if state.MKVDicoSelect:
                # Bouton de conversion des sous-titres
                option_subtitlesEnabled = True

            # Affichage des actions
            if state.SoftExec["BDSup2Sub"]:
                BDSup2SubOpenVisible = True
                BDSup2SubConvertVisible = True

            if state.SoftExec["FFMpeg"]:
                FFMpegConvertVisible = True

            Qtesseract5ConvertVisible = True
            Qtesseract5OpenVisible = True

            # Recherche une piste cochée de type sub/sup/pgs
            for valeurs in state.MKVDicoSelect.values():
                if valeurs[-1] in ("sup", "pgs", "sub"):
                    # Bouton de conversion des sous-titres
                    option_subtitlesChecked = self.ui.option_subtitles.isChecked()

                    if valeurs[-1] in ("sup", "pgs"):
                        # Activation de BDSup2Sub
                        if state.SoftExec["BDSup2Sub"]:
                            BDSup2SubConvertEnabled = True
                            BDSup2SubOpenEnabled = True

                            # Conserve l'état des coches
                            BDSup2SubConvertChecked = state.Sup2Sub[2].isChecked()
                            BDSup2SubOpenChecked = state.Sup2Sub[3].isChecked()

                        # Activation de FFMpeg
                        if state.SoftExec["FFMpeg"]:
                            FFMpegConvertEnabled = True

                            # Conserve l'état des coches
                            FFMpegConvertChecked = state.Sup2Sub[1].isChecked()

                        # Si BDSup2Sub ou FFMpeg sont actuellement utilisés
                        if BDSup2SubConvertChecked or FFMpegConvertChecked:
                            # Activation de Qtesseract
                            Qtesseract5ConvertEnabled = True
                            Qtesseract5OpenEnabled = True

                            # Conserve l'état des coches
                            Qtesseract5ConvertChecked = state.Sub2Srt[1].isChecked()
                            Qtesseract5OpenChecked = state.Sub2Srt[2].isChecked()

                            # On a déjà tout activé, on peut arrêter
                            break

                    else:
                        # Activation de Qtesseract
                        Qtesseract5ConvertEnabled = True
                        Qtesseract5OpenEnabled = True

                        # Conserve l'état des coches
                        Qtesseract5ConvertChecked = state.Sub2Srt[1].isChecked()
                        # [Claude] BUG : La variable était nommée BDSup2SubOpenChecked alors qu'on
                        # est dans le bloc Qtesseract, et qu'on lit state.Sub2Srt[2] (widget Qtesseract).
                        # Cela écrasait l'état de BDSup2Sub avec une valeur de Qtesseract.
                        Qtesseract5OpenChecked = state.Sub2Srt[2].isChecked()

        # Si Qtesseract est fonctionnel
        elif state.SoftExec["Qtesseract5"]:
            if state.MKVDicoSelect:
                # Bouton de conversion des sous-titres
                option_subtitlesEnabled = True

            # Affichage des actions
            Qtesseract5ConvertVisible = True
            Qtesseract5OpenVisible = True

            # S'il y a des pistes
            if state.MKVDicoSelect:
                # Recherche une piste cochée de type sub
                for valeurs in state.MKVDicoSelect.values():
                    if valeurs[-1] == "sub":
                        # Bouton de conversion des sous-titres
                        option_subtitlesChecked = self.ui.option_subtitles.isChecked()

                        # Activation de Qtesseract
                        Qtesseract5ConvertEnabled = True
                        Qtesseract5OpenEnabled = True

                        # Conserve l'état des coches
                        Qtesseract5ConvertChecked = state.Sub2Srt[1].isChecked()
                        # [Claude] BUG : Même erreur que plus haut — BDSup2SubOpenChecked
                        # était assigné avec la valeur du widget Qtesseract (state.Sub2Srt[2]).
                        # Ce bloc concerne exclusivement Qtesseract, la variable correcte est
                        # Qtesseract5OpenChecked.
                        Qtesseract5OpenChecked = state.Sub2Srt[2].isChecked()

                        break

        # Si BDSup2Sub/FFMpeg sont fonctionnels
        elif state.SoftExec["BDSup2Sub"] or state.SoftExec["FFMpeg"]:
            if state.MKVDicoSelect:
                # Bouton de conversion des sous-titres
                option_subtitlesEnabled = True

            # Affichage des actions
            if state.SoftExec["BDSup2Sub"]:
                BDSup2SubOpenVisible = True
                BDSup2SubConvertVisible = True

            if state.SoftExec["FFMpeg"]:
                FFMpegConvertVisible = True

            # S'il y a des pistes
            if state.MKVDicoSelect:
                # Recherche une piste cochée de type sup ou pgs
                for valeurs in state.MKVDicoSelect.values():
                    if valeurs[-1] in ("sup", "pgs"):
                        # Bouton de conversion des sous-titres
                        option_subtitlesChecked = self.ui.option_subtitles.isChecked()

                        # Activation de BDSup2Sub
                        if state.SoftExec["BDSup2Sub"]:
                            BDSup2SubConvertEnabled = True
                            BDSup2SubOpenEnabled = True

                            # Conserve l'état des coches
                            BDSup2SubConvertChecked = state.Sup2Sub[2].isChecked()
                            BDSup2SubOpenChecked = state.Sup2Sub[3].isChecked()

                        # Activation de FFMpeg
                        if state.SoftExec["FFMpeg"]:
                            FFMpegConvertEnabled = True

                            # Conserve l'état des coches
                            FFMpegConvertChecked = state.Sup2Sub[1].isChecked()

                        break

        # Mise à jour du bouton de conversion des sous titres
        self.ui.option_subtitles.setEnabled(option_subtitlesEnabled)
        self.ui.option_subtitles.setChecked(option_subtitlesChecked)

        # Mise à jour des info-bulles bloqué au démarrage
        if not self.StartInProgress:
            self.SubtitlesTranslation(False)

        # Mise à jour des actions de Qtesseract
        state.Sub2Srt[1].setChecked(Qtesseract5ConvertChecked)
        state.Sub2Srt[1].setEnabled(Qtesseract5ConvertEnabled)
        state.Sub2Srt[1].setVisible(Qtesseract5ConvertVisible)
        state.Sub2Srt[2].setChecked(Qtesseract5OpenChecked)
        state.Sub2Srt[2].setEnabled(Qtesseract5OpenEnabled)
        state.Sub2Srt[2].setVisible(Qtesseract5OpenVisible)

        # Mise à jour des actions de BDSup2Sub
        state.Sup2Sub[2].setChecked(BDSup2SubConvertChecked)
        state.Sup2Sub[2].setEnabled(BDSup2SubConvertEnabled)
        state.Sup2Sub[2].setVisible(BDSup2SubConvertVisible)
        state.Sup2Sub[3].setChecked(BDSup2SubOpenChecked)
        state.Sup2Sub[3].setEnabled(BDSup2SubOpenEnabled)
        state.Sup2Sub[3].setVisible(BDSup2SubOpenVisible)

        # Mise à jour des actions de FFMpeg
        state.Sup2Sub[1].setChecked(FFMpegConvertChecked)
        state.Sup2Sub[1].setEnabled(FFMpegConvertEnabled)
        state.Sup2Sub[1].setVisible(FFMpegConvertVisible)
    
