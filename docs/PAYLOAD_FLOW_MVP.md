# QTE Payload Flow MVP (Amplitudes + Entropy Certificates)

**Flow:** encode \|v⟩ → certify (Z/QFT) → keyed unitary mask → transmit → unmask → recertify & verify.
No extra qubit/bit overhead for integrity in the happy path.

**Capacity (no coding):** plain n bits/register; superdense 2n bits/register (needs n shared ebits).

## CLI
```bash
./tools/demo_payload_flow.py --n 8 --payload-int 42 --key demo-key
./tools/demo_payload_flow.py --n 8 --payload-int 42 --key demo-key --tamper
./tools/demo_payload_flow.py --n 10 --payload-hex deadbeef --key K1 --mac-key K2 --json
```
