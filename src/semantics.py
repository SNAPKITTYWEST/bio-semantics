# semantics.py
import math
import re

STAN_INT_MAX = 2_147_483_647
FIELDS = {
    "observation_id", "sample_id", "gene_id", "condition",
    "timepoint", "replicate", "batch", "cell_type", "count",
    "missing_reason", "exposure", "normalized_expression",
    "normalization", "measurement_quality",
}


def _require(ok, message):
    if not ok:
        raise ValueError(message)


def _identifier(value):
    return isinstance(value, str) and bool(value.strip())


def _finite_number(value):
    if type(value) not in (int, float):
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


def validate_dataset(dataset, conditions):
    """Validate without modifying, imputing, or coercing input.

    Null metadata stays null. Native adapters must explicitly exclude
    records missing required model metadata, preserving an exclusion map.
    Normalization is derived; counts are observed, unless synthetic.
    Source-byte hashes belong in the pipeline artifact manifest.
    """
    _require(
        isinstance(conditions, (list, tuple))
        and len(conditions) == 2
        and all(_identifier(x) for x in conditions)
        and conditions[0] != conditions[1],
        "config requires two distinct explicit conditions",
    )
    _require(isinstance(dataset, dict), "dataset must be an object")
    _require(
        {"dataset_id", "synthetic", "observations"} <= dataset.keys(),
        "missing dataset fields",
    )
    _require(_identifier(dataset["dataset_id"]), "invalid dataset_id")
    _require(type(dataset["synthetic"]) is bool, "synthetic must be boolean")
    _require(isinstance(dataset["observations"], list), "observations must be a list")

    seen = set()
    for index, row in enumerate(dataset["observations"]):
        prefix = f"observations[{index}]"
        _require(isinstance(row, dict), f"{prefix}: expected object")
        _require(FIELDS <= row.keys(), f"{prefix}: missing required fields")
        for field in ("observation_id", "sample_id", "gene_id"):
            _require(_identifier(row[field]), f"{prefix}: invalid {field}")
        identity = row["observation_id"]
        _require(identity not in seen, f"{prefix}: duplicate observation_id")
        seen.add(identity)

        condition = row["condition"]
        _require(
            condition is None
            or (isinstance(condition, str) and condition in conditions),
            f"{prefix}: unknown condition",
        )
        for field in ("replicate", "batch", "cell_type"):
            _require(
                row[field] is None or _identifier(row[field]),
                f"{prefix}: {field} must be null or nonempty string",
            )
        _require(
            row["timepoint"] is None or _finite_number(row["timepoint"]),
            f"{prefix}: timepoint must be null or finite number",
        )

        count, reason = row["count"], row["missing_reason"]
        if count is None:
            _require(_identifier(reason), f"{prefix}: missing count requires reason")
        else:
            _require(reason is None, f"{prefix}: present count cannot have missing reason")
            _require(
                isinstance(count, str)
                and re.fullmatch(r"(?:0|[1-9][0-9]*)", count) is not None,
                f"{prefix}: count must be canonical unsigned decimal string",
            )
            limit = str(STAN_INT_MAX)
            _require(
                len(count) < len(limit)
                or (len(count) == len(limit) and count <= limit),
                f"{prefix}: count exceeds Stan integer range",
            )

        exposure = row["exposure"]
        _require(
            _finite_number(exposure) and exposure > 0,
            f"{prefix}: exposure must be positive and finite",
        )
        for field in ("normalized_expression", "measurement_quality"):
            _require(
                row[field] is None or _finite_number(row[field]),
                f"{prefix}: {field} must be null or finite number",
            )

        normalization = row["normalization"]
        if row["normalized_expression"] is not None:
            _require(normalization is not None, f"{prefix}: normalization provenance required")
        if normalization is not None:
            _require(
                isinstance(normalization, dict)
                and {"method", "source_ids"} <= normalization.keys(),
                f"{prefix}: invalid normalization provenance",
            )
            _require(_identifier(normalization["method"]), f"{prefix}: missing normalization method")
            sources = normalization["source_ids"]
            _require(
                isinstance(sources, list)
                and bool(sources)
                and all(_identifier(s) for s in sources),
                f"{prefix}: normalization source_ids required",
            )
            _require(len(set(sources)) == len(sources), f"{prefix}: duplicate source_ids")
    return dataset


# Fixed PTM: input alphabet {0,1}; tape alphabet {0,1,_}.
# Output: final parity bit in the first formerly blank cell.
# q_accept and q_reject halt; malformed encodings reject before a transition.
DELTA = {
    ("q_even", "0"): ("q_even", "0", 1),
    ("q_even", "1"): ("q_odd", "1", 1),
    ("q_odd", "0"): ("q_odd", "0", 1),
    ("q_odd", "1"): ("q_even", "1", 1),
    ("q_even", "_"): ("q_accept", "0", 0),
    ("q_odd", "_"): ("q_accept", "1", 0),
}


def ptm_parity(bits):
    if not isinstance(bits, str) or any(bit not in "01" for bit in bits):
        return {
            "status": "rejected", "state": "q_reject",
            "reason": "invalid input encoding", "transitions": 0,
        }
    tape = list(bits) + ["_"]
    state, head, transitions = "q_even", 0, 0
    while state != "q_accept":
        state, write, move = DELTA[(state, tape[head])]
        tape[head] = write
        head += move
        transitions += 1
    return {
        "status": "accepted",
        "state": state,
        "output": tape[head],
        "output_cell": head,
        "encoded_input_bits": len(bits),
        "transitions": transitions,
        "total_tape_cells": len(tape),
        "auxiliary_tape_cells": 1,
    }
