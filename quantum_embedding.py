# quantum_embedding.py — drop-in backend for QTEGUI
# Implements:
#   qft_spectrum_from_series, index_qft_spectrum_circuit,
#   run_circuit, simulate_statevector, generate_series_encoding,
#   encode_entangled_constants, entangle_series_registers, entangle_series_multi,
#   analyze_tensor_structure, perform_schmidt_decomposition,
#   value_phase_estimation_circuit, periodic_phase_state, digit_qrom_circuit

from typing import Optional, List, Tuple, Dict
import numpy as np

from qiskit import QuantumCircuit, ClassicalRegister, transpile
from qiskit.circuit.library import QFT
from qiskit.quantum_info import Statevector, DensityMatrix
from qiskit_aer import Aer
try:
    from qiskit_aer import AerSimulator
except Exception:
    AerSimulator = None

# App module for series
from series_encoding import get_series_amplitudes, compute_series_value

# ----------------- small helpers -----------------

def _ensure_unit(vec: np.ndarray) -> np.ndarray:
    vec = np.asarray(vec, dtype=complex).reshape(-1)
    nrm = np.linalg.norm(vec)
    if nrm == 0:
        raise ValueError("Zero vector cannot be normalized.")
    return vec / nrm

def _center_hann(vec: np.ndarray) -> np.ndarray:
    x = np.asarray(vec, dtype=complex).reshape(-1)
    if x.size == 0:
        return x
    x = x - np.mean(x)
    if x.size > 1:
        x = x * np.hanning(x.size)
    return x

def _spectrum_metrics(vec: np.ndarray) -> Dict[str, float]:
    X = np.fft.fft(vec)
    P = np.abs(X) ** 2
    S = P.sum() or 1.0
    dc = float(P[0] / S)
    p = (P / S)
    p = p[p > 0]
    H = float(-np.sum(p * np.log2(p)))
    return {"len": int(len(vec)), "dc_frac": dc, "entropy_bits": H}

def _n_from_len(L: int) -> int:
    n = int(np.log2(L))
    if (1 << n) != L:
        raise ValueError(f"Length {L} is not a power of two.")
    return n

# ----------------- public API -----------------

def simulate_statevector(qc: QuantumCircuit) -> Statevector:
    return Statevector.from_instruction(qc)

def run_circuit(qc: QuantumCircuit, *, use_ibm: bool = False, measure: bool = True, shots: int = 2048):
    if not measure:
        return qc, {}
    try:
        backend = Aer.get_backend("qasm_simulator")
    except Exception:
        # fallback
        backend = AerSimulator() if AerSimulator is not None else None
        if backend is None:
            raise RuntimeError("No simulator backend available (Aer missing).")
    tqc = transpile(qc, backend)
    result = backend.run(tqc, shots=shots).result()
    return qc, result.get_counts()

def generate_series_encoding(
    label: str,
    *,
    n_qubits: int,
    method: Optional[str],
    phase_mode: str = "sign",
    amp_mode: str = "egf",
) -> Statevector:
    N = 1 << n_qubits
    amps = get_series_amplitudes(label, N, method=method, phase_mode=phase_mode, normalize=True, amp_mode=amp_mode)
    qc = QuantumCircuit(n_qubits)
    qc.initialize(_ensure_unit(amps), range(n_qubits))
    return Statevector.from_instruction(qc)

def index_qft_spectrum_circuit(
    vec: np.ndarray,
    *,
    use_stateprep: bool = True,
    do_measure: bool = True,
) -> QuantumCircuit:
    vec = _ensure_unit(np.asarray(vec, dtype=complex))
    n = _n_from_len(len(vec))
    qc = QuantumCircuit(n, n if do_measure else 0)
    if use_stateprep:
        qc.initialize(vec, range(n))
        qc.barrier()
    # Apply QFT to map "time" to "frequency" in the index domain
    qc.append(QFT(num_qubits=n, do_swaps=True).to_instruction(), range(n))
    if do_measure:
        qc.measure(range(n), range(n))
    return qc

