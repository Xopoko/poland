from __future__ import annotations

import json
import sys
import unittest
from datetime import date, datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lib"))

import poland_core as core  # noqa: E402
import contract_validation as contracts  # noqa: E402


class CoreTests(unittest.TestCase):
    def test_bundle_is_strict_validated_and_sized(self):
        report = core.validate_bundle("2026-08-21")
        self.assertTrue(report["valid"], report["errors"])
        self.assertEqual("OFFLINE_PACKAGED_DATA", report["data_mode"])
        self.assertEqual(135, report["counts"]["sources"])
        self.assertEqual(71, report["counts"]["scenarios"])
        self.assertEqual(114, report["counts"]["terms"])
        self.assertEqual(16, report["counts"]["regions"])
        self.assertEqual(36, report["counts"]["digital_channels"])
        self.assertRegex(report["bundle_sha256"], r"^[0-9a-f]{64}$")

    def test_sources_have_complete_provenance_and_safe_runtime_modes(self):
        sources = core.all_sources()
        self.assertEqual(len(sources), len({item["id"] for item in sources}))
        for item in sources:
            self.assertTrue(item["url"].startswith("https://"))
            self.assertLessEqual(date.fromisoformat(item["last_verified"]), date(2026, 8, 21))
            self.assertLessEqual(date.fromisoformat(item["accessed_at"]), date(2026, 8, 21))
            self.assertTrue(item["publisher"])
            self.assertIn(item["source_tier"], {"T0", "T1", "T2"})
            self.assertIn(
                item["locator"]["type"],
                {"page", "heading", "article", "paragraph", "annex", "table_row", "form_field"},
            )
            self.assertIn(
                item["automation"],
                {
                    "human_in_loop_operator",
                    "public_read_only",
                    "public_read_only_handoff",
                    "prohibited_external_effect",
                    "user_handoff_then_stop",
                },
            )

    def test_current_source_regressions(self):
        self.assertEqual("https://www.podatki.gov.pl/en", core.get_source("podatki-home")["url"])
        self.assertTrue(core.get_source("sworn-translators")["url"].endswith("/tlumacze-przysiegli"))
        self.assertTrue(core.get_source("apostille")["url"].endswith("/certification-of-documents"))
        drivers_act = core.get_source("drivers-act-consolidated")
        self.assertEqual("T0", drivers_act["source_tier"])
        self.assertEqual("article", drivers_act["locator"]["type"])
        self.assertEqual("Ministry of Infrastructure", core.get_source("gov-driving-licence-exchange")["authority"])

    def test_search_filters_and_accent_normalization(self):
        results = core.search_sources("PESEL", topic="identity")
        self.assertTrue(any(item["id"] == "gov-pesel-foreigners" for item in results))
        terms = core.lookup_terms("tlumacz")
        self.assertEqual("tlumacz-przysiegly", terms[0]["id"])

    def test_polish_query_normalization_and_powiat_route_fact(self):
        self.assertEqual("lodz zolc", core.normalize_text("Łódź Żółć"))
        self.assertEqual(
            "Jak wymienić prawo jazdy",
            core.validate_literal_query("Jak wymienić prawo jazdy"),
        )
        profile = core.validate_route_profile(
            {"facts": {"powiat": "poznański"}}
        )
        self.assertEqual("poznański", profile["facts"]["powiat"])
        self.assertIn("powiat", contracts.JURISDICTIONS)
        schema = json.loads(
            (ROOT / "schemas" / "source-registry.schema.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertIn(
            "powiat",
            schema["$defs"]["source"]["properties"]["jurisdiction"]["enum"],
        )

    def test_digital_channel_catalog_is_source_backed_and_fail_closed(self):
        self.assertEqual(36, len(core.all_digital_channels()))
        mos = core.get_digital_channel("mos", as_of="2026-08-20")
        self.assertEqual("caller_owned_operator", mos["channel_state"])
        self.assertTrue(mos["caller_owned_operator_eligible"])
        self.assertFalse(mos["bundled_interface_can_interact"])
        self.assertFalse(mos["protected_interaction_supported"])
        self.assertIn("submit_application", mos["protected_surface"])
        self.assertEqual(
            {"mos-residence", "udsc-mos-electronic-residence"},
            {item["id"] for item in mos["sources"]},
        )
        self.assertIn(
            "mos",
            {item["id"] for item in core.get_source("udsc-mos-electronic-residence")["digital_channels"]},
        )

        public = core.search_digital_channels(
            "registry", channel_kind="public_registry", access_scope="public", as_of="2026-08-20"
        )
        self.assertTrue(public)
        self.assertTrue(all(item["channel_state"] == "public_read_only" for item in public))

        stale = core.get_digital_channel("mos", as_of="2030-08-20")
        self.assertEqual("verification_required", stale["channel_state"])
        self.assertFalse(stale["evidence_gate"]["actionable"])

        sensitive_value = "person@example.com"
        with self.assertRaises(core.PolandDataError) as caught:
            core.search_digital_channels(sensitive_value)
        self.assertEqual("SENSITIVE_INPUT_REJECTED", caught.exception.code)
        self.assertNotIn(sensitive_value, json.dumps(caught.exception.as_dict()))

    def test_salvaged_routes_stay_compositional_and_undetermined_without_facts(self):
        for scenario_id in ("eu-blue-card", "settling-in-first-weeks"):
            with self.subTest(scenario_id=scenario_id):
                missing = core.route_scenario(scenario_id, as_of="2026-08-20")
                self.assertEqual(scenario_id, missing["id"])
                self.assertEqual("undetermined", missing["route_state"])
                self.assertFalse(missing["eligibility_assessed"])
                self.assertTrue(missing["missing_intake"])

        blue_card = core.route_scenario(
            "eu-blue-card",
            {
                "facts": {
                    "citizenship_group": "third_country",
                    "current_location_category": "inside_poland",
                    "current_status_category": "temporary_stay",
                    "contract_type": "employment_contract",
                    "employer_location": "mazowieckie",
                }
            },
            as_of="2026-08-20",
        )
        self.assertEqual("candidate", blue_card["route_state"])
        self.assertEqual("multi", blue_card["composition"])
        self.assertIn("mos-eu-blue-card", blue_card["source_ids"])
        self.assertIn("mos", {item["id"] for item in blue_card["digital_channels"]})

        first_weeks = core.route_scenario(
            "settling-in-first-weeks",
            {
                "facts": {
                    "current_location_category": "inside_poland",
                    "household_context": "single_adult",
                    "voivodeship": "mazowieckie",
                }
            },
            as_of="2026-08-20",
        )
        self.assertEqual("candidate", first_weeks["route_state"])
        self.assertEqual("multi", first_weeks["composition"])
        self.assertGreaterEqual(len(first_weeks["owner_skill_ids"]), 5)

    def test_unknown_source_invalid_limit_and_sensitive_search_fail_closed(self):
        with self.assertRaises(core.PolandDataError):
            core.get_source("not-a-source")
        with self.assertRaises(core.PolandDataError):
            core.search_sources(limit=101)
        with self.assertRaises(core.PolandDataError) as caught:
            core.search_sources("person@example.com")
        self.assertEqual("SENSITIVE_INPUT_REJECTED", caught.exception.code)
        self.assertNotIn("person@example.com", json.dumps(caught.exception.as_dict()))

    def test_every_golden_scenario_routes_to_expected_owner_and_source(self):
        fixture = json.loads(
            (ROOT / "tests" / "fixtures" / "scenario-golden-cases.json").read_text(
                encoding="utf-8"
            )
        )
        for case in fixture["cases"]:
            with self.subTest(case=case):
                result = core.route_scenario(case["query"], as_of="2026-08-21")
                self.assertEqual(case["scenario_id"], result["id"])
                self.assertIn(case["required_source"], result["source_ids"])
                self.assertTrue(result["owner_skill_ids"])
                self.assertFalse(result["eligibility_assessed"])

    def test_route_matching_uses_three_valued_fail_closed_states(self):
        unsupported = core.route_scenario("unsupported gardening", as_of="2026-08-20")
        self.assertEqual("not_applicable", unsupported["route_state"])
        self.assertEqual("false", unsupported["match_truth"])

        missing = core.route_scenario("residence-next-step", as_of="2026-08-20")
        self.assertEqual("undetermined", missing["route_state"])
        self.assertEqual("unknown", missing["match_truth"])
        self.assertTrue(missing["missing_intake"])
        self.assertTrue(all(state == "unknown" for state in missing["parameter_states"].values()))

        complete = core.route_scenario(
            "residence-next-step",
            {
                "facts": {
                    "citizenship_group": "third_country",
                    "current_location_category": "inside_poland",
                    "current_status_category": "temporary_stay",
                    "target_procedure": "temporary_residence",
                    "voivodeship": "mazowieckie",
                }
            },
            as_of="2026-08-20",
        )
        self.assertEqual("candidate", complete["route_state"])
        self.assertEqual("true", complete["match_truth"])
        self.assertEqual([], complete["missing_intake"])

    def test_router_polish_golden_near_neighbor_and_ambiguity_cases(self):
        fixture = json.loads(
            (ROOT / "tests" / "fixtures" / "router-language-cases.json").read_text(
                encoding="utf-8"
            )
        )
        for case in fixture["positive_cases"]:
            with self.subTest(kind="positive", case=case):
                result = core.route_scenario(case["query"], as_of="2026-08-21")
                self.assertEqual(case["scenario_id"], result["id"])
                self.assertEqual("undetermined", result["route_state"])
                self.assertEqual("unknown", result["match_truth"])

        for case in fixture["negative_cases"]:
            with self.subTest(kind="negative", case=case):
                result = core.route_scenario(
                    case["query"],
                    case.get("profile"),
                    as_of="2026-08-21",
                )
                self.assertIsNone(result["id"])
                self.assertEqual("not_applicable", result["route_state"])
                self.assertEqual("false", result["match_truth"])
                self.assertEqual("insufficient_evidence", result["evidence_gate"]["state"])
                self.assertFalse(result["evidence_gate"]["actionable"])
                self.assertEqual([], result["evidence_gate"]["usable_for"])

        for case in fixture["ambiguous_cases"]:
            with self.subTest(kind="ambiguous", case=case):
                result = core.route_scenario(case["query"], as_of="2026-08-21")
                self.assertIsNone(result["id"])
                self.assertEqual("undetermined", result["route_state"])
                self.assertEqual("unknown", result["match_truth"])
                self.assertTrue(
                    set(case["candidate_subset"]).issubset(result["intent_candidates"])
                )
                self.assertEqual("insufficient_evidence", result["evidence_gate"]["state"])
                self.assertFalse(result["evidence_gate"]["actionable"])

    def test_route_inputs_are_closed_non_identifying_and_never_echoed(self):
        with self.assertRaises(core.PolandDataError) as unknown:
            core.route_scenario("residence", {"facts": {"passport_number": "XX0000000"}})
        self.assertEqual("UNSUPPORTED_FIELD", unknown.exception.code)
        self.assertNotIn("XX0000000", json.dumps(unknown.exception.as_dict()))

        with self.assertRaises(core.PolandDataError) as sensitive:
            core.route_scenario("my PESEL is 44051401458")
        self.assertEqual("SENSITIVE_INPUT_REJECTED", sensitive.exception.code)
        self.assertNotIn("44051401458", json.dumps(sensitive.exception.as_dict()))

        for unsafe_value in ("C:\\documents\\passport.pdf", "https://example.invalid/file"):
            with self.subTest(unsafe_value=unsafe_value):
                with self.assertRaises(core.PolandDataError) as non_abstract:
                    core.route_scenario(
                        "foreign-document-use",
                        {"facts": {"document_type": unsafe_value}},
                    )
                self.assertEqual("NON_ABSTRACT_INPUT_REJECTED", non_abstract.exception.code)
                self.assertNotIn(unsafe_value, json.dumps(non_abstract.exception.as_dict()))

    def test_checklist_suppresses_user_handoff_when_unknown_or_stale(self):
        unknown = core.build_checklist("residence-next-step", as_of="2026-08-20")
        self.assertEqual("undetermined", unknown["route_state"])
        self.assertIn("human-action", unknown["suppressed_phase_ids"])

        stale = core.build_checklist(
            "residence-next-step",
            {
                "facts": {
                    "citizenship_group": "third_country",
                    "current_location_category": "inside_poland",
                    "current_status_category": "temporary_stay",
                    "target_procedure": "temporary_residence",
                    "voivodeship": "mazowieckie",
                }
            },
            as_of="2030-08-20",
        )
        self.assertEqual("undetermined", stale["route_state"])
        self.assertEqual("stale", stale["evidence_gate"]["state"])
        self.assertIn("human-action", stale["suppressed_phase_ids"])
        self.assertIn("STALE_PACKAGED_DATA", stale["evidence_gate"]["warnings"])

    def test_conflicts_are_visible_and_suppress_actionability(self):
        gate = core.evidence_gate(
            ["udsc-home", "mos-residence"],
            as_of="2026-08-20",
            conflicts=[{"source_id": "mos-residence", "conflict_type": "effective-date"}],
        )
        self.assertEqual("conflict", gate["state"])
        self.assertFalse(gate["actionable"])
        self.assertEqual(["OFFICIAL_SOURCE_CONFLICT"], gate["warnings"])

    def test_regions_are_complete_and_searchable(self):
        self.assertEqual(16, len(core.list_regions()))
        self.assertEqual("mazowieckie", core.list_regions("Warsaw")[0]["id"])

    def test_freshness_states_are_explicit(self):
        current = core.freshness_report("2026-08-21")
        self.assertEqual(134, current["summary"]["fresh"])
        self.assertEqual(1, current["summary"]["out_of_effective_period"])
        later = core.freshness_report("2030-08-20")
        self.assertEqual(134, later["summary"]["stale"])
        self.assertEqual(1, later["summary"]["out_of_effective_period"])

    def test_effective_period_and_inactive_source_states_fail_closed(self):
        source = core.get_source("udsc-home")
        source["effective_from"] = "2027-01-01"
        future = core._source_freshness_record(source, core._as_of_date("2026-08-20"))
        self.assertEqual("out_of_effective_period", future["status"])
        source["effective_from"] = None
        source["status"] = "superseded"
        inactive = core._source_freshness_record(source, core._as_of_date("2026-08-20"))
        self.assertEqual("inactive", inactive["status"])

    def test_action_boundary_routes_confirmation_user_only_and_fail_closed(self):
        for action in ("submit application", "book appointment", "pay the fee"):
            with self.subTest(action=action):
                result = core.action_boundary(action)
                self.assertEqual("human-submit", result["id"])
                self.assertEqual(
                    "confirmation_gated_external_effect", result["automation"]
                )
                self.assertEqual("requires_confirmation", result["disposition"])
        login = core.action_boundary("login to MOS")
        self.assertEqual("user-only-restricted", login["id"])
        self.assertEqual("never", login["disposition"])
        unknown = core.action_boundary("teleport paperwork")
        self.assertEqual("user-only-restricted", unknown["id"])
        self.assertEqual("fail_closed_default", unknown["matched_by"])

    def test_scenario_stop_before_values_are_pause_and_classify_checkpoints(self):
        routed = core.route_scenario("residence-next-step", as_of="2026-08-20")
        self.assertEqual(
            "pause_and_classify_checkpoint", routed["stop_before_semantics"]
        )
        human_action = next(
            phase for phase in routed["phases"] if phase["id"] == "human-action"
        )
        self.assertTrue(human_action["actions"])
        self.assertTrue(
            all(action.startswith("Pause before ") for action in human_action["actions"])
        )
        self.assertTrue(
            all("classify the concrete action" in action for action in human_action["actions"])
        )
        self.assertFalse(
            any(action.startswith("Stop before ") for action in human_action["actions"])
        )

    def test_receipt_is_claim_level_source_bound_and_non_narrative(self):
        receipt = core.evidence_receipt(
            "udsc-home",
            "verified",
            content_sha256="a" * 64,
            locator_type="heading",
            locator_value="International protection",
            supports=["route.owner_skill_ids", "route.source_ids"],
            effective_from="2026-01-01",
            checked_at=datetime(2026, 8, 20, tzinfo=timezone.utc),
        )
        self.assertEqual("poland.evidence-receipt.v2", receipt["schema_version"])
        self.assertEqual("Office for Foreigners", receipt["publisher"])
        self.assertEqual("T1", receipt["source_tier"])
        self.assertEqual("International protection", receipt["locator"]["value"])
        self.assertEqual("2026-01-01", receipt["effective_period"]["from"])
        self.assertEqual("a" * 64, receipt["content_hash_sha256"])
        self.assertNotIn("observation", receipt)
        self.assertNotIn("inference", receipt)

    def test_shared_response_envelope_contains_complete_citations(self):
        result = core.route_scenario("citizenship procedure", as_of="2026-08-20")
        envelope = core.response_envelope("route", result, as_of="2026-08-20")
        self.assertEqual("poland.response.v1", envelope["contract"])
        self.assertTrue(envelope["ok"])
        self.assertEqual("OFFLINE_PACKAGED_DATA", envelope["data_mode"])
        citation = next(item for item in envelope["citations"] if item["source_id"] == "gov-citizenship")
        self.assertEqual("T1", citation["source_tier"])
        self.assertEqual("2026-08-20", citation["accessed_at"])
        self.assertIn("locator", citation)


if __name__ == "__main__":
    unittest.main()
