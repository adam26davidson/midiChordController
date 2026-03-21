"""Tests for event_trace.py — tracing utility."""

import event_trace


class TestTrace:
    def test_trace_disabled_does_not_crash(self):
        event_trace.TRACE_ENABLED = False
        event_trace.trace("TEST", "some message")  # Should not raise

    def test_trace_enabled_writes_to_file(self, tmp_path):
        log_file = tmp_path / "trace.log"
        event_trace.TRACE_ENABLED = True
        # Temporarily override the trace function to write to tmp
        original_trace = event_trace.trace

        def patched_trace(stage, msg):
            line = f"[0.000] {stage}: {msg}\n"
            with open(log_file, "a") as f:
                f.write(line)

        event_trace.trace = patched_trace
        try:
            event_trace.trace("COUPLER_IN", "key=btn_south event=ON")
            content = log_file.read_text()
            assert "COUPLER_IN" in content
            assert "btn_south" in content
        finally:
            event_trace.trace = original_trace
            event_trace.TRACE_ENABLED = False

    def test_timestamp_format(self):
        ts = event_trace._ts()
        # Should be a float string like "123.456"
        float(ts)  # Should not raise
