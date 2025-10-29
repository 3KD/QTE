Unit 04 — Hardware Loader Execution and State Preparation Verification

Purpose:
Takes PrepSpec (Unit 03) and produces a backend-executable job: the concrete load into a simulator or real device, with exact metadata frozen for replay, attestation, and Quentroy Entropy comparison.

Dependencies:
• Unit 01 (NVE) • Unit 02 (LoaderSpec) • Unit 03 (PrepSpec + SimResult)

Outputs:
• ExecSpec → exact instructions for backend execution  
• RunReceipt → hash-bound record of the run result  
• ShotRecord → raw counts plus normalized distribution and backend metadata

ExecSpec structure:
{
  "nve_version": "Unit01",
  "loader_version": "Unit02",
  "prep_version": "Unit03",
  "exec_version": "Unit04",
  "backend_target": "ibm_qasm_simulator" | "ibmq_quito" | "local_aer" | ...,
  "shots": <int>,
  "transpile": true|false,
  "seed": <int>,
  "metadata": {
     "endianness": "little",
     "qft_kernel_sign": "+",
     "rail_mode": "...",
     "n_qubits": <int>,
     "padded_length": <int>,
     "pad_count": <int>
  },
  "circuit_source": "prep_spec.init_sequence",
  "amplitudes": "prep_spec.amplitudes.vector",
  "timestamp_utc": "<iso8601>",
  "hash_preimage": "sha256(JSON-of-this-dict-minus-hash)",
  "hash_digest": "<64-hex>"
}

RunReceipt structure:
{
  "exec_version": "Unit04",
  "backend_target": "...",
  "job_id": "<uuid>",
  "timestamp_start": "<iso8601>",
  "timestamp_end": "<iso8601>",
  "runtime_seconds": <float>,
  "counts": { "0": int, "1": int, ... },
  "distribution": { "0": float, ... },
  "norm_check_l2": <float>,
  "backend_info": { "name": "...", "simulator": bool, "n_qubits": int },
  "exec_hash": "<same-as-ExecSpec.hash_digest>"
}

Rules:
– No automatic padding, rail, or endian adjustment.  
– All metadata is carried through verbatim.  
– If backend cannot satisfy n_qubits, raise.  
– If measured distribution occupies padded states > 1 count, log leakage flag.  
– Deterministic serialization; same inputs → identical ExecSpec hash.  

Functions (hardware_loader.py):

1. build_exec_spec(prep_spec: dict, backend_target: str, shots: int, seed: int | None) → dict  
 – compose ExecSpec; compute sha256 digest; return.  
 – assert prep_spec.prep_version == "Unit03"  
 – assert endianness == "little", qft_kernel_sign == "+"  
 – assert shots > 0, backend_target non-empty  

2. run_backend(exec_spec: dict) → RunReceipt  
 – if backend_target contains "sim", sample multinomial |amp|² like Unit 03.  
 – otherwise, call qiskit or backend adapter (placeholder).  
 – collect counts, distribution, norm_check_l2.  
 – timestamp start/end, runtime_seconds, hash check.  

3. verify_exec_hash(exec_spec, receipt) → bool  
 – recompute hash from ExecSpec; compare with receipt["exec_hash"].  

4. exec_run_bundle(nve_bundle, backend_target, shots) → dict  
 Chain Units 01–04 in memory; return { "nve_version": ..., "loader_version": ..., "prep_version": ..., "exec_version": "Unit04", "receipt": RunReceipt }.  

Tests:

tests/test_exec_spec_hash.py  
 • same inputs → identical hash digest  

tests/test_exec_spec_fields.py  
 • all required fields present and non-null  

tests/test_run_backend_simulator.py  
 • ideal simulator run returns distribution matching |amp|²  

tests/test_verify_exec_hash.py  
 • verify_exec_hash returns True for matching digest, False otherwise  

CLI stub (nvqa_cli.py): `nve-run-exec`  
Flags: --object --weighting --phase-mode --rail-mode --N --shots --backend --out-spec --out-receipt  
Behavior: chain Units 01–04, emit ExecSpec and RunReceipt JSON.

