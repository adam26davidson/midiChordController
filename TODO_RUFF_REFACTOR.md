# Ruff Refactor TODO

Tracking remaining code quality warnings and the naming refactor. Rules are currently configured in `pyproject.toml`.

## Phase 1: Code Quality Fixes — COMPLETE

All 114 warnings resolved. Summary of what was done:

- **SIM118** (29): Removed `.keys()` from dict membership checks
- **E701/E702** (19): Split one-liners onto separate lines
- **RUF013** (13): Added explicit `| None` to optional parameters
- **SIM102** (5): Merged collapsible nested `if` statements
- **RET503** (5): Added explicit `return None` at end of mixed-return functions
- **PT009** (5): Replaced unittest-style assertions with plain `assert`
- **C416** (4): Replaced `[x for x in it]` with `list(it)`
- **SIM115** (4): Wrapped `open()` in `with` statements (1 suppressed — long-lived file handle)
- **B007** (3): Renamed unused loop variables to `_`
- **RUF005** (2): Used `[x, *y]` instead of `[x] + y`
- **RUF046** (2): Removed unnecessary `int()` casts
- **SIM103** (1): Returned condition directly
- **SIM110** (1): Used `all()` instead of for loop
- **B018** (1): Fixed missing `()` on function call (was a bug!)
- **N805** (1): Fixed first method argument name to `self`
- **B024/B027** (1): Added `@abstractmethod` to ABC method
- **TC001** (1): Moved import into `TYPE_CHECKING` block

Suppressed globally in `pyproject.toml` (intentional patterns, not worth changing):
- **E402**: Test files with `sys.path` manipulation before imports
- **RUF006**: Fire-and-forget `asyncio.ensure_future` tasks
- **TC001**: Moving runtime imports to `TYPE_CHECKING` can break things

---

## Phase 2: Naming Refactor (camelCase → snake_case)

These rules are currently **ignored** in `pyproject.toml`. Remove them from the ignore list as each phase is completed.

### 1. Function and method names (`N802`)

Rename all camelCase methods to snake_case. This is the largest change — 50+ methods across the codebase. Every call site must be updated too.

**Approach**: Do one module at a time and update all callers before moving on.

- [ ] `models/` — `appParameter.py`, `command.py`, etc.
- [ ] `controllerManager/` — `controller.py`, models
- [ ] `controllerCoupler/` — `__init__.py`, models
- [ ] `musicEngine/chordEngine/` — base class, both engines, all modules
- [ ] `musicEngine/midi/` — MIDI I/O
- [ ] `musicEngine/rhythmEngine/` — rhythm engine
- [ ] `display/` — all display components
- [ ] `redux/` — reducers, utils
- [ ] `test/` — test files

### 2. Function argument names (`N803`)

Rename camelCase function parameters to snake_case. Often done alongside N802.

- [ ] All files (same module-by-module order as above)

### 3. Variable names in functions (`N806`)

Rename camelCase local variables to snake_case.

- [ ] All files (same module-by-module order as above)

### 4. Class-scope variable names (`N815`)

Rename camelCase instance/class attributes to snake_case.

- [ ] All files (same module-by-module order as above)

### 5. Global-scope variable names (`N816`)

Rename camelCase module-level variables to snake_case.

- [ ] All files

### 6. Module and directory renames (`N999`, `N812`, `N813`)

Rename camelCase directories and files to snake_case. This requires updating every import in the project.

**Do this last** — it touches every file and is easiest once all other naming is settled.

- [ ] `controllerCoupler/` → `controller_coupler/`
- [ ] `controllerManager/` → `controller_manager/`
- [ ] `musicEngine/` → `music_engine/`
- [ ] `musicEngine/chordEngine/` → `chord_engine/`
- [ ] `musicEngine/chordEngine/externalChordEngine/` → `external_chord_engine/`
- [ ] `musicEngine/chordEngine/internalChordEngine/` → `internal_chord_engine/`
- [ ] `musicEngine/rhythmEngine/` → `rhythm_engine/`
- [ ] All camelCase `.py` filenames (e.g., `appParameter.py` → `app_parameter.py`)
- [ ] Update `pyproject.toml` isort `known-first-party` list
- [ ] Update `CLAUDE.md` references
- [ ] Remove N812, N813, N999 from ruff ignore list
