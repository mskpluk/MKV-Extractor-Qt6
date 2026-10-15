#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""État global de l'application, partagé entre tous les modules."""

# Application Qt
app = None

# Dossier du logiciel (défini au démarrage)
AppFolder = ""

# Configuration persistante (QSettings)
Configs = None

# Valeurs temporaires de session (QSettings)
TempValues = None

# Pistes du fichier MKV courant
MKVDico = {}

# Pistes sélectionnées
MKVDicoSelect = {}

# Infos des pistes qui ne tiennent pas dans le tableau : le nom affiché
# est-il un vrai nom ou une valeur de remplacement, et la langue
TrackMeta = {}

# Langues disponibles dans les combobox
MKVLanguages = []

# Widgets de puissance AC3
PowerList = {}

# Widgets de qualité AC3
QualityList = {}

# Widgets de conversion Sub→Srt
Sub2Srt = {}

# Widgets de conversion Sup→Sub
Sup2Sub = {}

# Fichiers temporaires avant ré-encapsulage
TempFiles = []

# Tous les fichiers créés (pour nettoyage en cas d'arrêt)
AllTempFiles = []

# File des commandes à exécuter
CommandList = []

# Fichiers sous-titres à ouvrir avant encapsulage
SubtitlesFiles = []

# Retours de mkvmerge en cas de warning
WarningReply = []

# Cache d'exécutabilité des logiciels
SoftExec = {}
