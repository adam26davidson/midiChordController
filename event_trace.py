from __future__ import annotations

import time

TRACE_ENABLED: bool = False
_start_time: float = time.time()

def _ts() -> str:
    return f"{time.time() - _start_time:.3f}"

def trace(stage: str, msg: str) -> None:
    if not TRACE_ENABLED:
        return
    line = f"[{_ts()}] {stage}: {msg}\n"
    with open("/tmp/event_trace.log", "a") as f:
        f.write(line)
