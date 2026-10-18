#!/bin/bash
# Builds a .deb straight from this repository.
#
#   sudo apt install pyside6-tools qt6-l10n-tools dpkg-dev
#   ./packaging/build-deb.sh
#
# Writes generated files into the working tree, so build from a copy if that
# matters. VERSION, MAINTAINER and OUT can be set from the environment.
#
# The result lands next to the repository. Set MAINTAINER to put your own
# name on a package you intend to hand to anybody else.

set -euo pipefail

REPO="$(cd "$(dirname "$0")/.."; pwd)"
VERSION="${VERSION:-26.04.29d+fork1}"
MAINTAINER="${MAINTAINER:-mskpluk <mskpluk@users.noreply.github.com>}"
BUILD="$(mktemp -d)"
PKG="${BUILD}/mkv-extractor-qt6"
OUT="${OUT:-${REPO}/../mkv-extractor-qt6_${VERSION}_all.deb}"

trap 'rm -rf "${BUILD}"' EXIT

### Generated files: the interface, the resources and the translations
cd "${REPO}"
LRELEASE="$(command -v lrelease || echo /usr/lib/qt6/bin/lrelease)"
"${LRELEASE}" Languages/*.ts QFileDialogCustom/*.ts >/dev/null

pyside6-rcc MKVRessources.qrc -o "${BUILD}/MKVRessources_rc.py"
pyside6-uic ui_MKVExtractorQt6.ui -o "${BUILD}/ui_MKVExtractorQt6.py"

# Fall back to the bundled icons when the theme has none, as build.sh does
for icon in img/*; do
    name="${icon##*/}"; name="${name%.*}"
    sed -i "s@QtGui.QIcon.fromTheme(\"${name}\")@QtGui.QIcon.fromTheme(\"${name}\", QtGui.QIcon(\":/${icon}\"))@" \
        "${BUILD}/ui_MKVExtractorQt6.py"
done

### The tree that gets installed
APP="${PKG}/usr/share/mkv-extractor-qt6"
install -d "${PKG}/usr/bin" "${APP}/Languages" "${APP}/QFileDialogCustom" "${APP}/WhatsUp" \
           "${PKG}/usr/share/applications" \
           "${PKG}/usr/share/icons/hicolor/256x256/apps" "${PKG}/usr/share/doc/mkv-extractor-qt6" \
           "${PKG}/usr/share/man/man1" "${PKG}/usr/share/man/fr/man1" "${PKG}/DEBIAN"

install -m 755 MKVExtractorQt6.py "${APP}/"
install -m 644 CodecListFile.py CommandMixin.py CustomWidgets.py MKVToolsMixin.py \
               SoftwareMixin.py state.py TracksMixin.py WorkMixin.py "${APP}/"
install -m 644 "${BUILD}/MKVRessources_rc.py" "${BUILD}/ui_MKVExtractorQt6.py" "${APP}/"
install -m 644 Languages/*.qm "${APP}/Languages/"
install -m 644 QFileDialogCustom/QFileDialogCustom.py QFileDialogCustom/*.qm "${APP}/QFileDialogCustom/"
install -m 644 WhatsUp/WhatsUp.py "${APP}/WhatsUp/"
ln -s /usr/share/mkv-extractor-qt6/MKVExtractorQt6.py "${PKG}/usr/bin/mkv-extractor-qt6"

install -m 644 mkv-extractor-qt6.desktop "${PKG}/usr/share/applications/"
install -m 644 icons/mkv-extractor-qt6.png icons/mkv-extractor-qt6.webp \
               "${PKG}/usr/share/icons/hicolor/256x256/apps/"
gzip -9nc man/mkv-extractor-qt6.1 > "${PKG}/usr/share/man/man1/mkv-extractor-qt6.1.gz"
gzip -9nc man/mkv-extractor-qt6.fr.1 > "${PKG}/usr/share/man/fr/man1/mkv-extractor-qt6.1.gz"
chmod 644 "${PKG}/usr/share/man/man1/mkv-extractor-qt6.1.gz" \
          "${PKG}/usr/share/man/fr/man1/mkv-extractor-qt6.1.gz"
install -m 644 LICENSE "${PKG}/usr/share/doc/mkv-extractor-qt6/copyright"
install -m 644 "${REPO}/packaging/AUTHORS" "${PKG}/usr/share/doc/mkv-extractor-qt6/AUTHORS"

### Changelog, shown by the program itself under "What's new"
sed -e "s/@VERSION@/${VERSION}/" -e "s/@MAINTAINER@/${MAINTAINER}/" \
    -e "s/@DATE@/$(date -R)/" "${REPO}/packaging/changelog.in" | gzip -9n \
    > "${PKG}/usr/share/doc/mkv-extractor-qt6/changelog.Debian.gz"
chmod 644 "${PKG}/usr/share/doc/mkv-extractor-qt6/changelog.Debian.gz"

### Package metadata
sed -e "s/@VERSION@/${VERSION}/" -e "s/@MAINTAINER@/${MAINTAINER}/" \
    -e "s/@SIZE@/$(du -ks "${PKG}" | cut -f1)/" "${REPO}/packaging/control.in" > "${PKG}/DEBIAN/control"
for script in postinst prerm postrm; do
    install -m 755 "${REPO}/packaging/${script}" "${PKG}/DEBIAN/${script}"
done

(cd "${PKG}" && find . -type f ! -path './DEBIAN/*' -printf '%P\0' | sort -z | xargs -0 md5sum > DEBIAN/md5sums)

dpkg-deb --build --root-owner-group "${PKG}" "${OUT}"
echo "Built ${OUT}"
