#!/usr/bin/env python3

"""Generate static SVG cards for Temporal's featured public repositories."""

from __future__ import annotations

import html
import json
import textwrap
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ORGANIZATION = "temporalio"
REPOSITORIES = (
    "sdk-go",
    "sdk-java",
    "sdk-typescript",
    "sdk-python",
    "sdk-dotnet",
    "sdk-ruby",
    "sdk-rust",
    "sdk-php",
    "cli",
    "ai-cookbook",
)
OUTPUT_DIR = Path(__file__).resolve().parents[2] / "profile" / "repository-cards"
API_ROOT = "https://api.github.com/repos"

THEMES = {
    "light": {
        "background": "#ffffff",
        "border": "#d0d7de",
        "title": "#0969da",
        "text": "#24292f",
        "muted": "#57606a",
        "accent": "#8250df",
    },
    "dark": {
        "background": "#0d1117",
        "border": "#30363d",
        "title": "#58a6ff",
        "text": "#c9d1d9",
        "muted": "#8b949e",
        "accent": "#bc8cff",
    },
}


def fetch_repository(name: str) -> dict[str, object]:
    url = f"{API_ROOT}/{ORGANIZATION}/{name}"
    request = Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "temporal-featured-repository-cards",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )

    for attempt in range(4):
        try:
            with urlopen(request, timeout=20) as response:
                data = json.load(response)
            if data.get("full_name") != f"{ORGANIZATION}/{name}":
                raise RuntimeError(f"Unexpected repository returned for {name}")
            return data
        except HTTPError as error:
            if error.code < 500 or attempt == 3:
                raise RuntimeError(f"GitHub API returned HTTP {error.code} for {name}") from error
        except (TimeoutError, URLError) as error:
            if attempt == 3:
                raise RuntimeError(f"Could not fetch repository data for {name}: {error}") from error
        time.sleep(2**attempt)

    raise RuntimeError(f"Could not fetch repository data for {name}")


def shorten_count(value: int) -> str:
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}m".replace(".0m", "m")
    if value >= 1_000:
        return f"{value / 1_000:.1f}k".replace(".0k", "k")
    return str(value)


def description_lines(description: str) -> list[str]:
    lines = textwrap.wrap(description, width=68, break_long_words=True, break_on_hyphens=False)
    if len(lines) > 2:
        lines = lines[:2]
        lines[1] = lines[1].rstrip(" .") + "…"
    return lines or ["No description provided."]


def render_card(repository: dict[str, object], theme: dict[str, str]) -> str:
    name = str(repository["name"])
    full_name = str(repository["full_name"])
    title = html.escape(full_name)
    description = description_lines(str(repository.get("description") or ""))
    language = html.escape(str(repository.get("language") or "Other"))
    stars = shorten_count(int(repository.get("stargazers_count") or 0))
    forks = shorten_count(int(repository.get("forks_count") or 0))
    description_svg = "\n".join(
        f'<text x="20" y="{64 + index * 18}" fill="{theme["muted"]}" font-size="13">{html.escape(line)}</text>'
        for index, line in enumerate(description)
    )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="490" height="124" viewBox="0 0 490 124" role="img" aria-labelledby="title">
  <title id="title">{title} repository card</title>
  <rect x="0.5" y="0.5" width="489" height="123" rx="6" fill="{theme["background"]}" stroke="{theme["border"]}"/>
  <circle cx="27" cy="29" r="8" fill="{theme["accent"]}"/>
  <text x="44" y="34" fill="{theme["title"]}" font-family="-apple-system,BlinkMacSystemFont,Segoe UI, sans-serif" font-size="16" font-weight="600">{title}</text>
  {description_svg}
  <circle cx="24" cy="104" r="4" fill="{theme["accent"]}"/>
  <text x="34" y="109" fill="{theme["text"]}" font-family="-apple-system,BlinkMacSystemFont,Segoe UI, sans-serif" font-size="12">{language}</text>
  <text x="190" y="109" fill="{theme["muted"]}" font-family="-apple-system,BlinkMacSystemFont,Segoe UI, sans-serif" font-size="12">Stars {stars}</text>
  <text x="300" y="109" fill="{theme["muted"]}" font-family="-apple-system,BlinkMacSystemFont,Segoe UI, sans-serif" font-size="12">Forks {forks}</text>
</svg>
'''


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for name in REPOSITORIES:
        repository = fetch_repository(name)
        for theme_name, theme in THEMES.items():
            destination = OUTPUT_DIR / f"{name}-{theme_name}.svg"
            destination.write_text(render_card(repository, theme), encoding="utf-8")
        print(f"Generated cards for {name}")


if __name__ == "__main__":
    main()
