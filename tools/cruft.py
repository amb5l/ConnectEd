"""Report functions and methods that nothing calls.

Scans ``ConnectEd``, ``tests``, ``tools``, ``scripts``, and ``examples``.
Skips ANTLR output and anything under pyVHDLParser. A name counts as
used when some other function calls it, loads it to pass it on (for
example into ``connect``), or names it in a string (for example a
subscriber method). Dunder methods, tests, pytest hooks, and methods
that override a third-party base are left out.

Published surfaces are left out too. A module that imports ``export``
from ``pyTooling.Decorators`` is an HDL model API. ``ConnectEd/scripting``
is the scripting API, and ``ConnectEd/ai`` is unfinished chat support.
Declarations there may have no caller yet. Calls inside those files
still count, so a private helper used only from the API is not reported.

Run from the repo root::

    .venv\\Scripts\\python.exe tools/cruft.py
    .venv\\Scripts\\python.exe tools/cruft.py ConnectEd/ai/driver.py
"""

from __future__ import annotations

import ast
import importlib

from dataclasses import dataclass
from pathlib     import Path


ROOT = Path(__file__).resolve().parents[1]

# ANTLR output. Regenerated from the .g4 grammars.
SKIP_FILES = frozenset({
    "vhdl_lexer.py",
    "vhdl_parser.py",
    "vhdl_parserListener.py",
    "vhdl_parserVisitor.py",
})

_WRAPPERS = frozenset({
    "checked",
    "staticmethod",
    "classmethod",
    "property",
    "setter",
    "deleter",
    "cache",
    "cached_property",
    "lru_cache",
})

# Bases that dispatch to visitXxx by name rather than defining those methods.
_VISIT_BASES = frozenset({
    "NodeVisitor",
    "ParseTreeVisitor",
})

# Surfaces that may declare methods before anything calls them.
API_DIRS = (
    "ConnectEd/ai/",
    "ConnectEd/scripting/",
)


@dataclass
class Defn:
    path : str
    line : int
    name : str
    qual : str
    cls  : str
    skip : bool = False


@dataclass
class ClassInfo:
    path     : str
    name     : str
    bases    : tuple[str, ...]
    bindings : dict[str, str]


