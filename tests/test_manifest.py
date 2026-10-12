"""Source-schema failures and approval boundaries, entirely offline."""

import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from collection_fixtures import manifest_data
from enterprise_mind.ingestion.manifest import (
    CATEGORIES,
    FORMAT_MIME_TYPES,
    ManifestError,
    blocked_reasons,
    load_manifest,
    validate_manifest,
)


class ManifestTests(unittest.TestCase):
    def test_valid_manifest_and_all_six_categories(self) -> None:
        data = manifest_data()
        first = data["sources"][0]
        data["sources"] = []
        data["allowlisted_urls"] = []
        for index, category in enumerate(sorted(CATEGORIES)):
            source = deepcopy(first)
            source.update(source_id=f"fictional-{index}", category=category,
                          url=f"https://documents.example.com/fictional-{index}.txt")
            data["sources"].append(source)
            data["allowlisted_urls"].append(source["url"])
        manifest = validate_manifest(data)
        self.assertEqual({source.category for source in manifest.sources}, CATEGORIES)
        self.assertTrue(all(not blocked_reasons(source, manifest) for source in manifest.sources))

    def test_required_source_fields(self) -> None:
        for field in manifest_data()["sources"][0]:
            with self.subTest(field=field):
                data = manifest_data()
                del data["sources"][0][field]
                with self.assertRaises(ManifestError):
                    validate_manifest(data)

    def test_unknown_fields_rejected(self) -> None:
        data = manifest_data()
        data["sources"][0]["approved"] = True
        with self.assertRaises(ManifestError):
            validate_manifest(data)

    def test_duplicate_ids_and_urls(self) -> None:
        for duplicate in ("source_id", "url"):
            with self.subTest(duplicate=duplicate):
                data = manifest_data()
                second = deepcopy(data["sources"][0])
                if duplicate == "source_id":
                    second["url"] = "https://documents.example.com/second.txt"
                else:
                    second["source_id"] = "fictional-second"
                data["sources"].append(second)
                with self.assertRaisesRegex(ManifestError, "duplicate"):
                    validate_manifest(data)

    def test_unsafe_urls_and_identifiers(self) -> None:
        for url in ("http://documents.example.com/file", "file:///etc/passwd",
                    "https://localhost/file", "https://127.0.0.1/file",
                    "https://user:password@documents.example.com/file",
                    "https://documents.example.com:8443/file",
                    "https://documents.example.com/file?token=secret",
                    "https://documents.example.com/file#fragment",
                    "https://documents.example.com/%0d%0aevil", "https://docs.internal/file"):
            with self.subTest(url=url):
                data = manifest_data()
                data["sources"][0]["url"] = url
                with self.assertRaises(ManifestError):
                    validate_manifest(data)
        for source_id in ("../escape", "con", "AUPPERCASE", "nul", "a" * 49):
            with self.subTest(source_id=source_id):
                data = manifest_data()
                data["sources"][0]["source_id"] = source_id
                with self.assertRaises(ManifestError):
                    validate_manifest(data)

    def test_supported_formats_and_unknown_format(self) -> None:
        for file_format in FORMAT_MIME_TYPES:
            data = manifest_data()
            data["sources"][0]["format"] = file_format
            validate_manifest(data)
        data["sources"][0]["format"] = "exe"
        with self.assertRaises(ManifestError):
            validate_manifest(data)

    def test_invalid_values_and_approval_metadata(self) -> None:
        for field, value in (("category", "unknown"), ("access_classification", "confidential"),
                             ("expected_sha256", "not-a-hash"), ("max_bytes", True),
                             ("max_bytes", 0), ("max_bytes", 100_000_000), ("title", "")):
            with self.subTest(field=field, value=value):
                data = manifest_data()
                data["sources"][0][field] = value
                with self.assertRaises(ManifestError):
                    validate_manifest(data)
        for field, value in (("approved", "true"), ("approved_by", ""),
                             ("approved_at", "2026-10-10T00:00:00"),
                             ("allowed_uses", ["fine_tuning"])):
            with self.subTest(field=field):
                data = manifest_data()
                data["sources"][0]["approval"][field] = value
                with self.assertRaises(ManifestError):
                    validate_manifest(data)

    def test_approval_cannot_bypass_source_or_license_review(self) -> None:
        for section in ("license", "verification"):
            data = manifest_data()
            data["sources"][0][section]["status"] = "pending_review"
            with self.assertRaises(ManifestError):
                validate_manifest(data)

    def test_unknown_and_duplicate_allowlisted_urls(self) -> None:
        for urls in (["https://other.example.com/file"],
                     [manifest_data()["sources"][0]["url"]] * 2):
            data = manifest_data()
            data["allowlisted_urls"] = urls
            with self.assertRaises(ManifestError):
                validate_manifest(data)

    def test_loader_rejects_duplicate_keys_general_yaml_and_large_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "manifest.yaml"
            for payload in ('{"schema_version":1,"schema_version":2}',
                            'schema_version: 1\nsources: []', '{"value": NaN}',
                            'x' * 1_048_577):
                path.write_text(payload, encoding="utf-8")
                with self.assertRaises(ManifestError):
                    load_manifest(path)

    def test_repository_inventory_approves_four_reviewed_sources_and_preserves_python(self) -> None:
        path = Path(__file__).resolve().parents[1] / "data" / "sources.yaml"
        manifest = load_manifest(path)
        self.assertEqual({source.category for source in manifest.sources}, CATEGORIES)
        self.assertEqual(len(manifest.sources), 6)
        expected_ids = {"technical-python-tutorial", "it-gnome-network",
                        "finance-govinfo-ftr-2025", "product-libreoffice-writer",
                        "support-bitext-v11"}
        self.assertEqual(manifest.allowlisted_urls, {
            "https://docs.python.org/3.12/tutorial/index.html",
            "https://help.gnome.org/gnome-help/net-problem.html",
            "https://www.govinfo.gov/content/pkg/CFR-2025-title41-vol4/pdf/CFR-2025-title41-vol4-subtitleF.pdf",
            "https://books.libreoffice.org/en/WG252/WG2500-Preface.html",
            "https://raw.githubusercontent.com/bitext/customer-support-llm-chatbot-training-dataset/main/data/Bitext_Sample_Customer_Support_Training_Dataset_27K_responses-v11.csv",
        })
        approved = [source for source in manifest.sources if source.approval["approved"]]
        self.assertEqual({source.source_id for source in approved}, expected_ids)
        for source in approved:
            self.assertEqual(source.approval["allowed_uses"], ["collection_for_rag"])
            self.assertFalse(blocked_reasons(source, manifest))
        for source in manifest.sources:
            if source.source_id not in expected_ids:
                self.assertEqual(source.source_id, "hr-gitlab-people")
                self.assertEqual(source.verification["status"], "pending_review")
                self.assertFalse(source.approval["approved"])
                self.assertIsNone(source.approval["approved_by"])
                self.assertIsNone(source.approval["approved_at"])
                self.assertEqual(source.approval["allowed_uses"], [])
                self.assertIn("explicit approval missing", blocked_reasons(source, manifest))
                self.assertIn("exact URL not allowlisted", blocked_reasons(source, manifest))

    def test_fingerprint_is_independent_of_json_whitespace(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "manifest.yaml"
            path.write_text(json.dumps(manifest_data(), indent=2), encoding="utf-8")
            self.assertEqual(load_manifest(path).sha256, validate_manifest(manifest_data()).sha256)


if __name__ == "__main__":
    unittest.main()
