# Local source movie

Project Malfoid uses a user-supplied local reference copy of *Harry Potter and the Philosopher's Stone* (2001), labeled as the extended edition. It supports private story, timing, and production research. The edition label describes the supplied file; it is not independent authentication of a studio release.

The file is stored locally at:

```text
production/assets/source/harry-potter-philosophers-stone-2001-extended.mkv
```

The repository's `.gitignore` excludes `production/assets/source/`. The movie must remain outside Git's index, Git LFS, release attachments, and public storage. This document describes the input without distributing a copy or a download link. Reading public stories, watching released project media, and using source-independent examples do not require this file. Any workflow that does require it must identify that dependency explicitly and offer a separate public example where practical.

## Recorded intake metadata

These details come from the existing October 4, 2026 intake record; this documentation update did not rerun a full media probe or byte comparison.

| Field | Recorded value |
|---|---|
| Source | User-supplied local file |
| Container | Matroska (`.mkv`) |
| File size | 7,397,079,120 bytes |
| Runtime | 2:38:50.56 (9,530.56 seconds) |
| Picture | 1920×1080 H.264, progressive |
| Frame rate | 24000/1001 fps |
| Color | BT.709, limited range |
| Audio | English AC-3, 48 kHz, 5.1(side) |
| Subtitles | English SubRip track |
| Timing | Recorded video start is 5 ms after audio start |
| Project copy | APFS clone; intake record reports a full byte comparison with the supplied file |

The project copy is not an independent backup. Preserve the intake record privately, including any machine-specific paths. Public documentation should use repository-relative paths and omit download-directory names, private service links, and personal information.

Possession and technical verification of this file do not establish adaptation, redistribution, training, or public-performance rights. Review the proposed use of source excerpts, references, voices, and franchise elements separately from the rule excluding the full movie. The project's own generated scenes and eventual finished feature have their own provenance and release decisions; they are not the source movie documented here.