def rel(path : Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def skip(path : Path) -> bool:
    if path.name in SKIP_FILES:
        return True
    parts = [part.lower() for part in path.parts]
    if "__pycache__" in path.parts or ".venv" in path.parts:
        return True
    return "pyvhdlparser" in parts


def py_files(raws : list[str]) -> list[Path]:
    if not raws:
        raws = ["ConnectEd", "tests", "tools", "scripts", "examples"]
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


def _generated(source : str) -> bool:
    head = "\n".join(source.splitlines()[:20])
    return "Generated from" in head and "ANTLR" in head


def _dotted(node : ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = _dotted(node.value)
        if parent:
            return f"{parent}.{node.attr}"
    return None


def _decorator_names(node : ast.FunctionDef | ast.AsyncFunctionDef) -> set[str]:
    names : set[str] = set()
    for dec in node.decorator_list:
        target = dec.func if isinstance(dec, ast.Call) else dec
        if isinstance(target, ast.Name):
            names.add(target.id)
        elif isinstance(target, ast.Attribute):
            names.add(target.attr)
    return names


def _bindings(tree : ast.AST) -> dict[str, str]:
    bound : dict[str, str] = {}
    if not isinstance(tree, ast.Module):
        return bound
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.asname:
                    bound[alias.asname] = alias.name
                else:
                    bound[alias.name.split(".", 1)[0]] = alias.name.split(".", 1)[0]
        elif isinstance(node, ast.ImportFrom):
            prefix = "project:" if node.level else (f"{node.module}." if node.module else "")
            for alias in node.names:
                if alias.name == "*":
                    continue
                local = alias.asname or alias.name
                bound[local] = f"{prefix}{alias.name}"
    return bound


class _Scan(ast.NodeVisitor):
    def __init__(self, path : str, bindings : dict[str, str]) -> None:
        self.path     = path
        self.bindings = bindings
        self.defs     : list[Defn] = []
        self.classes  : list[ClassInfo] = []
        self.uses     : set[str] = set()
        self._stack   : list[tuple[str, str]] = []

    def visit_ClassDef(self, node : ast.ClassDef) -> None:
        bases = tuple(
            dotted for base in node.bases
            if (dotted := _dotted(base)) is not None
        )
        self.classes.append(ClassInfo(self.path, node.name, bases, self.bindings))
        self._stack.append(("class", node.name))
        self.generic_visit(node)
        self._stack.pop()

    def visit_FunctionDef(self, node : ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        parent_is_class = bool(self._stack) and self._stack[-1][0] == "class"
        qual            = ".".join([*(name for _, name in self._stack), node.name])
        decorators      = _decorator_names(node)
        self.defs.append(Defn(
            path = self.path,
            line = node.lineno,
            name = node.name,
            qual = qual,
            cls  = self._stack[-1][1] if parent_is_class else "",
            skip = (
                node.name.startswith("__") and node.name.endswith("__")
                or node.name.startswith("test_")
                or node.name.startswith("pytest_")
                or bool(decorators - _WRAPPERS)
            ),
        ))
        self._stack.append(("func", node.name))
        self.generic_visit(node)
        self._stack.pop()

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Call(self, node : ast.Call) -> None:
        func = node.func
        if isinstance(func, ast.Name):
            self._use(func.id)
        elif isinstance(func, ast.Attribute):
            self._use(func.attr)
        self.generic_visit(node)

    def visit_Constant(self, node : ast.Constant) -> None:
        if isinstance(node.value, str):
            self._use(node.value)

    def visit_Name(self, node : ast.Name) -> None:
        if isinstance(node.ctx, ast.Load):
            self._use(node.id)

    def visit_Attribute(self, node : ast.Attribute) -> None:
        self._use(node.attr)
        self.generic_visit(node)

    def _use(self, name : str) -> None:
        caller = ".".join(name for _, name in self._stack)
        if caller == name or caller.endswith("." + name):
            return
        self.uses.add(name)


def _qual_of(expr : str, bindings : dict[str, str]) -> str | None:
    parts = expr.split(".")
    if parts[0] not in bindings:
        return None
    head = bindings[parts[0]]
    rest = parts[1:]
    if rest:
        return ".".join([head, *rest])
    return head


_class_cache : dict[str, type | None] = {}


def _load_class(qual : str) -> type | None:
    if qual in _class_cache:
        return _class_cache[qual]
    cls : type | None = None
    if not qual.startswith("project:") and "." in qual:
        mod_name, cls_name = qual.rsplit(".", 1)
        if not mod_name.startswith("ConnectEd"):
            try:
                module = importlib.import_module(mod_name)
                obj    = getattr(module, cls_name)
                if isinstance(obj, type):
                    cls = obj
            except Exception:
                cls = None
    _class_cache[qual] = cls
    return cls


def _external_defines(qual : str, method : str) -> bool:
    cls = _load_class(qual)
    if cls is None:
        return False
    return any(method in getattr(base, "__dict__", {}) for base in cls.__mro__)


def _is_visit_base(qual : str) -> bool:
    cls = _load_class(qual)
    if cls is None:
        return qual.split(".")[-1] in _VISIT_BASES
    return any(base.__name__ in _VISIT_BASES for base in cls.__mro__)


def _class_quals(
    bases    : tuple[str, ...],
    bindings : dict[str, str],
    by_class : dict[str, list[ClassInfo]],
    seen     : set[str],
) -> list[str]:
    quals : list[str] = []
    for expr in bases:
        qual = _qual_of(expr, bindings)
        if qual is not None and not qual.startswith("project:"):
            quals.append(qual)
            continue
        classname = expr.split(".")[-1]
        if qual is not None and qual.startswith("project:"):
            classname = qual.removeprefix("project:")
        if classname in seen:
            continue
        seen.add(classname)
        for info in by_class.get(classname, []):
            quals.extend(_class_quals(info.bases, info.bindings, by_class, seen))
    return quals


def _framework_method(
    item     : Defn,
    info     : ClassInfo | None,
    by_class : dict[str, list[ClassInfo]],
) -> bool:
    """True when a third-party base, or a class that mixes this one in, defines the method."""
    if info is None:
        return False
    hosts = [info]
    for other in by_class.values():
        for host in other:
            if host is info:
                continue
            if any(base.split(".")[-1] == info.name for base in host.bases):
                hosts.append(host)
    for host in hosts:
        quals = _class_quals(host.bases, host.bindings, by_class, set())
        if any(_external_defines(qual, item.name) for qual in quals):
            return True
        if item.name.startswith("visit") and any(_is_visit_base(qual) for qual in quals):
            return True
    return False


def _api_path(path : str) -> bool:
    return any(path.startswith(prefix) for prefix in API_DIRS)


def _exported_model(tree : ast.AST) -> bool:
    """True when the module publishes types with pyTooling's ``@export``."""
    if not isinstance(tree, ast.Module):
        return False
    for node in tree.body:
        if not isinstance(node, ast.ImportFrom) or node.module != "pyTooling.Decorators":
            continue
        if any(alias.name == "export" for alias in node.names):
            return True
    return False


def scan_file(path : Path) -> tuple[list[Defn], list[ClassInfo], set[str]] | str:
    try:
        source = path.read_text(encoding = "utf-8-sig")
        if _generated(source):
            return [], [], set()
        tree = ast.parse(source)
    except (OSError, SyntaxError) as exc:
        return str(exc)
    bindings = _bindings(tree)
    scanner  = _Scan(rel(path), bindings)
    scanner.visit(tree)
    if _api_path(scanner.path) or _exported_model(tree):
        for item in scanner.defs:
            item.skip = True
    return scanner.defs, scanner.classes, scanner.uses


def unused(raws : list[str]) -> list[Defn]:
    defs    : list[Defn] = []
    classes : list[ClassInfo] = []
    uses    : set[str] = set()
    for path in py_files(raws):
        loaded = scan_file(path)
        if isinstance(loaded, str):
            continue
        file_defs, file_classes, file_uses = loaded
        defs.extend(file_defs)
        classes.extend(file_classes)
        uses.update(file_uses)
    by_name : dict[tuple[str, str], ClassInfo] = {
        (info.path, info.name) : info for info in classes
    }
    by_class : dict[str, list[ClassInfo]] = {}
    for info in classes:
        by_class.setdefault(info.name, []).append(info)
    found : list[Defn] = []
    for item in defs:
        if item.skip or item.name in uses:
            continue
        info  = by_name.get((item.path, item.cls)) if item.cls else None
        bases = info.bases if info else ()
        if _framework_method(item, info, by_class):
            continue
        if any(base == "Protocol" or base.endswith(".Protocol") for base in bases):
            continue
        found.append(item)
    return found


def main(argv : list[str] | None = None) -> int:
    import sys
    args  = list(sys.argv[1:] if argv is None else argv)
    found = unused(args)
    print(f"{len(found)} unused in {len(py_files(args))} files")
    for item in found:
        print(f"{item.path}:{item.line}: {item.qual}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
