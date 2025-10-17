# Tab 05 — Gates

Draw circuits for:
- the **current QFT circuit** (if built), or
- a **prep circuit** that initializes the Active statevector.

## Controls
- **Decompose initialize** — expands `initialize` to native gates (verbose)
- **Hide initialize box** — show compact placeholder instead
- **Barrier after prep** — visual split between prep and later ops
- **Reverse bits** — flip wire order
- **Wrap width (fold)** — line-wrap threshold for drawer
- **Figure width** — width hint passed to the MPL drawer

## Actions
- **Draw Current QFT Circuit** — renders the last built QFT spectrum circuit
- **Draw Prep for Active/Last Saved** — builds `initialize(|ψ⟩)` and draws it
- **Draw (ASCII / Text)** — text drawer (always readable, no ellipses)
- **Show Summary** — quick numeric circuit summary (ops, depth, size)

### Notes
- When “decompose initialize” is on, the drawer uses `decompose(reps=4)`.
- The text drawer is useful in headless CI.
