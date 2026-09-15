"""Generate HTML pages from index.md files.

The generator intentionally uses only the Python standard library so it can be
run in GitHub Pages repositories without a package installation step.
"""

from __future__ import annotations

import argparse
import html
import os
import re
import sys
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse


SCRIPT_DIR = Path(__file__).resolve().parent
FRONT_MATTER_BOUNDARY = "---"


def safe_url(value: str) -> str:
    """Allow normal web/page URLs while preventing script URLs."""

    parsed = urlparse(value.strip())
    if parsed.scheme and parsed.scheme.lower() not in {"http", "https", "mailto"}:
        return "#"
    return html.escape(value.strip(), quote=True)


def inline_markdown(value: str) -> str:
    """Render the inline Markdown used by the site's pages."""

    raw_html: list[str] = []

    def protect_tag(match: re.Match[str]) -> str:
        raw_html.append(match.group(0))
        return f"__RAW_HTML_{len(raw_html) - 1}__"

    # Preserve explicitly written HTML such as badge images and <br>.
    value = re.sub(r"</?[A-Za-z][^>]*>", protect_tag, value)
    value = html.escape(value, quote=False)

    value = re.sub(
        r"!\[([^\]]*)\]\((\S+?)(?:\s+[\"']([^\"']*)[\"'])?\)",
        lambda match: (
            f'<img src="{safe_url(match.group(2))}" '
            f'alt="{html.escape(match.group(1), quote=True)}"'
            + (
                f' title="{html.escape(match.group(3), quote=True)}"'
                if match.group(3)
                else ""
            )
            + ">"
        ),
        value,
    )
    value = re.sub(
        r"\[([^\]]+)\]\((\S+?)(?:\s+[\"']([^\"']*)[\"'])?\)",
        lambda match: (
            f'<a href="{safe_url(match.group(2))}"'
            + (
                f' title="{html.escape(match.group(3), quote=True)}"'
                if match.group(3)
                else ""
            )
            + f">{inline_markdown(match.group(1))}</a>"
        ),
        value,
    )
    value = re.sub(
        r"`([^`]+)`",
        lambda match: f"<code>{match.group(1)}</code>",
        value,
    )
    value = re.sub(r"\*\*([^*]+)\*\*|__([^_]+)__", lambda m: f"<strong>{m.group(1) or m.group(2)}</strong>", value)
    value = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)|(?<!_)_([^_]+)_(?!_)", lambda m: f"<em>{m.group(1) or m.group(2)}</em>", value)

    for index, tag in enumerate(raw_html):
        value = value.replace(f"__RAW_HTML_{index}__", tag)
    return value


def heading_id(value: str, used_ids: set[str]) -> str:
    """Create a stable, readable fragment ID for a heading."""

    plain = re.sub(r"<[^>]+>", "", value)
    plain = re.sub(r"[`*_~]", "", plain).strip().lower()
    slug = re.sub(r"[^\w\-ぁ-んァ-ヶ一-龯ー]+", "-", plain, flags=re.UNICODE).strip("-")
    slug = slug or "section"
    candidate = slug
    suffix = 2
    while candidate in used_ids:
        candidate = f"{slug}-{suffix}"
        suffix += 1
    used_ids.add(candidate)
    return candidate


def split_table_row(line: str) -> list[str]:
    row = line.strip().strip("|")
    return [cell.strip() for cell in row.split("|")]


def is_table_separator(line: str) -> bool:
    cells = split_table_row(line)
    return len(cells) > 0 and all(re.fullmatch(r":?-+:?", cell) for cell in cells)


def render_table(lines: list[str]) -> str:
    headers = split_table_row(lines[0])
    rows = [split_table_row(line) for line in lines[2:]]
    output = ["<table>", "    <thead>", "        <tr>"]
    output.extend(f"            <th>{inline_markdown(cell)}</th>" for cell in headers)
    output.extend(["        </tr>", "    </thead>", "    <tbody>"])
    for row in rows:
        output.append("        <tr>")
        for index in range(len(headers)):
            cell = row[index] if index < len(row) else ""
            output.append(f"            <td>{inline_markdown(cell)}</td>")
        output.append("        </tr>")
    output.extend(["    </tbody>", "</table>"])
    return "\n".join(output)


def render_list(lines: list[str], ordered: bool) -> list[str]:
    tag = "ol" if ordered else "ul"
    output = [f"<{tag}>"]
    pattern = r"^\s*\d+[.)]\s+(.+)$" if ordered else r"^\s*[-+*]\s+(.+)$"
    for line in lines:
        match = re.match(pattern, line)
        if match:
            output.append(f"    <li>{inline_markdown(match.group(1))}</li>")
    output.append(f"</{tag}>")
    return output


