# Inspiration library

Use this folder to keep track of stories and visual references that inform Project Malfoid's development. The [tracked source catalog](sources.md) gives every item a link, source date (when available), catalog check date, short use note, and a source-appropriate way to save and refresh a private copy. Downloaded copies belong under `downloads/` and stay local; Git ignores that folder so third-party stories, art, and media are not redistributed by this repository.

## How to use it

- Add a source entry to [sources.md](sources.md) before or when saving a copy. Record the canonical URL, creator, source-posted/updated date if shown, **record checked** date, format and authorized download route, local-copy status, and any use limits. If a source date cannot be verified, write `not exposed` rather than guessing.
- Download only from an official source control and only for private research when allowed. For AO3, use its **Download** menu; for X or Reddit, bookmark first, and use the browser's Print → Save as PDF only for a personal text snapshot. Do not use third-party media downloaders or bypass a creator's download restriction.
- Put permitted offline text under `downloads/stories/`, images under `downloads/images/`, and other media under a clearly named subfolder. Use filenames like `creator-workid-format-YYYY-MM-DD.ext`; keep the canonical source URL and attribution notes in the catalog, not in a redistributable bundle.
- To update a record, reopen the canonical page, compare its displayed posted/updated date or version, and write a new `record checked` date. For works in progress, download again only through the source's official controls, replace the private copy, and update its local filename/date and SHA-256 in a private inventory. If the source is unchanged or its date is unavailable, record that; do not imply it was updated.
- Treat downloaded material as private reference. Do not copy its prose, dialogue, art, audio, or shot design into the project unless the contributor has permission and the reuse is documented.
- Commit only the catalog, original project notes, and permitted metadata. Never commit downloaded works, art, embedded media, private screenshots, or voice samples. Link publicly to creator pages or authorized releases instead.

The [creator directory](creator-directory.md) is a user-supplied list of artists, animators, writers, and other project inspirations. Its profile URLs are leads constructed from handles and are not verified endorsements or credits.

The [story-tweet index](tweets/INDEX.md) records reviewed source links and project-authored use notes. Only publish captured post text when the documented permission covers publication; keep archive-only captures local. The index distinguishes verified browser captures from owner-supplied text that could not be independently checked.

## Runnable research script

[`collect.py`](collect.py) is a Python 3 standard-library tool. It opens creator profiles in the default browser, records short findings and direct work links, writes a `research-results.json` file, and renders a shareable links-only [stories-and-projects.md](stories-and-projects.md) catalog. The initial [research-results.json](research-results.json) is seeded with all 123 unique X profiles found in the directory and the verified links gathered so far.

```sh
python3 inspiration/collect.py seed
python3 inspiration/collect.py review --limit 10
python3 inspiration/collect.py catalog
```

Repeat `review` until the accounts are checked. Use `--include-reviewed` to revisit earlier entries. The manual workflow needs no API key and saves progress after each creator.

Optional recent-post discovery uses the official X API, not X-page scraping. Set your own `X_BEARER_TOKEN` outside the repo, check X's current access, rate limits and pricing, then run:

```sh
export X_BEARER_TOKEN='your-own-X-app-bearer-token'
python3 inspiration/collect.py scan-x --max-accounts 10 --max-posts 20 --confirm-api-charges
```

`--max-accounts 0` scans all listed accounts; X API access can be paid and plan limits change. The API mode stores only post links, dates and outbound URLs, not post text or media. Review candidates in the browser and manually add direct story links and download methods.

### Download the AO3 works in the source list

The AO3 entries currently listed in [sources.md](sources.md) are [*Worst Enemy*](https://archiveofourown.org/works/93605026), [*Drakania Malfoy meets the Boy-Who-Lived*](https://archiveofourown.org/works/93572206), and [the first-year fanfic listing](https://archiveofourown.org/works/93789121). From the repository root, run:

```sh
python3 inspiration/collect.py download-ao3-list --format epub
```

The command reads canonical `/works/{id}` links from `sources.md`, shows the URLs, asks once before downloading, and saves offered EPUBs under the ignored `inspiration/downloads/stories/` folder. It skips copies already present. Add another AO3 work link to `sources.md` to include it in later runs. To refresh or replace existing files, add `--force` after checking the work's source page.

It only follows the format link AO3 itself exposes on each public work page. It does not log in, fetch restricted works, or work around disabled downloads. AO3 can ask clients to wait; this script spaces work requests and reports unavailable or restricted works. See AO3's [Downloading Fanworks FAQ](https://archiveofourown.org/faq/downloading-fanworks) for download formats and update behavior.

To save one permitted public work outside the source list, use the single-work command:

```sh
python3 inspiration/collect.py download-ao3 https://archiveofourown.org/works/123456 --format epub
```

Downloads remain private local copies; they are never added to the generated catalog or Git. For a work in progress, rerun the command after updates to fetch a newer copy.

### Convert an EPUB to plain text

For an EPUB you are permitted to keep, use the standard-library converter. It follows the EPUB reading order, keeps chapter and paragraph breaks, and needs no packages beyond Python 3. From the repository root, for example:

```sh
python3 inspiration/epub_to_text.py \
  "inspiration/downloads/stories/nomootwo-416789252-epub-2026-10-05.epub" \
  "inspiration/epub-text/nomootwo-416789252-text-2026-10-05.txt"
```

Replace the input and output paths for other books. The script refuses to overwrite an existing text file; remove the old output first if you want to regenerate it. EPUBs stay under the ignored `inspiration/downloads/stories/` folder, while converted text goes in the unignored `inspiration/epub-text/` folder and appears in `git status`. Conversion does not stage or commit the output; only commit or redistribute it when permission covers publication. The converter omits images and ebook layout.

For X API setup and endpoint behavior, see [user lookup](https://docs.x.com/x-api/users/get-user-by-username), [user posts timeline](https://docs.x.com/x-api/users/get-posts), and [application-only authentication](https://docs.x.com/fundamentals/authentication/oauth-2-0/application-only). Access and pricing can change; the script deliberately requires an explicit cost acknowledgement before scanning.

The local design-reference set currently copied into `downloads/images/malfoid-long-hair/` is private and ignored by Git. The tracked catalog records its attribution and reuse limits.
