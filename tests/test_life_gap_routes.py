from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def keyed(filename: str, key: str) -> dict[str, dict[str, object]]:
    payload = json.loads((ROOT / "data" / filename).read_text(encoding="utf-8"))
    return {item["id"]: item for item in payload[key]}


SOURCE_URLS = {
    "gov-professional-qualifications-incoming": "https://www.gov.pl/web/nauka/informacje-dla-przyjezdzajacych/",
    "nawa-regulated-professions": "https://www.nawa.gov.pl/uznawalnosc/podjecie-pracy-w-polsce/zawody-regulowane",
    "ejustice-succession-poland": "https://e-justice.europa.eu/topics/family-matters-inheritance/inheritance/succession/pl_en",
    "ejustice-succession-authorities-poland": "https://e-justice.europa.eu/topics/taking-legal-action/european-judicial-atlas-civil-matters/succession/pl_en",
    "justice-court-finder": "https://www.gov.pl/web/sprawiedliwosc/znajdz-wybrany-sad-powszechny",
    "gov-passport-adult": "https://www.gov.pl/web/gov/uzyskaj-paszport-usluga-dla-osoby-doroslej",
    "gov-temporary-passport": "https://www.gov.pl/web/gov/uzyskaj-paszport-tymczasowy",
    "mfa-passports-abroad": "https://www.gov.pl/web/dyplomacja/paszporty",
    "e-konsulat-portal": "https://secure.e-konsulat.gov.pl/",
    "gov-vehicle-technical-inspections": "https://www.gov.pl/web/infrastruktura/badania-techniczne-pojazdow",
    "gov-compulsory-vehicle-oc": "https://www.gov.pl/web/finanse/ubezpieczenia-obowiazkowe",
    "mobywatel-check-oc": "https://info.mobywatel.gov.pl/uslugi/sprawdz-oc",
    "gov-road-toll-payments": "https://www.gov.pl/web/infrastruktura/platnosci-za-przejazdy-drogowe",
    "etoll-system": "https://www.etoll.gov.pl/en/",
    "etoll-vehicle-classifier": "https://etoll.gov.pl/en/vehicle-classification-tool/",
    "etoll-light-vehicle-transition-2026": "https://etoll.gov.pl/en/news/abolition-of-the-electronic-toll-charge-in-the-e-toll-system-for-journeys-by-light-vehicles-with-a-trailer/",
    "eli-public-roads-act": "https://eli.gov.pl/eli/DU/2025/889/ogl",
    "puesc-import": "https://puesc.gov.pl/pl/uslugi/import",
    "podatki-car-excise": "https://www.podatki.gov.pl/akcyza/informacje-podstawowe",
    "puesc-car-excise-service": "https://puesc.gov.pl/uslugi/zloz-deklaracje-akcyzowa-od-samochodu-i-uzyskaj-potwierdzenie-zaplaty",
    "mswia-jst-directory": "https://www.gov.pl/web/mswia/baza-jst",
}


ROUTE_SOURCES = {
    "professional-qualification-recognition": {
        "gov-professional-qualifications-incoming",
        "nawa-regulated-professions",
    },
    "civil-succession-route": {
        "ejustice-succession-poland",
        "ejustice-succession-authorities-poland",
        "justice-court-finder",
    },
    "polish-passport-and-consular-appointment": {
        "gov-passport-adult",
        "gov-temporary-passport",
        "mfa-passports-abroad",
        "e-konsulat-portal",
    },
    "vehicle-roadworthiness-and-oc": {
        "gov-vehicle-technical-inspections",
        "gov-compulsory-vehicle-oc",
        "mobywatel-check-oc",
    },
    "road-tolls-and-local-parking": {
        "gov-road-toll-payments",
        "etoll-system",
        "etoll-vehicle-classifier",
        "etoll-light-vehicle-transition-2026",
        "eli-public-roads-act",
    },
    "imported-vehicle-customs-and-excise": {
        "puesc-import",
        "podatki-car-excise",
        "puesc-car-excise-service",
    },
    "local-authority-and-appointment": {
        "mswia-jst-directory",
        "gus-teryt-api",
        "bip-directory",
    },
}


