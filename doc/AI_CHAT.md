# AI chat pane

Implementation plan for a configurable AI assistant in ConnectEd. Users chat in
natural language; the assistant reads diagram context and invokes structured
**tools** (not raw mouse events) to operate the GUI — similar in spirit to
Cursor’s agent loop for code, but built on ConnectEd’s existing scripting and
scene APIs.

## Goals

- **Multiple chat docks** — users can open more than one AI conversation at a
  time (separate history and session per dock).
- **Dock widget** chat UI integrated with the main window (like Messages /
  Transcript).
- **Top-level AI menu** — New Chat, dynamic list of open chats, Recipes
  (curated workflows), Settings.
- **Configurable providers** — model, API key, base URL; swappable backends.
- **AI driver** — tool catalog the model can call; implementations delegate to
  [`ConnectEd/scripting/`](../ConnectEd/scripting/) and scene/view APIs with undo.
- **Exclusive editing lease** — only one AI chat may run write tools (or hold the
  scene for an agent loop) at a time; see [Agent editing lease](#agent-editing-lease).
- **Terse command catalog** in the system prompt so the model knows what ConnectEd
  can do (Place, Edit, View, scene operations).

## Non-goals (initially)

- Embedding **Cursor Composer 2.5** as an in-app provider (no public Composer API
  for third-party apps today; see [Providers](#providers)).
- Arbitrary **Python execution** of model-generated code in the GUI process
  (prefer explicit tools).
- Cloud-hosted ConnectEd backend or multi-user chat history sync.
- Full **preferences dialog** for all app settings (AI section can start minimal).
- **Web chat UI integration** — no copy/paste bridge, embedded provider pages, or
  automation against vendor websites; use **official APIs** or **local** models
  (e.g. Ollama) only.
- **Recorded UI macros** — Recipes are curated prompts + context, not QTest replay.
- **Full-window modal freeze** during every agent reply — use a **partial** edit lock
  instead (see [Agent editing lease](#agent-editing-lease)); optional strict mode later.

## Current state

**Implemented (scaffolding):**

- [`ConnectEd/ai/`](../ConnectEd/ai/) — `types`, `AiDriver`, `AiChatSession`,
  `register_provider` / `create_provider`, `DummyProvider` (`nobodyHome()` tool).
- [`ConnectEd/widgets/window/ai_chat/`](../ConnectEd/widgets/window/ai_chat/) —
  `AiChatDock`, `AiChatWidget` (`QTextBrowser` history with links, input, Send).
- **Welcome** — [`ConnectEd/ai/welcome.py`](../ConnectEd/ai/welcome.py) on new chat;
  **AI Settings** stub dialog + `connected://ai/settings` link.
- **Settings** — `ai/` section in [`FACTORY_SETTINGS`](../ConnectEd/core/settings.py);
  default provider `"dummy"`.
- **Window** — `AiChatManager`; one default chat on startup; bottom split (log tabs left, AI right).
- **AI menu** — New Chat, dynamic open-chat list, Settings; `windowAiChat` removed.
- **Tests** — unit tests for dummy provider; `MAIN_WIDGETS["AI Chat"]` in
  [`specs.py`](../tests/integration/gui/specs.py).

**Not yet implemented:**

- Real HTTP providers, `ContextBuilder`, read/write tools beyond `nobodyHome()`.
- **`AiEditLock`** — exclusive lease + partial UI lock for multi-chat safety.
- Optional `[ai]` deps in `pyproject.toml`.

**Existing infrastructure to build on:**

- **Scripting stack** — [`doc/SCRIPTING.md`](SCRIPTING.md):
  - `cs.gui(window)` → `GuiDriver` (menus, modals, mouse, docks).
  - `view.ui.*` — Place / Edit / View on active MDI subwindow.
  - Scene API — `addItems`, `editMove`, diagram APIs with `undoable=True`.
- **Command trees are manual** — [`tests/integration/gui/specs.py`](../tests/integration/gui/specs.py)
  (`MAIN_WIDGETS`, `MENUS_*`); no runtime introspection registry.

## Architecture

```mermaid
flowchart TB
  User[User message]
  AiMenu[AI menu]
  Manager[AiChatManager]
  ChatDock[AiChatDock]
  Session[AiChatSession]
  Lock[AiEditLock]
  Provider[AiProvider adapter]
  Driver[AiDriver tools]
  App[Window / view.ui / scene API]

  AiMenu -->|New Chat / focus| Manager
  Manager --> ChatDock
  User --> ChatDock --> Session
  Session -->|acquire / release| Lock
  Lock -->|blocks other sessions + edits| Session
  Session --> Provider
  Session --> Driver
  Lock --> Driver
  Driver --> App
  Driver --> Session
  Provider --> Session
  Context[ContextBuilder] --> Session
  App --> Context
```

| Layer | Responsibility |
|-------|----------------|
| **AiChatManager** | Owns open `AiChatDock` instances; create, focus, title, menu list |
| **AiChatDock** | Qt UI shell: history, input, send/stop, provider/model indicator, errors |
| **AiChatSession** | Per-dock message list, system prompt, tool-call loop, streaming |
| **AiEditLock** | Exclusive editing lease; partial UI lock while a session runs write-capable agent loop |
| **AiProvider** | HTTP/SDK to OpenAI, Anthropic, Ollama, etc.; tools + streaming |
| **ContextBuilder** | Active document, selection, scene/net summary for prompts |
| **AiDriver** | Registered tools; maps tool calls → scripting/scene/view calls |
| **Command catalog** | Terse tool/menu documentation for system prompt |
| **Recipes** | Curated prompt + context starters (menu actions, not tool replay) |

**Design rule:** the model **never** drives raw `QTest` mouse directly in v1.
It calls **named tools** with structured arguments. Mouse-based placement stays
inside tool implementations (or future placement tools) where drag threshold and
modal handling are handled deliberately.

## Menu: top-level **AI** (not under Window)

Use a dedicated **AI** menu bar entry. Do **not** nest AI under **Window** —
Window already lists fixed docks and dynamic MDI documents; AI has its own
lifecycle (new chat, recipes, settings).

### Structure

```
AI
  New Chat
  ─────────
  AI Chat          ← dynamic: one entry per open dock (show/raise)
  AI Chat 2
  ─────────
  Recipes          ← submenu; stage later
    HDL → Diagram
    …
  ─────────
  Settings…
```

| Item | Behaviour |
|------|-----------|
| **New Chat** | `AiChatManager.newChat()` — create dock, focus, update menu |
| **Open chats** | Rebuilt by `updateAiMenu()` (same pattern as MDI list in `updateWindowMenu()`) |
| **Recipes** | Open/focus chat, pre-fill prompt + context; optional auto-send (see [Recipes](#recipes)) |
| **Settings…** | Stub → prefs dialog writing `ai/*` settings |

**Window menu** keeps Navigator, Messages, Transcript, Log only. Remove
`windowAiChat` once the AI menu is wired. Optional later: **Window → Focus AI
Chat** that raises the most recently used chat (single shortcut only; no duplicate
list).

**Integration tests:** extend `MENUS_*` in [`specs.py`](../tests/integration/gui/specs.py)
with an `"AI"` menu tree; adjust `MAIN_WIDGETS` for multi-dock (see below).

## Multiple chat docks

Today `Window` holds a single `_ai_chat_dock`. Refactor to **`AiChatManager`**
(owned by `Window` or co-located under `widgets/window/ai_chat/`):

- **`newChat() -> AiChatDock`** — allocate id, default title (`"AI Chat"`,
  `"AI Chat 2"`, …), create session, add dock to bottom-right pane.
- **`chats() -> list[AiChatDock]`** — for menu and scripting.
- **`focusChat(dock)`** — show, raise, optionally tabify among AI docks only.
- **`closeChat(dock)`** — on dock close: remove from list, update AI menu.
- **Titles** — start numeric; later: first user message snippet or user rename.

Each **`AiChatWidget`** owns one **`AiChatSession`** (already the case). Sessions
do not share history.

### Dock layout

**Resolved** — bottom horizontal split:

| Region | Docks |
|--------|--------|
| **Bottom left** | Messages, Transcript, Log (tabbed together) |
| **Bottom right** | One or more **AI Chat** docks (tabbed with each other, **not** with Messages/Transcript/Log) |

Setup order in [`Window`](../ConnectEd/widgets/window/__init__.py) matters for Qt:

1. Add Messages to bottom.
2. Add first AI Chat to bottom; `splitDockWidget(messages, aiChat, Horizontal)`.
3. Add Transcript and Log; tabify with Messages only.
4. Further AI chats: add to bottom-right area; tabify with existing AI docks.

Saved window geometry (`startup/geometry`) can restore an old tab arrangement;
users may need to reset layout once after dock changes.

## Agent editing lease

With **multiple chat docks**, each `AiChatSession` has its own history, but
**`AiDriver` shares one window** — one active MDI view, one scene, one undo stack.
Without coordination, two agent loops (or user edits interleaved with AI tools)
can corrupt state.

### Exclusive lease (lock / unlock)

Introduce **`AiEditLock`** (on [`Window`](../ConnectEd/widgets/window/__init__.py)
or owned by `AiChatManager`):

```python
class AiEditLock(QObject):
    lockChanged = pyqtSignal()

    def holder(self) -> AiChatSession | None: ...
    def isLocked(self) -> bool: ...
    def acquire(self, session : AiChatSession) -> bool: ...
    def release(self, session : AiChatSession) -> None: ...
```

**Bracket** each agent run that may mutate the diagram:

```
send() → acquire(session) → tool loop → release(session)   # always in finally
```

| Rule | Behaviour |
|------|-----------|
| **Holder** | Only the session that acquired the lease may invoke **write** tools |
| **Other chats** | **Send** disabled or rejected with “Chat N is editing…”; read-only tools optional |
| **User manual edits** | Blocked on the active scene while lease held (partial UI lock) |
| **Stop / Cancel** | Aborts provider + **releases** lease in `finally` |
| **Close chat dock** | If holder, **release** on destroy |
| **Failure** | `release` in `finally` — never leave the app locked |

Read-only tools (`get_selection_summary`, `list_commands`, …) may run **without**
the lease, or concurrently while another chat holds it — default: **read-only without
lease**, **write requires lease**.

Write tools (`edit_delete`, `scene_add_items`, `run_menu_action`, …) **must**
check `AiEditLock` before executing (defence in depth).

### Partial UI lock (not a full modal)

Do **not** freeze the entire application for every assistant reply. While the lease
is held:

| Block | Allow |
|-------|--------|
| Scene mouse edits, Edit menu mutations, Place menu | View pan / zoom |
| Other chats’ **Send** (and write agent loops) | **Stop** on the holding chat |
| Destructive menu actions on the active design | Messages, Navigator browse, log docks |
| | Typing in other chat inputs (Send still blocked) |

Optional later setting **`ai/strict_agent_lock`** — also disable pan/zoom during
write loops (off by default).

### User-visible state

- Holding dock title or banner: **`Editing…`** (in addition to `[provider]` suffix).
- Other docks: grey **Send**, tooltip explaining which chat holds the lease.
- Optional status bar: `AI: Chat 2 editing`.

Connect `AiEditLock.lockChanged` → refresh all `AiChatWidget` send buttons and
menu sensitivity.

### Phasing

| Stage | Lease scope |
|-------|-------------|
| **§3.5 skeleton** | `AiEditLock` type, acquire/release in `AiChatSession.send()`; UI hints optional |
| **§5 read-only agent** | Lease bracketing validated; read tools run without blocking other chats |
| **§6 write tools** | **Required** — write tools refuse without lease; partial UI lock enforced |
| **§8 polish** | Stop/cancel releases lease; integration test: Chat A blocks Chat B **Send** |

### Rejected alternatives

- **No lock** — unsafe once write tools exist.
- **Global tool queue** — Chat B silently waits; confusing UX.
- **Single “active agent chat”** — defeats multi-chat for parallel Q&A (read-only).

## Recipes

**Recipes** (UI label; not “macros”) are **curated workflows** — not recorded UI
automation. Each recipe:

- Opens or focuses a chat (usually **New Chat** with a recipe-specific system appendix).
- Pre-fills user input and/or injects context (selection, active design, clipboard).
- May restrict tools (e.g. read-only pass before write tools for HDL → diagram).

Example entries (later):

| Recipe | Intent |
|--------|--------|
| **HDL → Diagram** | Parse HDL snippet into blocks/nets via write tools |
| **Explain selection** | Read-only context + summary |
| **Document netlist** | `get_netlist_summary` + narrative |

Implement in [`ConnectEd/ai/recipes.py`](../ConnectEd/ai/recipes.py); menu
built from a registry (similar to `register_provider`).

## Providers

### Pluggable adapter

```python
class AiProvider(Protocol):
    def chat(
        self,
        messages : list[ChatMessage],
        tools    : list[ToolDefinition],
    ) -> Iterator[ChatEvent]: ...  # tokens, tool_calls, done, error
```

Each adapter maps ConnectEd’s tool JSON schema to the provider’s function-calling
format (OpenAI `tools`, Anthropic `tool_use`, etc.).

### Implemented

| Provider key | Notes |
|--------------|--------|
| `dummy` | Default for new installs; **getting-started welcome** (no API key); optional `nobodyHome()` demo on user send (see [Dummy provider](#dummy-provider-getting-started)) |

### Planned adapters

| Provider key | Notes |
|--------------|--------|
| `openai` | Official OpenAI API |
| `openai_compatible` | Ollama, LM Studio, Azure-style; `base_url` + `api_key` optional |
| `anthropic` | Claude API |
| `xai` | xAI Grok API (official REST; models e.g. `grok-3`, `grok-2`) |
| `ollama` | Convenience wrapper defaulting to `http://localhost:11434` |
| `not_configured` | User-facing message when provider/key missing |

Add others (Gemini, etc.) behind the same interface. Optional later: [LiteLLM](https://github.com/BerriAI/litellm)
as a single backend for many providers — weigh dependency cost vs thin `httpx`
adapters per vendor.

### Composer 2.5

**Composer 2.5 is Cursor’s in-IDE model**, not a public API ConnectEd can call
today. The plan is:

- Build a **provider-agnostic** agent loop (chat + tools + context).
- Document that a future **Cursor/Composer adapter** could plug in if Cursor
  exposes a supported API.
- Do **not** block v1 on Composer branding; use OpenAI-compatible or Ollama for
  development and user choice.

For evaluation without paid API access, prefer **Ollama** (local) or vendors’
**official free API tiers** where available — not consumer web chat products.

### Provider registry

Grok’s `register_driver` / `get_driver` pattern applies to **LLM backends only**:

```python
# ConnectEd/ai/providers/__init__.py
_providers : dict[str, type[AiProvider]] = {}

def register_provider(name: str, cls: type[AiProvider]) -> None:
    _providers[name] = cls

def create_provider(name: str, **kwargs) -> AiProvider: ...
```

Each module (`dummy.py`, `openai.py`, `xai.py`, …) calls `register_provider` at
import time. Settings `ai/provider` selects the implementation. **Do not** conflate
this with GUI tool execution (see [Naming](#naming-ai-provider-vs-ai-driver)).

### Dummy provider (getting started)

Keep **`dummy`** as the factory default in settings so ConnectEd works out of the
box without API keys. It is not a stand-in for a real model — it orients the user
toward configuration and evaluation options.

**On new chat** (first paint, before the user sends anything), show a static
**welcome** assistant message. Suggested content:

- ConnectEd AI is not configured yet; choose a provider under **AI → Settings…**
- **Local, no key:** [Ollama](https://ollama.com/) — install, pull a model, set
  `ai/provider` to `ollama` and `base_url` to `http://localhost:11434`
- **Cloud (official APIs only):** sign up and create an API key — e.g.
  [OpenAI](https://platform.openai.com/),
  [Anthropic](https://console.anthropic.com/),
  [xAI](https://console.x.ai/) — then set provider, model, and key in Settings
- **Eval / free tier:** note vendor trial credits where they exist (wording kept
  generic; link to vendor docs — tiers change often)
- Link to this plan or in-app help when available

Implementation options (pick one in code):

| Approach | Pros |
|----------|------|
| **`ConnectEd/ai/welcome.py`** template rendered into chat on `newChat()` | Single source of truth; easy to localize later |
| **`DummyProvider.welcome()`** static text/HTML returned to widget | Keeps “dummy” self-contained |

After welcome, **user messages** while still on `dummy`:

- **Option A (friendly):** reply with short “configure Settings” text; no tool call.
- **Option B (dev demo):** keep current `nobodyHome()` tool loop to exercise the agent stack.

Product default: **welcome + Option A**; retain Option B behind a dev flag or first
user message containing `"demo"` if we still want a smoke test.

When the user switches to a real provider in Settings, new sessions use that
provider; existing chat history stays on whatever provider created it (or show a
read-only banner if provider changed mid-chat — defer).

## Naming: `AiProvider` vs `AiDriver`

External suggestions often use one **`AIDriver`** for both the LLM client and GUI
actions. This plan **splits** them deliberately:

| Name | Role | Grok analogue |
|------|------|----------------|
| **`AiProvider`** | HTTP/SDK to the LLM; streaming; native **tool/function calling** | `GrokDriver.chat()` |
| **`AiDriver`** | Executes ConnectEd **tools** on the GUI thread (`scene`, `view.ui`, menus) | `_execute_actions()` |
| **`AiChatSession`** | Message history, agent loop, connects provider ↔ driver; acquires/releases lease | `send_message()` orchestration |
| **`AiChatManager`** | Multiple docks, menu list, focus/new/close | — |
| **`AiEditLock`** | Exclusive editing lease; partial UI lock while write agent runs | — |
| **`ContextBuilder`** | Terse diagram snapshot for prompts | `_build_context()` |

Grok’s `AIResponse` with `text` + `actions: list[dict]` is a valid **fallback**
when a provider lacks tool calling: parse JSON from assistant text. **Prefer**
native tool calls where supported (OpenAI, Anthropic, xAI); keep JSON-action
parsing as optional fallback only.

Example action dict (fallback schema, aligned with tool names):

```python
{"action": "place_rectangle", "params": {"x1": 0, "y1": 0, "x2": 100, "y2": 50}}
```

Catalog tools use **snake_case** names matching `view.ui` / scene API where
possible (`place_rectangle`, `add_block`, `connect`, …).

## Review: Grok suggestions (May 2025)

Independent review of a Grok-generated outline. **Adopt** what fits ConnectEd;
**reject or correct** what conflicts with project rules or this plan.

### Adopted

- **AI chat dock** — same [`Window`](../ConnectEd/widgets/window/__init__.py) dock wiring pattern as Messages/Transcript.
- **Configurable multi-provider** stack — OpenAI, Anthropic, **xAI/Grok**, Ollama; API keys in settings.
- **Terse command/context schema** for the LLM — symbols, selection, available commands (tool catalog).
- **Structured actions** — undoable via existing `QUndoCommand` / `undoable=True` scene paths.
- **Provider registry** for LLM backends (see above).
- **Security** — never log API keys; optional local models.
- **Streaming** responses where the API supports it.
- **Reuse scripting** — `cs.gui(window)`, `view.ui.*`, scene API for tool implementations.
- **Project style** — PyQt6, `@checked`, `| None`, mixins; optional `[ai]` deps in `pyproject.toml`.

### Corrected (Grok sample code issues)

| Grok sample | ConnectEd plan |
|-------------|----------------|
| `AIChatDock(QWidget)` | **`QDockWidget`** subclass (like [`NavigatorDock`](../ConnectEd/widgets/window/navigator/__init__.py)), inner `AiChatWidget` |
| `window()` inside chat widget | Pass **`Window`** / active view into `ContextBuilder`; avoid global `window()` from widget code |
| Single `AIDriver.chat(prompt, context)` | **`AiChatSession`** + **`AiProvider`** tool loop + **`AiDriver`** per tool |
| AI under Window menu | **Top-level AI menu**; Window lists MDI docs + log docks only |
| Single chat instance | **`AiChatManager`** — multiple docks, dynamic menu list |
| `requests` in driver | Prefer **`httpx`** (async-friendly) in optional `[ai]` extra |
| Broad `except Exception` in UI | Log via `logger()`; show user-safe message in chat |
| Config-only in dock | Persist **`ai/*` in settings**; **Settings…** on AI menu (dock may show read-only provider label) |
| “All on dev branch” | Branch policy is team choice; plan is branch-agnostic |

### Rejected (already in non-goals)

- **Web chat / free-tier browser** — ToS; official APIs or Ollama only.
- **Composer 2.5 in-app** — no public embeddable API.

### Module layout

```
ConnectEd/ai/
  __init__.py          # types, public exports
  types.py             # ChatMessage, ToolDefinition, ChatEvent, …
  session.py           # AiChatSession (acquire/release lease around send)
  lock.py              # AiEditLock — exclusive editing lease + lockChanged
  context.py           # ContextBuilder
  catalog.py           # command / tool descriptions (+ read vs write tool metadata)
  driver.py            # AiDriver tool implementations (GUI thread; checks lease for writes)
  recipes.py           # recipe registry + handlers (later)
  providers/
    __init__.py        # register_provider, create_provider
    dummy.py           # scaffolding provider
    openai_compatible.py
    anthropic.py
    xai.py
    ollama.py
ConnectEd/widgets/window/ai_chat/
  __init__.py          # exports
  dock.py              # AiChatDock
  widget.py            # AiChatWidget (Send enabled from AiEditLock)
  manager.py           # AiChatManager (multi-dock)
```

When implementation starts, add to [`TODO.md`](../TODO.md): “AI chat — see [`doc/AI_CHAT.md`](AI_CHAT.md)”.

## Settings (`ai/`)

Extend [`FACTORY_SETTINGS`](../ConnectEd/core/settings.py):

```python
"ai" : {
    "provider"            : "dummy",             # str — dev default; production: openai_compatible / ollama
    "api_key"             : "",                  # str — never log in debug
    "model"               : "",                  # str
    "base_url"            : "",                  # str — Ollama / proxy
    "system_prompt_extra" : "",                  # str — user appendix
    "confirm_destructive" : True,                # bool — delete etc.
    "max_tool_rounds"     : 10,                  # int — agent loop cap
    "strict_agent_lock"   : False,                # bool — also block pan/zoom during write loop
}
```

Access: `settings().get("ai/provider")`, `settings().set("ai/api_key", ...)`.

**Security:** QSettings is user-scoped, not encrypted by default; document that
users should use env-specific keys and local-only providers when possible.

Optional later: per-provider sub-keys (`ai/openai/model`, …) if one global model
field is too limiting.

## AI driver (tools)

New package [`ConnectEd/ai/`](../ConnectEd/ai/) — see [module layout](#module-layout).

### Implemented

| Tool | Returns |
|------|---------|
| `nobodyHome` | `{"ok": true, "message": "Nobody home."}` — scaffolding only |

### Context tools (read-only) — stage 5

No **`AiEditLock`** required (may run while another chat holds the lease).

| Tool | Returns |
|------|---------|
| `get_active_document` | Design name, path, dirty flag, subwindow type |
| `get_selection_summary` | Selected item types, ids/uuids, key properties |
| `get_scene_summary` | Item counts by type, sheet rect, grid snap state |
| `get_netlist_summary` | Named nets / subnets (when netlist available) |
| `list_commands` | Subset of command catalog (filter by prefix) |

### Action tools (write) — stage 6+

**Require** holder of **`AiEditLock`**; return structured error JSON if called without lease.

| Tool | Delegates to |
|------|----------------|
| `run_menu_action` | `MenuBar` path → `Action.trigger()` + `withModal` where needed |
| `place_rectangle`, `place_line`, … | `view.ui.place*` + optional `mouseDrag` helper |
| `edit_delete`, `edit_undo`, `edit_redo` | `view.ui.edit*` |
| `edit_item_properties` | Properties API / dialog automation (harder; defer) |
| `scene_add_items` | `scene.addItems(..., undoable=True)` |
| `scene_edit_move` | `scene.editMove(...)` |
| `file_new_design`, `file_save` | Menu or model API |

Each tool returns structured JSON:

```python
{"ok": True, "summary": "Added rectangle at ...", "error": None}
```

**Undo:** prefer scene/view paths with `undoable=True`. Surface undo hints in
tool results (“user can Edit → Undo”).

**Destructive ops:** when `ai/confirm_destructive`, show inline confirm in chat
UI or modal before executing `edit_delete` and similar.

### Command catalog

Maintain [`ConnectEd/ai/catalog.py`](../ConnectEd/ai/catalog.py) (or generate from
specs):

- Terse one-liners per menu action and major `view.ui` method.
- Parameters: coordinates in **scene space**, grid snap behaviour, modal side
  effects.
- Injected into system prompt; `list_commands` tool for on-demand lookup.

Long-term: generate from [`tests/integration/gui/specs.py`](../tests/integration/gui/specs.py)
and view UI docstrings to reduce drift.

### System prompt (sketch)

- Role: ConnectEd diagram assistant.
- Rules: use tools only; scene coordinates; respect grid; confirm destructive
  actions; prefer undoable scene API over menu when both exist.
- Append `settings().get("ai/system_prompt_extra")`.
- Include compact catalog (or instruct model to call `list_commands` first).

## Chat dock UI

Follow existing dock pattern ([`widgets/window/__init__.py`](../ConnectEd/widgets/window/__init__.py)):

| Piece | Approach |
|-------|----------|
| Widget | `AiChatWidget` in [`widgets/window/ai_chat/`](../ConnectEd/widgets/window/ai_chat/) |
| Dock | `AiChatDock(QDockWidget)`; title `"AI Chat"`, `"AI Chat 2"`, … |
| Manager | `AiChatManager` — create/focus/close; feeds **AI** menu |
| Placement | Bottom **right**; split from Messages/Transcript/Log on bottom **left** |
| Menu | **AI → New Chat** + dynamic open-chat list; **not** Window → AI Chat |
| Tests | `MENUS_*` AI tree; `MAIN_WIDGETS` — at least one chat dock or manager accessor |
| Scripting | Export `AiChatDock`, manager API from [`ConnectEd/scripting/`](../ConnectEd/scripting/) if needed |

UI behaviour:

- Send on Enter (Shift+Enter newline when input becomes multiline).
- Stop button cancels in-flight HTTP (provider-dependent).
- Show streaming tokens; distinguish user / assistant / tool / error blocks.
- Optional: copy transcript to Transcript dock.

Settings access: **AI → Settings…** (primary); dock may show read-only provider
label until prefs exist.

### Hyperlinks and rich text

**Today:** the chat history uses `QPlainTextEdit` — **plain text only**; URLs are
not clickable.

**Planned:** migrate the history pane to **`QTextBrowser`** (or read-only
`QTextEdit`) with a constrained rich-text subset:

| Link type | Example | Action |
|-----------|---------|--------|
| **External** | `https://ollama.com/` | `QDesktopServices.openUrl` in the system browser; **https** (and optionally `http`) only |
| **In-app** | `connected://ai/settings` | Open **AI → Settings…** dialog (custom URL scheme handled in `anchorClicked`) |

Rendering rules:

- **Welcome / system messages:** authored HTML or Markdown → HTML from templates
  (`welcome.py`); may include links freely.
- **Assistant streaming:** prefer **Markdown → HTML** with a safe subset (links,
  `**bold**`, `` `code` ``, fenced blocks); do not inject raw model HTML until
  sanitization exists.
- **User messages:** plain text escaped; optional auto-linkify of pasted `https://`
  URLs.
- **Tool / error blocks:** monospace plain text or `<pre>`; no clickable links unless
  explicitly generated by ConnectEd.

Security: never load remote images or scripts; block `javascript:` and non-http(s)
schemes except `connected://`. Log opened external URLs at debug level only.

Optional later: copy-as-Markdown, export transcript with links preserved.

## Dependencies

Add optional dependency group in [`pyproject.toml`](../pyproject.toml), e.g.
`[project.optional-dependencies] ai = ["httpx", ...]` so core install stays lean.

Avoid heavy SDKs if `httpx` + JSON suffices for OpenAI-compatible and Anthropic
REST.

## Threading / Qt

- Network I/O off the GUI thread (`QThread` + signals or `QNetworkAccessManager`).
- Tool execution **on GUI thread** (Qt widgets, scene mutations).
- Session orchestrates: await provider chunk → on tool_call →
  `QMetaObject.invokeMethod` / signal to main thread → post tool result → continue.
- **`AiEditLock`** is main-thread only; `acquire` / `release` in `AiChatSession.send()`
  `try` / `finally` around the full tool loop (including provider streaming waits).

## TODO checklist

Work in order unless noted.

### 1. Plan and scaffolding

- [x] Create `ConnectEd/ai/` package (`types`, `ChatMessage`, `ToolDefinition`, `ChatEvent`).
- [x] `register_provider` / `create_provider` registry in `ai/providers/`.
- [x] `DummyProvider` + `nobodyHome()` tool on `AiDriver`.
- [x] `AiChatSession` minimal tool loop.
- [x] Add `ai/` section to `FACTORY_SETTINGS` (default provider `dummy`).
- [ ] Add optional `[ai]` deps to `pyproject.toml`; document in README or dev notes.
- [ ] Stub `AiProvider` protocol + `NotConfiguredProvider` that explains missing key.

### 2. Chat dock (single instance — done)

- [x] `AiChatWidget` — message list, input, Send.
- [x] `AiChatDock` — `WINDOW_TITLE = "AI Chat"`.
- [x] Wire in `Window`: dock, bottom split (log tabs left, AI right).
- [x] `windowAiChat` action + Window menu entry (temporary; **removed** in §3).
- [x] `MAIN_WIDGETS["AI Chat"]` in `specs.py`.
- [x] Dummy backend: user message → `nobodyHome()` → assistant reply (dev demo).
- [x] Getting-started **welcome** on new chat (`welcome.py`).
- [x] Rich history pane + hyperlink handling (`QTextBrowser`, `connected://ai/settings`, https).
- [ ] **AI → Settings…** menu entry (stub dialog exists; menu wiring in §3). — **done** in §3 (`aiSettings` action).

### 3. Multi-chat + AI menu

- [x] `AiChatManager` on `Window` — `newChat()`, `chats()`, focus, close handling.
- [x] Tabify multiple AI docks together (never with Messages/Transcript/Log).
- [x] Top-level **AI** menu: New Chat, dynamic open-chat list, Settings… (stub).
- [x] `updateAiMenu()` — rebuild open-chat section (mirror `updateWindowMenu()`).
- [x] Remove `windowAiChat` from Window menu and actions/slots.
- [x] Update `MENUS_*` / `MAIN_WIDGETS` in `specs.py` for AI menu + multi-dock.
- [x] One default chat on startup (current behaviour).

### 3.5 Agent editing lease

- [ ] `ConnectEd/ai/lock.py` — `AiEditLock` on `Window` (`holder`, `acquire`, `release`, `lockChanged`).
- [ ] `AiChatSession.send()` — acquire at start, `release` in `finally`; reject second session if busy.
- [ ] `AiChatWidget` — disable **Send** on non-holders when locked; optional `Editing…` title suffix.
- [ ] `AiDriver.call()` — stub check: write tools list empty for now; hook ready for §6.
- [ ] Unit test: acquire/release, second session rejected, release on session destroy.

### 4. Provider layer + settings UI

- [ ] `OpenAiCompatibleProvider` — chat completions + tools via `httpx`, streaming.
- [ ] `XaiProvider` — xAI Grok API (`ai/provider` = `xai`).
- [ ] `AnthropicProvider` (optional in same stage or next).
- [ ] `OllamaProvider` as thin `openai_compatible` preset (`base_url`, no key).
- [ ] `NotConfiguredProvider` when key/model missing.
- [ ] **AI → Settings…** menu entry — **done** in §3; extend dialog in §4.
- [ ] In-app link `connected://ai/settings` from welcome message — **done** in widget.
- [ ] Read `ai/*` before send; user-visible errors in dock.

### 5. Session + read-only agent

- [ ] `ContextBuilder` — active MDI widget, selection, scene summary.
- [ ] Register read-only tools; extend session system prompt assembly.
- [ ] Streaming assistant text into dock.
- [ ] Lease acquired during send but read-only tools do not require exclusive write access.
- [ ] Manual test: “what is selected?”, “how many rectangles?” without mutating scene.

### 6. Write tools + safety

- [ ] Expand `AiDriver` — `cs.gui(window)` + active `view.ui` / `scene`.
- [ ] **Enforce `AiEditLock`** on all write tools; partial UI lock (block Edit/Place/scene input).
- [ ] Low-risk write tools: `edit_undo`, `edit_redo`, `view_zoom_all`.
- [ ] Placement tools via scene API where possible before mouse.
- [ ] `run_menu_action` for catalogued paths; `withModal` wrapper.
- [ ] Destructive confirm gate (`ai/confirm_destructive`).
- [ ] `catalog.py` v1 — hand-maintained list aligned with `MENUS_BASE` + `view.ui`.
- [ ] Optional JSON-action fallback for providers without native tool calling.

### 7. Recipes

- [ ] `recipes.py` registry + `register_recipe`.
- [ ] **AI → Recipes** submenu; first recipe stub (e.g. “Explain selection”).
- [ ] HDL → Diagram recipe when write tools exist.

### 8. Polish and docs

- [ ] Stop/cancel in-flight requests; **must release `AiEditLock`**.
- [ ] Transcript export (optional).
- [ ] Unit tests for catalog, context builder, provider request shaping (mock HTTP).
- [ ] Integration test: scripted provider mock → tool call → scene change.
- [ ] Integration test: Chat A holds lease → Chat B **Send** blocked until release.
- [ ] Update [`SCRIPTING.md`](SCRIPTING.md) — “AI agent tools” cross-link.
- [ ] User-facing note: supported providers, no Composer API, API key storage.

## Implementation order (summary)

1. §1 Scaffolding — **done** (dummy provider, session, settings).
2. §2 Single chat dock — **done** (bottom-right split).
3. §3 Multi-chat + AI menu — **done**.
4. **§3.5 Agent editing lease** — next (before write tools).
5. §4 Real providers + Settings dialog.
6. §5 Read-only agent (context + tools + streaming).
7. §6 Write tools, catalog, safety (**lease enforced**).
8. §7 Recipes.
9. §8 Polish, tests, docs.

## Open questions

- **Default on startup:** one empty chat dock vs none until **New Chat**? — **one chat** (§3 done).
- **Multi-chat contention:** exclusive **`AiEditLock`** + partial UI lock (see [Agent editing lease](#agent-editing-lease)).
- **Strict agent lock:** block pan/zoom during write loops (`ai/strict_agent_lock`)?
- **First production default provider:** Ollama (local, no key) vs OpenAI-compatible cloud?
- **Approval UX:** inline chat “Allow delete?” vs modal?
- **Diagram-only tools:** refuse or no-op when active subwindow is spreadsheet/symbol?
- **Catalog maintenance:** hand-written vs generated from specs in CI?
- **Chat titles:** numeric only vs first-message snippet vs explicit rename?
- **Persist chat history** across app restarts (currently out of scope)?
- **Dummy user replies:** drop `nobodyHome()` demo entirely vs keep behind dev flag?

## Related docs

- [`SCRIPTING.md`](SCRIPTING.md) — GUI driver, mouse, modals, CLI mode.
- [`tests/integration/gui/specs.py`](../tests/integration/gui/specs.py) — menu/widget specs for catalog alignment.
- [`NET_LABEL.md`](NET_LABEL.md) — example of phased feature plan in this repo.
