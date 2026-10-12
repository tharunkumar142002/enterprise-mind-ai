"""Fictional HR contracts, consistency, privacy and immutable local generation."""

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

import collection_fixtures  # Adds the local src package without installation.
from enterprise_mind.ingestion.synthetic_hr import (
    BANNER, CONTACT_PATTERN, DOCUMENT_IDS, OUTPUT, SECRET_PATTERN, SOURCE_KIND,
    SyntheticDataError, _safe_path, build_artifacts, build_documents, encode, generate,
    load_template, main, sha256, validate_documents, validate_template,
)


class SyntheticHRTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.workspace = Path(temporary.name)
        for target in ("socket.create_connection", "socket.getaddrinfo"):
            guard = patch(target, side_effect=AssertionError("network forbidden"))
            guard.start()
            self.addCleanup(guard.stop)

    def test_required_document_metadata_and_fictional_scope(self):
        documents = build_documents()
        required = {"document_id", "title", "category", "version", "effective_date",
                    "owner_department", "access_classification", "provenance", "content"}
        for doc in documents:
            self.assertTrue(required <= doc.keys())
            self.assertEqual(doc["category"], "human_resources")
            self.assertEqual(doc["effective_date"], "2026-10-12")
            self.assertEqual(doc["access_classification"], "internal_demo")
            self.assertEqual(doc["provenance"]["kind"], SOURCE_KIND)
            self.assertIs(doc["is_fictional"], True)
            self.assertIsNone(doc["provenance"]["source_url"])
            self.assertTrue(doc["content"].startswith(BANNER))
            self.assertEqual(doc["content_sha256"], sha256(doc["content"].encode()))
            for field in required:
                altered = deepcopy(documents)
                del altered[0][field]
                with self.assertRaises(SyntheticDataError):
                    validate_documents(altered)
        validate_documents(documents)

    def test_exact_unique_ids_and_duplicate_rejection(self):
        documents = build_documents()
        self.assertEqual({doc["document_id"] for doc in documents}, DOCUMENT_IDS)
        documents[1]["document_id"] = documents[0]["document_id"]
        with self.assertRaisesRegex(SyntheticDataError, "duplicate"):
            validate_documents(documents)
        template = load_template()
        template["documents"][1]["document_id"] = template["documents"][0]["document_id"]
        with self.assertRaisesRegex(SyntheticDataError, "duplicate"):
            validate_template(template)

    def test_unknown_or_non_synthetic_classification_is_rejected(self):
        for value in ("public_document", "public_synthetic_dataset", "private", None):
            documents = build_documents()
            documents[0]["provenance"]["kind"] = value
            with self.assertRaises(SyntheticDataError):
                validate_documents(documents)
        for field, value in (("is_fictional", False), ("is_fictional", 1),
                             ("schema_version", True), ("access_classification", "public")):
            documents = build_documents()
            documents[0][field] = value
            with self.assertRaises(SyntheticDataError):
                validate_documents(documents)

    def test_reproducible_bytes_and_manifest_checksums(self):
        first = build_artifacts()
        self.assertEqual(first, build_artifacts())
        manifest = json.loads(first["manifest.json"])
        self.assertEqual(manifest["document_count"], 5)
        for item in manifest["documents"]:
            self.assertEqual(item["sha256"], sha256(first[item["path"]]))
            self.assertEqual(item["size_bytes"], len(first[item["path"]]))
        with tempfile.TemporaryDirectory() as another:
            generate(workspace=self.workspace, write=True)
            generate(workspace=Path(another), write=True)
            for name in first:
                self.assertEqual((self.workspace / OUTPUT / name).read_bytes(),
                                 (Path(another) / OUTPUT / name).read_bytes())

    def test_template_serialization_is_order_and_line_ending_independent(self):
        template = load_template()
        reordered = dict(reversed(list(template.items())))
        self.assertEqual(build_documents(template), build_documents(reordered))
        self.assertEqual(encode(template), encode(json.loads(encode(template).replace(b"\n", b"\r\n"))))

    def test_shared_policy_definitions_and_hours_are_consistent(self):
        template = load_template()
        rules = template["rules"]
        self.assertEqual(rules["annual_leave_days"], 20)
        self.assertEqual(rules["sick_leave_days"], 10)
        self.assertEqual(rules["daily_hours"], 8)
        self.assertEqual(rules["weekly_hours"], 40)
        self.assertEqual(rules["remote_days_per_week"], 3)
        seen = {}
        for doc in build_documents(template):
            for key, value in doc["policy_values"].items():
                self.assertEqual(value, rules[key])
                if key in seen:
                    self.assertEqual(value, seen[key])
                seen[key] = value
        values = {**rules, "company": template["company"]}
        docs = {doc["document_id"]: doc for doc in build_documents(template)}
        for spec in template["documents"]:
            for reference in spec["clauses"]:
                self.assertIn(template["clauses"][reference].format_map(values),
                              docs[spec["document_id"]]["content"])

    def test_conflicting_schedule_leave_and_remote_rules_are_rejected(self):
        for key, value in (("daily_hours", 9), ("weekly_hours", 35),
                           ("core_end_hour", 20), ("carryover_days", 30),
                           ("remote_days_per_week", 6), ("approval_business_days", 10),
                           ("leave_unit_days", 1), ("annual_leave_days", -1)):
            template = load_template()
            template["rules"][key] = value
            with self.assertRaises(SyntheticDataError):
                validate_template(template)
        template = load_template()
        template["clauses"]["schedule"] += " Employees must work 99 hours."
        with self.assertRaisesRegex(SyntheticDataError, "outside shared rules"):
            validate_template(template)

    def test_conflicting_rendered_content_rejected_even_with_updated_checksum(self):
        documents = build_documents()
        documents[0]["content"] += "\nAnnual leave is five hundred days.\n"
        documents[0]["content_sha256"] = sha256(documents[0]["content"].encode())
        with self.assertRaises(SyntheticDataError):
            validate_documents(documents)
        documents = build_documents()
        documents[0]["policy_values"]["daily_hours"] = 12
        with self.assertRaises(SyntheticDataError):
            validate_documents(documents)

    def test_no_contact_details_credentials_or_person_records(self):
        for doc in build_documents():
            self.assertIsNone(CONTACT_PATTERN.search(doc["content"]))
            self.assertIsNone(SECRET_PATTERN.search(doc["content"]))
            self.assertFalse({"employee_name", "email", "phone", "password", "credentials"} & doc.keys())
        for content in ("Contact fictional.person@example.com", "Visit https://example.com",
                        "Call +1 202 555 0100", "password=FICTIONAL_TEST_ONLY"):
            template = load_template()
            template["clauses"]["scope"] += " " + content
            with self.assertRaises(SyntheticDataError):
                build_documents(template)
        # The approved templates have roles only. New named-person text is not
        # accepted merely because a regex misses it; exact edition validation fails.
        documents = build_documents()
        documents[0]["content"] += "\nFictional Example Person is the employee.\n"
        documents[0]["content_sha256"] = sha256(documents[0]["content"].encode())
        with self.assertRaises(SyntheticDataError):
            validate_documents(documents)

    def test_unknown_rule_and_unsafe_template_substitutions_are_rejected(self):
        for clause in ("{missing}", "{company.__class__}", "{company[0]}", "{company!r}"):
            template = load_template()
            template["clauses"]["scope"] = clause
            with self.assertRaises(SyntheticDataError):
                build_documents(template)

    def test_default_plan_writes_nothing_and_never_uses_network(self):
        result = generate(workspace=self.workspace)
        self.assertEqual(result["mode"], "dry_run")
        self.assertEqual(len(result["artifacts"]), 6)
        self.assertFalse(list(self.workspace.iterdir()))

    def test_idempotent_generation_preserves_existing_files_and_raw_data(self):
        sentinel = self.workspace / "data/raw/blobs/fictional-sentinel"
        sentinel.parent.mkdir(parents=True)
        sentinel.write_bytes(b"FICTIONAL RAW FIXTURE")
        first = generate(workspace=self.workspace, write=True)
        self.assertEqual(len(first["created_files"]), 6)
        before = {p: (p.read_bytes(), p.stat().st_mtime_ns)
                  for p in (self.workspace / OUTPUT).iterdir()}
        second = generate(workspace=self.workspace, write=True)
        self.assertEqual(second["created_files"], [])
        self.assertEqual({p: (p.read_bytes(), p.stat().st_mtime_ns) for p in before}, before)
        self.assertEqual(sentinel.read_bytes(), b"FICTIONAL RAW FIXTURE")
        self.assertEqual(generate(workspace=self.workspace, check=True)["mode"], "check")

    def test_tampered_output_blocks_all_writes_and_check(self):
        generate(workspace=self.workspace, write=True)
        root = self.workspace / OUTPUT
        existing = root / "em-hr-leave-v1.json"
        existing.write_bytes(b"FICTIONAL CORRUPTED FIXTURE")
        missing = root / "manifest.json"
        missing.unlink()
        for options in ({"write": True}, {"check": True}):
            with self.assertRaisesRegex(SyntheticDataError, "refusing overwrite"):
                generate(workspace=self.workspace, **options)
        self.assertEqual(existing.read_bytes(), b"FICTIONAL CORRUPTED FIXTURE")
        self.assertFalse(missing.exists())

    def test_missing_unexpected_and_nonregular_artifacts_fail(self):
        with self.assertRaisesRegex(SyntheticDataError, "missing"):
            generate(workspace=self.workspace, check=True)
        root = self.workspace / OUTPUT
        root.mkdir(parents=True)
        (root / "unexpected.txt").write_text("fictional fixture")
        with self.assertRaisesRegex(SyntheticDataError, "unexpected"):
            generate(workspace=self.workspace, write=True)
        (root / "unexpected.txt").unlink()
        (root / "em-hr-leave-v1.json").mkdir()
        with self.assertRaisesRegex(SyntheticDataError, "path type"):
            generate(workspace=self.workspace, write=True)

    def test_traversal_symlink_and_junction_paths_fail(self):
        for relative in (Path("data/raw/overwrite"), OUTPUT / "../escape", self.workspace / OUTPUT):
            with self.assertRaises(SyntheticDataError):
                _safe_path(self.workspace, relative)
        for method in ("is_symlink", "is_junction"):
            with patch.object(Path, method, return_value=True):
                with self.assertRaisesRegex(SyntheticDataError, "symlinks/junctions"):
                    generate(workspace=self.workspace, write=True)
        self.assertFalse(list(self.workspace.iterdir()))

    def test_existing_lock_is_preserved(self):
        root = self.workspace / OUTPUT
        root.mkdir(parents=True)
        lock = root / ".generation.lock"
        lock.write_text("FICTIONAL LOCK FIXTURE")
        with self.assertRaisesRegex(SyntheticDataError, "lock exists"):
            generate(workspace=self.workspace, write=True)
        self.assertEqual(lock.read_text(), "FICTIONAL LOCK FIXTURE")
        self.assertEqual(len(list(root.iterdir())), 1)

    def test_atomic_publication_failure_cleans_own_temporary_files(self):
        with patch("enterprise_mind.ingestion.synthetic_hr.os.link", side_effect=OSError("fixture failure")):
            with self.assertRaises(OSError):
                generate(workspace=self.workspace, write=True)
        self.assertFalse(list((self.workspace / OUTPUT).iterdir()))

    def test_cli_dry_run_write_and_readonly_check(self):
        with patch("enterprise_mind.ingestion.synthetic_hr.Path.cwd", return_value=self.workspace):
            for arguments, expected in (([], "dry_run"), (["--write"], "write"), (["--check"], "check")):
                output = io.StringIO()
                with redirect_stdout(output):
                    self.assertEqual(main(arguments), 0)
                self.assertEqual(json.loads(output.getvalue())["mode"], expected)


if __name__ == "__main__":
    unittest.main()