class LifeGapRouteTests(unittest.TestCase):
    def test_added_sources_have_exact_current_official_locations(self):
        sources = keyed("sources.json", "sources")
        self.assertTrue(set(SOURCE_URLS) <= set(sources))
        for source_id, expected_url in SOURCE_URLS.items():
            source = sources[source_id]
            self.assertEqual(expected_url, source["url"], source_id)
            self.assertEqual("2026-08-21", source["accessed_at"], source_id)
            self.assertEqual("2026-08-21", source["last_verified"], source_id)
            self.assertEqual("active", source["status"], source_id)
            self.assertTrue(source["publisher"], source_id)

    def test_every_advertised_route_is_source_backed(self):
        scenarios = keyed("scenarios.json", "scenarios")
        source_ids = set(keyed("sources.json", "sources"))
        for scenario_id, required_sources in ROUTE_SOURCES.items():
            self.assertIn(scenario_id, scenarios)
            scenario = scenarios[scenario_id]
            advertised = set(scenario["source_ids"])
            self.assertTrue(required_sources <= advertised, scenario_id)
            self.assertTrue(advertised <= source_ids, scenario_id)
            self.assertTrue(scenario["stop_before"], scenario_id)
            self.assertTrue(scenario["escalate_when"], scenario_id)

        self.assertIn("target_date", scenarios["road-tolls-and-local-parking"]["required_parameters"])
        transition = keyed("sources.json", "sources")["etoll-light-vehicle-transition-2026"]
        self.assertEqual("2026-09-21", transition["effective_from"])

    def test_advertised_operator_channels_are_source_backed_and_confirmation_gated(self):
        channels = keyed("digital-channels.json", "channels")
        sources = set(keyed("sources.json", "sources"))
        expected = {
            "e-konsulat": {"e-konsulat-portal"},
            "etoll": {"etoll-system", "etoll-light-vehicle-transition-2026"},
            "puesc": {"puesc-import", "puesc-car-excise-service"},
            "cepik": {"mobywatel-check-oc", "gov-vehicle-technical-inspections"},
        }
        for channel_id, required_sources in expected.items():
            channel = channels[channel_id]
            self.assertEqual("human_in_loop_operator", channel["agent_mode"], channel_id)
            self.assertTrue(required_sources <= set(channel["source_ids"]), channel_id)
            self.assertTrue(set(channel["source_ids"]) <= sources, channel_id)
            self.assertTrue(channel["stop_before"], channel_id)
            self.assertTrue(channel["live_verify"], channel_id)
            self.assertIn("no ", channel["notes"].lower(), channel_id)
            self.assertIn("connector", channel["notes"].lower(), channel_id)

    def test_powiat_owned_routes_require_powiat_and_keep_gmina_optional(self):
        scenarios = keyed("scenarios.json", "scenarios")
        powiat_owned = {
            "unemployment-registration",
            "vehicle-registration-and-transfer",
            "adult-disability-route",
            "child-disability-route",
            "disability-support-and-pfron",
        }
        for scenario_id in powiat_owned:
            scenario = scenarios[scenario_id]
            self.assertIn("powiat", scenario["required_parameters"], scenario_id)
            self.assertNotIn("gmina", scenario["required_parameters"], scenario_id)
            self.assertIn("gmina", scenario["optional_parameters"], scenario_id)

        local = scenarios["local-authority-and-appointment"]
        self.assertEqual(
            {"mswia-jst-directory", "gus-teryt-api", "bip-directory"},
            set(local["source_ids"]),
        )
        self.assertTrue({"voivodeship", "powiat", "gmina"} <= set(local["optional_parameters"]))


if __name__ == "__main__":
    unittest.main()
