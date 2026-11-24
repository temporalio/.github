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

LANGUAGE_COLORS = {
    "Go": "#00ADD8",
    "Java": "#b07219",
    "TypeScript": "#3178c6",
    "Python": "#3572A5",
    "C#": "#178600",
    "Ruby": "#701516",
    "Rust": "#dea584",
    "PHP": "#4F5D95",
    "JavaScript": "#f1e05a",
    "Jupyter Notebook": "#DA5B0B",
}

THEMES = {
    "light": {
        "background": "#ffffff",
        "border": "#d0d7de",
        "title": "#0969da",
        "text": "#24292f",
        "muted": "#57606a",
        "accent": "#fb8c00",
        "fallback_language": "#8c959f",
    },
    "dark": {
        "background": "#0d1117",
        "border": "#30363d",
        "title": "#58a6ff",
        "text": "#c9d1d9",
        "muted": "#8b949e",
        "accent": "#f0883e",
        "fallback_language": "#8b949e",
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
    lines = textwrap.wrap(description, width=46, break_long_words=True, break_on_hyphens=False)
    if len(lines) > 2:
        lines = lines[:2]
        lines[1] = lines[1].rstrip(" .") + "…"
    return lines or ["No description provided."]


def render_card(repository: dict[str, object], theme: dict[str, str]) -> str:
    full_name = html.escape(str(repository["full_name"]))
    description = description_lines(str(repository.get("description") or ""))
    language_name = str(repository.get("language") or "Other")
    language = html.escape(language_name)
    language_color = LANGUAGE_COLORS.get(language_name, theme["fallback_language"])
    stars = shorten_count(int(repository.get("stargazers_count") or 0))
    forks = shorten_count(int(repository.get("forks_count") or 0))
    description_svg = "\n".join(
        f'<text x="42" y="{60 + index * 16}" fill="{theme["muted"]}" font-family="Arial,Helvetica,sans-serif" font-size="13">{html.escape(line)}</text>'
        for index, line in enumerate(description)
    )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="400" height="120" viewBox="0 0 400 120" role="img" aria-labelledby="title">
  <title id="title">{full_name} repository card</title>
  <rect x="0.5" y="0.5" width="399" height="119" rx="6" fill="{theme["background"]}" stroke="{theme["border"]}"/>
  <g transform="translate(20 18)" fill="none" stroke="{theme["muted"]}" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.7">
    <path d="M3 1.5h10a2 2 0 0 1 2 2v15H5a3 3 0 0 1-3-3v-12a2 2 0 0 1 1-2z"/>
    <path d="M2 14.5a3 3 0 0 1 3-3h10.5"/>
    <path d="M11.5 11.5v7"/>
  </g>
  <text x="42" y="34" fill="{theme["title"]}" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="600">{full_name}</text>
  <path d="M30 49 23 58h5l-1 8 8-11h-5l2-6z" fill="{theme["accent"]}"/>
  {description_svg}
  <circle cx="21" cy="101" r="5" fill="{language_color}"/>
  <text x="32" y="105" fill="{theme["muted"]}" font-family="Arial,Helvetica,sans-serif" font-size="12">{language}</text>
  <path d="m157 92 3.2 6.4 7.1 1-5.1 5 1.2 7.1-6.4-3.4-6.4 3.4 1.2-7.1-5.1-5 7.1-1z" fill="none" stroke="{theme["muted"]}" stroke-linejoin="round" stroke-width="1.7"/>
  <text x="171" y="105" fill="{theme["muted"]}" font-family="Arial,Helvetica,sans-serif" font-size="12">{stars}</text>
  <g transform="translate(242 91)" fill="none" stroke="{theme["muted"]}" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.7">
    <circle cx="4" cy="4" r="2.4"/>
    <circle cx="16" cy="4" r="2.4"/>
    <circle cx="4" cy="16" r="2.4"/>
    <path d="M4 6.5v7M16 6.5a6 6 0 0 1-6 6H6.5"/>
  </g>
  <text x="265" y="105" fill="{theme["muted"]}" font-family="Arial,Helvetica,sans-serif" font-size="12">{forks}</text>
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
