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

---

## Phase 2: Naming Refactor (camelCase → snake_case) — COMPLETE (steps 1-5)

All 1320 naming violations resolved across the entire codebase. Renamed functions, methods, arguments, local variables, class attributes, and global variables from camelCase to snake_case.

### Steps 1-5: COMPLETE

- **N802** (467): All function/method names renamed
- **N803** (184): All argument names renamed
- **N806** (510): All local variable names renamed
- **N815** (131): All class-scope variable names renamed
- **N816** (28): All global-scope variable names renamed

Rules N802, N803, N806, N815, N816 are now **enforced** in `pyproject.toml`.

### 6. Module and directory renames (`N999`, `N812`, `N813`) — COMPLETE

Renamed all camelCase directories, `.py` files, and `.json` files to snake_case. Updated all imports (79 files renamed, 17 directories renamed, 74+ files with import updates). Also fixed 6 remaining N812 violations (camelCase import aliases like `meActions` → `me_actions`).

- [x] `controllerCoupler/` → `controller_coupler/`
- [x] `controllerManager/` → `controller_manager/`
- [x] `musicEngine/` → `music_engine/`
- [x] `musicEngine/chordEngine/` → `chord_engine/`
- [x] `musicEngine/chordEngine/externalChordEngine/` → `external_chord_engine/`
- [x] `musicEngine/chordEngine/internalChordEngine/` → `internal_chord_engine/`
- [x] `musicEngine/rhythmEngine/` → `rhythm_engine/`
- [x] All camelCase `.py` filenames (e.g., `appParameter.py` → `app_parameter.py`)
- [x] Update `pyproject.toml` isort `known-first-party` list
- [x] Update `CLAUDE.md` references
- [x] Remove N812, N813, N999 from ruff ignore list
- [x] Fix hardcoded file paths in `constants.py`
- [x] Fix N812 import alias violations (`ccActions`, `meActions`, `m21Chord`)
