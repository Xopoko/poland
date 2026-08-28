from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lib"))

import poland_core as core  # noqa: E402


class OntologyAndRealityTests(unittest.TestCase):
    def test_ontology_counts_and_relationships_are_derived_from_live_registries(self):
        result = core.ontology_map(as_of="2026-08-28")
        layers = {item["id"]: item for item in result["layers"]}
        self.assertEqual(len(core.all_sources()), layers["evidence"]["record_count"])
        self.assertEqual(len(core._scenario_records()), layers["services"]["record_count"])
        self.assertEqual(len(core.all_digital_channels()), layers["channels"]["record_count"])
        self.assertEqual(0, result["summary"]["broken_edges"])

        relationships = {item["id"]: item for item in result["relationships"]}
        expected_scenario_sources = sum(
            len(item["source_ids"]) for item in core._scenario_records()
        )
        self.assertEqual(
            expected_scenario_sources,
            relationships["service-references-evidence"]["edge_count"],
        )
        self.assertEqual(
            relationships["service-references-evidence"]["edge_count"],
            relationships["service-references-evidence"]["resolved"],
        )
        self.assertEqual(
            relationships["service-selects-channel-by-rule"]["edge_count"],
            relationships["service-selects-channel-by-rule"]["resolved"],
        )
        encoded = json.dumps(result, ensure_ascii=False).encode("utf-8")
        self.assertLess(len(encoded), 196608)
        schema = json.loads(
            (ROOT / "schemas" / "ontology-map.schema.json").read_text(encoding="utf-8")
        )
        identifier_pattern = schema["$defs"]["identifier"]["pattern"]
        self.assertTrue(
            all(re.fullmatch(identifier_pattern, item["entity_type"]) for item in result["layers"])
        )

    def test_full_coverage_distinguishes_direct_unlinked_and_discovery_paths(self):
        result = core.ontology_map(detail="full", as_of="2026-08-28")
        coverage = {item["id"]: item for item in result["coverage"]}
        self.assertEqual(
            {
                "dolnoslaskie-foreigners",
                "malopolskie-foreigners",
                "mazowieckie-foreigners",
                "wielkopolskie-foreigners",
            },
            set(coverage["direct-source-linkage"]["ids"]),
        )
        self.assertEqual([], coverage["source-discovery-reachability"]["ids"])
        current = coverage["current-source-evidence"]
        self.assertEqual(current["total"] - current["observed"], len(current["ids"]))
        self.assertGreater(
            len(coverage["explicit-service-applicability"]["ids"]),
            0,
        )
        self.assertTrue(
            {"topic-taxonomy", "locality-to-region", "checkpoint-to-action-boundary"}
            <= {item["id"] for item in result["unmodeled"]}
        )

    def test_layer_projection_is_bounded_without_changing_global_summary(self):
        full = core.ontology_map(as_of="2026-08-28")
        evidence = core.ontology_map(layer="evidence", as_of="2026-08-28")
        self.assertEqual(full["summary"], evidence["summary"])
        self.assertEqual(["evidence"], [item["id"] for item in evidence["layers"]])
        self.assertTrue(
            all(
                "evidence" in {item["from_layer"], item["to_layer"]}
                for item in evidence["relationships"]
            )
        )
        self.assertEqual([], evidence["unmodeled"])

    def test_reality_projection_keeps_global_problem_ids_and_bounds_records(self):
        complete = core.freshness_report("2026-08-28", summary_only=True)
        projected = core.freshness_report(
            "2026-08-28",
            statuses=["review_due"],
            topic="residence",
            limit=2,
        )
        self.assertEqual(complete["summary"], projected["summary"])
        self.assertEqual(complete["problem_source_ids"], projected["problem_source_ids"])
        self.assertEqual([], complete["sources"])
        self.assertEqual([], complete["repair_queue"])
        self.assertTrue(complete["projection"]["truncated"])
        self.assertTrue(complete["projection"]["queue_truncated"])
        self.assertEqual(
            complete["repair_summary"].keys(),
            complete["problem_source_ids_by_issue"].keys(),
        )
        self.assertLessEqual(len(projected["sources"]), 2)
        self.assertTrue(all(item["status"] == "review_due" for item in projected["sources"]))
        returned_ids = {item["source_id"] for item in projected["sources"]}
        self.assertTrue(
            all(item["source_id"] in returned_ids for item in projected["repair_queue"])
        )

        future = core.freshness_report("2030-08-20", limit=100)
        self.assertLessEqual(len(future["repair_queue"]), 64)
        self.assertTrue(future["projection"]["queue_truncated"])
        self.assertLess(len(json.dumps(future, ensure_ascii=False).encode("utf-8")), 196608)

    def test_reality_queue_preserves_conflicts_and_safe_verification_routes(self):
        audit = core.source_reality_audit("2026-08-28")
        conflicts = [
            item
            for item in audit["repair_queue"]
            if item["issue_code"] == "SCENARIO_SOURCE_CONFLICT"
        ]
        self.assertEqual(2, len(conflicts))
        self.assertEqual(
            {"affected-group-scope", "legal-effect-certainty"},
            {item["conflict_type"] for item in conflicts},
        )
        self.assertTrue(all(item["verification_route"] == "browser" for item in conflicts))
        self.assertTrue(
            all(
                item["next_step"]
                == "compare_all_scenario_sources_and_preserve_unresolved_conflict"
                for item in conflicts
            )
        )
        self.assertTrue(all(item["automatic_update_allowed"] is False for item in conflicts))
        self.assertNotIn("SOURCE_ORPHANED", audit["repair_summary"])

        validation = core.validate_bundle("2026-08-28")
        self.assertIn(
            "gov-pesel-ukr-passport-update-2026",
            validation["reality"]["problem_source_ids"],
        )
        self.assertTrue(
            any(
                warning.startswith("SCENARIO_SOURCE_CONFLICT:")
                for warning in validation["warnings"]
            )
        )

    def test_future_verification_metadata_is_not_masked_by_effective_state(self):
        sources = core.all_sources()
        source = next(item for item in sources if item["id"] == "udsc-home")
        source["last_verified"] = "2027-02-01"
        source["effective_from"] = "2027-01-01"
        with mock.patch.object(core, "all_sources", return_value=sources):
            audit = core.source_reality_audit("2026-08-28")
        issue_codes = {
            item["issue_code"]
            for item in audit["repair_queue"]
            if item["source_id"] == "udsc-home"
        }
        self.assertIn("SOURCE_VERIFICATION_DATE_IN_FUTURE", issue_codes)
        self.assertIn("SOURCE_NOT_YET_EFFECTIVE", issue_codes)

    def test_freshness_rejects_malformed_status_iterables_with_contract_error(self):
        for value in (123, [["review_due"]], {"review_due": True}):
            with self.subTest(value=value), self.assertRaises(core.PolandDataError):
                core.freshness_report("2026-08-28", statuses=value)

    def test_meldunek_and_mobywatel_axes_are_explicit(self):
        meldunek = core.get_source("gov-meldunek-foreigners")
        self.assertEqual("public", meldunek["access"])
        self.assertEqual("public_read_only_handoff", meldunek["automation"])
        scenario = next(
            item for item in core._scenario_records() if item["id"] == "first-address-and-pesel"
        )
        self.assertIn("pesel_status", scenario["required_parameters"])
        self.assertIn("delivery_channel", scenario["optional_parameters"])
        self.assertIn("eu_efta_family_member_status", scenario["optional_parameters"])
        self.assertTrue(scenario["channel_rules"])
        self.assertNotIn("polish", scenario["applicability"]["citizenship_group"])

        web_source = core.get_source("mobywatel-web")
        mobile_source = core.get_source("mobywatel-mobile")
        self.assertEqual("public", web_source["access"])
        self.assertEqual("public", mobile_source["access"])
        self.assertNotEqual(web_source["url"], mobile_source["url"])
        web_channel = core.get_digital_channel("mobywatel-web", as_of="2026-08-28")
        mobile_channel = core.get_digital_channel("mobywatel-mobile", as_of="2026-08-28")
        self.assertIn("submit_application", web_channel["protected_surface"])
        self.assertIn("present_digital_document", mobile_channel["protected_surface"])
        self.assertNotEqual(web_channel["agent_mode"], mobile_channel["agent_mode"])

    def test_foreigner_meldunek_channel_rules_preserve_legal_profile_branches(self):
        common = {
            "gmina": "warsaw",
            "procedure": "permanent",
            "residence_status": "current",
        }
        third_country_online = core.route_scenario(
            "first-address-and-pesel",
            {
                "facts": {
                    **common,
                    "citizenship_group": "third_country",
                    "delivery_channel": "online",
                    "eu_efta_family_member_status": "absent",
                    "pesel_status": "present",
                }
            },
            as_of="2026-08-28",
        )
        self.assertEqual("unavailable", third_country_online["channel_selection"]["state"])
        self.assertEqual([], third_country_online["digital_channels"])
        self.assertIn(
            "REQUESTED_CHANNEL_UNAVAILABLE_FOR_PROFILE",
            third_country_online["channel_selection"]["warnings"],
        )

        third_country_office = core.route_scenario(
            "first-address-and-pesel",
            {
                "facts": {
                    **common,
                    "citizenship_group": "third_country",
                    "delivery_channel": "in_person",
                    "eu_efta_family_member_status": "absent",
                    "pesel_status": "absent",
                }
            },
            as_of="2026-08-28",
        )
        self.assertEqual(
            "third-country-office-no-pesel",
            third_country_office["channel_selection"]["matched_rule_id"],
        )
        self.assertIn("personal_appearance", third_country_office["channel_selection"]["requirements"])

        eu_online = core.route_scenario(
            "first-address-and-pesel",
            {
                "facts": {
                    **common,
                    "citizenship_group": "eu_eea_swiss",
                    "delivery_channel": "online",
                    "pesel_status": "present",
                }
            },
            as_of="2026-08-28",
        )
        self.assertEqual(
            {"mobywatel-web", "profil-zaufany"},
            {item["id"] for item in eu_online["digital_channels"]},
        )

        unresolved_family = core.route_scenario(
            "first-address-and-pesel",
            {
                "facts": {
                    **common,
                    "citizenship_group": "third_country",
                    "delivery_channel": "online",
                    "pesel_status": "present",
                }
            },
            as_of="2026-08-28",
        )
        self.assertEqual("unresolved", unresolved_family["channel_selection"]["state"])
        self.assertIn("eu_efta_family_member_status", unresolved_family["missing_intake"])


if __name__ == "__main__":
    unittest.main()
