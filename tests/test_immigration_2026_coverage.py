from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def keyed(filename: str, collection: str) -> dict[str, dict[str, object]]:
    payload = json.loads((ROOT / "data" / filename).read_text(encoding="utf-8"))
    return {item["id"]: item for item in payload[collection]}


class Immigration2026CoverageTests(unittest.TestCase):
    def test_cukr_and_pesel_ukr_transition_sources_are_dated_and_scoped(self):
        sources = keyed("sources.json", "sources")
        expected = {
            "udsc-cukr-procedure",
            "udsc-ukraine-status-transition-2026",
            "sejm-ukraine-transition-act-2026",
            "gov-pesel-ukr-passport-update-2026",
        }
        self.assertTrue(expected <= set(sources))

        for source_id in expected:
            source = sources[source_id]
            self.assertEqual("active", source["status"], source_id)
            self.assertEqual("2026-08-20", source["accessed_at"], source_id)
            self.assertEqual("2026-08-20", source["last_verified"], source_id)

        self.assertEqual(["api.sejm.gov.pl"], sources["sejm-ukraine-transition-act-2026"]["domains"])
        for source_id in expected - {"sejm-ukraine-transition-act-2026"}:
            self.assertEqual(["gov.pl"], sources[source_id]["domains"], source_id)

        legal_source = sources["sejm-ukraine-transition-act-2026"]
        self.assertEqual("T0", legal_source["source_tier"])
        self.assertEqual("legal_text", legal_source["source_kind"])
        self.assertEqual({"type": "article", "value": "Articles 25-26"}, legal_source["locator"])
        legal_notes = str(legal_source["notes"]).lower()
        for phrase in ("article 25", "2026-08-31", "article 26", "60-day", "do not collapse"):
            self.assertIn(phrase, legal_notes)

        deadline_source = sources["gov-pesel-ukr-passport-update-2026"]
        self.assertEqual("2026-08-31", deadline_source["effective_to"])
        notes = str(deadline_source["notes"]).lower()
        for phrase in ("outreach notice", "lacked a passport", "child lacked a passport", "60-day", "do not apply"):
            self.assertIn(phrase, notes)

        cukr_source = sources["udsc-cukr-procedure"]
        self.assertEqual("2026-05-04", cukr_source["effective_from"])
        self.assertIn("eligibility conclusion", str(cukr_source["notes"]).lower())

    def test_cukr_and_pesel_routes_keep_user_only_and_confirmation_boundaries(self):
        scenarios = keyed("scenarios.json", "scenarios")

        cukr = scenarios["cukr-residence-card-transition"]
        self.assertEqual(["poland-protection-referral"], cukr["owner_skill_ids"])
        self.assertTrue(
            {
                "udsc-cukr-procedure",
                "udsc-ukraine-status-transition-2026",
                "mos-residence",
            }
            <= set(cukr["source_ids"])
        )
        self.assertTrue(
            {
                "eligibility_conclusion",
                "authentication",
                "user_only_signature",
                "sensitive_attachment_upload",
                "payment_initiation",
                "application_submission",
            }
            <= set(cukr["stop_before"])
        )

        pesel_update = scenarios["pesel-ukr-passport-data-update-2026"]
        self.assertEqual(["poland-protection-referral"], pesel_update["owner_skill_ids"])
        self.assertIn("gov-pesel-ukr-passport-update-2026", pesel_update["source_ids"])
        self.assertIn("sejm-ukraine-transition-act-2026", pesel_update["source_ids"])
        self.assertTrue(
            {
                "affected_group_conclusion",
                "legal_effect_conclusion",
                "official_record_change",
                "user_only_identity_presentation",
            }
            <= set(pesel_update["stop_before"])
        )
        self.assertIn("problem_type", pesel_update["required_parameters"])
        self.assertIn("gmina", pesel_update["required_parameters"])

    def test_permanent_residence_has_a_dedicated_non_citizenship_route(self):
        sources = keyed("sources.json", "sources")
        scenarios = keyed("scenarios.json", "scenarios")
        terms = keyed("terms.json", "terms")

        permanent_source = sources["mos-permanent-residence"]
        self.assertIn("/permanent-residence-permit/", permanent_source["url"])
        self.assertEqual("Office for Foreigners", permanent_source["authority"])
        self.assertEqual("2026-08-20", permanent_source["last_verified"])

        permanent = scenarios["permanent-residence-permit-route"]
        self.assertEqual(["poland-citizenship-long-term"], permanent["owner_skill_ids"])
        self.assertIn("mos-permanent-residence", permanent["source_ids"])
        self.assertNotIn("gov-citizenship", permanent["source_ids"])
        self.assertNotIn("udsc-long-term-eu-resident", permanent["source_ids"])
        self.assertTrue(
            {"eligibility_conclusion", "user_only_signature", "application_submission"}
            <= set(permanent["stop_before"])
        )
        self.assertIn("mos-permanent-residence", terms["zezwolenie-na-pobyt-staly"]["source_ids"])

    def test_terms_skills_reference_map_and_mos_channel_are_connected(self):
        terms = keyed("terms.json", "terms")
        channels = keyed("digital-channels.json", "channels")

        self.assertEqual(
            {"pesel-ukr", "status-ukr", "karta-pobytu-cukr"},
            {term_id for term_id in terms if term_id in {"pesel-ukr", "status-ukr", "karta-pobytu-cukr"}},
        )

        mos = channels["mos"]
        self.assertIn("mos-residence", mos["source_ids"])
        self.assertTrue(
            {"applicant_group", "filing_window", "status_transition"}
            <= set(mos["live_verify"])
        )
        self.assertIn("signature_confirmation", mos["stop_before"])
        self.assertIn("final_submission", mos["stop_before"])

        protection = (ROOT / "skills" / "poland-protection-referral" / "SKILL.md").read_text(encoding="utf-8")
        long_term = (ROOT / "skills" / "poland-citizenship-long-term" / "SKILL.md").read_text(encoding="utf-8")
        status_map = (ROOT / "references" / "immigration-status-map.md").read_text(encoding="utf-8")
        for source_id in (
            "udsc-cukr-procedure",
            "udsc-ukraine-status-transition-2026",
            "sejm-ukraine-transition-act-2026",
            "gov-pesel-ukr-passport-update-2026",
        ):
            self.assertIn(source_id, protection)
            self.assertIn(source_id, status_map)
        self.assertIn("mos-permanent-residence", long_term)
        self.assertIn("mos-permanent-residence", status_map)


if __name__ == "__main__":
    unittest.main()
