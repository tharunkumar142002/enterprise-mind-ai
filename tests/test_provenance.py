"""Record-schema regressions run only against fictional temporary artifacts."""

import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

from collection_fixtures import FakeTransport
from enterprise_mind.ingestion.collector import CollectionError, collect
from enterprise_mind.ingestion.distribution import prepare_distribution
from enterprise_mind.ingestion.licensing import PYTHON_SOURCE_ID
from enterprise_mind.ingestion.manifest import validate_manifest
from enterprise_mind.ingestion.provenance import MAX_RECORD_BYTES, ProvenanceError, load_record
from test_license_preservation import HTML, python_fixture


class ProvenanceTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.workspace = Path(temporary.name)
        for target in ("socket.getaddrinfo", "socket.create_connection"):
            guard = patch(target, side_effect=AssertionError("network forbidden"))
            guard.start()
            self.addCleanup(guard.stop)
        self.manifest = validate_manifest(python_fixture())
        self.transport = FakeTransport(HTML, headers={"content-type": "text/html"})
        result = self.collect()[0]
        self.path = self.workspace / result["record_path"]
        self.original = self.path.read_bytes()
        self.record = json.loads(self.original)

    def collect(self):
        return collect(self.manifest, [PYTHON_SOURCE_ID], workspace=self.workspace,
                       transport=self.transport, download=True)

    def assert_rejected_by_both_consumers(self, value):
        raw = value if isinstance(value, bytes) else json.dumps(value).encode("utf-8")
        self.path.write_bytes(raw)
        with self.assertRaises(CollectionError):
            prepare_distribution(workspace=self.workspace, record_path=self.path)
        with self.assertRaises(CollectionError):
            self.collect()
        self.assertEqual(self.path.read_bytes(), raw)
        self.assertFalse((self.workspace / "data/raw/.collection.lock").exists())
        self.assertFalse(list((self.workspace / "data/raw/.staging").iterdir()))
        self.path.write_bytes(self.original)

    def test_missing_mandatory_fields_fail_collection_reuse_and_distribution(self):
        for field in self.record:
            with self.subTest(field=field):
                record = deepcopy(self.record)
                del record[field]
                self.assert_rejected_by_both_consumers(record)
        for section in ("provenance", "checksum", "license"):
            for field in self.record[section]:
                with self.subTest(section=section, field=field):
                    record = deepcopy(self.record)
                    del record[section][field]
                    self.assert_rejected_by_both_consumers(record)

    def test_invalid_timestamps_fail_both_consumers(self):
        for timestamp in (
            None, True, 123, [], "", "not a date", "2026-10-11", "2026-10-11T12:00:00",
            "2026-02-30T12:00:00Z", "2026-10-11T25:00:00Z", "2026-10-11T12:00:00+24:00",
            "2026-10-11T12:00:00+00:99", "2026-10-11 12:00:00Z", "20261011T120000Z",
            "2026-10-11T12:00:00Z\n",
        ):
            with self.subTest(timestamp=timestamp):
                record = deepcopy(self.record)
                record["collected_at"] = timestamp
                self.assert_rejected_by_both_consumers(record)

    def test_only_integer_schema_one_is_supported(self):
        for version in (None, True, False, "1", 1.0, 0, 2, [], {}):
            with self.subTest(version=version):
                record = deepcopy(self.record)
                record["schema_version"] = version
                self.assert_rejected_by_both_consumers(record)

    def test_valid_schema_one_timestamps_and_transfer_metadata_are_preserved(self):
        for timestamp in ("2026-10-11T12:00:00Z", "2026-10-11T12:00:00.123456+05:30"):
            record = deepcopy(self.record)
            record["collected_at"] = timestamp
            record["transfer"] = {"etag": '"fictional-v1"', "last-modified": "fictional-date"}
            raw = json.dumps(record).encode("utf-8")
            self.path.write_bytes(raw)
            self.assertIn("provenance.json", prepare_distribution(
                workspace=self.workspace, record_path=self.path))
            self.assertEqual(self.collect()[0]["status"], "already_collected")
            self.assertEqual(self.path.read_bytes(), raw)

    def test_wrong_types_unknown_fields_and_nested_metadata_are_rejected(self):
        for field, replacement in (
            ("size_bytes", True), ("size_bytes", 1.0), ("size_bytes", 0),
            ("transfer", []), ("transfer", {"etag": None}),
            ("transfer", {"etag": "line\r\ninjection"}), ("transfer", {"extra": "x"}),
            ("provenance", []), ("checksum", []), ("license", []),
            ("license_preservation", None), ("unsupported", "extra"),
        ):
            with self.subTest(field=field, replacement=replacement):
                record = deepcopy(self.record)
                record[field] = replacement
                self.assert_rejected_by_both_consumers(record)
        for section in ("provenance", "checksum", "license"):
            record = deepcopy(self.record)
            record[section]["unsupported"] = "extra"
            self.assert_rejected_by_both_consumers(record)
        record = deepcopy(self.record)
        record["provenance"]["approval"]["approved"] = 1
        self.assert_rejected_by_both_consumers(record)

    def test_malformed_duplicate_key_and_non_json_records_are_rejected(self):
        duplicate = b'{"schema_version": 1,' + self.original.lstrip()[1:]
        for raw in (b"[]", b"null", b"{", b"\xff", duplicate,
                    b'{"value": NaN}', b"[" * 1100 + b"]" * 1100,
                    b"x" * (MAX_RECORD_BYTES + 1)):
            with self.subTest(prefix=raw[:30]):
                self.assert_rejected_by_both_consumers(raw)
        record = deepcopy(self.record)
        record["title"] = "\ud800"
        self.assert_rejected_by_both_consumers(record)

    def test_record_loader_reports_controlled_errors(self):
        for raw in (b"null", b"\xff", b'{"x":1,"x":2}', b"[" * 1100):
            with self.assertRaises(ProvenanceError):
                load_record(raw)


if __name__ == "__main__":
    unittest.main()