def qft_spectrum_from_series(
    label: str,
    *,
    n_qubits: int,
    method: Optional[str],
    phase_mode: str = "sign",
    amp_mode: str = "egf",
    preprocess: bool = True,
    use_stateprep: bool = True,
    do_measure: bool = True,
    pad_len: Optional[int] = None,   # ignored in circuit path; padding matters only for classical FFT
):
    N = 1 << n_qubits
    vec = get_series_amplitudes(label, N, method=method, phase_mode=phase_mode, normalize=True, amp_mode=amp_mode)
    proc = _center_hann(vec) if preprocess else np.asarray(vec, dtype=complex)
    qc = index_qft_spectrum_circuit(proc, use_stateprep=use_stateprep, do_measure=do_measure)
    mets = _spectrum_metrics(proc)
    return qc, proc, mets

def encode_entangled_constants(c1: float, c2: float) -> QuantumCircuit:
    """
    Minimal 2-qubit entangled encoding: |ψ> = a|00> + b|11>, with a∝c1, b∝c2.
    Useful only as a demo for simple 'fractional' entanglement.
    """
    vec = np.array([c1, 0.0, 0.0, c2], dtype=complex)
    vec = _ensure_unit(vec)
    qc = QuantumCircuit(2)
    qc.initialize(vec, [0, 1])
    return qc

def entangle_series_registers(
    const1: str,
    const2: str,
    *,
    n_qubits_each: int,
    method1: Optional[str],
    method2: Optional[str],
    phase_mode1: str = "sign",
    phase_mode2: str = "sign",
    pattern: str = "cx_all",
    use_stateprep: bool = True,
    do_measure: bool = False,
) -> QuantumCircuit:
    N = 1 << n_qubits_each
    a1 = get_series_amplitudes(const1, N, method=method1, phase_mode=phase_mode1, normalize=True, amp_mode="egf")
    a2 = get_series_amplitudes(const2, N, method=method2, phase_mode=phase_mode2, normalize=True, amp_mode="egf")
    qc = QuantumCircuit(2 * n_qubits_each, 0)
    if use_stateprep:
        qc.initialize(_ensure_unit(a1), list(range(n_qubits_each)))
        qc.initialize(_ensure_unit(a2), list(range(n_qubits_each, 2 * n_qubits_each)))
        qc.barrier()
    if pattern == "cx_all":
        for i in range(n_qubits_each):
            qc.cx(i, n_qubits_each + i)
    elif pattern == "bell_on_0":
        qc.h(0); qc.cx(0, n_qubits_each)
    else:
        # noop / unknown pattern
        pass
    if do_measure:
        qc.measure_all()
    return qc

def entangle_series_multi(
    labels: List[str],
    *,
    n_qubits_each: int,
    methods: Optional[List[Optional[str]]] = None,
    phase_mode: str = "sign",
    topology: str = "chain",   # "chain" | "star" | "all_to_all"
    use_stateprep: bool = True,
    do_measure: bool = False,
) -> QuantumCircuit:
    R = len(labels)
    total_q = R * n_qubits_each
    if methods is None:
        methods = [None] * R
    amps: List[np.ndarray] = []
    for lab, meth in zip(labels, methods):
        N = 1 << n_qubits_each
        a = get_series_amplitudes(lab, N, method=meth, phase_mode=phase_mode, normalize=True, amp_mode="egf")
        amps.append(_ensure_unit(a))
    qc = QuantumCircuit(total_q, 0)
    if use_stateprep:
        for r in range(R):
            start = r * n_qubits_each
            qc.initialize(amps[r], list(range(start, start + n_qubits_each)))
        qc.barrier()
    # simple wiring using first qubit of each register
    def first_of(r): return r * n_qubits_each
    if topology == "chain":
        for r in range(R - 1):
            qc.cx(first_of(r), first_of(r + 1))
    elif topology == "star" and R >= 2:
        for r in range(1, R):
            qc.cx(first_of(0), first_of(r))
    elif topology == "all_to_all":
        for i in range(R):
            for j in range(i + 1, R):
                qc.cx(first_of(i), first_of(j))
    if do_measure:
        qc.measure_all()
    return qc

def analyze_tensor_structure(sv: Statevector, *, cut: Optional[int] = None):
    """
    Return (rhoA, rhoB, rhoAB) where the bipartition is [0..cut-1] | [cut..n-1].
    If cut is None, use n//2.
    """
    psi = np.asarray(sv.data, dtype=complex)
    n = int(np.log2(psi.size))
    if cut is None:
        cut = n // 2
    A, B = (1 << cut), (1 << (n - cut))
    M = psi.reshape(A, B)
    rhoA = DensityMatrix(M @ M.conj().T)
    rhoB = DensityMatrix(M.conj().T @ M)
    rhoAB = DensityMatrix(np.outer(psi, psi.conj()))
    return rhoA, rhoB, rhoAB

