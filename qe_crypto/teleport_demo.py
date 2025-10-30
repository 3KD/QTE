from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

def one_qubit_teleport()->QuantumCircuit:
    """Standard 1-qubit teleport: |ψ> on q0 ends on q2."""
    q = QuantumRegister(3,'q')
    c0 = ClassicalRegister(1,'m0'); c1 = ClassicalRegister(1,'m1')
    qc = QuantumCircuit(q, c0, c1, name="Teleport1")
    # Bell pair on q1-q2
    qc.h(q[1]); qc.cx(q[1], q[2])
    # Bell-basis on q0-q1
    qc.cx(q[0], q[1]); qc.h(q[0])
    # measurements
    qc.measure(q[0], c0[0]); qc.measure(q[1], c1[0])
    # corrections
    qc.z(q[2]).c_if(c0, 1)
    qc.x(q[2]).c_if(c1, 1)
    return qc
