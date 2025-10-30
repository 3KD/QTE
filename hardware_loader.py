"""
hardware_loader.py — Unit 04 (Hardware Loader Execution and State Preparation Verification)
"""
import json, time, hashlib, numpy as np
def build_exec_spec(prep_spec: dict, backend_target: str, shots: int, seed=None) -> dict: raise NotImplementedError
def run_backend(exec_spec: dict) -> dict: raise NotImplementedError
def verify_exec_hash(exec_spec: dict, receipt: dict) -> bool: raise NotImplementedError
def exec_run_bundle(nve_bundle: dict, backend_target: str, shots: int) -> dict: raise NotImplementedError
