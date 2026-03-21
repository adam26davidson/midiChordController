import time

TRACE_ENABLED = False
_start_time = time.time()

def _ts():
    return f"{time.time() - _start_time:.3f}"

def trace(stage, msg):
    if not TRACE_ENABLED:
        return
    line = f"[{_ts()}] {stage}: {msg}\n"
    with open("/tmp/event_trace.log", "a") as f:
        f.write(line)
