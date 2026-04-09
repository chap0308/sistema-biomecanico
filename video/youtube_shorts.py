"""Discover YouTube Shorts URLs from a channel page with Playwright."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal
from urllib.parse import parse_qs, urlparse

Order = Literal["newest", "popular", "oldest"]

_ORDER_LABELS: dict[Order, tuple[str, ...]] = {
    "newest": ("Most recent", "M?s recientes"),
    "popular": ("Popular", "Populares"),
    "oldest": ("Oldest", "M?s antiguos"),
}


@dataclass(slots=True)
class ShortsVideo:
    """A YouTube Shorts card discovered on the channel page."""

    video_id: str
    url: str
    title: str
    views_label: str
    order_index: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "video_id": self.video_id,
            "url": self.url,
            "title": self.title,
            "views_label": self.views_label,
            "order_index": self.order_index,
        }


def normalize_channel_shorts_url(url: str) -> str:
    """Ensure the URL points to the `/shorts` channel tab."""
    cleaned = url.strip().rstrip("/")
    if "/shorts" in cleaned:
        return cleaned
    return f"{cleaned}/shorts"


def extract_video_id(url: str) -> str:
    """Extract a video id from either a Shorts URL or a regular watch URL."""
    parsed = urlparse(url)
    if "/shorts/" in parsed.path:
        return parsed.path.rstrip("/").split("/shorts/")[1].split("/")[0]
    if parsed.path == "/watch":
        return parse_qs(parsed.query).get("v", [""])[0]
    match = re.search(r"(?:youtu\.be/)([A-Za-z0-9_-]{6,})", url)
    return match.group(1) if match else ""


def load_seen_state(path: Path) -> dict[str, Any]:
    """Read persisted discovery state if it exists."""
    if not path.exists():
        return {
            "channel_url": "",
            "last_checked_at": "",
            "seen_video_ids": [],
            "seen_urls": [],
            "history": [],
        }
    return json.loads(path.read_text(encoding="utf-8"))


def save_seen_state(path: Path, state: dict[str, Any]) -> None:
    """Persist discovery state to disk."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def diff_new_videos(videos: list[ShortsVideo], seen_video_ids: set[str]) -> list[ShortsVideo]:
    """Return only videos whose ids have not been seen before."""
    return [video for video in videos if video.video_id not in seen_video_ids]


def update_seen_state(
    *,
    state: dict[str, Any],
    channel_url: str,
    order: Order,
    limit: int,
    videos: list[ShortsVideo],
) -> dict[str, Any]:
    """Merge the latest scrape into persisted state."""
    seen_video_ids = list(dict.fromkeys([*(state.get("seen_video_ids", [])), *[item.video_id for item in videos]]))
    seen_urls = list(dict.fromkeys([*(state.get("seen_urls", [])), *[item.url for item in videos]]))
    history_entry = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "order": order,
        "limit": limit,
        "discovered_video_ids": [item.video_id for item in videos],
    }
    history = [history_entry, *state.get("history", [])][:20]
    return {
        "channel_url": channel_url,
        "last_checked_at": history_entry["checked_at"],
        "seen_video_ids": seen_video_ids,
        "seen_urls": seen_urls,
        "history": history,
    }


def scrape_channel_shorts(
    *,
    channel_url: str,
    limit: int,
    order: Order = "newest",
    browser_channel: str = "msedge",
    headless: bool = True,
    timeout_ms: int = 30_000,
) -> list[ShortsVideo]:
    """Scrape a YouTube channel Shorts tab and return up to `limit` videos."""
    from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
    from playwright.sync_api import sync_playwright

    normalized_url = normalize_channel_shorts_url(channel_url)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel=browser_channel, headless=headless)
        context = browser.new_context(viewport={"width": 1600, "height": 2200})
        page = context.new_page()
        try:
            page.goto(normalized_url, wait_until="domcontentloaded", timeout=timeout_ms)
            _select_order(page, order=order, timeout_ms=timeout_ms)
            _wait_for_shorts_grid(page, timeout_ms=timeout_ms)
            items = _collect_shorts(page, limit=limit)
        finally:
            context.close()
            browser.close()

    deduped: list[ShortsVideo] = []
    seen_ids: set[str] = set()
    for index, item in enumerate(items):
        video_id = extract_video_id(item["url"])
        if not video_id or video_id in seen_ids:
            continue
        seen_ids.add(video_id)
        deduped.append(
            ShortsVideo(
                video_id=video_id,
                url=item["url"],
                title=item["title"],
                views_label=item["views_label"],
                order_index=index,
            )
        )
        if len(deduped) >= limit:
            break
    return deduped


def _select_order(page: Any, *, order: Order, timeout_ms: int) -> None:
    for label in _ORDER_LABELS[order]:
        locator = page.get_by_text(label, exact=True)
        try:
            if locator.count() > 0:
                locator.first.click(timeout=timeout_ms)
                page.wait_for_timeout(1000)
                return
        except PlaywrightTimeoutError:
            continue


def _wait_for_shorts_grid(page: Any, *, timeout_ms: int) -> None:
    page.wait_for_selector('a[href^="/shorts/"]', timeout=timeout_ms)


def _collect_shorts(page: Any, *, limit: int) -> list[dict[str, str]]:
    stagnant_rounds = 0
    previous_count = 0
    max_rounds = max(12, limit)

    for _ in range(max_rounds):
        items = _read_shorts_cards(page)
        if len(items) >= limit:
            return items
        if len(items) == previous_count:
            stagnant_rounds += 1
        else:
            stagnant_rounds = 0
        if stagnant_rounds >= 3:
            return items
        previous_count = len(items)
        page.mouse.wheel(0, 7000)
        page.wait_for_timeout(1200)

    return _read_shorts_cards(page)


def _read_shorts_cards(page: Any) -> list[dict[str, str]]:
    script = """
    () => {
      const rows = Array.from(document.querySelectorAll('ytd-rich-item-renderer'));
      return rows.map((row) => {
        const anchor = row.querySelector('a[href^="/shorts/"]');
        const titleEl = row.querySelector('h3.shortsLockupViewModelHostMetadataTitle, h3');
        const attributedSpans = Array.from(row.querySelectorAll('span.yt-core-attributed-string'))
          .map((span) => (span.textContent || '').trim())
          .filter(Boolean);
        const viewsLabel = attributedSpans.length >= 2 ? attributedSpans[1] : '';
        const href = anchor ? anchor.getAttribute('href') || '' : '';
        const url = href ? new URL(href, window.location.origin).toString() : '';
        return {
          url,
          title: (titleEl?.textContent || '').trim(),
          views_label: viewsLabel,
        };
      }).filter((item) => item.url);
    }
    """
    return list(page.evaluate(script))
