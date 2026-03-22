"""Tests for event_trace.py — tracing utility."""

import event_trace


class TestTrace:
    def test_trace_disabled_does_not_crash(self):
        event_trace.TRACE_ENABLED = False
        event_trace.trace("TEST", "some message")  # Should not raise

    def test_trace_enabled_writes_to_file(self, tmp_path):
        log_file = tmp_path / "event_trace.log"
        event_trace.TRACE_ENABLED = True

        # Temporarily point trace to our tmp file by monkeypatching the function

        def patched_trace(stage: str, msg: str) -> None:
            if not event_trace.TRACE_ENABLED:
                return
            line = f"[{event_trace._ts()}] {stage}: {msg}\n"
            with open(log_file, "a") as f:
                f.write(line)

        original = event_trace.trace
        event_trace.trace = patched_trace  # type: ignore[invalid-assignment]
        try:
            event_trace.trace("COUPLER_IN", "key=btn_south event=ON")
            content = log_file.read_text()
            assert "COUPLER_IN" in content
            assert "btn_south" in content
        finally:
            event_trace.trace = original
            event_trace.TRACE_ENABLED = False
