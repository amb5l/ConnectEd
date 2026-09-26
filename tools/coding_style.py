"""Report colon-alignment and import-style issues.

Colon alignment (a block of two or more lines):
  Multi-line parameters, consecutive ``name : type`` lines, and flat dict
  literals share one ``:`` column. On a parameter list the longest name
  is followed by one space; ``*`` and ``**`` do not widen that column.
  Union ``|`` tokens in those parameter and ``name : type`` blocks share
  a column too. A dict whose entries span lines is left alone.

Import style:
  ``from __future__``, then straight ``import`` lines, then ``from``
  imports. A blank line separates those, and also separates the
  ``from`` groups: standard library, Qt, other third-party, then the
  project (absolute imports, then relative imports with more leading
  dots before fewer). A blank line also separates a project import
  from one that extends it (``import xxx`` before ``import xxx.yyy``,
  and the same for ``from``), a change in leading-dot depth
  (``from ..x`` before ``from .y``), and a change in path length at
  the same leading-dot depth (``from ....app`` before
  ``from ....core.check``). Standard-library, Qt, and other
  third-party imports are exempt from the extending-path and
  path-length blanks. Imports under ``if TYPE_CHECKING:`` are exempt
  from every one of those blanks, and that block itself contains no
  blank lines. At the same distance a shorter path comes before a longer one
  (``x.y`` before ``x.y.z``). Standard-library ``from``
  imports follow ``_STDLIB_ORDER`` (``typing``, then ``types``, then the
  rest of that list). A standard-library name not listed sorts after
  those, A–Z. PyQt6 submodules are
  ``QtCore``, ``QtWidgets``, ``QtGui``, then any other ``Qt*`` A–Z.
  Other third-party modules, and absolute project imports, run A–Z.
  Relative imports of equal length are left in place. ``from typing import
  TYPE_CHECKING`` is not part of that order: it stands alone on the line
  immediately before ``if TYPE_CHECKING:``. Within a blank-line group,
  ``from`` lines share one ``import`` column.

The leading import block and each ``if TYPE_CHECKING`` block are checked.
``=`` alignment is not checked.

Run from the repo root::

    .venv\\Scripts\\python.exe tools/coding_style.py
    .venv\\Scripts\\python.exe tools/coding_style.py ConnectEd/widgets/foo.py
"""

from __future__ import annotations

import io
import sys
import tokenize

from collections.abc import Iterator, Sequence
from dataclasses     import dataclass
from pathlib         import Path


ROOT = Path(__file__).resolve().parents[1]

STDLIB = sys.stdlib_module_names

# ``from`` import order. Earlier names come first. A submodule stays with
# its top-level name (``typing`` before ``typing.io``), then A–Z.
_STDLIB_ORDER = (
    "typing",
    "types",
    "abc",
    "collections",
    "copy",
    "dataclasses",
    "enum",
    "functools",
    "importlib",
    "inspect",
    "io",
    "logging",
    "math",
    "os",
    "pathlib",
    "threading",
    "unittest",
    "urllib",
)
_STDLIB_RANK = {name : index for index, name in enumerate(_STDLIB_ORDER)}

# ANTLR output. Regenerated from the .g4 grammars; not house style.
SKIP_FILES = frozenset({
    "vhdl_lexer.py",
    "vhdl_parser.py",
    "vhdl_parserListener.py",
    "vhdl_parserVisitor.py",
})

# Soft keywords that can sit where a name would, and are not annotations.
_NOT_ANN = frozenset({"match", "case", "type"})

_QT_RANK = {
    "QtCore"    : 0,
    "QtWidgets" : 1,
    "QtGui"     : 2,
}

# Not the standard library and not this project. Qt is ordered separately.
_THIRD_PARTY = frozenset({
    "anthropic",
    "antlr4",
    "openai",
    "pytest",
    "typeguard",
    "yaml",
})

_Key = tuple[int, int, int, int, str]

_KINDS = (
    "colon", "pipe", "import-order", "import-blank", "import-align", "parse",
)


@dataclass
class Hit:
    path   : str
    line   : int
    kind   : str
    detail : str


