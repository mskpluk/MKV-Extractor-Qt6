# Changelog

This fork follows MKV Extractor Qt6 v26.04.29 and repairs what does not work in it.
Nothing else is changed: same program, same interface, same way of working.

## Unreleased — fixes on top of v26.04.29

### Extraction

- **Extracting an audio track with no name failed.** Pressing Execute did nothing
  at all and the terminal showed `AttributeError: 'int' object has no attribute
  'replace'`. Most releases carry a single unnamed audio track, so this stopped the
  program from doing its main job.
- **Extracted files are named after the language.** A track with no name used to
  produce `1_audio_48000.eac3`, named after the sampling frequency that the table
  shows as a placeholder. It now produces `1_audio_pol.eac3`, which tells you which
  track you are looking at. Named tracks keep their name, attachments keep theirs.
- **A forced subtitle track says so in its file name.** It comes out as
  `2_subtitles_pol_forced.srt`, which is the difference you actually look for when a
  film carries two Polish tracks. A track whose name already says it is forced is
  left alone.
- **An extracted video track no longer pretends to be a Matroska file.** It was
  always called `.mkv`, although what is written is a raw stream. It now gets the
  extension of its codec, `0_video_eng.h264` for H.264.

### Remux

- **Remux crashed before it started.** Every path leading to it ended in
  `NameError: name 'Qt' is not defined`, because the module using it never imported
  it. This affected both the window asking whether to use MKVToolNix-Gui and the one
  asking where to save the result.
- **Placeholder names are no longer written into the file.** Remuxing used to store
  the table placeholder as the real track name, so tracks came out of it called
  `48000` or `640x360`. A track that had no name keeps having none.
- **Track flags survive a remux.** A forced subtitle track came out of a remux no
  longer forced, and every track came out marked as the default one — two default
  subtitle tracks at once, so players picked whichever they felt like.
- **The video track keeps its language.** An English video track came out of a remux
  as undefined, because the language was never passed on.

### Appearance and packaging

- **The program has its icon back.** The desktop entry pointed at a directory where
  no icon is installed, so menus had nothing to show.
- **The button offering this program is spelled correctly.** It read
  "MKV Extracor Qt 5" — a missing letter, and the version of the predecessor.
- **The About entry and its translations say Qt6.** Six languages still described
  the program as its Qt5 predecessor. Links to the old project pages and titles of
  old articles are left alone, since those are genuinely about Qt5.
- **The build notes point at packages that exist.** `python3-pyside6` is the name of
  a source package; Debian and Ubuntu ship PySide6 one module per package. The same
  wrong name reached users through the AppImage error message.

### Still open

The `.deb` packages published upstream declare `Depends: python3-pyside6` and
therefore install on no Debian or Ubuntu release. That file is not part of this
repository, so it cannot be fixed here; the three package names to use instead are
`python3-pyside6.qtcore`, `python3-pyside6.qtgui` and `python3-pyside6.qtwidgets`.
