# Local downloaded references

Downloaded stories, art, audio, and video in this directory stay local for private research and must not be committed. The three tracked `.txt` files under `stories/` are link-only reference notes; they contain titles and canonical AO3 links, not story text. The tracked source index and per-source download/update instructions are at `../sources.md`.

## Download and refresh routine

1. Find the work at its canonical creator/platform page and add or update its entry in `../sources.md` first. Record the source's posted/updated date if visible and today's `record checked` date. Use `not exposed` when a date cannot be confirmed.
2. Follow only the platform's own download action. For AO3, use the work's **Download** menu and choose a reading format. For X/Reddit text, prefer a bookmark; if an offline snapshot is needed, use browser Print → Save as PDF. If a creator disables downloading or the page provides no supported download, keep a link instead of bypassing the restriction.
3. Save an allowed personal copy in the matching subfolder with creator/work ID/format/retrieved date in the filename. Put no copies in Git.
4. To refresh, reopen the canonical link, check whether the source has a newer posted/updated date or content, and use the official download control again if permitted. Replace the old private copy and refresh its date and SHA-256 in a private inventory; otherwise, record that it was checked and unchanged or that its update date is unavailable.
5. Keep attribution, access limits, and the reason for saving alongside the catalog record. Do not use the copy as a generation input or redistribute it without separate permission.

Subfolders:

- `stories/` — private reading copies where downloading is permitted; tracked text notes contain links only.
- `images/` — private visual references; record creator, source, and use limits beside each set.
- Add `audio/` or `video/` only when needed, and document source and permission before saving material.
