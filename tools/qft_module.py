from qiskit import QuantumCircuit
from qiskit.circuit.library import QFT as QFTGate

def qft(n:int, inverse:bool=False, do_swaps:bool=True, approximation_degree:int=0)->QuantumCircuit:
    """QFT / inverse QFT wrapper with sane defaults."""
    qc = QuantumCircuit(n, name=("QFT†" if inverse else "QFT"))
    gate = QFTGate(num_qubits=n, approximation_degree=approximation_degree, do_swaps=do_swaps, inverse=inverse)
    qc.append(gate, range(n))
    return qc

def st_qft(n:int, window_size:int, step:int):
    """Short-Time QFT: QFT on sliding windows over an n-qubit register."""
    if window_size<1 or window_size>n: raise ValueError("bad window_size")
    circs=[]
    for start in range(0, n-window_size+1, step):
        qc = QuantumCircuit(n, name=f"STQFT[{start}:{start+window_size}]")
        gate = QFTGate(window_size, do_swaps=False)
        qc.append(gate, list(range(start, start+window_size)))
        circs.append(qc)
    return circs
