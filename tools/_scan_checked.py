"""Find annotated boundary methods missing @checked (see doc/CHECKED.md)."""
from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path

ROOT = Path("ConnectEd")

SKIP_PATH_PARTS = (
    "hdl/",
    "/tests/",
    "/examples/",
    "/scripts/",
    "\\tests\\",
    "\\examples\\",
    "\\scripts\\",
)

QT_SKIP = frozenset({
    "paint", "boundingRect", "shape", "itemChange",
    "mousePressEvent", "mouseMoveEvent", "mouseReleaseEvent",
    "mouseDoubleClickEvent", "wheelEvent", "keyPressEvent", "keyReleaseEvent",
    "event", "eventFilter", "resizeEvent", "showEvent", "hideEvent", "closeEvent",
    "contextMenuEvent", "dragEnterEvent", "dragMoveEvent", "dragLeaveEvent",
    "dropEvent", "focusInEvent", "focusOutEvent", "enterEvent", "leaveEvent",
    "hoverEnterEvent", "hoverMoveEvent", "hoverLeaveEvent", "timerEvent",
    "customEvent", "drawBackground", "drawForeground", "inputMethodEvent",
    "changeEvent", "moveEvent",
})

SKIP_FILES = frozenset({
    "ConnectEd/core/check.py",
})


@dataclass
class Hit:
    path   : str
    line   : int
    qual   : str
    reason : str


def skip_path(path: Path) -> bool:
    s = path.as_posix()
    if s in SKIP_FILES:
        return True
    return any(part in s for part in SKIP_PATH_PARTS)


def has_checked(decorators: list[ast.expr]) -> bool:
    for dec in decorators:
        if isinstance(dec, ast.Name) and dec.id == "checked":
            return True
        if isinstance(dec, ast.Call):
            func = dec.func
            if isinstance(func, ast.Name) and func.id == "checked":
                return True
    return False


def annotation_str(node: ast.expr | None) -> str | None:
    if node is None:
        return None
    return ast.unparse(node)


def params_fully_annotated(args: ast.arguments) -> bool:
    posonly = list(args.posonlyargs)
    regular = list(args.args)
    kwonly  = list(args.kwonlyargs)
    all_params = posonly + regular + kwonly
    if not all_params:
        return False

    for arg in all_params:
        if arg.arg in ("self", "cls"):
            continue
        if arg.annotation is None:
            return False

    if args.vararg and args.vararg.annotation is None:
        return False
    if args.kwarg and args.kwarg.annotation is None:
        return False

    if args.vararg and annotation_str(args.vararg.annotation) == "Any":
        return False
    if args.kwarg and annotation_str(args.kwarg.annotation) == "Any":
        return False

    return True


DOC_BOUNDARY = frozenset({
    "isClean",
    "name",
    "setName",
    "path",
    "setPath",
    "save",
    "load",
    "navItemSpec",
    "navLabel",
    "navSetLabel",
    "navDisplayLabel",
    "navToolTip",
    "navContextMenu",
    "showWindow",
    "newWindow",
    "windowTitle",
    "closeSubWindow",
    "onSubWindowClosed",
    "commit",
    "isPrimarySubject",
    "onChanged",
})


def boundary_reason(name: str, path: str, class_names: list[str]) -> str | None:
    in_cmd = any("Cmd" in c for c in class_names) or "/cmd/" in path

    if name == "__init__":
        if any(
            seg in path
            for seg in (
                "/items/",
                "/scenes/",
                "/views/",
                "/dialogs/",
                "/widgets/window/",
                "/widgets/",
                "/documents/",
                "/ai/",
                "/cmd/",
            )
        ):
            return "__init__"
        return None

    if in_cmd and name in ("redo", "undo"):
        return name

    if name in ("fromXml", "toXml"):
        return name

    if name.startswith("set") and len(name) > 3 and name[3].isupper():
        if "/items/" in path or "/scenes/" in path or "/properties.py" in path:
            return "setter"

    if name.startswith("get") and len(name) > 3 and name[3].isupper():
        if "/items/" in path or "/scenes/" in path or "/properties.py" in path:
            return "getter"

    if "/api/" in path and not name.startswith("_"):
        return "api"

    if path.endswith("/netlist.py") and not name.startswith("_"):
        return "netlist"

    if "/interaction/" in path and name in ("commit", "_commit", "start", "cancel"):
        return "interaction"

    if "/state/" in path and name in ("enter", "leave", "go"):
        return "state"

    if "/documents/" in path and name in DOC_BOUNDARY:
        return "doc"

    if name in DOC_BOUNDARY and any(n.endswith("Doc") for n in class_names):
        return "doc"

    return None