@dataclass
class Annotated:
    line       : int
    colon      : int
    pipes      : list[int]
    name_start : int = 0
    name_len   : int = 0


@dataclass
class ImportStmt:
    line       : int
    end        : int
    level      : int
    module     : str
    plain      : bool
    import_col : int | None
    bound      : tuple[str, ...] = ()


def rel(path : Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def skip(path : Path) -> bool:
    if path.name in SKIP_FILES:
        return True
    return "__pycache__" in path.parts or ".venv" in path.parts


def py_files(raws : Sequence[str]) -> list[Path]:
    if not raws:
        raws = ["ConnectEd", "tests", "tools", "scripts"]
    found : list[Path] = []
    for raw in raws:
        path = Path(raw)
        if not path.is_absolute():
            path = ROOT / path
        if path.is_file():
            found.append(path)
        elif path.is_dir():
            found.extend(item for item in path.rglob("*.py") if not skip(item))
    return sorted(set(found))


def load(path : Path) -> tuple[str, list[tokenize.TokenInfo]] | str:
    try:
        source = path.read_text(encoding="utf-8-sig")
        tokens = list(tokenize.generate_tokens(io.StringIO(source).readline))
    except (OSError, SyntaxError, tokenize.TokenError, IndentationError) as exc:
        return str(exc)
    return source, tokens


def _opens(text : str) -> bool:
    return text in "([{"


def _closes(text : str) -> bool:
    return text in ")]}"


def _column(tok : tokenize.TokenInfo) -> int:
    return tok.start[1] + 1


def _aligned(
    path   : str,
    kind   : str,
    points : list[tuple[int, int]],
    what   : str,
) -> list[Hit]:
    if len(points) < 2:
        return []
    expected = max(col for _, col in points)
    return [
        Hit(path, line, kind, f"{what} at column {col}, expected {expected}")
        for line, col in points
        if col != expected
    ]


def _pipe_hits(
    path  : str,
    lines : list[str],
    block : list[Annotated],
) -> list[Hit]:
    """Align ``|`` from the right, so ``| NoChange`` meets ``| None | NoChange``."""
    hits : list[Hit] = []
    widest = max((len(row.pipes) for row in block), default=0)
    for index in range(widest):
        points = [
            (row.line, row.pipes[-1 - index])
            for row in block
            if len(row.pipes) > index
        ]
        hits.extend(_aligned(path, "pipe", points, "'|'"))
    for row in block:
        text = lines[row.line - 1] if 0 < row.line <= len(lines) else ""
        for col in row.pipes:
            at = col - 1
            if at < 0 or at >= len(text) or text[at] != "|":
                continue
            before = text[at - 1] if at else ""
            after  = text[at + 1] if at + 1 < len(text) else ""
            if not (before.isspace() and after.isspace()):
                hits.append(Hit(
                    path, row.line, "pipe",
                    f"'|' at column {col} needs spaces on both sides",
                ))
    return hits


def _block_hits(path : str, lines : list[str], block : list[Annotated]) -> list[Hit]:
    if len(block) < 2:
        return []
    hits = _aligned(
        path, "colon",
        [(row.line, row.colon) for row in block],
        "':'",
    )
    hits.extend(_pipe_hits(path, lines, block))
    return hits


def _param_span(
    tokens : list[tokenize.TokenInfo],
    def_at : int,
) -> tuple[int, int] | None:
    i = def_at + 1
    n = len(tokens)

    def skip_gap() -> None:
        nonlocal i
        while i < n and tokens[i].type in (
            tokenize.NL, tokenize.NEWLINE, tokenize.COMMENT,
            tokenize.INDENT, tokenize.DEDENT,
        ):
            i += 1

    skip_gap()
    if i < n and tokens[i].type == tokenize.NAME:
        i += 1
    skip_gap()
    if i < n and tokens[i].string == "[":
        depth = 1
        i += 1
        while i < n and depth:
            if tokens[i].string == "[":
                depth += 1
            elif tokens[i].string == "]":
                depth -= 1
            i += 1
    skip_gap()
    if i >= n or tokens[i].string != "(":
        return None
    start = i
    depth = 1
    i += 1
    while i < n and depth:
        if _opens(tokens[i].string):
            depth += 1
        elif _closes(tokens[i].string):
            depth -= 1
        i += 1
    return start, i - 1


def _annotated_params(
    tokens : list[tokenize.TokenInfo],
    start  : int,
    end    : int,
) -> list[Annotated]:
    open_line = tokens[start].start[0]
    depth = 1
    by_line : dict[int, list[tuple[int, tokenize.TokenInfo]]] = {}
    for tok in tokens[start + 1 : end]:
        if tok.type in (tokenize.NL, tokenize.NEWLINE, tokenize.COMMENT):
            continue
        by_line.setdefault(tok.start[0], []).append((depth, tok))
        if _opens(tok.string):
            depth += 1
        elif _closes(tok.string):
            depth -= 1
    rows : list[Annotated] = []
    for line, items in by_line.items():
        if line == open_line:
            continue
        colon = next(
            (tok for depth_at, tok in items if depth_at == 1 and tok.string == ":"),
            None,
        )
        if colon is None:
            continue
        name = next(
            (
                tok for depth_at, tok in items
                if depth_at == 1 and tok.type == tokenize.NAME
            ),
            None,
        )
        if name is None:
            continue
        pipes : list[int] = []
        seen = False
        for depth_at, tok in items:
            if tok is colon:
                seen = True
                continue
            if not seen or depth_at != 1:
                continue
            if tok.string in (",", "="):
                break
            if tok.string == "|":
                pipes.append(_column(tok))
        rows.append(Annotated(
            line, _column(colon), pipes, _column(name), len(name.string),
        ))
    return rows


def _signature_hits(
    path  : str,
    lines : list[str],
    rows  : list[Annotated],
) -> list[Hit]:
    """Longest parameter name, then one space. ``*`` and ``**`` do not count."""
    if len(rows) < 2:
        return []
    left     = min(row.name_start for row in rows)
    expected = left + max(row.name_len for row in rows) + 1
    hits = [
        Hit(
            path, row.line, "colon",
            f"':' at column {row.colon}, expected {expected}",
        )
        for row in rows
        if row.colon != expected
    ]
    hits.extend(_pipe_hits(path, lines, rows))
    return hits


def scan_signatures(
    path   : str,
    lines  : list[str],
    tokens : list[tokenize.TokenInfo],
) -> list[Hit]:
    hits : list[Hit] = []
    for index, tok in enumerate(tokens):
        if tok.type != tokenize.NAME or tok.string != "def":
            continue
        span = _param_span(tokens, index)
        if span is None:
            continue
        start, end = span
        if tokens[start].start[0] == tokens[end].start[0]:
            continue
        hits.extend(_signature_hits(
            path, lines, _annotated_params(tokens, start, end),
        ))
    return hits


def _depth0_lines(
    tokens : list[tokenize.TokenInfo],
) -> Iterator[list[tokenize.TokenInfo]]:
    depth = 0
    buf   : list[tokenize.TokenInfo] = []
    for tok in tokens:
        if tok.type in (
            tokenize.ENCODING, tokenize.ENDMARKER, tokenize.COMMENT,
            tokenize.INDENT, tokenize.DEDENT,
        ):
            continue
        if tok.type in (tokenize.NL, tokenize.NEWLINE):
            if depth == 0 and buf:
                yield buf
                buf = []
            continue
        if depth == 0:
            buf.append(tok)
        if _opens(tok.string):
            depth += 1
        elif _closes(tok.string):
            depth = max(0, depth - 1)
    if depth == 0 and buf:
        yield buf


def _as_annotated(buf : list[tokenize.TokenInfo]) -> Annotated | None:
    if len(buf) < 2 or buf[0].type != tokenize.NAME:
        return None
    if buf[0].string in _NOT_ANN or buf[1].string != ":":
        return None
    pipes : list[int] = []
    depth = 0
    for tok in buf[2:]:
        if tok.string == "=" and depth == 0:
            break
        if tok.string == "|" and depth == 0:
            pipes.append(_column(tok))
        if _opens(tok.string):
            depth += 1
        elif _closes(tok.string):
            depth = max(0, depth - 1)
    return Annotated(buf[1].start[0], _column(buf[1]), pipes)


def scan_annotations(
    path   : str,
    lines  : list[str],
    tokens : list[tokenize.TokenInfo],
) -> list[Hit]:
    hits  : list[Hit] = []
    run   : list[Annotated] = []
    prev  : tuple[int, int] | None = None
    for buf in _depth0_lines(tokens):
        row = _as_annotated(buf)
        if row is None:
            hits.extend(_block_hits(path, lines, run))
            run = []
            prev = None
            continue
        indent = buf[0].start[1]
        if prev == (row.line - 1, indent):
            run.append(row)
        else:
            hits.extend(_block_hits(path, lines, run))
            run = [row]
        prev = (row.line, indent)
    hits.extend(_block_hits(path, lines, run))
    return hits


def _parse_dict(
    tokens  : list[tokenize.TokenInfo],
    open_at : int,
) -> tuple[list[tuple[int, int]], bool]:
    depth   = 1
    entries : list[tuple[int, int]] = []
    spans   = False
    colon   : tuple[int, int] | None = None
    started = False
    broken  = False
    i = open_at + 1
    n = len(tokens)
    while i < n and depth:
        tok = tokens[i]
        if tok.type in (
            tokenize.COMMENT, tokenize.ENCODING, tokenize.ENDMARKER,
            tokenize.INDENT, tokenize.DEDENT,
        ):
            i += 1
            continue
        if tok.type in (tokenize.NL, tokenize.NEWLINE):
            if started and colon is not None:
                broken = True
            i += 1
            continue
        text = tok.string
        if _opens(text):
            depth += 1
            started = True
        elif _closes(text):
            depth -= 1
            if depth == 0 and colon is not None:
                if broken:
                    spans = True
                else:
                    entries.append(colon)
            if depth == 0:
                break
        elif depth == 1 and text == ",":
            if colon is not None:
                if broken:
                    spans = True
                else:
                    entries.append(colon)
            colon   = None
            started = False
            broken  = False
        elif depth == 1 and text == ":" and colon is None:
            colon   = (tok.start[0], _column(tok))
            started = True
        else:
            started = True
        i += 1
    return entries, spans


def scan_dicts(
    path   : str,
    tokens : list[tokenize.TokenInfo],
) -> list[Hit]:
    hits : list[Hit] = []
    for index, tok in enumerate(tokens):
        if tok.string != "{":
            continue
        entries, spans = _parse_dict(tokens, index)
        if spans or len({line for line, _ in entries}) < 2:
            continue
        hits.extend(_aligned(path, "colon", entries, "':'"))
    return hits


def _shown(stmt : ImportStmt) -> str:
    if stmt.level:
        return ("." * stmt.level) + stmt.module
    return stmt.module


def _is_future(stmt : ImportStmt) -> bool:
    return stmt.level == 0 and stmt.module == "__future__"


def _top(stmt : ImportStmt) -> str:
    return stmt.module.split(".", 1)[0]


def _from_group(stmt : ImportStmt) -> int:
    """0 stdlib, 1 Qt, 2 other third-party, 3 project."""
    if stmt.level > 0:
        return 3
    top = _top(stmt)
    if top in STDLIB:
        return 0
    if top == "PyQt6":
        return 1
    if top in _THIRD_PARTY:
        return 2
    return 3


def _extends(left : ImportStmt, right : ImportStmt) -> bool:
    """Project ``xxx`` against ``xxx.yyy``: same kind and distance, one path extends the other."""
    if _from_group(left) != 3 or _from_group(right) != 3:
        return False
    if left.plain != right.plain or left.level != right.level:
        return False
    if not left.module or not right.module:
        return False
    return (
        right.module.startswith(left.module + ".")
        or left.module.startswith(right.module + ".")
    )


def _part_change(left : ImportStmt, right : ImportStmt) -> bool:
    """Same leading-dot depth, different module-component count."""
    if left.plain or right.plain:
        return False
    if left.level == 0 or right.level == 0 or left.level != right.level:
        return False
    if _from_group(left) != 3 or _from_group(right) != 3:
        return False
    left_parts  = left.module.split(".")  if left.module  else []
    right_parts = right.module.split(".") if right.module else []
    return len(left_parts) != len(right_parts)


def _level_change(left : ImportStmt, right : ImportStmt) -> bool:
    """Project ``from`` imports whose leading-dot depth differs."""
    if left.plain or right.plain:
        return False
    if _from_group(left) != 3 or _from_group(right) != 3:
        return False
    return left.level != right.level


def _section(stmt : ImportStmt) -> tuple[int, int]:
    """Blank line between ``__future__``, straight imports, and ``from`` groups."""
    if _is_future(stmt):
        return (0, 0)
    if stmt.plain:
        return (1, 0)
    return (2, _from_group(stmt))


def _sort_key(stmt : ImportStmt) -> _Key:
    if _is_future(stmt):
        return (0, 0, 0, 0, "")
    if stmt.plain:
        return (1, 0, 0, 0, "")
    group = _from_group(stmt)
    if group == 0:
        rank = _STDLIB_RANK.get(_top(stmt), len(_STDLIB_ORDER))
        return (2, 0, rank, 0, stmt.module)
    if group == 1:
        sub  = stmt.module.split(".")[1] if "." in stmt.module else ""
        rank = _QT_RANK.get(sub, 9)
        return (2, 1, rank, 0, stmt.module)
    if group == 2:
        return (2, 2, 0, 0, stmt.module)
    if stmt.level > 0:
        parts = stmt.module.split(".") if stmt.module else []
        return (2, 3, 1, -stmt.level, f"{len(parts):02d}")
    parts = stmt.module.split(".") if stmt.module else []
    return (2, 3, 0, len(parts), stmt.module)


def _parse_import(
    tokens : list[tokenize.TokenInfo],
    start  : int,
) -> tuple[ImportStmt, int]:
    first = tokens[start]
    plain = first.string == "import"
    level = 0
    names : list[str] = []
    import_col = _column(first) if plain else None
    i = start + 1
    n = len(tokens)
    if plain:
        while i < n:
            tok = tokens[i]
            if tok.type in (tokenize.NL, tokenize.COMMENT):
                i += 1
                continue
            if tok.type == tokenize.NAME or tok.string == ".":
                if tok.string == ",":
                    break
                if tok.type == tokenize.NAME:
                    names.append(tok.string)
                i += 1
                if i < n and tokens[i].string == ".":
                    continue
                break
            break
    else:
        while i < n:
            tok = tokens[i]
            if tok.type in (tokenize.NL, tokenize.COMMENT, tokenize.NEWLINE):
                i += 1
                continue
            if tok.type == tokenize.NAME and tok.string == "import":
                import_col = _column(tok)
                i += 1
                break
            if tok.string == ".":
                if not names:
                    level += 1
                i += 1
                continue
            if tok.string == "...":
                if not names:
                    level += 3
                i += 1
                continue
            if tok.type == tokenize.NAME:
                names.append(tok.string)
                i += 1
                continue
            break
    depth = 0
    end_line = first.start[0]
    bound : list[str] = []
    after_as = False
    while i < n:
        tok = tokens[i]
        if _opens(tok.string):
            depth += 1
        elif _closes(tok.string):
            depth -= 1
        elif depth == 0 and tok.type == tokenize.NAME:
            if tok.string == "as":
                after_as = True
            elif after_as:
                after_as = False
            else:
                bound.append(tok.string)
        end_line = max(end_line, tok.start[0])
        i += 1
        if tok.type == tokenize.NEWLINE and depth <= 0:
            break
    return ImportStmt(
        first.start[0], end_line, level, ".".join(names), plain, import_col,
        tuple(bound),
    ), i


def _is_type_checking(tokens : list[tokenize.TokenInfo], at : int) -> bool:
    nxt = at + 1
    while nxt < len(tokens) and tokens[nxt].type in (tokenize.NL, tokenize.COMMENT):
        nxt += 1
    return nxt < len(tokens) and tokens[nxt].string == "TYPE_CHECKING"


def _skip_clause(tokens : list[tokenize.TokenInfo], at : int) -> int:
    """Move past an ``if`` test, leaving the index on the suite colon."""
    i = at + 1
    depth = 0
    while i < len(tokens):
        tok = tokens[i]
        if _opens(tok.string):
            depth += 1
        elif _closes(tok.string):
            depth -= 1
        elif tok.string == ":" and depth == 0:
            return i
        i += 1
    return i


def _import_sections(
    tokens : list[tokenize.TokenInfo],
) -> list[list[ImportStmt]]:
    module  : list[ImportStmt] = []
    extras  : list[list[ImportStmt]] = []
    indent  = 0
    started = False
    i = 0
    n = len(tokens)
    while i < n:
        tok = tokens[i]
        if tok.type == tokenize.INDENT:
            indent += 1
            i += 1
            continue
        if tok.type == tokenize.DEDENT:
            indent = max(0, indent - 1)
            i += 1
            continue
        if indent != 0 or tok.type in (
            tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE,
            tokenize.ENCODING, tokenize.ENDMARKER,
        ):
            i += 1
            continue
        if tok.type == tokenize.STRING and not started and not module:
            i += 1
            continue
        if tok.type == tokenize.NAME and tok.string in ("import", "from"):
            stmt, i = _parse_import(tokens, i)
            module.append(stmt)
            started = True
            continue
        if (
            tok.type == tokenize.NAME
            and tok.string == "if"
            and _is_type_checking(tokens, i)
        ):
            body : list[ImportStmt] = []
            i = _skip_clause(tokens, i) + 1
            body_indent = None
            while i < n:
                tok = tokens[i]
                if tok.type == tokenize.INDENT:
                    indent += 1
                    if body_indent is None:
                        body_indent = indent
                    i += 1
                    continue
                if tok.type == tokenize.DEDENT:
                    indent = max(0, indent - 1)
                    i += 1
                    if body_indent is not None and indent < body_indent:
                        break
                    continue
                if tok.type in (
                    tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE,
                    tokenize.ENCODING,
                ):
                    i += 1
                    continue
                if tok.type == tokenize.NAME and tok.string in ("import", "from"):
                    stmt, i = _parse_import(tokens, i)
                    body.append(stmt)
                    continue
                if body_indent is not None and indent < body_indent:
                    break
                i += 1
            extras.append(body)
            started = True
            continue
        break
    return [module, *extras]


def _is_type_checking_prelude(stmt : ImportStmt) -> bool:
    return (
        not stmt.plain
        and stmt.level == 0
        and stmt.module == "typing"
        and stmt.bound == ("TYPE_CHECKING",)
    )


def _imports_type_checking(stmt : ImportStmt) -> bool:
    return (
        not stmt.plain
        and stmt.level == 0
        and stmt.module == "typing"
        and "TYPE_CHECKING" in stmt.bound
    )


def _type_checking_hits(
    path  : str,
    lines : list[str],
    stmts : list[ImportStmt],
) -> list[Hit]:
    """``TYPE_CHECKING`` is imported alone, on the line before the test."""
    hits : list[Hit] = []
    for stmt in stmts:
        if not _imports_type_checking(stmt):
            continue
        if stmt.bound != ("TYPE_CHECKING",):
            hits.append(Hit(
                path, stmt.line, "import-order",
                "import TYPE_CHECKING alone, immediately before if TYPE_CHECKING",
            ))
            continue
        nxt = stmt.end
        if nxt >= len(lines) or lines[nxt].strip() != "if TYPE_CHECKING:":
            hits.append(Hit(
                path, stmt.line, "import-order",
                "from typing import TYPE_CHECKING must immediately precede if TYPE_CHECKING",
            ))
    for index, line in enumerate(lines):
        if line.strip() != "if TYPE_CHECKING:":
            continue
        prev = index - 1
        if prev < 0 or lines[prev].strip() != "from typing import TYPE_CHECKING":
            hits.append(Hit(
                path, index + 1, "import-order",
                "if TYPE_CHECKING must be immediately preceded by from typing import TYPE_CHECKING",
            ))
    return hits


def _order_hits(path : str, stmts : list[ImportStmt]) -> list[Hit]:
    hits : list[Hit] = []
    seen : list[tuple[ImportStmt, _Key]] = []
    for stmt in stmts:
        key   = _sort_key(stmt)
        first = next(
            (prior for prior, prior_key in seen if key < prior_key),
            None,
        )
        if first is not None:
            hits.append(Hit(
                path, stmt.line, "import-order",
                f"{_shown(stmt)} belongs before {_shown(first)} (line {first.line})",
            ))
        seen.append((stmt, key))
    return hits


def _blank_hits(
    path     : str,
    stmts    : list[ImportStmt],
    extended : bool,
) -> list[Hit]:
    hits : list[Hit] = []
    prev : ImportStmt | None = None
    for stmt in stmts:
        if prev is not None:
            adjacent = stmt.line <= prev.end + 1
            if extended and adjacent and (
                _section(stmt) != _section(prev)
                or _level_change(prev, stmt)
                or _extends(prev, stmt)
                or _part_change(prev, stmt)
            ):
                hits.append(Hit(
                    path, stmt.line, "import-blank",
                    f"expected a blank line before {_shown(stmt)}",
                ))
            elif not extended and not adjacent:
                hits.append(Hit(
                    path, stmt.line, "import-blank",
                    "no blank line inside if TYPE_CHECKING",
                ))
        prev = stmt
    return hits


def _align_hits(path : str, stmts : list[ImportStmt]) -> list[Hit]:
    hits  : list[Hit] = []
    group : list[ImportStmt] = []

    def flush() -> None:
        points = [
            (stmt.line, stmt.import_col)
            for stmt in group
            if not stmt.plain and stmt.import_col is not None
        ]
        hits.extend(_aligned(path, "import-align", points, "'import'"))
        group.clear()

    prev_end = 0
    for stmt in stmts:
        if group and stmt.line > prev_end + 1:
            flush()
        group.append(stmt)
        prev_end = stmt.end
    flush()
    return hits


def scan_imports(
    path   : str,
    lines  : list[str],
    tokens : list[tokenize.TokenInfo],
) -> list[Hit]:
    hits : list[Hit] = []
    sections = _import_sections(tokens)
    for index, stmts in enumerate(sections):
        ordered = [stmt for stmt in stmts if not _is_type_checking_prelude(stmt)]
        hits.extend(_order_hits(path, ordered))
        hits.extend(_blank_hits(path, ordered, index == 0))
        hits.extend(_align_hits(path, ordered))
    hits.extend(_type_checking_hits(
        path, lines, [stmt for stmts in sections for stmt in stmts],
    ))
    return hits


def scan_file(path : Path) -> list[Hit]:
    name = rel(path)
    loaded = load(path)
    if isinstance(loaded, str):
        return [Hit(name, 1, "parse", loaded)]
    source, tokens = loaded
    lines = source.splitlines()
    hits : list[Hit] = []
    hits.extend(scan_signatures(name, lines, tokens))
    hits.extend(scan_annotations(name, lines, tokens))
    hits.extend(scan_dicts(name, tokens))
    hits.extend(scan_imports(name, lines, tokens))
    return hits


def main(argv : Sequence[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    hits : list[Hit] = []
    files = py_files(args)
    for path in files:
        hits.extend(scan_file(path))
    hits.sort(key=lambda hit: (hit.path, hit.line, hit.kind))
    counts = {kind: 0 for kind in _KINDS}
    for hit in hits:
        counts[hit.kind] = counts.get(hit.kind, 0) + 1
    print(f"{len(hits)} issues in {len(files)} files")
    for kind in _KINDS:
        print(f"  {kind}: {counts.get(kind, 0)}")
    if hits:
        print()
    for hit in hits:
        print(f"{hit.path}:{hit.line}: {hit.kind}: {hit.detail}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