def render_blocks(lines: list[str], used_ids: set[str] | None = None) -> list[str]:
    """Render block-level Markdown and return indented HTML lines."""

    used_ids = used_ids if used_ids is not None else set()
    output: list[str] = []
    index = 0

    while index < len(lines):
        line = lines[index]
        if not line.strip():
            index += 1
            continue

        details_match = re.fullmatch(r"\s*<details>\s*", line, flags=re.IGNORECASE)
        if details_match:
            end = index + 1
            depth = 1
            while end < len(lines):
                if re.fullmatch(r"\s*<details>\s*", lines[end], flags=re.IGNORECASE):
                    depth += 1
                elif re.fullmatch(r"\s*</details>\s*", lines[end], flags=re.IGNORECASE):
                    depth -= 1
                    if depth == 0:
                        break
                end += 1
            if depth != 0:
                raise ValueError("details block is missing a closing </details>")

            output.append("<details>")
            inner = lines[index + 1 : end]
            if inner and re.fullmatch(r"\s*<summary>.*</summary>\s*", inner[0], flags=re.IGNORECASE):
                summary = re.sub(r"^\s*<summary>|</summary>\s*$", "", inner.pop(0), flags=re.IGNORECASE)
                output.append(f"    <summary>{inline_markdown(summary)}</summary>")
            for rendered_line in render_blocks(inner, used_ids):
                output.append(f"    {rendered_line}")
            output.append("</details>")
            index = end + 1
            continue

        if line.startswith("```") or line.startswith("~~~"):
            fence = line[:3]
            language = line[3:].strip()
            end = index + 1
            while end < len(lines) and not lines[end].startswith(fence):
                end += 1
            if end == len(lines):
                raise ValueError("fenced code block is missing its closing fence")
            class_attribute = (
                f' class="language-{html.escape(language, quote=True)}"' if language else ""
            )
            code = "\n".join(lines[index + 1 : end])
            output.append(f"<pre><code{class_attribute}>{html.escape(code)}</code></pre>")
            index = end + 1
            continue

        heading_match = re.match(r"^(#{1,6})\s+(.+?)\s*#*\s*$", line)
        if heading_match:
            level = len(heading_match.group(1))
            content = heading_match.group(2)
            output.append(
                f'<h{level} id="{heading_id(content, used_ids)}">{inline_markdown(content)}</h{level}>'
            )
            index += 1
            continue

        if re.fullmatch(r"\s*([-*_])(?:\s*\1){2,}\s*", line):
            output.append("<hr>")
            index += 1
            continue

        if line.startswith(":::"):
            end = index + 1
            while end < len(lines) and lines[end].strip() != ":::":
                end += 1
            if end == len(lines):
                raise ValueError("directive block is missing its closing :::")
            output.append("<blockquote>")
            for rendered_line in render_blocks(lines[index + 1 : end], used_ids):
                output.append(f"    {rendered_line}")
            output.append("</blockquote>")
            index = end + 1
            continue

        if line.lstrip().startswith(">"):
            quote_lines: list[str] = []
            while index < len(lines) and (lines[index].lstrip().startswith(">") or not lines[index].strip()):
                quote_lines.append(re.sub(r"^\s*>\s?", "", lines[index]))
                index += 1
            output.append("<blockquote>")
            for rendered_line in render_blocks(quote_lines, used_ids):
                output.append(f"    {rendered_line}")
            output.append("</blockquote>")
            continue

        if (
            "|" in line
            and index + 1 < len(lines)
            and is_table_separator(lines[index + 1])
        ):
            table_lines = [line, lines[index + 1]]
            index += 2
            while index < len(lines) and "|" in lines[index] and lines[index].strip():
                table_lines.append(lines[index])
                index += 1
            output.extend(render_table(table_lines).splitlines())
            continue

        unordered = re.match(r"^\s*[-+*]\s+.+$", line)
        ordered = re.match(r"^\s*\d+[.)]\s+.+$", line)
        if unordered or ordered:
            list_lines: list[str] = []
            pattern = r"^\s*\d+[.)]\s+.+$" if ordered else r"^\s*[-+*]\s+.+$"
            while index < len(lines) and re.match(pattern, lines[index]):
                list_lines.append(lines[index])
                index += 1
            output.extend(render_list(list_lines, ordered is not None))
            continue

        # Preserve raw HTML blocks that are not Markdown containers.
        if line.lstrip().startswith("<") and re.match(r"^\s*</?[A-Za-z]", line):
            output.append(line.strip())
            index += 1
            continue

        paragraph = [line.strip()]
        index += 1
        while index < len(lines) and lines[index].strip():
            next_line = lines[index]
            if (
                re.match(r"^(#{1,6})\s+", next_line)
                or next_line.startswith(("```", "~~~", ":::"))
                or re.match(r"^\s*[-+*]\s+", next_line)
                or re.match(r"^\s*\d+[.)]\s+", next_line)
                or next_line.lstrip().startswith(">")
                or re.fullmatch(r"\s*<details>\s*", next_line, flags=re.IGNORECASE)
            ):
                break
            paragraph.append(next_line.strip())
            index += 1
        output.append(f"<p>{inline_markdown(' '.join(paragraph))}</p>")

    return output


