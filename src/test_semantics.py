# test_semantics.py
import copy
import unittest

from semantics import validate_dataset, ptm_parity


def fixture():
    # Explicitly synthetic: excluded from scientific conclusions.
    return {
        "dataset_id": "synthetic-validator-fixture",
        "synthetic": True,
        "observations": [{
            "observation_id": "fixture-o1",
            "sample_id": "fixture-s1",
            "gene_id": "fixture-g1",
            "condition": "control",
            "timepoint": None,
            "replicate": None,
            "batch": None,
            "cell_type": None,
            "count": "0",
            "missing_reason": None,
            "exposure": 1.0,
            "normalized_expression": None,
            "normalization": None,
            "measurement_quality": None,
        }],
    }


class SemanticsTests(unittest.TestCase):
    conditions = ["control", "comparison"]

    def test_zero_and_missing_remain_distinct_without_mutation(self):
        data = fixture()
        missing = copy.deepcopy(data["observations"][0])
        missing.update(
            observation_id="fixture-o2",
            count=None,
            missing_reason="not_measured",
        )
        data["observations"].append(missing)
        before = copy.deepcopy(data)
        validate_dataset(data, self.conditions)
        self.assertEqual(data, before)
        self.assertEqual(data["observations"][0]["count"], "0")
        self.assertIsNone(data["observations"][1]["count"])

    def test_bad_counts_are_rejected(self):
        for count in [0, True, "-1", "1.5", "1e3", "01", " 1", "2147483648"]:
            with self.subTest(count=count):
                data = fixture()
                data["observations"][0]["count"] = count
                with self.assertRaises(ValueError):
                    validate_dataset(data, self.conditions)

    def test_invalid_states_are_rejected(self):
        patches = [
            {"count": None},  # no missing reason
            {"missing_reason": "not_measured"},  # count still present
            {"exposure": 0},
            {"exposure": float("inf")},
            {"exposure": True},
            {"condition": "undeclared"},
            {"normalized_expression": 1.2},  # no provenance
            {"measurement_quality": float("nan")},
        ]
        for patch in patches:
            with self.subTest(patch=patch):
                data = fixture()
                data["observations"][0].update(patch)
                with self.assertRaises(ValueError):
                    validate_dataset(data, self.conditions)

    def test_duplicate_identity_and_condition_config(self):
        data = fixture()
        data["observations"].append(copy.deepcopy(data["observations"][0]))
        with self.assertRaises(ValueError):
            validate_dataset(data, self.conditions)
        with self.assertRaises(ValueError):
            validate_dataset(fixture(), ["control", "control"])

    def test_normalized_expression_requires_declared_sources(self):
        data = fixture()
        data["observations"][0].update(
            normalized_expression=2.5,
            normalization={
                "method": "synthetic-test-transform",
                "source_ids": ["synthetic-source-artifact"],
            },
        )
        validate_dataset(data, self.conditions)

    def test_ptm_outputs_and_resource_bound(self):
        for bits, output in [("", "0"), ("0", "0"), ("1", "1"), ("1011", "1")]:
            with self.subTest(bits=bits):
                result = ptm_parity(bits)
                self.assertEqual(result["output"], output)
                self.assertEqual(result["transitions"], len(bits) + 1)
                self.assertEqual(result["total_tape_cells"], len(bits) + 1)
        self.assertEqual(ptm_parity("102")["status"], "rejected")


if __name__ == "__main__":
    unittest.main()
