"""Update category links in the site's top-level index.html."""

from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SECTION_PATTERN = re.compile(
    r'(?P<open><section\b(?=[^>]*\bname\s*=\s*["\'](?P<name>[^"\']+)["\'])[^>]*>)'
    r"(?P<body>.*?)"
    r"(?P<close></section>)",
    re.IGNORECASE | re.DOTALL,
)
LIST_PATTERN = re.compile(
    r"[ \t]*<ul\b[^>]*>.*?</ul>", re.IGNORECASE | re.DOTALL
)


def page_label(page: Path, category: Path) -> str:
    """Use the page folder name as the link label."""

    return page.relative_to(category).parts[-1]


def collect_pages(category: Path) -> list[Path]:
    """Find nested pages, excluding the category's own index.html."""

    return sorted(
        (
            candidate.parent
            for candidate in category.rglob("index.html")
            if candidate.parent != category and ".git" not in candidate.parts
        ),
        key=lambda page: page.relative_to(category).as_posix().casefold(),
    )


def links_html(pages: list[Path], root: Path, category: Path) -> str:
    items: list[str] = []
    for page in pages:
        target = page.joinpath("index.html").relative_to(root).as_posix()
        label = page_label(page, category)
        items.append(
            f'                <li><a href="{html.escape(target, quote=True)}" '
            f'target="_self">{html.escape(label)}</a></li>'
        )
    if not items:
        items.append("                <!-- index.htmlを持つページがまだありません -->")
    return "            <ul class=\"diary-list\">\n" + "\n".join(items) + "\n            </ul>"


def default_section(category_name: str, list_html: str) -> str:
    return f"""        <section class="card" name="{html.escape(category_name, quote=True)}">
            <h2>{html.escape(category_name)}</h2>
{list_html}
        </section>"""


def update_index(index_path: Path, check: bool = False) -> bool:
    root = index_path.parent.resolve()
    original = index_path.read_text(encoding="utf-8")
    updated = original

    categories = sorted(
        (
            path
            for path in root.iterdir()
            if path.is_dir() and not path.name.startswith(".") and path.name != "__pycache__"
        ),
        key=lambda path: path.name.casefold(),
    )
    for category in categories:
        pages = collect_pages(category)
        if not pages:
            continue
        name = category.name
        list_html = links_html(pages, root, category)
        match = next(
            (
                section
                for section in SECTION_PATTERN.finditer(updated)
                if section.group("name") == name
            ),
            None,
        )
        if match:
            body = match.group("body")
            replaced_body, count = LIST_PATTERN.subn(list_html, body, count=1)
            if count == 0:
                heading_end = re.search(r"</h[1-6]\s*>", body, re.IGNORECASE)
                insertion = heading_end.end() if heading_end else 0
                replaced_body = body[:insertion] + "\n" + list_html + body[insertion:]
            updated = updated[: match.start("body")] + replaced_body + updated[match.end("body") :]
        else:
            marker = re.search(r"</main\s*>", updated, re.IGNORECASE)
            if not marker:
                raise ValueError(f"{index_path} に </main> がありません")
            section = default_section(name, list_html)
            updated = updated[: marker.start()] + section + "\n\n" + updated[marker.start() :]

    if updated == original:
        return False
    if check:
        print(f"差分あり: {index_path}")
    else:
        index_path.write_text(updated, encoding="utf-8", newline="\n")
        print(f"更新: {index_path}")
    return True


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="各トップレベルフォルダのページリンクをindex.htmlへ反映します。"
    )
    parser.add_argument(
        "index",
        nargs="?",
        type=Path,
        default=SCRIPT_DIR / "index.html",
        help="更新対象のトップページ（既定: .\\index.html）",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="ファイルを書き換えず、差分の有無だけを確認する",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        changed = update_index(args.index.resolve(), args.check)
        return 1 if args.check and changed else 0
    except (OSError, ValueError) as error:
        print(f"エラー: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