def scan_class(path: str, class_node: ast.ClassDef) -> list[Hit]:
    hits: list[Hit] = []
    for node in class_node.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if has_checked(node.decorator_list):
            continue
        for dec in node.decorator_list:
            if isinstance(dec, ast.Name) and dec.id in ("property", "classmethod", "staticmethod"):
                break
        else:
            pass
        # re-check property skip
        if any(
            isinstance(d, ast.Name) and d.id in ("property", "classmethod", "staticmethod")
            for d in node.decorator_list
        ):
            continue
        if any(
            isinstance(d, ast.Name) and d.id == "abstractmethod"
            or (
                isinstance(d, ast.Call)
                and isinstance(d.func, ast.Name)
                and d.func.id == "abstractmethod"
            )
            for d in node.decorator_list
        ):
            continue

        if node.name in QT_SKIP:
            continue
        if node.name.startswith("__") and node.name != "__init__":
            continue
        if node.returns is None:
            continue
        if not params_fully_annotated(node.args):
            continue

        reason = boundary_reason(node.name, path, [class_node.name])
        if reason is None:
            continue

        qual = f"{class_node.name}.{node.name}"
        hits.append(Hit(path, node.lineno, qual, reason))
    return hits


def scan_module_functions(path: str, tree: ast.Module) -> list[Hit]:
    hits: list[Hit] = []
    if "/api/" not in path:
        return hits
    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if has_checked(node.decorator_list):
            continue
        if node.name.startswith("_"):
            continue
        if node.returns is None:
            continue
        if not params_fully_annotated(node.args):
            continue
        hits.append(Hit(path, node.lineno, node.name, "api"))
    return hits


def read_source(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace")


def scan_file(path: Path) -> tuple[list[Hit], str | None]:
    source = read_source(path)
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as exc:
        return [], str(exc)
    rel = path.as_posix()
    hits: list[Hit] = []
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            hits.extend(scan_class(rel, node))
    hits.extend(scan_module_functions(rel, tree))
    return hits, None


def main() -> None:
    all_hits: list[Hit] = []
    parse_errors: list[tuple[str, str]] = []
    for path in sorted(ROOT.rglob("*.py")):
        if skip_path(path):
            continue
        hits, err = scan_file(path)
        all_hits.extend(hits)
        if err:
            parse_errors.append((path.as_posix(), err))

    by_reason: dict[str, list[Hit]] = {}
    for hit in all_hits:
        by_reason.setdefault(hit.reason, []).append(hit)

    print(f"Missing @checked on annotated boundary methods: {len(all_hits)}")
    print("(Scope: doc/CHECKED.md — __init__, cmd, set/get, fromXml/toXml, api/, netlist, doc/)")
    print()

    order = [
        "__init__", "redo", "undo", "setter", "getter",
        "fromXml", "toXml", "doc", "api", "netlist", "interaction", "state",
    ]
    for reason in order:
        hits = by_reason.pop(reason, [])
        if not hits:
            continue
        print(f"=== {reason} ({len(hits)}) ===")
        current = None
        for hit in sorted(hits, key=lambda h: (h.path, h.line)):
            if hit.path != current:
                current = hit.path
                print(f"\n{current}")
            print(f"  L{hit.line:4d}  {hit.qual}")

    for reason, hits in sorted(by_reason.items()):
        print(f"\n=== {reason} ({len(hits)}) ===")
        for hit in sorted(hits, key=lambda h: (h.path, h.line)):
            print(f"  {hit.path}:L{hit.line}  {hit.qual}")

    if parse_errors:
        print(f"\n=== Skipped (parse error — often UTF-8 BOM); re-scan manually ({len(parse_errors)}) ===")
        for rel, err in parse_errors:
            print(f"  {rel}")


if __name__ == "__main__":
    main()