def read_document(source: Path) -> tuple[dict[str, str], list[str]]:
    lines = source.read_text(encoding="utf-8").splitlines()
    metadata: dict[str, str] = {}
    if lines and lines[0].strip() == FRONT_MATTER_BOUNDARY:
        end = next((i for i, line in enumerate(lines[1:], 1) if line.strip() == FRONT_MATTER_BOUNDARY), None)
        if end is None:
            raise ValueError(f"{source}: front matter is missing its closing ---")
        for line in lines[1:end]:
            key, separator, value = line.partition(":")
            if separator:
                metadata[key.strip().lower()] = value.strip().strip("\"'")
        lines = lines[end + 1 :]
    return metadata, lines


def plain_title(value: str) -> str:
    value = re.sub(r"<[^>]+>", "", value)
    value = re.sub(r"[`*_~]", "", value)
    return html.unescape(value).strip()


def render_document(source: Path, output: Path, site_root: Path) -> str:
    metadata, lines = read_document(source)
    title = metadata.get("title", "")
    if not title:
        for line in lines:
            match = re.match(r"^#\s+(.+?)\s*#*\s*$", line)
            if match:
                title = plain_title(match.group(1))
                break
    if not title:
        title = source.parent.name or "Official Pages"

    # The first H1 is represented by the document header instead of being
    # duplicated in the article body.
    title_line = next(
        (index for index, line in enumerate(lines) if re.match(r"^#\s+.+", line)),
        None,
    )
    if title_line is not None:
        lines = lines[:title_line] + lines[title_line + 1 :]

    content_lines = [line for line in lines if line.strip()]
    diary_page = bool(content_lines) and all(
        re.match(r"^\s*[-+*]\s+.+$", line) for line in content_lines
    )
    rendered = render_blocks(lines)
    if diary_page and rendered and rendered[0] == "<ul>":
        rendered[0] = '<ul class="diary-list">'

    stylesheet = site_root / "assets" / "css" / "style_qiita.css"
    relative_stylesheet = os.path.relpath(stylesheet, output.parent).replace("\\", "/")

    body = "\n".join(f"            {line}" for line in rendered)
    if diary_page:
        main = f"""    <main>
        <section class="card">
{body}
        </section>
    </main>"""
    else:
        description = metadata.get("description")
        header = f"""            <div class="article-header">
                <h1 class="article-title">{html.escape(title)}</h1>
{f'                <p>{inline_markdown(description)}</p>' if description else ''}
            </div>
"""
        main = f"""    <main>
        <article class="card">
{header}            <div class="article-body">
{body}
            </div>
        </article>
    </main>"""

    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(title)}</title>
    <link rel="stylesheet" href="{relative_stylesheet}">
</head>
<body>
{main}
</body>
</html>
"""


def discover_sources(paths: Iterable[Path]) -> list[Path]:
    sources: set[Path] = set()
    for path in paths:
        if not path.exists():
            raise FileNotFoundError(f"入力パスが見つかりません: {path}")
        if path.is_file():
            if path.name.lower() != "index.md":
                raise ValueError(f"入力ファイルはindex.mdにしてください: {path}")
            sources.add(path.resolve())
        else:
            sources.update(
                candidate.resolve()
                for candidate in path.rglob("index.md")
                if ".git" not in candidate.parts
            )
    return sorted(sources)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="index.mdを同じフォルダのindex.htmlへ変換します。"
    )
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="Markdownファイルまたは検索対象フォルダ（省略時はリポジトリ全体）",
    )
    parser.add_argument(
        "--site-root",
        type=Path,
        default=SCRIPT_DIR,
        help="assetsフォルダがあるサイトルート（既定: スクリプトのあるフォルダ）",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="単一入力時の出力先。既定は入力と同じフォルダのindex.html",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="ファイルを書き換えず、生成結果と既存HTMLが異なれば終了コード1にする",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    site_root = args.site_root.resolve()
    search_paths = args.paths or [site_root]
    try:
        sources = discover_sources(search_paths)
        if not sources:
            raise ValueError("index.mdが見つかりません")
        if args.output and len(sources) != 1:
            raise ValueError("--outputは入力が1件のときだけ指定できます")

        changed = False
        for source in sources:
            output = args.output.resolve() if args.output else source.with_name("index.html")
            generated = render_document(source, output, site_root)
            current = output.read_text(encoding="utf-8") if output.exists() else None
            if current != generated:
                changed = True
                if not args.check:
                    output.write_text(generated, encoding="utf-8", newline="\n")
                    print(f"生成: {output}")
                else:
                    print(f"差分あり: {output}")
            elif not args.check:
                print(f"変更なし: {output}")
        return 1 if args.check and changed else 0
    except (FileNotFoundError, OSError, ValueError) as error:
        print(f"エラー: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
