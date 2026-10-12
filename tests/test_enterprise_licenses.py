"""Five-source preservation/security tests with fictional bytes and no network."""

import hashlib
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

from collection_fixtures import FakeTransport
from enterprise_mind.ingestion.__main__ import main
from enterprise_mind.ingestion.collector import CollectionError, collect
from enterprise_mind.ingestion.distribution import prepare_distribution
from enterprise_mind.ingestion.licensing import license_preservation
from enterprise_mind.ingestion.manifest import blocked_reasons, load_manifest, validate_manifest
from enterprise_mind.ingestion.reviewed_sources import REVIEWED_SOURCES

REPOSITORY = Path(__file__).resolve().parents[1]
BITEXT = "support-bitext-v11"
FINANCE = "finance-govinfo-ftr-2025"
LIMIT = 20 * 1024 * 1024
PAYLOADS = {
    "html": b"<html>FICTIONAL TEST DOCUMENT ONLY.</html>",
    "pdf": b"%PDF-1.7\nFICTIONAL TEST DOCUMENT ONLY.\n%%EOF",
    "csv": b"instruction,response\nFICTIONAL TEST QUESTION,FICTIONAL TEST ANSWER\n",
}


def fixture(source_id, *, payload=None):
    """Test-only approval/checksum; never edits or contacts production inventory."""
    data = json.loads((REPOSITORY / "data/sources.yaml").read_text(encoding="utf-8"))
    source = deepcopy(next(s for s in data["sources"] if s["source_id"] == source_id))
    source["verification"]["status"] = "verified"
    source["approval"] = {"approved": True, "approved_by": "fictional-test-reviewer",
                          "approved_at": "2026-10-11T00:00:00+00:00",
                          "allowed_uses": ["collection_for_rag"]}
    source["expected_sha256"] = hashlib.sha256(
        payload if payload is not None else PAYLOADS[source["format"]]).hexdigest()
    data["sources"] = [source]
    data["allowlisted_urls"] = [source["url"]]
    return data


class EnterpriseLicenseTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.workspace = Path(temporary.name)
        for target in ("socket.create_connection", "socket.getaddrinfo"):
            guard = patch(target, side_effect=AssertionError("network forbidden"))
            guard.start()
            self.addCleanup(guard.stop)

    def collect_fixture(self, source_id, *, data=None, payload=None, max_bytes=LIMIT):
        data = data or fixture(source_id, payload=payload)
        source = data["sources"][0]
        payload = payload if payload is not None else PAYLOADS[source["format"]]
        mime = {"html": "text/html", "pdf": "application/pdf", "csv": "text/plain"}
        transport = FakeTransport(payload, headers={"content-type": mime[source["format"]]})
        result = collect(validate_manifest(data), [source_id], workspace=self.workspace,
                         transport=transport, download=True, max_bytes=max_bytes)[0]
        path = self.workspace / result["record_path"]
        return path, json.loads(path.read_bytes()), transport

    def test_all_five_collect_and_export_terms_notices_and_original_bytes(self):
        for source_id, binding in REVIEWED_SOURCES.items():
            with self.subTest(source_id=source_id):
                path, record, transport = self.collect_fixture(source_id)
                preserved = record["license_preservation"]
                self.assertEqual(preserved["identifier"], binding["identifier"])
                self.assertEqual(record["provenance"]["source_metadata"], binding["source_metadata"])
                self.assertEqual(record["provenance"]["original_source_url"], binding["url"])
                self.assertEqual(record["provenance"]["license_attribution"], preserved["attribution"])
                for key in ("license", "notices"):
                    artifact = preserved[key]
                    self.assertEqual(artifact["sha256"], binding[key + "_sha256"])
                    self.assertEqual((self.workspace / artifact["path"]).read_bytes(),
                                     artifact["text"].encode())
                before = {p: p.read_bytes() for p in self.workspace.rglob("*") if p.is_file()}
                bundle = prepare_distribution(workspace=self.workspace, record_path=path)
                self.assertEqual(set(bundle), {f"document.{binding['format']}", "LICENSE.txt",
                                               "NOTICE.txt", "provenance.json"})
                self.assertEqual(bundle[f"document.{binding['format']}"], PAYLOADS[binding["format"]])
                self.assertIn(binding["url"].encode(), bundle["NOTICE.txt"])
                self.assertEqual(bundle["LICENSE.txt"], preserved["license"]["text"].encode())
                self.assertEqual({p: p.read_bytes() for p in before}, before)
                self.assertEqual(transport.calls, [binding["url"]])

    def test_gnome_notice_preserves_exact_author_and_license_inclusion(self):
        _, record, _ = self.collect_fixture("it-gnome-network")
        notice = record["license_preservation"]["notices"]["text"]
        self.assertIn("The Ubuntu Documentation Team", notice)
        self.assertIn("legal.xml via XInclude", notice)
        self.assertIn("Attribution-ShareAlike 3.0 Unported", notice)

    def test_finance_date_jurisdiction_and_historical_claim_are_preserved(self):
        _, record, _ = self.collect_fixture(FINANCE)
        context = record["provenance"]["source_metadata"]
        self.assertEqual(context["publication_date"], "2025-07-01")
        self.assertEqual(context["jurisdiction"], "United States federal")
        self.assertTrue(context["historical_reference"])
        self.assertFalse(context["current_law_claim"])
        self.assertIn("not represented as current 2026 law",
                      record["license_preservation"]["notices"]["text"])

    def test_bitext_classification_and_sharing_obligations_are_preserved(self):
        _, record, _ = self.collect_fixture(BITEXT)
        context = record["provenance"]["source_metadata"]
        self.assertEqual(record["provenance"]["kind"], "public_synthetic_dataset")
        self.assertFalse(context["is_real_ticket_data"])
        self.assertFalse(context["is_project_authored_fictional"])
        self.assertIn("3.1", record["license_preservation"]["license"]["text"])
        self.assertIn("prominent modification notices",
                      record["license_preservation"]["notices"]["text"])

    def test_binding_changes_fail_before_network_or_output(self):
        for source_id in REVIEWED_SOURCES:
            for field, value in (("url", "https://unreviewed.example.com/file"),
                                 ("format", "json"), ("category", "technical_documentation")):
                with self.subTest(source=source_id, field=field):
                    data = fixture(source_id)
                    data["sources"][0][field] = value
                    data["allowlisted_urls"] = [data["sources"][0]["url"]]
                    transport = FakeTransport()
                    with self.assertRaisesRegex(CollectionError, "license preservation preflight"):
                        collect(validate_manifest(data), [source_id], workspace=self.workspace,
                                transport=transport, download=True)
                    self.assertFalse(transport.calls)
                    self.assertFalse((self.workspace / "data").exists())
            for field, value in (("identifier", "LicenseRef-Wrong"),
                                 ("url", "https://unreviewed.example.com/license")):
                data = fixture(source_id)
                data["sources"][0]["license"][field] = value
                transport = FakeTransport()
                with self.assertRaises(CollectionError):
                    collect(validate_manifest(data), [source_id], workspace=self.workspace,
                            transport=transport, download=True)
                self.assertFalse(transport.calls)

    def test_reviewed_url_cannot_be_reassigned_an_unknown_source_id(self):
        source = fixture(FINANCE)["sources"][0]
        with self.assertRaises(ValueError):
            license_preservation("fictional-wrong", source["url"], source["license"])

    def test_modified_local_terms_and_notices_fail_before_network(self):
        for source_id in REVIEWED_SOURCES:
            for text in ("altered", "", "x" * 65_537):
                with self.subTest(source=source_id, text_size=len(text)):
                    with patch("enterprise_mind.ingestion.licensing.files") as assets:
                        assets.return_value.joinpath.return_value.joinpath.return_value.read_text.return_value = text
                        transport = FakeTransport()
                        with self.assertRaises(CollectionError):
                            collect(validate_manifest(fixture(source_id)), [source_id],
                                    workspace=self.workspace, transport=transport, download=True)
                        self.assertFalse(transport.calls)
                        self.assertFalse((self.workspace / "data").exists())

    def test_missing_local_resources_fail_closed(self):
        with patch("enterprise_mind.ingestion.licensing.files", side_effect=FileNotFoundError):
            with self.assertRaises(CollectionError):
                self.collect_fixture(FINANCE)
        self.assertFalse((self.workspace / "data").exists())

    def test_tampered_license_or_notice_sidecar_cannot_be_exported(self):
        for source_id in REVIEWED_SOURCES:
            path, record, _ = self.collect_fixture(source_id)
            for key in ("license", "notices"):
                artifact = self.workspace / record["license_preservation"][key]["path"]
                original = artifact.read_bytes()
                artifact.write_bytes(b"altered")
                with self.assertRaises(CollectionError):
                    prepare_distribution(workspace=self.workspace, record_path=path)
                artifact.write_bytes(original)
                artifact.unlink()
                with self.assertRaises(CollectionError):
                    prepare_distribution(workspace=self.workspace, record_path=path)
                artifact.write_bytes(original)

    def test_tampered_context_and_classification_cannot_be_exported(self):
        path, original, _ = self.collect_fixture(BITEXT)
        for section, field, value in (("provenance", "kind", "public_document"),
                                      ("provenance", "publisher", "wrong"),
                                      ("provenance", "source_metadata", {}),
                                      ("license_preservation", "source_metadata", {})):
            record = deepcopy(original)
            record[section][field] = value
            path.write_text(json.dumps(record), encoding="utf-8")
            with self.assertRaises(CollectionError):
                prepare_distribution(workspace=self.workspace, record_path=path)
        for field in ("category", "format", "title", "source_version", "version"):
            record = deepcopy(original)
            record[field] = "wrong"
            path.write_text(json.dumps(record), encoding="utf-8")
            with self.assertRaises(CollectionError):
                prepare_distribution(workspace=self.workspace, record_path=path)

    def test_bitext_large_synthetic_csv_and_twenty_mib_cap(self):
        prefix = b"FICTIONAL TEST ONLY\n"
        payload = prefix + b"x" * (19_202_474 - len(prefix))
        self.assertEqual(len(payload), 19_202_474)
        data = fixture(BITEXT, payload=payload)
        with self.assertRaisesRegex(CollectionError, "size exceeds limit"):
            self.collect_fixture(BITEXT, data=data, payload=payload, max_bytes=5 * 1024 * 1024)
        path, record, _ = self.collect_fixture(BITEXT, data=data, payload=payload)
        self.assertEqual(record["size_bytes"], len(payload))
        self.assertEqual(prepare_distribution(workspace=self.workspace, record_path=path)["document.csv"],
                         payload)
        for length in (LIMIT, LIMIT + 1):
            transport = FakeTransport(headers={"content-type": "text/plain", "content-length": str(length)})
            with self.assertRaisesRegex(CollectionError, "truncated|size exceeds limit"):
                collect(validate_manifest(fixture(BITEXT)), [BITEXT], workspace=self.workspace,
                        download=True, transport=transport, max_bytes=32 * 1024 * 1024)

    def test_csv_checksum_and_redirect_controls_remain_active(self):
        for source_id in REVIEWED_SOURCES:
            data = fixture(source_id)
            for transport in (FakeTransport(status=302), FakeTransport(b"wrong checksum", headers={
                "content-type": {"html": "text/html", "pdf": "application/pdf", "csv": "text/plain"}[
                    data["sources"][0]["format"]]})):
                with self.assertRaises(CollectionError):
                    collect(validate_manifest(data), [source_id], workspace=self.workspace,
                            download=True, transport=transport, max_bytes=LIMIT)
        self.assertFalse((self.workspace / "data/raw/records").exists())

    def test_inventory_authorizes_only_reviewed_sources_and_keeps_hr_batch_blocked(self):
        manifest = load_manifest(REPOSITORY / "data/sources.yaml")
        approved_ids = set(REVIEWED_SOURCES) - {"hr-gitlab-people"}
        expected_urls = {REVIEWED_SOURCES[sid]["url"] for sid in approved_ids}
        self.assertEqual(manifest.allowlisted_urls,
                         expected_urls | {"https://docs.python.org/3.12/tutorial/index.html"})
        for source in manifest.sources:
            if source.source_id not in REVIEWED_SOURCES:
                continue
            self.assertEqual(source.license["status"], "verified")
            if source.source_id == "hr-gitlab-people":
                self.assertEqual(source.verification["status"], "pending_review")
                self.assertFalse(source.approval["approved"])
                self.assertIn("explicit approval missing", blocked_reasons(source, manifest))
                self.assertIn("exact URL not allowlisted", blocked_reasons(source, manifest))
            else:
                self.assertEqual(source.verification["status"], "verified")
                self.assertTrue(source.approval["approved"])
                self.assertEqual(source.approval["allowed_uses"], ["collection_for_rag"])
                self.assertFalse(blocked_reasons(source, manifest))
            if source.source_id == BITEXT:
                self.assertEqual(source.max_bytes, LIMIT)
                self.assertEqual(source.expected_sha256,
                                 "6f81102b0100b97b8468eb04368033a23206bf1fde9d53500d5806ec1001a434")
        self.assertNotIn("it-ubuntu-network", {s.source_id for s in manifest.sources})
        self.assertNotIn("finance-gsa-travel", {s.source_id for s in manifest.sources})
        transport = FakeTransport()
        with patch("enterprise_mind.ingestion.licensing.files", side_effect=AssertionError):
            plan = collect(manifest, list(REVIEWED_SOURCES), workspace=self.workspace,
                           transport=transport, max_bytes=LIMIT)
            self.assertEqual({p["source_id"] for p in plan if p["eligible"]}, approved_ids)
            with self.assertRaises(CollectionError):
                collect(manifest, list(REVIEWED_SOURCES), workspace=self.workspace,
                        transport=transport, download=True, max_bytes=LIMIT)
        self.assertFalse(transport.calls)
        self.assertFalse((self.workspace / "data").exists())

    def test_cli_twenty_mib_plan_is_offline_and_bounded(self):
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(main(["collect", "--manifest", str(REPOSITORY / "data/sources.yaml"),
                                   "--source", BITEXT, "--max-bytes", str(LIMIT)]), 0)
        result = json.loads(output.getvalue())["results"][0]
        self.assertEqual(result["max_bytes"], LIMIT)
        self.assertTrue(result["eligible"])


if __name__ == "__main__":
    unittest.main()
