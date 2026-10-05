# Scene production folders

Use this folder for scene-by-scene production packets. Give each scene a stable ID, for example `MF01-SC010/`, and keep its script revision, shot list, storyboard links, status, provenance, and review notes together or linked from its scene index.

## Video location

Put local scene videos under the scene folder’s `video/` subfolder, for example `films/scenes/MF01-SC010/video/`. Render files in these folders are intentionally ignored by Git; do not commit video binaries. Keep the video locally, or publish an approved cut to a durable release or media host and put the URL, version, checksum, and access notes in a tracked scene index. Do not use machine-specific file links in public notes.

The repository’s existing reviewed demo in `media/video/` is a separately curated public preview. New scene renders do not belong there by default; move a cut into public media only after a release review of picture, sound, rights, provenance, and credits.

## Suggested scene packet

- `README.md` — scene ID, status, logline, current cut link, continuity dependencies, and review checklist.
- `script/` — dated or versioned dialogue drafts.
- `boards/` — board pages or links to a reviewed board export.
- `video/` — local, ignored working renders and animatics.
- `references.md` — allowed reference links, source notes, and provenance.

Keep work-in-progress clearly labeled. A preview render does not mean the scene is approved or locked in the feature.
