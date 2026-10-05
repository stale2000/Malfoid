#!/usr/bin/env python3
"""Review creator profiles, track story links, and save permitted AO3 copies.

This tool is intentionally user-assisted. It does not scrape X pages or fetch
creator media. Optional X API discovery requires the caller's own credentials
and explicit acknowledgement of possible API charges.
"""

from __future__ import annotations

import argparse
import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import sys
from datetime import date
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urljoin, urlparse
from urllib.request import Request, urlopen
import webbrowser


ROOT = Path(__file__).resolve().parent
DIRECTORY = ROOT / "creator-directory.md"
DATA_FILE = ROOT / "research-results.json"
CATALOG_FILE = ROOT / "stories-and-projects.md"
SOURCE_CATALOG = ROOT / "sources.md"
DOWNLOAD_DIR = ROOT / "downloads" / "stories"
USER_AGENT = "MalfoidInspirationResearch/1.0 (user-directed; no scraping)"
ALLOWED_AO3_HOSTS = {
    "archiveofourown.org",
    "www.archiveofourown.org",
    "download.archiveofourown.org",
    "archive.transformativeworks.org",
}


def today() -> str:
    return date.today().isoformat()


def load_data() -> dict:
    if not DATA_FILE.exists():
        return {"schema_version": 1, "creators": []}
    with DATA_FILE.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if data.get("schema_version") != 1 or not isinstance(data.get("creators"), list):
        raise ValueError(f"Unsupported research file: {DATA_FILE}")
    return data


