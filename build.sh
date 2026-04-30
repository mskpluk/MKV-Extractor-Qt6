#!/bin/bash

# sudo apt install pyside6-tools qt6-tools-dev-tools python3-pyside6

# Script de build pour PySide6

chemin="$(cd "$(dirname "$0")"; pwd)"
cd "${chemin}"

### Mise à jour des fichiers .ts depuis les fichiers sources
pyside6-lupdate ui_MKVExtractorQt6.ui MKVExtractorQt6.py -ts Languages/MKVExtractorQt6_fr_FR.ts \
    Languages/MKVExtractorQt6_cs_CZ.ts \
    Languages/MKVExtractorQt6_de_DE.ts \
    Languages/MKVExtractorQt6_es_ES.ts \
    Languages/MKVExtractorQt6_en_US.ts \
    Languages/MKVExtractorQt6_it_IT.ts \
    Languages/MKVExtractorQt6_tr_TR.ts

pyside6-lupdate QFileDialogCustom/QFileDialogCustom.py -ts QFileDialogCustom/QFileDialogCustom_fr_FR.ts \
    QFileDialogCustom/QFileDialogCustom_cs_CZ.ts \
    QFileDialogCustom/QFileDialogCustom_de_DE.ts \
    QFileDialogCustom/QFileDialogCustom_en_US.ts \
    QFileDialogCustom/QFileDialogCustom_es_ES.ts \
    QFileDialogCustom/QFileDialogCustom_it_IT.ts \
    QFileDialogCustom/QFileDialogCustom_tr_TR.ts


### Compilation des fichiers .ts en .qm
if [[ -e "/usr/lib/x86_64-linux-gnu/qt6/bin/lrelease" ]]; then
    /usr/lib/x86_64-linux-gnu/qt6/bin/lrelease Languages/*.ts QFileDialogCustom/*.ts

elif [[ -e "/usr/lib/i386-linux-gnu/qt6/bin/lrelease" ]]; then
    /usr/lib/i386-linux-gnu/qt6/bin/lrelease Languages/*.ts QFileDialogCustom/*.ts

elif [[ $(which pyside6-lrelease) ]] ; then
    pyside6-lrelease Languages/*.ts QFileDialogCustom/*.ts

else
    echo "cannot find 'lrelease' for Qt6"
    exit 1
fi

### Génération du fichier .qrc (ressources)
echo '<RCC>
  <qresource prefix="/">' > MKVRessources.qrc

for icon in img/*
do
    echo "    <file>${icon}</file>" >> MKVRessources.qrc
done

echo "    <file>icons/mkv-extractor-qt6.webp</file>" >> MKVRessources.qrc
echo '  </qresource>
</RCC>' >> MKVRessources.qrc

### Compilation des ressources Qt
pyside6-rcc MKVRessources.qrc -o MKVRessources_rc.py

### Compilation de l'interface Qt Designer
pyside6-uic ui_MKVExtractorQt6.ui -o ui_MKVExtractorQt6.py

### Ajout des icônes par défaut si absents du thème
for icon in img/*
do
    nom=${icon##*/}
    nom=${nom%.*}
    sed -i "s@QtGui.QIcon.fromTheme(\"${nom}\")@QtGui.QIcon.fromTheme(\"${nom}\", QtGui.QIcon(\":/${icon}\"))@" ui_MKVExtractorQt6.py
done

### Génération de l'AppImage
VERSION=$(grep 'setApplicationVersion' MKVExtractorQt6.py | grep -oP '"\K[^"]+')
APPDIR="/tmp/MKVExtractorQt6.AppDir"
OUTPUT="$(dirname "${chemin}")"
APPIMAGETOOL="${HOME}/.local/bin/appimagetool"
APPIMAGE="${OUTPUT}/MKVExtractorQt6-${VERSION}-x86_64.AppImage"

# Téléchargement de appimagetool si absent
if [[ ! -x "${APPIMAGETOOL}" ]]; then
    echo "Téléchargement de appimagetool..."
    mkdir -p "${HOME}/.local/bin"
    curl -L -o "${APPIMAGETOOL}" \
        "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
    chmod +x "${APPIMAGETOOL}"
fi

# Création de l'arborescence AppDir
rm -rf "${APPDIR}"
mkdir -p "${APPDIR}/usr/share/mkv-extractor-qt6"
mkdir -p "${APPDIR}/usr/share/icons/hicolor/256x256/apps"

# Copie des fichiers de l'application
cp *.py "${APPDIR}/usr/share/mkv-extractor-qt6/"
cp -r Languages QFileDialogCustom icons img WhatsUp "${APPDIR}/usr/share/mkv-extractor-qt6/"

# Icône
cp icons/mkv-extractor-qt6.png "${APPDIR}/mkv-extractor-qt6.png"
cp icons/mkv-extractor-qt6.png "${APPDIR}/usr/share/icons/hicolor/256x256/apps/mkv-extractor-qt6.png"

# Fichier desktop (Icon sans chemin absolu, requis par AppImage)
sed 's|^Icon=.*|Icon=mkv-extractor-qt6|' mkv-extractor-qt6.desktop > "${APPDIR}/mkv-extractor-qt6.desktop"

# Script AppRun
cat > "${APPDIR}/AppRun" << 'APPRUN'
#!/bin/bash
APPDIR="$(dirname "$(readlink -f "$0")")"
APPDATA="$APPDIR/usr/share/mkv-extractor-qt6"

check_dep() {
    python3 -c "import $1" 2>/dev/null || {
        echo "Erreur : le module Python '$1' n'est pas installé."
        echo "  Sur Ubuntu/Debian : sudo apt install python3-pyside6"
        exit 1
    }
}

check_dep PySide6

if ! command -v mkvextract &>/dev/null; then
    echo "Avertissement : mkvtoolnix n'est pas installé. Installez-le avec : sudo apt install mkvtoolnix"
fi

exec python3 "$APPDATA/MKVExtractorQt6.py" "$@"
APPRUN
chmod +x "${APPDIR}/AppRun"

# Construction de l'AppImage
echo "Génération de l'AppImage : ${APPIMAGE}"
ARCH=x86_64 "${APPIMAGETOOL}" "${APPDIR}" "${APPIMAGE}"

if [[ -f "${APPIMAGE}" ]]; then
    echo "AppImage générée : ${APPIMAGE} ($(du -sh "${APPIMAGE}" | cut -f1))"
else
    echo "Échec de la génération de l'AppImage"
    exit 1
fi
