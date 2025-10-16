# --- top of file ---
from file_naming import build_qte_filename, schmidt_entropies_all_cuts, parse_multi_label

# ... inside your sweep loop, after you create a Statevector `sv` ...
# Suppose you already know constants/mode/phase/regq/topology/ pattern:
constants = current_constant_pairs      # e.g., [("pi","Machin")] or [("Li(2,0.5)",None), ("e",None)]
mode      = current_mode                # "EGF" / "Terms" / ...
phase     = current_phase_mode          # "sign" / "abs"
label     = current_state_label         # if you track "multi[...|topo|regq]"
N         = int(np.log2(len(sv.data)))

# Entanglement per register-cut (only if we have a multi-register structure)
ents = None
regq = None
topology = None
pattern = None

parsed = parse_multi_label(label) if isinstance(label, str) else None
if parsed:
    regs, topology, regq = parsed
    n_regs = len(regs)
    ents = schmidt_entropies_all_cuts(sv, regq=regq, n_regs=n_regs)

# Build filename for a PNG (same call works for .csv/.npy by changing suffix)
fname_png = build_qte_filename(
    constants=constants,
    mode=mode,
    n_qubits=N,
    phase_mode=phase,
    regq=regq,
    topology=topology,
    pattern=pattern,                # set if you use "cx_all"/"bell_on_0"/etc.
    entropies_bits=ents,
    extra={"sweep":"polylog", "trial": sweep_idx},
    suffix=".png"
)

# Save your figure
fig.savefig(fname_png, dpi=160)

# If you also save data (e.g., amplitudes or metrics):
fname_csv = fname_png[:-4] + ".csv"
np.savetxt(fname_csv, your_array, delimiter=",")

