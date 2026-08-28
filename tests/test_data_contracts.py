from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lib"))

from contract_validation import DATASET_FILES, validate_datasets, validate_payloads  # noqa: E402


def live_payloads() -> dict[str, object]:
    return {
        name: json.loads((ROOT / "data" / filename).read_text(encoding="utf-8"))
        for name, filename in DATASET_FILES.items()
    }


class DataContractTests(unittest.TestCase):
    def test_live_datasets_satisfy_strict_contracts(self):
        self.assertEqual([], validate_datasets(ROOT / "data"))

    def test_unknown_source_field_is_rejected(self):
        payloads = copy.deepcopy(live_payloads())
        payloads["sources"]["sources"][0]["unexpected"] = True
        errors = validate_payloads(payloads)
        self.assertIn(
            "sources.json.sources[0].unexpected: unsupported field",
            errors,
        )

    def test_malformed_scenario_parameter_array_is_rejected(self):
        payloads = copy.deepcopy(live_payloads())
        payloads["scenarios"]["scenarios"][0]["required_parameters"] = 123
        errors = validate_payloads(payloads)
        self.assertIn(
            "scenarios.json.scenarios[0].required_parameters: expected array",
            errors,
        )

    def test_scenario_applicability_is_closed_and_uses_supported_citizenship_groups(self):
        payloads = copy.deepcopy(live_payloads())
        payloads["scenarios"]["scenarios"][0]["applicability"] = {
            "citizenship_group": ["unsupported_group"]
        }
        errors = validate_payloads(payloads)
        self.assertIn(
            "scenarios.json.scenarios[0].applicability.citizenship_group: unsupported value",
            errors,
        )

    def test_scenario_conflict_source_must_exist_and_be_listed_on_the_scenario(self):
        payloads = copy.deepcopy(live_payloads())
        scenario = payloads["scenarios"]["scenarios"][0]
        scenario["conflicts"] = [
            {"source_id": "missing-source", "conflict_type": "effective-date"}
        ]
        errors = validate_payloads(payloads)
        self.assertIn(
            "scenarios.json.scenarios[0].conflicts[0].source_id: unknown source reference",
            errors,
        )

        scenario["conflicts"][0]["source_id"] = "mos-permanent-residence"
        errors = validate_payloads(payloads)
        self.assertIn(
            "scenarios.json.scenarios[0].conflicts[0].source_id: conflict source must also appear in source_ids",
            errors,
        )

    def test_scenario_channel_rules_are_closed_and_reference_known_channels(self):
        payloads = copy.deepcopy(live_payloads())
        scenario = next(
            item
            for item in payloads["scenarios"]["scenarios"]
            if item["id"] == "first-address-and-pesel"
        )
        scenario["channel_rules"][0]["channel_ids"] = ["missing-channel"]
        errors = validate_payloads(payloads)
        self.assertTrue(
            any(error.endswith("unknown digital-channel reference") for error in errors),
            errors,
        )

        payloads = copy.deepcopy(live_payloads())
        scenario = next(
            item
            for item in payloads["scenarios"]["scenarios"]
            if item["id"] == "first-address-and-pesel"
        )
        scenario["channel_rules"][0]["channel_ids"] = ["mos"]
        scenario["channel_rules"][0]["when"]["matter"] = ["residence"]
        errors = validate_payloads(payloads)
        self.assertTrue(
            any(
                error.endswith("channel rule must share an official source with the scenario")
                for error in errors
            ),
            errors,
        )
        self.assertTrue(
            any(error.endswith("fact must be declared as a scenario parameter") for error in errors),
            errors,
        )

    def test_nested_action_value_with_wrong_type_is_rejected(self):
        payloads = copy.deepcopy(live_payloads())
        payloads["action-boundaries"]["boundaries"][0]["allowed"][0] = {
            "command": "not-allowed"
        }
        errors = validate_payloads(payloads)
        self.assertIn(
            "action-boundaries.json.boundaries[0].allowed[0]: expected string",
            errors,
        )

    def test_unknown_cross_dataset_source_reference_is_rejected(self):
        payloads = copy.deepcopy(live_payloads())
        payloads["terms"]["terms"][0]["source_ids"] = ["missing-source"]
        errors = validate_payloads(payloads)
        self.assertIn(
            "terms.json.terms[0].source_ids[0]: unknown source reference",
            errors,
        )

    def test_new_schema_objects_are_closed(self):
        expected = {
            "scenario.schema.json": "scenario",
            "term.schema.json": "term",
            "region.schema.json": "region",
            "action-boundary.schema.json": "boundary",
            "digital-channel.schema.json": "channel",
        }
        for filename, definition in expected.items():
            schema = json.loads((ROOT / "schemas" / filename).read_text(encoding="utf-8"))
            self.assertFalse(schema["additionalProperties"], filename)
            self.assertFalse(schema["$defs"][definition]["additionalProperties"], filename)

    def test_digital_channel_contract_rejects_unknown_fields_and_unsafe_public_auth(self):
        payloads = copy.deepcopy(live_payloads())
        payloads["digital-channels"]["channels"][0]["unexpected"] = True
        errors = validate_payloads(payloads)
        self.assertIn(
            "digital-channels.json.channels[0].unexpected: unsupported field",
            errors,
        )

        payloads = copy.deepcopy(live_payloads())
        public_channel = next(
            item
            for item in payloads["digital-channels"]["channels"]
            if item["access_scope"] == "public"
        )
        public_channel["authentication_categories"] = ["login_gov_pl"]
        errors = validate_payloads(payloads)
        self.assertTrue(
            any(error.endswith("public channel must not require authentication") for error in errors),
            errors,
        )

    def test_digital_channel_source_references_are_closed(self):
        payloads = copy.deepcopy(live_payloads())
        payloads["digital-channels"]["channels"][0]["source_ids"] = ["missing-source"]
        errors = validate_payloads(payloads)
        self.assertIn(
            "digital-channels.json.channels[0].source_ids[0]: unknown source reference",
            errors,
        )

    def test_operator_and_handoff_modes_are_strictly_enumerated(self):
        payloads = copy.deepcopy(live_payloads())
        epuap = next(
            item for item in payloads["digital-channels"]["channels"] if item["id"] == "epuap"
        )
        self.assertEqual("human_in_loop_operator", epuap["agent_mode"])
        trusted_profile = next(
            item
            for item in payloads["digital-channels"]["channels"]
            if item["id"] == "profil-zaufany"
        )
        self.assertEqual("user_handoff_then_stop", trusted_profile["agent_mode"])
        self.assertEqual([], validate_payloads(payloads))

        epuap["agent_mode"] = "autonomous_external_effect"
        errors = validate_payloads(payloads)
        self.assertTrue(
            any(error.endswith("unsupported value") for error in errors),
            errors,
        )

    def test_interface_and_receipt_contracts_are_closed_and_provenance_complete(self):
        response = json.loads((ROOT / "schemas" / "response.schema.json").read_text(encoding="utf-8"))
        for definition in ("citation", "error"):
            self.assertFalse(response["$defs"][definition]["additionalProperties"], definition)
        for definition in ("success", "failure"):
            self.assertFalse(response["$defs"][definition]["allOf"][1]["additionalProperties"], definition)
        citation_required = set(response["$defs"]["citation"]["required"])
        self.assertTrue(
            {"publisher", "source_tier", "accessed_at", "effective_period", "locator"}
            <= citation_required
        )

        receipt = json.loads(
            (ROOT / "schemas" / "evidence-receipt.schema.json").read_text(encoding="utf-8")
        )
        self.assertFalse(receipt["additionalProperties"])
        self.assertTrue(
            {"publisher", "source_tier", "source_accessed_at", "effective_period", "locator", "supports"}
            <= set(receipt["required"])
        )


if __name__ == "__main__":
    unittest.main()
