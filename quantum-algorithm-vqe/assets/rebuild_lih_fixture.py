"""Regenerate the bundled LiH fixture from a checksum-verified upstream FCIDUMP.

Usage: python rebuild_lih_fixture.py --source lih.fcidump --output result.json
Download the pinned source URL below before running; this script does not fetch
or execute remote code. Requires Qiskit Nature 0.8 and Qiskit 2.5.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path

SOURCE_REVISION = "5944cdb3b4f6505084a8b24083be9de6a1a1d1fc"
SOURCE_PATH = "test/second_q/formats/fcidump/test_fcidump_lih.fcidump"
SOURCE_URL = (
    "https://raw.githubusercontent.com/qiskit-community/qiskit-nature/"
    f"{SOURCE_REVISION}/{SOURCE_PATH}"
)
SOURCE_SHA256 = "8ff5a3137aa3c46158bdf6fdeac267ac9259f04e324de3c1a612448569305ffe"


def rebuild(source: Path) -> dict:
    import numpy as np
    from qiskit_nature.second_q.formats.fcidump import FCIDump
    from qiskit_nature.second_q.formats.fcidump_translator import fcidump_to_problem
    from qiskit_nature.second_q.mappers import JordanWignerMapper
    from qiskit_nature.second_q.transformers import ActiveSpaceTransformer

    if hashlib.sha256(source.read_bytes()).hexdigest() != SOURCE_SHA256:
        raise ValueError(
            "Source FCIDUMP checksum differs from the pinned upstream fixture"
        )
    full = fcidump_to_problem(FCIDump.from_file(source))
    reduced = ActiveSpaceTransformer(2, 2, active_orbitals=[1, 2]).transform(full)
    operator = (
        JordanWignerMapper().map(reduced.hamiltonian.second_q_op()).simplify(atol=1e-12)
    )
    matrix = operator.to_matrix()
    sector = [5, 6, 9, 10]
    reference = float(np.linalg.eigvalsh(matrix[np.ix_(sector, sector)])[0])
    offsets = {k: float(v) for k, v in reduced.hamiltonian.constants.items()}
    return {
        "schema_version": 1,
        "instance_id": "lih-upstream-sto3g-nominal-1.6a-cas2e2o-jw",
        "source_url": SOURCE_URL,
        "source_sha256": SOURCE_SHA256,
        "source_revision": SOURCE_REVISION,
        "source_test_url": (
            "https://github.com/qiskit-community/qiskit-nature/blob/"
            f"{SOURCE_REVISION}/test/second_q/drivers/test_driver_methods_gsc.py"
        ),
        "source_license": "Apache-2.0; derived from Qiskit Nature's IBM-authored LiH regression fixture",
        "molecule": "LiH",
        "basis": "STO-3G",
        "nominal_bond_length_angstrom": 1.6,
        "geometry_convention": "Upstream test's nominal geometry; original FCIDUMP nuclear constant retained exactly",
        "charge": 0,
        "multiplicity": 1,
        "num_qubits": 4,
        "num_particles": [1, 1],
        "active_orbitals": [1, 2],
        "inactive_occupied_orbitals": [0],
        "excluded_virtual_orbitals": [3, 4, 5],
        "mapping": "JordanWignerMapper; alpha modes 0,1; beta modes 2,3",
        "pauli_order": "q3 q2 q1 q0; little-endian basis indices",
        "energy_unit": "hartree",
        "operator_energy_scope": "active electronic only; excludes both constants",
        "offsets": offsets,
        "sector_basis_indices": sector,
        "reference_active_energy": reference,
        "reference_total_energy": reference + sum(offsets.values()),
        "paulis": [[p, float(complex(c).real)] for p, c in operator.to_list()],
        "generation": {
            "transformer": "qiskit_nature.second_q.transformers.ActiveSpaceTransformer(2, 2, active_orbitals=[1, 2])",
            "versions": {
                p: importlib.metadata.version(p)
                for p in ("qiskit", "qiskit-nature", "numpy")
            },
        },
        "limitations": [
            "Fixed upstream LiH instance at nominal 1.6 angstrom; no arbitrary geometry or basis inputs",
            "CAS(2e,2o) approximation, not full six-orbital LiH or experimental chemical accuracy",
            "Exact local statevector simulation; no hardware or quantum advantage claim",
        ],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = rebuild(args.source)
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "terms": len(result["paulis"]),
                "reference_total_energy": result["reference_total_energy"],
            }
        )
    )
