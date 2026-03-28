# Pi Tester Learnings

Accumulated knowledge from running tests on the Pi. Read this before starting a test session. Add new findings as you discover them.

## Tool Usage

- `pi_sequence` causes token overflow when it includes multiple screenshot steps. The result payload can exceed 240,000+ tokens. Use individual tool calls (`pi_screenshot`, `pi_touch`, `pi_send_and_screenshot`) instead of combining screenshot steps inside a single `pi_sequence` call.
- `pi_sequence` is still useful for non-screenshot sequences (e.g., press + delay + midi query) where the payload stays small.
- `pi_touch` returns an annotated screenshot with a red crosshair/line showing exactly where the touch landed. This is the primary way to confirm that a tap hit its intended target.
- `pi_send_and_screenshot` is the most efficient way to press a button and immediately capture the result in one call.

## Timing & Sequencing

- A delay of ~400ms between a tap and a screenshot is sufficient to capture settings UI changes reliably. Shorter delays (100ms) may miss the visual state update.
- When verifying a toggle's behavior, tap the alternate state first, then the target state. This gives a clear before/after comparison instead of a single ambiguous screenshot.

## Common Pitfalls

- Toggle button visual states can be ambiguous in a single screenshot if you don't know the starting state. Always confirm starting state before testing a toggle, or test both states (toggle away, then toggle back) to observe the difference clearly.
- The physical game controller's gyroscope and joysticks continuously stream analog events. Disconnect the physical controller before any remote control testing session, or these events will interfere with values set remotely.
- `pi_reset` at the start of each test is essential — stale controller state from a previous session can cause unexpected behavior.

## Patterns That Work Well

- Settings UI coordinate accuracy: All coordinates documented in CLAUDE.md for the main menu and MIDI settings page have been verified accurate as of 2026-03-24:
  - Menu: MIDI (400, 96), STRUM (176, 240), PERFORM (400, 240), CHORD (400, 384)
  - Back button: (55, 30)
  - Velocity mode CONST: (55, 280), RAND: (150, 280)
- Standard UI test flow that works: `pi_reset` → `pi_send_and_screenshot START_BUTTON` (open menu) → `pi_touch` (navigate) → `pi_screenshot` (capture state) → `pi_touch` back button (55, 30) → `pi_screenshot` (confirm return).
- Using `pi_touch` for navigation and `pi_screenshot` for state verification (rather than `pi_send_and_screenshot`) gives more predictable timing control.
