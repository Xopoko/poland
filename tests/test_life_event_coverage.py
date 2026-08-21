from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def records(filename: str, key: str) -> list[dict[str, object]]:
    return json.loads((ROOT / "data" / filename).read_text(encoding="utf-8"))[key]


ADDED_SCENARIO_IDS = {
    "adult-disability-route",
    "annual-pit-route",
    "bank-safety-and-financial-complaint",
    "birth-registration",
    "child-disability-route",
    "citizenship-recognition-or-confirmation",
    "civil-marriage-and-name-change",
    "court-case-and-electronic-delivery",
    "crime-victim-support",
    "criminal-record-certificate",
    "death-and-funeral-route",
    "disability-support-and-pfron",
    "discrimination-and-public-rights",
    "education-support-needs",
    "ekuz-cross-border-healthcare",
    "eu-citizen-and-family-residence",
    "family-childcare-benefits",
    "foreign-health-coverage",
    "foreign-school-certificate-recognition",
    "higher-education-route",
    "housing-assistance",
    "inheritance-and-donation-tax",
    "long-term-resident-route",
    "lost-or-stolen-polish-document",
    "penalty-points-and-vehicle-records",
    "pesel-record-and-fraud-protection",
    "privacy-and-data-complaint",
    "private-transaction-tax",
    "property-register-and-tax",
    "purpose-specific-residence",
    "retirement-survivor-pension",
    "senior-or-home-care-support",
    "sickness-maternity-care-benefit",
    "treatment-provider-search",
    "unemployment-registration",
    "utilities-and-waste",
    "vehicle-registration-and-transfer",
    "voter-register-and-polling-place",
}

ADDED_CHANNEL_IDS = {
    "central-voter-register",
    "cepik",
    "civil-status-services",
    "court-information-portal",
    "criminal-record-certificate",
    "free-legal-aid-booking",
    "land-registers",
    "nfz-treatment-dates",
    "pesel-services",
    "pfron-sow",
    "victim-support-directory",
    "vehicle-services",
    "waste-recipient-search",
    "your-e-pit",
}

LIFE_EVENT_SOURCE_IDS = {
    "residence": {
        "udsc-eu-citizens-family",
        "mos-temporary-stay-checklists",
        "mos-stay-purposes",
        "udsc-long-term-eu-resident",
        "gov-citizenship-recognition",
        "gov-citizenship-confirmation",
    },
    "identity-and-civil-status": {
        "gov-pesel-register-data",
        "gov-pesel-reservation",
        "gov-lost-id-card",
        "gov-lost-passport",
        "gov-birth-registration",
        "gov-civil-marriage",
        "gov-death-registration",
        "gov-name-change",
    },
    "tax-social-insurance-and-family": {
        "tax-your-e-pit",
        "tax-pit",
        "tax-pcc",
        "gov-pcc-filing",
        "tax-inheritance-donations",
        "gov-sd-z2",
        "zus-cash-benefits",
        "zus-pensions",
        "zus-disability-survivor-pensions",
        "zus-funeral-benefit",
        "family-800-plus",
        "active-parent",
    },
    "disability": {
        "gov-disability-determination-adult",
        "gov-disability-determination-child",
        "gov-disability-parking-card",
        "gov-supporting-benefit",
        "pfron-sow",
    },
    "health-education-and-work": {
        "gov-ekuz",
        "nfz-treatment-dates",
        "healthcare-foreigners",
        "education-psychological-counselling",
        "education-school-certificate-recognition",
        "higher-education-foreigners",
        "gov-unemployment-registration",
    },
    "housing-utilities-vehicles-and-elections": {
        "gov-housing-allowance",
        "gov-property-tax",
        "ure-household-energy",
        "ure-consumer-disputes",
        "gios-waste-recipients",
        "gov-land-registers",
        "gov-vehicle-registration",
        "gov-vehicle-transfer-notice",
        "gov-penalty-points",
        "cepik-services",
        "gov-central-voter-register",
        "gov-change-voting-place",
    },
    "justice-rights-banking-and-safety": {
        "justice-court-information-portal",
        "gov-criminal-record-certificate",
        "uodo-complaints",
        "rpo-equal-treatment",
        "rpo-migrants",
        "bfg-deposit-guarantee",
        "justice-victim-support",
        "free-legal-aid-general",
    },
}


