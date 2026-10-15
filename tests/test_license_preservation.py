"""License preservation tests use fictional HTML and never contact the source."""

import hashlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from collection_fixtures import FakeTransport, manifest_data
from enterprise_mind.ingestion.collector import CollectionError, collect
from enterprise_mind.ingestion.distribution import prepare_distribution
from enterprise_mind.ingestion.licensing import (
    MAX_LICENSE_BYTES,
    PYTHON_LICENSE_URL,
    PYTHON_RESOURCE_HASHES,
    PYTHON_SOURCE_ID,
    PYTHON_SOURCE_URL,
    license_preservation,
)
from enterprise_mind.ingestion.manifest import load_manifest, validate_manifest

HTML = b"<html>FICTIONAL TEST DOCUMENT ONLY. Not Python tutorial content.</html>"


def python_fixture():
    """Test-only approval metadata; the actual source manifest is never edited."""
    data = manifest_data()
    data["allowlisted_urls"] = [PYTHON_SOURCE_URL]
    source = data["sources"][0]
    source.update(source_id=PYTHON_SOURCE_ID, url=PYTHON_SOURCE_URL, format="html",
                  category="technical_documentation")
    source["license"].update(identifier="PSF-2.0", url=PYTHON_LICENSE_URL,
                             attribution="Python Software Foundation and listed copyright holders")
    return data


class LicensePreservationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.workspace = Path(temporary.name)
        self.transport = FakeTransport(HTML, headers={"content-type": "text/html"})
        for name in ("socket.create_connection", "socket.getaddrinfo"):
            guard = patch(name, side_effect=AssertionError("network forbidden"))
            guard.start()
            self.addCleanup(guard.stop)

    def collect_fixture(self, data=None):
        results = collect(validate_manifest(data or python_fixture()), [PYTHON_SOURCE_ID],
                          workspace=self.workspace, transport=self.transport, download=True)
        path = self.workspace / results[0]["record_path"]
        return path, json.loads(path.read_text(encoding="utf-8"))

    def test_collect_preserves_complete_license_notices_and_provenance(self):
        _, record = self.collect_fixture()
        preservation = record["license_preservation"]
        self.assertEqual(preservation["identifier"], "PSF-2.0")
        self.assertEqual(preservation["original_source_url"], PYTHON_SOURCE_URL)
        self.assertEqual(record["provenance"]["original_source_url"], PYTHON_SOURCE_URL)
        self.assertEqual(record["provenance"]["license_attribution"], preservation["attribution"])
        for key in ("license", "notices"):
            artifact = preservation[key]
            content = (self.workspace / artifact["path"]).read_bytes()
            self.assertEqual(content, artifact["text"].encode("utf-8"))
            self.assertEqual(hashlib.sha256(content).hexdigest(), artifact["sha256"])
        for clause in range(1, 9):
            self.assertIn(f"\n{clause}. ", preservation["license"]["text"])
        self.assertIn("2001-2023 Python Software Foundation", preservation["license"]["text"])
        for holder in ("Python Software Foundation", "BeOpen.com",
                       "Corporation for National Research Initiatives", "Stichting Mathematisch"):
            self.assertIn(holder, preservation["notices"]["text"])
        self.assertEqual(self.transport.calls, [PYTHON_SOURCE_URL])

    def test_distribution_includes_document_full_license_attribution_and_source(self):
        path, record = self.collect_fixture()
        before = sorted(p.relative_to(self.workspace) for p in self.workspace.rglob("*"))
        bundle = prepare_distribution(workspace=self.workspace, record_path=path)
        self.assertEqual(set(bundle),
                         {"document.html", "LICENSE.txt", "NOTICE.txt", "provenance.json"})
        self.assertEqual(bundle["document.html"], HTML)
        self.assertEqual(bundle["LICENSE.txt"],
                         record["license_preservation"]["license"]["text"].encode())
        self.assertIn(PYTHON_SOURCE_URL.encode(), bundle["NOTICE.txt"])
        self.assertIn(record["license"]["attribution"].encode(), bundle["NOTICE.txt"])
        self.assertIn(b"original downloaded bytes preserved", bundle["NOTICE.txt"])
        self.assertEqual(json.loads(bundle["provenance.json"]), record)
        after = sorted(p.relative_to(self.workspace) for p in self.workspace.rglob("*"))
        self.assertEqual(before, after)
        self.assertEqual(self.transport.calls, [PYTHON_SOURCE_URL])

    def test_missing_or_corrupt_sidecars_block_distribution(self):
        path, record = self.collect_fixture()
        for key in ("license", "notices"):
            sidecar = self.workspace / record["license_preservation"][key]["path"]
            original = sidecar.read_bytes()
            for corruption in (None, b"altered notice"):
                if corruption is None:
                    sidecar.unlink()
                else:
                    sidecar.write_bytes(corruption)
                with self.assertRaises(CollectionError):
                    prepare_distribution(workspace=self.workspace, record_path=path)
                sidecar.write_bytes(original)

    def test_missing_or_tampered_preservation_and_provenance_block_distribution(self):
        path, original = self.collect_fixture()
        for section, field in (("license_preservation", "attribution"),
                               ("license_preservation", "original_source_url"),
                               ("provenance", "license_attribution"),
                               ("provenance", "original_source_url")):
            record = json.loads(json.dumps(original))
            record[section][field] = "altered"
            path.write_text(json.dumps(record), encoding="utf-8")
            with self.assertRaises(CollectionError):
                prepare_distribution(workspace=self.workspace, record_path=path)
        del original["license_preservation"]
        path.write_text(json.dumps(original), encoding="utf-8")
        with self.assertRaises(CollectionError):
            prepare_distribution(workspace=self.workspace, record_path=path)

    def test_corrupt_document_and_manifest_block_distribution(self):
        path, record = self.collect_fixture()
        blob = self.workspace / record["blob_path"]
        blob.write_bytes(b"altered HTML")
        with self.assertRaises(CollectionError):
            prepare_distribution(workspace=self.workspace, record_path=path)
        blob.write_bytes(HTML)
        manifest = self.workspace / "data/raw/manifests" / (
            record["provenance"]["manifest_sha256"] + ".json")
        data = json.loads(manifest.read_bytes())
        data["sources"][0]["license"]["attribution"] = "altered"
        manifest.write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaises(CollectionError):
            prepare_distribution(workspace=self.workspace, record_path=path)

    def test_repeated_collection_preserves_sidecars_and_original_record(self):
        path, _ = self.collect_fixture()
        before = {p: p.read_bytes() for p in (self.workspace / "data/raw/licenses").iterdir()}
        original = path.read_bytes()
        self.collect_fixture()
        self.assertEqual(path.read_bytes(), original)
        self.assertEqual({p: p.read_bytes() for p in before}, before)

    def test_corrupt_existing_license_blocks_collection_record(self):
        path, record = self.collect_fixture()
        (self.workspace / record["license_preservation"]["license"]["path"]).write_bytes(b"corrupt")
        original = path.read_bytes()
        with self.assertRaises(CollectionError):
            self.collect_fixture()
        self.assertEqual(path.read_bytes(), original)

    def test_license_binding_and_missing_asset_fail_before_network_or_writes(self):
        data = python_fixture()
        data["sources"][0]["license"]["identifier"] = "LicenseRef-Wrong"
        with self.assertRaises(CollectionError):
            self.collect_fixture(data)
        with patch("enterprise_mind.ingestion.licensing.files", side_effect=FileNotFoundError):
            with self.assertRaises(CollectionError):
                self.collect_fixture()
        self.assertFalse(self.transport.calls)
        self.assertFalse((self.workspace / "data").exists())

    def test_python_terms_and_copyright_pins_reject_alteration_and_oversize(self):
        directory = Path(__file__).resolve().parents[1] / "src/enterprise_mind/ingestion/licenses"
        originals = {name: (directory / name).read_text(encoding="utf-8")
                     for name in PYTHON_RESOURCE_HASHES}
        for filename in originals:
            for replacement in ("altered fictional terms", "", "x" * (MAX_LICENSE_BYTES + 1),
                                "\u00e9" * MAX_LICENSE_BYTES):
                streams = []

                def open_resource(name):
                    resource = MagicMock()
                    stream = io.StringIO(replacement if name == filename else originals[name])
                    streams.append(stream)
                    resource.open.return_value = stream
                    return resource

                with self.subTest(filename=filename, size=len(replacement)):
                    with patch("enterprise_mind.ingestion.licensing.files") as assets:
                        resources = assets.return_value.joinpath.return_value
                        resources.joinpath.side_effect = open_resource
                        with self.assertRaises(CollectionError):
                            self.collect_fixture()
                    self.assertTrue(all(stream.closed for stream in streams))
                    self.assertFalse(self.transport.calls)
                    self.assertFalse((self.workspace / "data").exists())

    def test_python_resources_use_bounded_reads_and_preserve_reviewed_text(self):
        directory = Path(__file__).resolve().parents[1] / "src/enterprise_mind/ingestion/licenses"
        originals = {name: (directory / name).read_text(encoding="utf-8")
                     for name in PYTHON_RESOURCE_HASHES}
        streams = []

        def resource(name):
            asset = MagicMock()
            stream = MagicMock(wraps=io.StringIO(originals[name]))
            stream.__enter__.return_value = stream
            streams.append(stream)
            asset.open.return_value = stream
            return asset

        source = python_fixture()["sources"][0]
        with patch("enterprise_mind.ingestion.licensing.files") as assets:
            assets.return_value.joinpath.return_value.joinpath.side_effect = resource
            preserved = license_preservation(PYTHON_SOURCE_ID, PYTHON_SOURCE_URL, source["license"])
        for stream in streams:
            stream.read.assert_called_once_with(MAX_LICENSE_BYTES + 1)
        for key, filename in (("license", "PSF-2.0.txt"), ("notices", "python-copyright.txt")):
            self.assertEqual(preserved[key]["text"], originals[filename])
            self.assertEqual(preserved[key]["sha256"], PYTHON_RESOURCE_HASHES[filename])

    def test_deadline_is_checked_before_license_and_record_publication(self):
        # manifest, document, license, notices and record each have a flush.
        for expires_on_flush in (3, 5):
            now, flushes = [0], [0]

            def delayed_fsync(descriptor):
                flushes[0] += 1
                if flushes[0] == expires_on_flush:
                    now[0] = 16

            with (self.subTest(expires_on_flush=expires_on_flush),
                  tempfile.TemporaryDirectory() as folder):
                self.workspace = Path(folder)
                with patch("enterprise_mind.ingestion.collector.time.monotonic",
                           side_effect=lambda: now[0]):
                    with patch("enterprise_mind.ingestion.collector.os.fsync", delayed_fsync):
                        with self.assertRaisesRegex(CollectionError, "deadline"):
                            self.collect_fixture()
                root = self.workspace / "data/raw"
                self.assertFalse(list(root.glob("records/**/*.json")))
                self.assertFalse(list(root.rglob(".record-*")))
                self.assertFalse(list((root / ".staging").iterdir()))
                self.assertFalse((root / ".collection.lock").exists())
                if expires_on_flush == 3:
                    self.assertFalse(list((root / "licenses").glob("*.txt")))

    def test_dry_run_and_unapproved_source_never_read_assets_or_use_network(self):
        data = python_fixture()
        data["allowlisted_urls"] = []
        data["sources"][0]["approval"] = {
            "approved": False, "approved_by": None, "approved_at": None, "allowed_uses": [],
        }
        manifest = validate_manifest(data)
        with patch("enterprise_mind.ingestion.licensing.files", side_effect=AssertionError):
            result = collect(manifest, [PYTHON_SOURCE_ID], workspace=self.workspace,
                             transport=self.transport)
            self.assertFalse(result[0]["eligible"])
            with self.assertRaises(CollectionError):
                collect(manifest, [PYTHON_SOURCE_ID], workspace=self.workspace,
                        transport=self.transport, download=True)
        self.assertFalse(self.transport.calls)
        self.assertFalse((self.workspace / "data").exists())

    def test_prepared_repository_source_only_plans_without_execution(self):
        manifest = load_manifest(Path(__file__).resolve().parents[1] / "data/sources.yaml")
        with patch("enterprise_mind.ingestion.licensing.files", side_effect=AssertionError):
            result = collect(manifest, [PYTHON_SOURCE_ID], workspace=self.workspace,
                             transport=self.transport)
        self.assertTrue(result[0]["eligible"])
        self.assertEqual(result[0]["url"], PYTHON_SOURCE_URL)
        self.assertFalse(self.transport.calls)
        self.assertFalse((self.workspace / "data").exists())

    def test_prepared_source_cannot_authorize_an_unapproved_batch_member(self):
        manifest = load_manifest(Path(__file__).resolve().parents[1] / "data/sources.yaml")
        with self.assertRaisesRegex(CollectionError, "download rejected"):
            collect(manifest, [PYTHON_SOURCE_ID, "hr-gitlab-people"], workspace=self.workspace,
                    transport=self.transport, download=True)
        self.assertFalse(self.transport.calls)
        self.assertFalse((self.workspace / "data").exists())

    def test_unsupported_license_does_not_gain_python_terms(self):
        source = manifest_data()["sources"][0]
        self.assertIsNone(license_preservation(
            source["source_id"], source["url"], source["license"]))
        self.transport = FakeTransport()
        result = collect(validate_manifest(manifest_data()), [source["source_id"]],
                         workspace=self.workspace, transport=self.transport, download=True)[0]
        with self.assertRaises(CollectionError):
            prepare_distribution(workspace=self.workspace, record_path=Path(result["record_path"]))


if __name__ == "__main__":
    unittest.main()