def perform_schmidt_decomposition(sv: Statevector, *, cut: int) -> np.ndarray:
    psi = np.asarray(sv.data, dtype=complex)
    n = int(np.log2(psi.size))
    A, B = (1 << cut), (1 << (n - cut))
    M = psi.reshape(A, B)
    S = np.linalg.svd(M, compute_uv=False)
    return S  # singular values (Schmidt coeffs)

def value_phase_estimation_circuit(
    label: str,
    *,
    K: int = 10,
    method: Optional[str] = None,
    do_measure: bool = True,
) -> QuantumCircuit:
    """
    PEA for a 'black-box' phase U = e^{2πi x}, where x = frac(constant(label)).
    Implements controlled-U^{2^k} by controlled Phase rotations on a single 'eigen' qubit.
    """
    # crude-but-effective fractional estimate
    x = compute_series_value(label, terms=2048, method=method) % 1.0
    ctrl = K
    qc = QuantumCircuit(K + 1, K if do_measure else 0)
    # eigenstate |1>
    qc.x(ctrl)
    # Hadamards on counting register
    for k in range(K):
        qc.h(k)
    # controlled-U^{2^k}  ~ controlled phase on |1> target
    for k in range(K):
        angle = 2 * np.pi * x * (2 ** k)
        qc.cp(angle, k, ctrl)
    # inverse QFT on counting register
    iqft = QFT(num_qubits=K, inverse=True, do_swaps=True).to_instruction()
    qc.append(iqft, list(range(K)))
    if do_measure:
        qc.measure(range(K), range(K))
    return qc

def periodic_phase_state(
    p: int, q: int, *, n_qubits: int, do_measure: bool = False, apply_qft: bool = False
) -> QuantumCircuit:
    """
    Prepare |ψ> with amplitudes ψ[n] ∝ exp(2πi p n / q), n=0..N-1 (uniform magnitude).
    Implemented via direct state initialization for simulation convenience.
    Optionally apply QFT to look for peaks at multiples of N/q.
    """
    N = 1 << n_qubits
    n = np.arange(N)
    vec = np.exp(2j * np.pi * (p * n / q)) / np.sqrt(N)
    qc = QuantumCircuit(n_qubits, n_qubits if do_measure else 0)
    qc.initialize(_ensure_unit(vec), range(n_qubits))
    if apply_qft:
        qc.barrier()
        qc.append(QFT(num_qubits=n_qubits, do_swaps=True).to_instruction(), range(n_qubits))
    if do_measure:
        qc.measure(range(n_qubits), range(n_qubits))
    return qc

def digit_qrom_circuit(
    label: str,
    *,
    base: int = 10,
    n_index: int = 6,            # # index qubits → L = 2**n_index digits
    bits_per_digit: int = 4,     # store each digit in binary on this many qubits
    method: Optional[str] = None,
    do_measure: bool = False,
) -> QuantumCircuit:
    """
    Simulation-friendly QROM:
      Prepare (1/√L) Σ_i |i⟩ |digit_i⟩  where digit_i = i-th fractional digit of constant(label) in 'base'.
    Implemented by direct state initialization (no actual multi-controlled logic).
    """
    L = 1 << n_index
    # compute fractional digits
    x = abs(compute_series_value(label, terms=4096, method=method)) % 1.0
    digits = []
    tmp = x
    for _ in range(L):
        tmp *= base
        d = int(tmp); digits.append(d); tmp -= d
    # build full statevector over n_index + bits_per_digit qubits
    n_tot = n_index + bits_per_digit
    N = 1 << n_tot
    vec = np.zeros(N, dtype=complex)
    amp = 1.0 / np.sqrt(L)
    for i, d in enumerate(digits):
        # clamp digit into available bits
        d = d & ((1 << bits_per_digit) - 1)
        basis = (i << bits_per_digit) | d
        vec[basis] = amp
    qc = QuantumCircuit(n_tot, n_tot if do_measure else 0)
    qc.initialize(_ensure_unit(vec), range(n_tot))
    if do_measure:
        qc.measure(range(n_tot), range(n_tot))
    return qc

