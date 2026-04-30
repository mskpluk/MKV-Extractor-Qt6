#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Mixin d'exécution des processus et gestion du travail en cours."""

from datetime import timedelta
try:
    import psutil
except ImportError:
    pass
import state
from PySide6.QtCore import QDir, QFile, QFileInfo, QProcess, Qt, QUrl
from PySide6.QtWidgets import QCheckBox, QMessageBox, QPushButton, QSystemTrayIcon
from PySide6.QtGui import QDesktopServices, QIcon, QPixmap


class WorkMixin:
    # ========================================================================
    def LittleProcess(self, Program, Arguments):
        """Petite fonction récupérant les retours de process simples."""
        # Command est le nom du logiciel à utiliser
        # Arguments est la liste des arguments
        # Utilisation de ce système plutôt qu'une simple string donnée à start() qui ne comprend pas les " dans les noms'

        ### Envoie d'information en mode debug
        if state.Configs.value("DebugMode"):
            self.SetInfo(
                self.Trad["WorkCmd"].format(Program + " " + " ".join(Arguments)),
                newline=True,
            )

        ### Liste qui contiendra les retours
        reply = []

        ### Création du QProcess avec unification des 2 sorties (normale + erreur)
        process = QProcess()
        process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)

        ### Préparation de la commande
        process.setProgram(Program)
        process.setArguments(Arguments)

        ### Exécution de la commande et attente de sa fin
        # [Claude] AMÉLIORATION : waitForFinished() sans argument attend indéfiniment (-1 ms).
        # Si le processus externe se bloque ou ne répond pas, l'application se fige entièrement.
        # Un timeout de 30 secondes est un compromis raisonnable pour les commandes mkvmerge/mkvinfo.
        process.start()
        if not process.waitForFinished(30000):  # 30 secondes max
            process.kill()
            process.waitForFinished(3000)

        ### Ajoute les lignes du retour dans la liste
        for line in bytes(process.readAllStandardOutput()).decode("utf-8").splitlines():
            reply.append(line)

        ### Renvoie le résultat
        return reply

    def WorkStart(self):
        """Fonction vérifiant la présence des fichiers nécessaires au bon lancement de la commande."""
        ### Si des fichiers sont nécessaires
        if state.TempValues.value("Command")[2]:
            FilesMissing = []

            # Teste chaque fichier
            for File in state.TempValues.value("Command")[3]:
                if not QFile(File).exists():
                    FilesMissing.append(File)

            # S'il manque des fichiers
            if FilesMissing:
                QMessageBox.critical(
                    self,
                    self.Trad["WorkFileCheckTitle"],
                    self.Trad["WorkFileCheckText"].format("\n - ".join(FilesMissing)),
                )

                self.SetInfo(
                    self.Trad["WorkFileCheckTitle"]
                    + "\n"
                    + self.Trad["WorkFileCheckText"].format("\n - ".join(FilesMissing)),
                    "FF0000",
                    True,
                )  # Erreur pendant le travail

                self.WorkStop("Error")
                return

        ### Vérification de la présence de mkvmerge et mkvextract
        # if not state.SoftExec["MKVMerge"] or not state.SoftExec["MKVExtract"]:
        #     return

        ### Si tout est OK, on lance la commande
        self.process.start(
            state.TempValues.value("Command")[1], state.TempValues.value("Command")[2]
        )

    # ========================================================================
    def WorkInProgress(self, value):
        """Fonction de modifications graphiques en fonction d'un travail en cours ou non."""
        ### Dans le cas d'un lancement de travail
        if value:
            ## Modifications graphiques
            self.setCursor(Qt.WaitCursor)  # Curseur de chargement
            self.ui.mkv_execute.hide()  # Cache le bouton exécuter
            self.mkv_execute_2.setEnabled(False)  # Grise le bouton exécuter
            self.ui.mkv_stop.show()  # Affiche le bouton arrêter

            # Affiche le bouton pause si l'option de cache auto est inactive ou si elle est active mais que psutil est présent
            if not state.Configs.value("HideOptions") or (
                state.Configs.value("HideOptions") and "psutil" in globals()
            ):
                self.ui.mkv_pause.show()

            for widget in (self.ui.menubar, self.ui.tracks_bloc):
                widget.setEnabled(False)  # Blocage de widget

        ### Dans le cas où le travail vient de se terminer (bien ou mal)
        else:
            ## Modifications graphiques
            self.ui.mkv_execute.show()  # Affiche le bouton exécuter
            self.ui.mkv_stop.hide()  # Cache le bouton arrêter
            self.ui.mkv_pause.hide()  # Cache le bouton pause

            if state.TempValues.value("MKVLoaded") and state.MKVDicoSelect:
                self.mkv_execute_2.setEnabled(True)  # Dégrise le bouton exécuter

            if self.ui.progressBar.format() != "%p %":
                self.ui.progressBar.setFormat(
                    "%p %"
                )  # Réinitialisation du bon formatage de la barre de progression

            if self.ui.progressBar.maximum() != 100:
                self.ui.progressBar.setMaximum(
                    100
                )  # Réinitialisation de la valeur maximale de la barre de progression

            # Si on est déjà sur les pistes ou sur la config des logiciels
            if self.ui.stackedMiddle.currentIndex() not in (0, 2):
                self.ui.stackedMiddle.setCurrentIndex(
                    0
                )  # Ré-affiche le tableau des pistes si ce n'est plus lui qui est affiché

            for widget in (self.ui.menubar, self.ui.tracks_bloc):
                widget.setEnabled(True)  # Blocage de widget

            self.setCursor(Qt.ArrowCursor)  # Curseur normal

    # ========================================================================
    def WorkReply(self):
        """Fonction recevant tous les retours du travail en cours."""
        ### Récupération du retour (les 2 sorties sont sur la standard)
        data = self.process.readAllStandardOutput()

        ### Reset de la dernière valeur
        state.TempValues.setValue("WorkOldLine", "")

        ### Converti les data en textes et les traite
        for line in bytes(data).decode("utf-8").splitlines():
            progression = 0
            debugLine = line

            ## Passe la boucle si le retour est vide
            if line == "":
                continue

            ## Dans le cas d'un encapsulation
            elif state.TempValues.value("Command")[0] == "MKVMerge":
                # Récupère le nombre de retour en cas de présence de pourcentage
                if line[-1] == "%":
                    try:
                        progression = int(line.split(": ")[1].strip()[0:-1])

                    except Exception:
                        progression = "Fake text"

            ## Dans le cas d'une conversion
            elif state.TempValues.value("Command")[0] == "FileToMKV":
                # Récupère le nombre de retour en cas de présence de pourcentage
                if line[-1] == "%":
                    try:
                        progression = int(line.split(": ")[1].strip()[0:-1])

                    except Exception:
                        progression = "Fake text"

            elif state.TempValues.value("Command")[0] == "MKVExtract Tags":
                TagsFile = QFile(state.TempValues.value("TagsFile"))
                TagsFile.open(QFile.Append)
                TagsFile.write((line + "\n").encode())
                TagsFile.close()

                line = ""

            elif state.TempValues.value("Command")[0] == "MKVExtract Chapters":
                ChaptersFile = QFile(state.TempValues.value("ChaptersFile"))
                ChaptersFile.open(QFile.Append)
                ChaptersFile.write((line + "\n").encode())
                ChaptersFile.close()

                line = ""

            ## MKVExtract renvoie une progression. Les fichiers joints ne renvoient rien.
            elif "MKVExtract" in state.TempValues.value("Command")[0]:
                # Récupère le nombre de retour en cas de présence de pourcentage
                if line[-1] == "%":
                    try:
                        progression = int(line.split(": ")[1].strip()[0:-1])

                    except Exception:
                        progression = "Fake text"

            ## MKValidator ne renvoie pas de pourcentage mais des infos ou des points, on vire les . qui indiquent un travail en cours
            elif state.TempValues.value("Command")[0] == "MKValidator":
                line = line.strip().replace(".", "")

            ## MKClean renvoie une progression et des infos, on ne traite que les pourcentages
            elif state.TempValues.value("Command")[0] == "MKClean":
                if line[-1] == "%":
                    try:
                        progression = int(line.split(": ")[1].strip()[0:-1])

                    except Exception:
                        progression = "Fake text"

            ## FFMpeg ne renvoie pas de pourcentage mais la durée de vidéo encodée en autre
            elif state.TempValues.value("Command")[0] in ["FFMpeg", "AvConv"]:
                if "time=" in line and state.TempValues.contains("DurationFile"):
                    # Pour les versions renvoyant : 00:00:00
                    try:
                        value = line.split("=")[2].strip().split(".")[0].split(":")
                        value2 = timedelta(
                            hours=int(value[0]),
                            minutes=int(value[1]),
                            seconds=int(value[2]),
                        ).seconds

                    # Pour les versions renvoyant : 00000 secondes
                    except Exception:
                        value = "caca"
                        value2 = line.split("=")[2].strip().split(".")[0]

                    # Pourcentage maison se basant sur la durée du fichier
                    try:
                        progression = int(
                            (value2 * 100) / state.TempValues.value("DurationFile")
                        )

                    except Exception:
                        progression = "Fake text"

            ## Qtesseract5
            elif state.TempValues.value("Command")[0] == "Qtesseract5":
                if "Temporary folder:" in line:
                    state.TempValues.setValue("Qtesseract5Folder", line.split(": ")[1])

                try:
                    progression = int(
                        (int(line.split("/")[0]) / int(line.split("/")[1])) * 100
                    )

                except Exception:
                    progression = "Fake text"

            ## BDSup2Sub
            elif state.TempValues.value("Command")[0] == "BDSup2Sub":
                # Progression
                if "Decoding frame" in line:
                    try:
                        values = line.split(" ")[2].split("/")
                        progression = int((int(values[0]) / int(values[1])) * 100)

                    except Exception:
                        progression = "Fake text"

                # Cache ces infos
                elif "#>" in line:
                    line = ""

            ## Affichage du texte ou de la progression si c'est une nouvelle valeur
            if line and line != state.TempValues.value(
                "WorkOldLine"
            ):  # Comparaison anti doublon
                state.TempValues.setValue(
                    "WorkOldLine", line
                )  # Mise à jour de la variable anti doublon

                # Mode debug
                if state.Configs.value("DebugMode") and debugLine:
                    self.SetInfo(debugLine)

                # Envoie du pourcentage à la barre de progression si c'est un nombre
                if isinstance(progression, int):
                    self.ui.progressBar.setValue(progression)

                # Envoie de l'info à la boite de texte si c'est du texte
                else:
                    # On ajoute le texte dans une variable en cas de conversion (utile pour le ressortir dans une fenêtre)
                    if state.TempValues.value("Command")[0] == "FileToMKV":
                        state.WarningReply.append(line)

                    self.SetInfo(line)

    # ========================================================================
    def WorkError(self, error):
        """Fonction appelée lors du plantage d'un programme lancée via self.process"""
        try:
            self.WorkStop("Error")
        except RuntimeError:
            pass

    # ========================================================================
    def WorkFinished(self):
        """Fonction appelée à la fin du travail, que ce soit une fin normale ou une annulation."""
        # state.TempValues.value("Command")[0] : Nom de la commande
        # state.TempValues.value("Command")[1] : Commande à exécuter
        # state.TempValues.value("Command")[2] : Arguments de la commande
        try:
            _ = self.process.state()
        except RuntimeError:
            return
        FileList = ""

        ### Si le travail est annulé (via le bouton stop ou via la fermeture du logiciel) et qu'il n'y a pas déjà un arrêt en cours
        if not self.StopInProgress:
            # mkvmerge renvoie 1 s'il y a des warnings et 2 en cas d'erreur
            if state.TempValues.value("Command")[0] in ["FileToMKV", "MKVMerge"]:
                if self.process.exitCode() == 1:
                    self.SetInfo(
                        self.Trad["WorkWarning"].format(state.TempValues.value("Command")[0]),
                        "FFA500",
                        True,
                    )

                elif self.process.exitCode() == 2:
                    self.WorkStop("Error")
                    return

            # Cas spécifique de Qtesseract
            elif state.TempValues.value("Command")[0] == "Qtesseract5":
                if self.process.exitCode() != 0:
                    self.WorkStop("SrtError")
                    return

            # Dans les autres cas
            else:
                if self.process.exitCode() != 0:
                    self.WorkStop("Error")
                    return

        ### Traitement différent en fonction de la commande, rien de particulier pour MKValidator, MKClean, FFMpeg
        if state.TempValues.value("Command")[0] == "Open Subtitles":
            # Boucle ouvrant tous les fichiers srt d'un coup et remplissant la liste pour la Dialog d'attente
            for Item in state.SubtitlesFiles:
                QDesktopServices.openUrl(QUrl.fromLocalFile(Item))
                FileList += "{}\n".format(Item)

        ### Indication de fin de pack de commande
        else:
            # Travail terminé
            self.SetInfo(
                self.Trad["WorkFinished"].format(state.TempValues.value("Command")[0]),
                "800080",
                True,
            )

            # Mise à 100% de la barre de progression pour signaler la fin ok
            self.ui.progressBar.setValue(100)

            if state.Configs.value("SysTray"):
                # Si tout est OK
                if not self.StopInProgress:
                    self.SysTrayIcon.showMessage(
                        self.Trad["SysTrayFinishTitle"],
                        self.Trad["SysTrayFinishText"].format(
                            state.TempValues.value("Command")[0]
                        ),
                        QSystemTrayIcon.Information,
                        3000,
                    )

        ### Lancement de l'ouverture du fichier MKV, ici pour un soucis esthétique du texte affiché
        # Dans le cas d'une conversion
        if state.TempValues.value("Command")[0] == "FileToMKV":
            ## Si mkvmerge a renvoyé un warning, on l'indique
            if self.process.exitCode() == 1 and not state.Configs.value("ConfirmWarning"):
                # Création d'une fenêtre de confirmation avec case à cocher pour se souvenir du choix
                dialog = QMessageBox(
                    QMessageBox.Warning,
                    self.Trad["Convert3"],
                    self.Trad["Convert4"],
                    QMessageBox.NoButton,
                    self,
                )
                CheckBox = QCheckBox(self.Trad["Convert5"])
                dialog.setCheckBox(CheckBox)
                dialog.setStandardButtons(QMessageBox.Ok)
                dialog.setDefaultButton(QMessageBox.Ok)
                dialog.setDetailedText("\n".join(state.WarningReply))
                dialog.exec()

                # Mise en mémoire de la case à cocher
                state.Configs.setValue("ConfirmWarning", CheckBox.isChecked())

            ## Lancement de la fonction d'ouverture du fichier MKV créé dans le soft
            self.InputFile(state.AllTempFiles[-1])

        ### Lors de l'ouverture des sous-titres avant réencapsulation, on bloque ici
        if state.TempValues.value("Command")[0] == "Open Subtitles":
            # Création du texte de la Dialog
            Translation = "{}{}".format(self.Trad["WaitWinText"], FileList)

            # Création d'une fenêtre de confirmation de reprise
            ChoiceBox = QMessageBox(
                QMessageBox.NoIcon,
                self.Trad["WaitWinTitle"],
                Translation,
                QMessageBox.NoButton,
                self,
                Qt.WindowSystemMenuHint,
            )
            Button1 = QPushButton(
                QIcon.fromTheme("dialog-ok", QIcon(":/img/dialog-ok.png")),
                self.Trad["WaitWinButton1"],
                ChoiceBox,
            )
            Button2 = QPushButton(
                QIcon.fromTheme("process-stop", QIcon(":/img/process-stop.png")),
                self.Trad["WaitWinButton2"],
                ChoiceBox,
            )
            ChoiceBox.addButton(Button1, QMessageBox.AcceptRole)
            ChoiceBox.addButton(Button2, QMessageBox.RejectRole)
            ChoiceBox.setDefaultButton(QMessageBox.Ok)
            ChoiceBox.setIconPixmap(
                QPixmap(
                    QIcon()
                    .fromTheme(
                        "media-playback-pause", QIcon(":/img/media-playback-pause.png")
                    )
                    .pixmap(64)
                )
            )
            Choice = ChoiceBox.exec()

            # Arrêt du travail
            if Choice == 1:
                self.WorkStop("Stop")
                return

        ### S'il reste des commandes, exécution de la commande suivante
        if state.CommandList:
            ## Récupération de la commande suivante à exécuter
            state.TempValues.setValue("Command", state.CommandList.pop(0))

            ## Traitement des boites de messages
            Message = ""

            # N'affiche les messages que si le fichier test est réutilisé par la suite
            if state.TempValues.value("Command")[0] == "Message":
                # Le try permet de sortir de toutes les boucles en une fois
                class Found(Exception):
                    pass

                try:
                    for Command in state.CommandList:
                        for File in Command[3]:
                            # Le fichier est retrouvé dans un paramètre de commande par la suite
                            if state.TempValues.value("Command")[2][2] == File:
                                # Message d'information
                                if state.TempValues.value("Command")[1] == "Information":
                                    Message = (
                                        state.TempValues.value("Command")[2][0]
                                        + " : "
                                        + state.TempValues.value("Command")[2][1]
                                    )
                                    QMessageBox.information(
                                        self,
                                        state.TempValues.value("Command")[2][0],
                                        state.TempValues.value("Command")[2][1],
                                    )

                                raise Found

                except Found:
                    pass

                # Si c'était la dernière commande
                if not state.CommandList:
                    self.WorkFinishedCompletly()
                    return

                # Récupération de la commande suivante à exécuter
                state.TempValues.setValue("Command", state.CommandList.pop(0))

            ## Mise à 0% de la barre de progression pour signaler le début du travail
            self.ui.progressBar.setValue(0)

            ## Messages d'info
            if state.TempValues.value("Command")[0] != "Open Subtitles":
                self.SetInfo(
                    self.Trad["WorkProgress"].format(state.TempValues.value("Command")[0]),
                    "800080",
                    True,
                    True,
                )

            if state.TempValues.value("Command")[1] != "echo":
                self.SetInfo(
                    self.Trad["WorkCmd"].format(
                        state.TempValues.value("Command")[1]
                        + " "
                        + " ".join(state.TempValues.value("Command")[2])
                    )
                )

            if Message:
                self.SetInfo(Message)

            ## Commande suivante
            self.WorkStart()

        ### Si c'était la dernière commande
        else:
            self.WorkFinishedCompletly()

    # ========================================================================
    def WorkFinishedCompletly(self):
        """Appelée lorsqu'il n'y a plus aucune commande à exécuter."""
        ### Si l'option de suppression des fichiers temporaire est activée
        if state.Configs.value("DelTempFiles"):
            ## Suppression des fichiers temporaires
            self.RemoveTempFiles()

        ### Remise en état des widgets
        self.WorkInProgress(False)

        ### Envoi de l'information au systray
        if state.Configs.value("SysTray"):
            # En cas d'arrêt
            if self.StopInProgress:
                self.SysTrayIcon.showMessage(
                    self.Trad["SysTrayStopTitle"],
                    self.Trad["SysTrayTotalStopText"],
                    QSystemTrayIcon.Warning,
                    3000,
                )

            # En cas d'erreur
            elif self.FinishState == "Error":
                self.SysTrayIcon.showMessage(
                    self.Trad["SysTrayErrorTitle"],
                    self.Trad["SysTrayTotalErrorText"],
                    QSystemTrayIcon.Critical,
                    3000,
                )
                self.RemoveTempFiles()

            # Si tout est OK
            else:
                self.SysTrayIcon.showMessage(
                    self.Trad["SysTrayFinishTitle"],
                    self.Trad["SysTrayTotalFinishText"],
                    QSystemTrayIcon.Information,
                    3000,
                )

    # ========================================================================
    def WorkPause(self):
        """Fonction de mise en pause du travail en cours."""
        ### PID du processus en cours
        PID = self.process.processId()

        ### Si aucun PID, c'est qu'il n'y a pas de processus
        if PID <= 0:
            return

        ### Chargement du PID
        try:
            Process = psutil.Process(PID)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            # [Claude] AMÉLIORATION : bare except remplacé par les exceptions psutil pertinentes.
            # NoSuchProcess si le PID a disparu entre la récupération et l'accès,
            # AccessDenied si les droits sont insuffisants.
            return

        ### Si le processus est en pause
        if Process.status() == "stopped":
            ## Reprise
            Process.resume()

            ## Bouton pose
            Icon = QIcon.fromTheme(
                "media-playback-pause", QIcon(":/img/media-playback-pause.png")
            )
            self.ui.mkv_pause.setIcon(Icon)
            self.ui.mkv_pause.setText(self.Trad["PauseText"])
            self.ui.mkv_pause.setStatusTip(self.Trad["PauseStatusTip"])

        ### S'il est en cours
        else:
            ## Mise en pause
            Process.suspend()

            ## Bouton reprise
            Icon = QIcon.fromTheme(
                "media-playback-start", QIcon(":/img/media-playback-start.png")
            )
            self.ui.mkv_pause.setIcon(Icon)
            self.ui.mkv_pause.setText(self.Trad["ResumeText"])
            self.ui.mkv_pause.setStatusTip(self.Trad["ResumeStatusTip"])

    # ========================================================================
    def WorkStop(self, Type):
        """Fonction d'arrêt du travail en cours."""
        # Type :
        # Error (en cas de plantage)
        # Stop (en cas d'arrêt du travail)
        # Close (en cas de fermeture du logiciel)
        # SrtError (en cas d'erreur tesseract)

        ### Variable évitant que la fonction soit appelée plusieurs fois comme avec Stop puis Error
        self.StopInProgress = True

        ### Teste l'état du processus pour ne pas le killer plusieurs fois (stop puis error)
        if self.process.state() != 0:
            ## Kill le boulot en cours
            self.process.kill()

            if not self.process.waitForFinished(1000):
                self.process.kill()  # Attend que le travail soit arrêté pdt 1s

        ### Suppression des fichiers temporaires
        self.RemoveTempFiles()

        ### Dans le cas spécifique de Qtesseract
        if state.TempValues.contains("Qtesseract5Folder"):
            Qtesseract5Folder = QFileInfo(state.TempValues.value("Qtesseract5Folder"))

            ## Suppression du dossier temporaire
            if Qtesseract5Folder.exists():
                QDir(Qtesseract5Folder.absoluteFilePath()).removeRecursively()

                state.TempValues.remove("Qtesseract5Folder")

        ### Réinitialisation de la liste des commandes
        state.CommandList.clear()

        ### Envoie du texte le plus adapté
        if Type == "Stop":
            self.StopInProgress = True
            self.SetInfo(self.Trad["WorkCanceled"], "FF0000", True)  # Travail annulé
            self.RemoveAllTempFiles()

            if state.Configs.value("SysTray"):
                self.SysTrayIcon.showMessage(
                    self.Trad["SysTrayStopTitle"],
                    self.Trad["SysTrayTotalStopText"],
                    QSystemTrayIcon.Warning,
                    3000,
                )

        elif Type in ("Error", "SrtError"):
            self.SetInfo(
                self.Trad["WorkError"], "FF0000", True
            )  # Erreur pendant le travail
            self.RemoveAllTempFiles()

            if state.Configs.value("SysTray"):
                self.SysTrayIcon.showMessage(
                    self.Trad["SysTrayErrorTitle"],
                    self.Trad["SysTrayTotalErrorText"],
                    QSystemTrayIcon.Critical,
                    3000,
                )

        elif Type == "Close":
            return

        ### Bouton pause
        if "psutil" in globals():
            Icon = QIcon.fromTheme(
                "media-playback-pause", QIcon(":/img/media-playback-pause.png")
            )
            self.ui.mkv_pause.setIcon(Icon)
            self.ui.mkv_pause.setText(self.Trad["PauseText"])
            self.ui.mkv_pause.setStatusTip(self.Trad["PauseStatusTip"])

        ### Modifications graphiques
        self.ui.progressBar.setValue(
            0
        )  # Remise à 0 de la barre de progression signifiant une erreur
        self.WorkInProgress(False)  # Remise en état des widgets

        ### Remise en place de la variable bloquante
        self.StopInProgress = False