Acceptance:
hardware_loader.py implements build_exec_spec, run_backend, verify_exec_hash, exec_run_bundle;  
tests exist and pass static validation;  
nvqa_cli.py contains nve-run-exec stub;  
no implicit mutation of prior units; hashes deterministic.

## CONTRACT (DO NOT CHANGE)

This section is machine-checked by pytest.  
If you edit / rename / remove any required tokens here without updating tests, pytest will fail and you will not be allowed to push.

Required CLI subcommand (must exist in nvqa_cli.py and stay spelled exactly like this):
- `nve-run-exec`

Required CLI flags for `nve-run-exec`:
- `--object`
- `--weighting`
- `--phase-mode`
- `--rail-mode`
- `--N`
- `--shots`
- `--backend`
- `--out-spec`
- `--out-receipt`

Behavioral contract for `nve-run-exec`:
1. Build canonical state ψ via NVE (Unit01) using Normalized Vector Embedding.
2. Build LoaderSpec (Unit02) with deterministic rail layout + rail_layout JSON, including `loader_version="Unit02"`.
3. Build PrepSpec (Unit03) with a staged state-prep circuit + shot plan, including `prep_version="Unit03"`.
4. Build ExecSpec (Unit04) that binds PrepSpec to a physical backend, sets `backend_name`, and records how many `shots` were actually requested. ExecSpec MUST carry:
   - `loader_version`
   - `prep_version`
   - `exec_version="Unit04"`
   - `rail_layout`
   - `backend_name`
   - `shots`
   - `endianness`
   - `qft_kernel_sign`
5. Run the backend (hardware or qasm/simulator).
6. Emit a RunReceipt JSON with:
   - `counts` (basis measurement histogram)
   - `backend_name`
   - `shots`
   - `exec_version`
   - `receipt_version="Unit04"`

Both ExecSpec and RunReceipt MUST be written to disk at the paths given by:
- `--out-spec`
- `--out-receipt`

Security / attestation expectations:
- The `rail_layout` frozen in LoaderSpec/PrepSpec MUST match the loader layout the backend actually used, or downstream Quentroy / audit will reject the run.
- The `exec_version="Unit04"` tag is mandatory. This proves which version of exec semantics produced the receipt.
- The `endianness` MUST still be `"little"`.
- `qft_kernel_sign` MUST still be `"+"`.
If any of those drift, downstream Units (05/11/25) will treat the run as untrusted.

Downstream dependency:
- Unit05 and later pull `counts` and `exec_version` and `rail_layout` from the RunReceipt when computing Quentroy Entropy and audit trails.
- Unit11 / Unit25 pull `backend_name`, `shots`, and layout info during tamper detection and crypto watermark attestation.

## CONTRACT (DO NOT CHANGE)

This section is test-enforced. These exact substrings MUST remain visible in this file,
because downstream tooling and attestation logic grep for them. If you drift this text,
pytest will fail and you're not allowed to ship.

nvqa_cli.py subcommand surface (must exist exactly as shown):
  nve-run-exec \
    --object <...> \
    --weighting <...> \
    --phase-mode <...> \
    --rail-mode <...> \
    --N <int> \
    --shots <int> \
    --backend <backend_name> \
    --out-spec exec_spec.json \
    --out-receipt run_receipt.json \
    exec_version="Unit04"

exec_spec.json MUST include:
  {
    "nve_version": "Unit01",
    "loader_version": "Unit02",
    "prep_version": "Unit03",
    "exec_version": "Unit04",
    "endianness": "little",
    "qft_kernel_sign": "+",
    "rail_layout": "... layout of rails to logical qubits ...",
    "backend_name": "ibm_torino_or_whatever",
    "shots": 1024
  }

run_receipt.json MUST include:
  {
    "receipt_version": "Unit04",
    "backend_name": "ibm_torino_or_whatever",
    "shots": 1024,
    "rail_layout": "... same semantic rail_layout ...",
    "endianness": "little",
    "qft_kernel_sign": "+",
    "exec_version": "Unit04"
  }

The strings "rail_layout", "backend_name", "shots",
"endianness": "little", "qft_kernel_sign": "+",
and "receipt_version": "Unit04" are all considered frozen API markers.