def save_data(data: dict) -> None:
    data["last_catalog_updated"] = today()
    temporary = DATA_FILE.with_suffix(".json.tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    temporary.replace(DATA_FILE)


def creator_rows() -> list[dict]:
    """Read X profile links and section names from the human-maintained list."""
    section = "Uncategorized"
    found: dict[str, dict] = {}
    link_pattern = re.compile(r"\[([^\]]+)\]\((https?://(?:www\.)?x\.com/[^)]+)\)")
    for line in DIRECTORY.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            section = line[3:].strip()
        for label, profile in link_pattern.findall(line):
            parsed = urlparse(profile)
            handle = parsed.path.strip("/").split("/", 1)[0]
            if not handle or handle.lower() in {"home", "search", "explore"}:
                continue
            # A status link is a specific post, not an account profile.
            if parsed.path.strip("/").split("/")[1:2] == ["status"]:
                continue
            key = handle.casefold()
            row = found.setdefault(key, {
                "handle": handle,
                "profile_url": f"https://x.com/{handle}",
                "categories": [],
                "status": "not_reviewed",
                "checked_on": None,
                "summary": "",
                "works": [],
                "candidate_posts": [],
            })
            if section not in row["categories"]:
                row["categories"].append(section)
    return list(found.values())


def seed() -> None:
    data = load_data()
    current = {row["handle"].casefold(): row for row in data["creators"]}
    added = 0
    for row in creator_rows():
        key = row["handle"].casefold()
        if key not in current:
            data["creators"].append(row)
            current[key] = row
            added += 1
        else:
            # Keep research and user edits, but refresh profile/group links.
            current[key]["profile_url"] = row["profile_url"]
            current[key]["categories"] = sorted(set(current[key].get("categories", []) + row["categories"]))
    data["creators"].sort(key=lambda row: row["handle"].casefold())
    save_data(data)
    pending = sum(row.get("status") != "reviewed" for row in data["creators"])
    print(f"Added {added} accounts; {len(data['creators'])} unique accounts in {DATA_FILE} ({pending} still need review).")


def download_hint(url: str) -> str:
    host = (urlparse(url).hostname or "").lower()
    if host.endswith("archiveofourown.org") or host.endswith("transformativeworks.org"):
        return "Open the AO3 work page and use Download if offered; choose a format. Redownload WIPs after updates."
    if host in {"x.com", "www.x.com", "twitter.com", "www.twitter.com"}:
        return "Bookmark the post. For text-only offline reference, browser Print > Save as PDF; use creator-enabled media download only."
    if host.endswith("reddit.com"):
        return "Use Reddit Save; for a text snapshot, browser Print > Save as PDF."
    if host.endswith("suno.com"):
        return "Use the track's own share/download controls; otherwise keep the link."
    return "Use the source's own download/share controls; otherwise keep the link."


def prompt_text(label: str, current: str = "") -> str:
    suffix = f" [{current}]" if current else ""
    value = input(f"{label}{suffix}: ").strip()
    return value if value else current


def review(limit: int | None, include_reviewed: bool) -> None:
    if not DATA_FILE.exists():
        seed()
    data = load_data()
    rows = [row for row in data["creators"] if include_reviewed or row.get("status") != "reviewed"]
    if limit is not None:
        rows = rows[:limit]
    print("Review each profile in the browser. Record only short factual notes and direct links, not story text.")
    for index, row in enumerate(rows, 1):
        print(f"\n[{index}/{len(rows)}] @{row['handle']} — {', '.join(row.get('categories', []))}")
        print(row["profile_url"])
        if input("Press Enter to open the profile (or type q to stop): ").strip().lower() == "q":
            break
        if input("Open this profile now? [Y/n] ").strip().lower() not in {"n", "no"}:
            webbrowser.open_new_tab(row["profile_url"])
        candidates = row.get("candidate_posts", [])
        if candidates:
            print("Candidate posts from the optional X API scan:")
            for candidate in candidates:
                print(f"  {candidate.get('posted', 'date unknown')} {candidate['url']}")
                for outbound in candidate.get("outbound_urls", []):
                    print(f"    -> {outbound}")
        if input("Was the creator/project verified from the source page? [y/N] ").strip().lower() not in {"y", "yes"}:
            row["status"] = "not_verified"
            row["checked_on"] = today()
            row["verification_note"] = prompt_text("Why not verified", row.get("verification_note", ""))
            save_data(data)
            continue

        row["summary"] = prompt_text("What are they building? (brief factual summary)", row.get("summary", ""))
        row["source_updated"] = prompt_text("Source posted/updated date (YYYY-MM-DD or unknown)", row.get("source_updated", "unknown"))
        row["checked_on"] = today()
        row["status"] = "reviewed"
        print("Add direct story/project URLs. Leave URL blank when finished.")
        while True:
            url = input("Work/post URL: ").strip()
            if not url:
                break
            title = prompt_text("Title (or short label)")
            method = prompt_text("Download/save method", download_hint(url))
            source_updated = prompt_text("Work's posted/updated date (YYYY-MM-DD or unknown)", "unknown")
            row.setdefault("works", []).append({
                "title": title or url,
                "url": url,
                "source_updated": source_updated,
                "checked_on": today(),
                "download_method": method,
            })
        save_data(data)  # Save after each profile so an interrupted pass retains work.
    print(f"\nSaved research metadata to {DATA_FILE}. No work text or media was copied.")


def markdown_escape(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()


def render_catalog() -> None:
    data = load_data()
    lines = [
        "# Creator activity and story links",
        "",
        f"**Catalog generated:** {today()}  ",
        "**Research file:** `research-results.json`  ",
        "**Scope:** User-reviewed source links and short notes only; this file never embeds story text or media.",
        "",
        "Entries are not verified until the source page is checked. Source dates and catalog check dates are recorded separately.",
        "",
    ]
    for row in data["creators"]:
        lines.extend([
            f"## [{markdown_escape('@' + row['handle'])}]({row['profile_url']})",
            "",
            f"- **Status:** {markdown_escape(row.get('status', 'not_reviewed'))}",
            f"- **Categories:** {markdown_escape(', '.join(row.get('categories', [])))}",
            f"- **Last checked:** {markdown_escape(row.get('checked_on') or 'not checked')}",
            f"- **Activity:** {markdown_escape(row.get('summary') or 'Not yet recorded.')}",
        ])
        if row.get("verification_note"):
            lines.append(f"- **Verification note:** {markdown_escape(row['verification_note'])}")
        works = row.get("works", [])
        if works:
            lines.extend(["", "### Stories and projects", ""])
            for work in works:
                lines.extend([
                    f"- [{markdown_escape(work.get('title', 'Untitled'))}]({work['url']})",
                    f"  - **Source date:** {markdown_escape(work.get('source_updated', 'unknown'))}; **checked:** {markdown_escape(work.get('checked_on', 'unknown'))}.",
                    f"  - **Download/save:** {markdown_escape(work.get('download_method', 'Use the source site’s official controls.'))}",
                ])
        candidates = row.get("candidate_posts", [])
        if candidates:
            lines.extend(["", "### X posts awaiting manual review", ""])
            for candidate in candidates:
                posted = markdown_escape(candidate.get("posted", "date unknown"))
                lines.append(f"- [{posted}]({candidate['url']})")
                for outbound in candidate.get("outbound_urls", []):
                    lines.append(f"  - Link in post: {outbound}")
        lines.append("")
    CATALOG_FILE.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print(f"Wrote {CATALOG_FILE} with {len(data['creators'])} creator records.")


def x_api_get(url: str, token: str) -> dict:
    request = Request(url, headers={
        "Authorization": f"Bearer {token}",
        "User-Agent": USER_AGENT,
    })
    with urlopen(request, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return payload


def scan_x(max_accounts: int, max_posts: int, since: str | None, confirmed: bool) -> None:
    """Use official X API read endpoints; never scrape x.com HTML or save post text."""
    token = os.environ.get("X_BEARER_TOKEN", "").strip()
    if not token:
        raise ValueError("Set X_BEARER_TOKEN to your own X developer app bearer token. The script never stores it.")
    if not confirmed:
        raise ValueError("X API usage can incur charges. Recheck current X pricing, then pass --confirm-api-charges to proceed.")
    if max_posts < 5:
        raise ValueError("--max-posts must be at least 5 because that is the API minimum page size.")
    if not DATA_FILE.exists():
        seed()
    data = load_data()
    rows = data["creators"] if max_accounts == 0 else data["creators"][:max_accounts]
    print(f"Scanning up to {len(rows)} accounts, up to {max_posts} recent posts each. X fees and rate limits vary; no post text/media will be saved.")
    if input("Continue with official X API requests? [y/N] ").strip().lower() not in {"y", "yes"}:
        print("Cancelled.")
        return

    for index, row in enumerate(rows, 1):
        handle = row["handle"]
        print(f"[{index}/{len(rows)}] @{handle}")
        try:
            user_data = x_api_get(f"https://api.x.com/2/users/by/username/{handle}", token)
            user = user_data.get("data") or {}
            user_id = user.get("id")
            if not user_id:
                row["api_status"] = "user_not_found"
                row["api_checked_on"] = today()
                save_data(data)
                continue
            params = {"max_results": str(min(max(max_posts, 5), 100)), "tweet.fields": "created_at,entities"}
            if since:
                params["start_time"] = f"{since}T00:00:00Z"
            candidate_posts = []
            next_token = None
            fetched = 0
            while fetched < max_posts:
                remaining = max_posts - fetched
                if fetched and remaining < 5:
                    break  # X's endpoint minimum page size is five.
                query = dict(params)
                query["max_results"] = str(min(100, remaining))
                if next_token:
                    query["pagination_token"] = next_token
                query_string = urlencode(query)
                payload = x_api_get(f"https://api.x.com/2/users/{user_id}/tweets?{query_string}", token)
                posts = payload.get("data", [])
                for post in posts:
                    entities = post.get("entities", {})
                    urls = []
                    for entity in entities.get("urls", []):
                        expanded = entity.get("unwound_url") or entity.get("expanded_url") or entity.get("url")
                        if expanded:
                            urls.append(expanded)
                    post_id = post.get("id")
                    if post_id:
                        candidate_posts.append({
                            "url": f"https://x.com/{handle}/status/{post_id}",
                            "posted": post.get("created_at", "unknown"),
                            "outbound_urls": list(dict.fromkeys(urls)),
                        })
                fetched += len(posts)
                next_token = payload.get("meta", {}).get("next_token")
                if not posts or not next_token:
                    break
            row["candidate_posts"] = candidate_posts
            row["api_status"] = "ok"
            row["api_checked_on"] = today()
            row["api_posts_fetched"] = fetched
        except HTTPError as exc:
            row["api_status"] = f"http_{exc.code}"
            row["api_checked_on"] = today()
            row["api_note"] = "Check X app access, protected-account visibility, developer plan, and rate-limit reset."
            if exc.code in {401, 402, 429}:
                save_data(data)
                print(f"Stopping the scan after HTTP {exc.code}; check credentials, billing, or rate limits before retrying.")
                break
        except (URLError, TimeoutError, json.JSONDecodeError) as exc:
            row["api_status"] = "request_error"
            row["api_checked_on"] = today()
            row["api_note"] = str(exc)
        save_data(data)
    print(f"Saved post links and outbound URLs in {DATA_FILE}. Use review to inspect candidates and enter direct work links.")


class DownloadLinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        href = dict(attrs).get("href")
        if href:
            self.links.append(href)


class AO3RateLimitError(RuntimeError):
    """Signal that a batch should stop making requests for now."""


def validate_ao3_work(url: str) -> tuple[str, str]:
    parsed = urlparse(url)
    match = re.fullmatch(r"/works/(\d+)(?:/.*)?", parsed.path)
    if parsed.scheme != "https" or parsed.hostname not in ALLOWED_AO3_HOSTS or not match:
        raise ValueError("Use a canonical HTTPS AO3 work URL, such as https://archiveofourown.org/works/123456")
    work_id = match.group(1)
    work_url = f"https://archiveofourown.org/works/{work_id}"
    return work_id, work_url


def ao3_work_urls(source_list: Path) -> list[str]:
    """Return unique canonical AO3 work links listed in the source catalog."""
    if not source_list.is_file():
        raise FileNotFoundError(f"AO3 source list not found: {source_list}")
    markdown = source_list.read_text(encoding="utf-8")
    urls = re.findall(
        r"\]\((https://archiveofourown\.org/works/(\d+))(?:/[^)]*)?\)",
        markdown,
        flags=re.IGNORECASE,
    )
    seen: set[str] = set()
    work_urls = []
    for url, work_id in urls:
        canonical_url = f"https://archiveofourown.org/works/{work_id}"
        if work_id not in seen:
            seen.add(work_id)
            work_urls.append(canonical_url)
    return work_urls


def download_ao3(url: str, file_format: str, force: bool, confirm: bool = True) -> None:
    work_id, work_url = validate_ao3_work(url)
    if confirm and input(f"Make a private local {file_format.upper()} copy of work {work_id}? [y/N] ").strip().lower() not in {"y", "yes"}:
        print("Cancelled.")
        return
    request = Request(work_url, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(request, timeout=30) as response:
            page_url = response.geturl()
            page_host = (urlparse(page_url).hostname or "").lower()
            if page_host not in ALLOWED_AO3_HOSTS:
                raise ValueError("AO3 redirected outside its approved hosts; stopped.")
            html = response.read(8_000_000).decode("utf-8", errors="replace")
    except HTTPError as exc:
        if exc.code in {429, 503}:
            raise AO3RateLimitError(f"AO3 returned HTTP {exc.code}; stopping the batch to avoid further requests.") from exc
        raise RuntimeError(f"Could not open the public AO3 work page: {exc}") from exc
    except (URLError, TimeoutError) as exc:
        raise RuntimeError(f"Could not open the public AO3 work page: {exc}") from exc

    parser = DownloadLinkParser()
    parser.feed(html)
    chosen = None
    for href in parser.links:
        absolute = urljoin(page_url, href)
        parsed = urlparse(absolute)
        if parsed.hostname not in ALLOWED_AO3_HOSTS:
            continue
        if re.search(rf"/downloads/{re.escape(work_id)}/[^?#]+\.{re.escape(file_format)}(?:$|[?#])", absolute, re.I):
            chosen = absolute
            break
    if not chosen:
        raise RuntimeError("No official download link for that format was visible. Open the work in a browser and use its Download menu if offered; this may be a restriction or an AO3 login/confirmation page.")

    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    output = DOWNLOAD_DIR / f"ao3-{work_id}.{file_format}"
    if output.exists() and not force:
        raise FileExistsError(f"{output} already exists. Use --force to replace it after confirming this refresh is wanted.")
    download_request = Request(chosen, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(download_request, timeout=60) as response:
            final_host = (urlparse(response.geturl()).hostname or "").lower()
            if final_host not in ALLOWED_AO3_HOSTS:
                raise ValueError("Download redirected outside approved AO3 hosts; stopped.")
            content = response.read(50_000_001)
            if len(content) > 50_000_000:
                raise RuntimeError("Download exceeded the 50 MB safety limit; use AO3's browser Download menu instead.")
    except HTTPError as exc:
        if exc.code in {429, 503}:
            raise AO3RateLimitError(f"AO3 returned HTTP {exc.code}; stopping the batch to avoid further requests.") from exc
        raise RuntimeError(f"AO3 download failed: {exc}") from exc
    except (URLError, TimeoutError) as exc:
        raise RuntimeError(f"AO3 download failed: {exc}") from exc
    output.write_bytes(content)
    digest = hashlib.sha256(content).hexdigest()
    inventory = ROOT / "downloads" / "download-inventory.json"
    entries = []
    if inventory.exists():
        entries = json.loads(inventory.read_text(encoding="utf-8"))
    entries = [entry for entry in entries if entry.get("file") != output.name]
    entries.append({
        "work_url": work_url,
        "format": file_format,
        "file": output.name,
        "downloaded_on": today(),
        "bytes": len(content),
        "sha256": digest,
        "private_local_copy": True,
    })
    inventory.write_text(json.dumps(entries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Saved private copy: {output} ({len(content)} bytes; sha256 {digest})")


def download_ao3_list(source_list: Path, file_format: str, force: bool) -> None:
    work_urls = ao3_work_urls(source_list)
    if not work_urls:
        raise ValueError(f"No canonical AO3 work links found in {source_list}")
    print(f"Found {len(work_urls)} AO3 work(s) in {source_list}:")
    for url in work_urls:
        print(f"  {url}")
    print("Only the selected public AO3 format link will be followed; no login cookies or access-control workarounds are used.")
    if input(f"Download offered {file_format.upper()} copies to {DOWNLOAD_DIR}? [y/N] ").strip().lower() not in {"y", "yes"}:
        print("Cancelled.")
        return

    failures = []
    saved = 0
    already_present = 0
    attempted = 0
    for index, url in enumerate(work_urls, 1):
        attempted = index
        print(f"\n[{index}/{len(work_urls)}] {url}")
        try:
            download_ao3(url, file_format, force, confirm=False)
            saved += 1
        except FileExistsError as exc:
            already_present += 1
            print(f"Skipped: {exc}")
        except AO3RateLimitError as exc:
            failures.append((url, str(exc)))
            print(f"Stopping batch: {exc}", file=sys.stderr)
            break
        except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
            failures.append((url, str(exc)))
            print(f"Could not download this work: {exc}", file=sys.stderr)
        if index < len(work_urls):
            time.sleep(2)
    print(f"\nFinished: {saved} saved, {len(failures)} failed or unavailable, {already_present} already present, {len(work_urls) - attempted} not attempted.")
    if failures:
        raise RuntimeError("Some works could not be downloaded; see the messages above and check AO3's work page and download controls.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("seed", help="initialize/update the research JSON from creator-directory.md")
    review_parser = subparsers.add_parser("review", help="open profiles and interactively record activity and work links")
    review_parser.add_argument("--limit", type=int, help="review at most N pending accounts")
    review_parser.add_argument("--include-reviewed", action="store_true", help="review accounts already marked reviewed")
    subparsers.add_parser("catalog", help="render research-results.json as stories-and-projects.md")
    api_parser = subparsers.add_parser("scan-x", help="discover recent post links using the official X API (may incur charges)")
    api_parser.add_argument("--max-accounts", type=int, default=10, help="accounts from the seeded list; 0 means all")
    api_parser.add_argument("--max-posts", type=int, default=20, help="recent posts per account (5-3200), default 20")
    api_parser.add_argument("--since", help="only request posts on/after YYYY-MM-DD where API access allows")
    api_parser.add_argument("--confirm-api-charges", action="store_true", help="acknowledge current X developer API pricing may apply")
    download_parser = subparsers.add_parser("download-ao3", help="save one publicly offered AO3 format to the ignored local downloads folder")
    download_parser.add_argument("work_url")
    download_parser.add_argument("--format", choices=("azw3", "epub", "mobi", "pdf", "html"), default="epub")
    download_parser.add_argument("--force", action="store_true", help="replace the same local file after the confirmation prompt")
    download_list_parser = subparsers.add_parser("download-ao3-list", help="download offered AO3 formats for works linked in inspiration/sources.md")
    download_list_parser.add_argument("--source-list", type=Path, default=SOURCE_CATALOG, help=f"Markdown file containing AO3 work links (default: {SOURCE_CATALOG})")
    download_list_parser.add_argument("--format", choices=("azw3", "epub", "mobi", "pdf", "html"), default="epub")
    download_list_parser.add_argument("--force", action="store_true", help="replace existing local copies after the confirmation prompt")
    args = parser.parse_args()
    try:
        if args.command == "seed":
            seed()
        elif args.command == "review":
            review(args.limit, args.include_reviewed)
        elif args.command == "catalog":
            render_catalog()
        elif args.command == "scan-x":
            if args.max_accounts < 0 or not 5 <= args.max_posts <= 3200:
                raise ValueError("--max-accounts must be 0 or greater and --max-posts must be 5–3200.")
            scan_x(args.max_accounts, args.max_posts, args.since, args.confirm_api_charges)
        elif args.command == "download-ao3":
            download_ao3(args.work_url, args.format, args.force)
        elif args.command == "download-ao3-list":
            download_ao3_list(args.source_list, args.format, args.force)
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