class LifeEventCoverageTests(unittest.TestCase):
    def test_life_event_clusters_have_current_official_source_records(self):
        by_id = {item["id"]: item for item in records("sources.json", "sources")}
        expected = set().union(*LIFE_EVENT_SOURCE_IDS.values())
        self.assertEqual(58, len(expected))
        self.assertTrue(expected <= set(by_id))
        for source_id in expected:
            source = by_id[source_id]
            self.assertEqual("2026-08-20", source["accessed_at"], source_id)
            self.assertEqual("2026-08-20", source["last_verified"], source_id)
            self.assertEqual("active", source["status"], source_id)
            self.assertTrue(source["publisher"], source_id)
            self.assertTrue(source["url"].startswith("https://"), source_id)

    def test_new_scenarios_are_source_backed_and_preserve_local_uncertainty(self):
        source_ids = {item["id"] for item in records("sources.json", "sources")}
        skill_ids = {path.parent.name for path in (ROOT / "skills").glob("*/SKILL.md")}
        by_id = {item["id"]: item for item in records("scenarios.json", "scenarios")}
        self.assertTrue(ADDED_SCENARIO_IDS <= set(by_id))
        for scenario_id in ADDED_SCENARIO_IDS:
            scenario = by_id[scenario_id]
            self.assertTrue(set(scenario["source_ids"]) <= source_ids, scenario_id)
            self.assertTrue(set(scenario["owner_skill_ids"]) <= skill_ids, scenario_id)
            purpose = scenario["purpose"].lower()
            self.assertIn("appointment", purpose, scenario_id)
            self.assertTrue(
                any(token in purpose for token in ("local", "gmina", "voivod", "office", "court", "authority", "provider", "institution")),
                scenario_id,
            )
            self.assertTrue(scenario["stop_before"], scenario_id)
            self.assertTrue(scenario["escalate_when"], scenario_id)

    def test_new_channels_are_live_verified_and_do_not_claim_bundled_connectors(self):
        source_ids = {item["id"] for item in records("sources.json", "sources")}
        by_id = {item["id"]: item for item in records("digital-channels.json", "channels")}
        self.assertTrue(ADDED_CHANNEL_IDS <= set(by_id))
        for channel_id in ADDED_CHANNEL_IDS:
            channel = by_id[channel_id]
            self.assertTrue(set(channel["source_ids"]) <= source_ids, channel_id)
            self.assertTrue(channel["live_verify"], channel_id)
            self.assertTrue(channel["stop_before"], channel_id)
            notes = channel["notes"].lower()
            self.assertIn("appointment", notes, channel_id)
            self.assertTrue(
                any(token in notes for token in ("verify", "vary", "uncertain", "not ")),
                channel_id,
            )
            if channel["agent_mode"] == "human_in_loop_operator":
                self.assertIn("no ", notes, channel_id)
                self.assertIn("connector", notes, channel_id)

    def test_operator_modes_are_explicit_in_both_public_schemas(self):
        for filename in ("source-registry.schema.json", "digital-channel.schema.json"):
            schema = json.loads((ROOT / "schemas" / filename).read_text(encoding="utf-8"))
            definition = "source" if filename.startswith("source") else "channel"
            modes = set(schema["$defs"][definition]["properties"]["automation" if definition == "source" else "agent_mode"]["enum"])
            self.assertIn("human_in_loop_operator", modes, filename)
            self.assertIn("user_handoff_then_stop", modes, filename)


if __name__ == "__main__":
    unittest.main()
