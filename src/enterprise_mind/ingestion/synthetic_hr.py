"""Deterministic fictional HR records; local templates only, with immutable output."""

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from datetime import date
from importlib.resources import files
from pathlib import Path
from string import Formatter
from typing import Any

BANNER = "FICTIONAL ENTERPRISE RECORD - FOR DEMONSTRATION ONLY"
GENERATOR_VERSION = "1.0.0"
TEMPLATE_PATH = "src/enterprise_mind/ingestion/templates/hr-v1.json"
OUTPUT = Path("data/synthetic/hr/v1")
SOURCE_KIND = "project_authored_synthetic"
MAX_FILE_BYTES = 128 * 1024
DOCUMENT_IDS = frozenset({"em-hr-leave-v1", "em-hr-onboarding-v1", "em-hr-remote-work-v1",
                          "em-hr-attendance-v1", "em-hr-offboarding-v1"})
RULE_KEYS = frozenset({"work_days", "timezone", "start_hour", "end_hour", "break_minutes",
                       "daily_hours", "weekly_hours", "core_start_hour", "core_end_hour",
                       "annual_leave_days", "sick_leave_days", "leave_unit_days",
                       "annual_notice_business_days", "approval_business_days", "carryover_days",
                       "onboarding_business_days", "onboarding_review_calendar_days",
                       "remote_days_per_week", "offboarding_notice_calendar_days",
                       "asset_return_business_days"})
CONTACT_PATTERN = re.compile(r"[\w.+-]+@[\w.-]+|https?://|www\.|(?:\+?\d[ ()-]*){8,}")
SECRET_PATTERN = re.compile(r"(?i)(?:password|api[_ -]?key|secret|token)\s*[:=]\s*\S+")


class SyntheticDataError(ValueError):
    """Invalid fictional records or unsafe/conflicting runtime artifacts."""


def encode(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False, indent=2)
            + "\n").encode("utf-8")


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _unique_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise SyntheticDataError("duplicate template key")
        result[key] = value
    return result


def load_template() -> dict[str, Any]:
    resource = files("enterprise_mind.ingestion").joinpath("templates", "hr-v1.json")
    raw = resource.read_bytes()
    if len(raw) > MAX_FILE_BYTES:
        raise SyntheticDataError("template exceeds size bound")
    return json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_keys)


def _fields(text: str) -> set[str]:
    fields = set()
    for _, name, spec, conversion in Formatter().parse(text):
        if name is not None:
            if not re.fullmatch(r"[a-z_]+", name) or spec not in ("", "02d") or conversion:
                raise SyntheticDataError("unsupported template substitution")
            fields.add(name)
    return fields


def validate_template(template: dict[str, Any]) -> None:
    expected = {"schema_version", "dataset_id", "version", "effective_date", "company",
                "owner_department", "rules", "clauses", "documents"}
    if set(template) != expected or type(template["schema_version"]) is not int:
        raise SyntheticDataError("invalid template metadata")
    if (template["schema_version"] != 1 or template["dataset_id"] != "hr-enterprisemind-synthetic-v1"
            or template["version"] != "1.0.0" or template["effective_date"] != "2026-10-12"
            or template["company"] != "EnterpriseMind Demo Company (fictional)"
            or template["owner_department"] != "People Operations (fictional)"):
        raise SyntheticDataError("template does not match this reviewed fictional edition")
    date.fromisoformat(template["effective_date"])
    rules = template["rules"]
    if not isinstance(rules, dict) or set(rules) != RULE_KEYS:
        raise SyntheticDataError("invalid policy rule fields")
    if rules["work_days"] != "Monday through Friday" or rules["timezone"] != "Asia/Calcutta":
        raise SyntheticDataError("unexpected work calendar")
    for key in RULE_KEYS - {"work_days", "timezone", "leave_unit_days"}:
        if type(rules[key]) is not int or not 0 <= rules[key] <= 60:
            raise SyntheticDataError("invalid numeric policy rule")
    if (type(rules["leave_unit_days"]) is not float or rules["leave_unit_days"] != 0.5
            or not 0 <= rules["start_hour"] < rules["end_hour"] <= 23
            or rules["end_hour"] - rules["start_hour"] - rules["break_minutes"] / 60
            != rules["daily_hours"] or rules["daily_hours"] <= 0
            or rules["weekly_hours"] != rules["daily_hours"] * 5
            or not rules["start_hour"] <= rules["core_start_hour"]
            < rules["core_end_hour"] <= rules["end_hour"]
            or not 0 <= rules["carryover_days"] <= rules["annual_leave_days"]
            or not 0 <= rules["remote_days_per_week"] <= 5
            or rules["approval_business_days"] > rules["annual_notice_business_days"]):
        raise SyntheticDataError("conflicting policy definitions")
    clauses = template["clauses"]
    if not isinstance(clauses, dict) or not clauses:
        raise SyntheticDataError("missing policy clauses")
    for name, clause in clauses.items():
        if (not re.fullmatch(r"[a-z_]+", name) or not isinstance(clause, str) or not clause
                or CONTACT_PATTERN.search(clause) or SECRET_PATTERN.search(clause)):
            raise SyntheticDataError("invalid clause or contact/credential-like content")
        if _fields(clause) - (RULE_KEYS | {"company"}):
            raise SyntheticDataError("undefined policy substitution")
        # Quantitative definitions must come from shared rules, not repeated literals.
        # Whole-hour clock suffixes are formatting; the hour remains a shared rule.
        quantitative = re.sub(
            r"\{(?:start_hour|end_hour|core_start_hour|core_end_hour):02d\}:00", "", clause
        )
        literal = "".join(part for part, _, _, _ in Formatter().parse(quantitative))
        if re.search(r"\d", literal):
            raise SyntheticDataError("numeric policy definition outside shared rules")
    specs = template["documents"]
    if not isinstance(specs, list) or len(specs) != 5:
        raise SyntheticDataError("expected five policy documents")
    ids = []
    used = set()
    for spec in specs:
        if set(spec) != {"document_id", "title", "clauses"}:
            raise SyntheticDataError("invalid document specification")
        ids.append(spec["document_id"])
        if (not isinstance(spec["title"], str) or not spec["title"].strip()
                or CONTACT_PATTERN.search(spec["title"]) or SECRET_PATTERN.search(spec["title"])):
            raise SyntheticDataError("invalid document title")
        references = spec["clauses"]
        if (not isinstance(references, list) or not references or references[0] != "scope"
                or len(set(references)) != len(references) or set(references) - clauses.keys()):
            raise SyntheticDataError("invalid clause references")
        used.update(references)
    if len(set(ids)) != len(ids) or set(ids) != DOCUMENT_IDS:
        raise SyntheticDataError("duplicate or unexpected document IDs")
    if used != clauses.keys():
        raise SyntheticDataError("unreferenced policy clauses")


def build_documents(template: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    template = load_template() if template is None else template
    validate_template(template)
    generator_bytes = Path(__file__).read_text(encoding="utf-8").encode("utf-8")
    provenance = {
        "kind": SOURCE_KIND, "is_fictional": True,
        "authoring_method": "Codex-assisted original project policy templates; human review pending",
        "generation_method": "deterministic versioned templates; no model/network at generation",
        "generator_version": GENERATOR_VERSION, "generator_sha256": sha256(generator_bytes),
        "template_path": TEMPLATE_PATH, "template_sha256": sha256(encode(template)),
        "authored_on": "2026-10-12", "source_url": None,
        "allowed_uses": ["collection_for_rag"],
        "rights": "Project-authored demonstration material; external distribution/license decision pending owner review",
    }
    values = {**template["rules"], "company": template["company"]}
    documents = []
    for spec in sorted(template["documents"], key=lambda item: item["document_id"]):
        sections = []
        used_fields = set()
        for reference in spec["clauses"]:
            clause = template["clauses"][reference]
            used_fields.update(_fields(clause) - {"company"})
            sections.append(f"## {reference.replace('_', ' ').title()}\n\n" + clause.format_map(values))
        content = f"{BANNER}\n\n# {spec['title']}\n\n" + "\n\n".join(sections) + "\n"
        if CONTACT_PATTERN.search(content) or SECRET_PATTERN.search(content):
            raise SyntheticDataError("contact/credential-like content in rendered policy")
        documents.append({
            "schema_version": 1, "document_id": spec["document_id"], "title": spec["title"],
            "source_id": template["dataset_id"], "category": "human_resources",
            "version": template["version"], "effective_date": template["effective_date"],
            "owner_department": template["owner_department"], "company": template["company"],
            "access_classification": "internal_demo", "language": "en",
            "is_fictional": True, "provenance": dict(provenance),
            "policy_values": {key: template["rules"][key] for key in sorted(used_fields)},
            "format": "markdown", "content": content,
            "content_sha256": sha256(content.encode("utf-8")),
        })
    return documents


def validate_documents(documents: list[dict[str, Any]], template: dict[str, Any] | None = None) -> None:
    expected = build_documents(template)
    if (not isinstance(documents, list) or len(documents) != len(expected)
            or any(not isinstance(doc, dict) for doc in documents)):
        raise SyntheticDataError("missing policy documents")
    ids = [doc.get("document_id") for doc in documents]
    if any(not isinstance(sid, str) for sid in ids) or len(set(ids)) != len(ids):
        raise SyntheticDataError("duplicate or invalid document IDs")
    for actual, reference in zip(sorted(documents, key=lambda doc: doc["document_id"]), expected):
        if encode(actual) != encode(reference):
            raise SyntheticDataError("metadata, classification, content or policy definitions differ from templates")


def build_artifacts() -> dict[str, bytes]:
    documents = build_documents()
    artifacts = {doc["document_id"] + ".json": encode(doc) for doc in documents}
    manifest = {
        "schema_version": 1, "dataset_id": "hr-enterprisemind-synthetic-v1",
        "version": "1.0.0", "category": "human_resources", "source_kind": SOURCE_KIND,
        "is_fictional": True, "document_count": len(documents),
        "provenance": documents[0]["provenance"],
        "documents": [{"document_id": name.removesuffix(".json"), "path": name,
                       "sha256": sha256(payload), "size_bytes": len(payload)}
                      for name, payload in artifacts.items()],
    }
    artifacts["manifest.json"] = encode(manifest)
    if any(len(payload) > MAX_FILE_BYTES for payload in artifacts.values()):
        raise SyntheticDataError("generated artifact exceeds size bound")
    return artifacts


def _safe_path(workspace: Path, relative: Path, *, directory: bool = False) -> Path:
    if relative.is_absolute() or relative.parts[:4] != OUTPUT.parts or ".." in relative.parts:
        raise SyntheticDataError("output must stay within data/synthetic/hr/v1")
    current = workspace.resolve(strict=True)
    for index, part in enumerate(relative.parts):
        current /= part
        if current.is_symlink() or current.is_junction():
            raise SyntheticDataError("symlinks/junctions are forbidden")
        if current.exists():
            is_directory = directory or index < len(relative.parts) - 1
            if (is_directory and not current.is_dir()) or (not is_directory and not current.is_file()):
                raise SyntheticDataError("unexpected output path type")
    return current


def _preflight(workspace: Path, artifacts: dict[str, bytes], *, require_all: bool) -> None:
    root = _safe_path(workspace, OUTPUT, directory=True)
    if root.exists() and {p.name for p in root.iterdir()} - (artifacts.keys() | {".generation.lock"}):
        raise SyntheticDataError("unexpected files in generated edition; manual review required")
    for name, payload in artifacts.items():
        target = _safe_path(workspace, OUTPUT / name)
        if target.exists():
            if target.stat().st_size != len(payload) or target.read_bytes() != payload:
                raise SyntheticDataError("existing generated artifact differs; refusing overwrite")
        elif require_all:
            raise SyntheticDataError("generated artifact missing")


def generate(*, workspace: Path, write: bool = False, check: bool = False) -> dict[str, Any]:
    if write and check:
        raise SyntheticDataError("write and check are mutually exclusive")
    artifacts = build_artifacts()
    _preflight(workspace, artifacts, require_all=check)
    created = []
    if write:
        root = _safe_path(workspace, OUTPUT, directory=True)
        root.mkdir(parents=True, exist_ok=True)
        lock = _safe_path(workspace, OUTPUT / ".generation.lock")
        try:
            lock_stream = lock.open("x", encoding="utf-8")
        except FileExistsError as exc:
            raise SyntheticDataError("generation lock exists; verify active writer before recovery") from exc
        try:
            with lock_stream:
                _preflight(workspace, artifacts, require_all=False)
                for name, payload in artifacts.items():
                    target = _safe_path(workspace, OUTPUT / name)
                    if target.exists():
                        continue
                    descriptor, staging_name = tempfile.mkstemp(prefix=".generation-", dir=root)
                    staging = Path(staging_name)
                    try:
                        with os.fdopen(descriptor, "wb") as stream:
                            stream.write(payload)
                            stream.flush()
                            os.fsync(stream.fileno())
                        os.link(staging, _safe_path(workspace, OUTPUT / name))
                        created.append(name)
                    finally:
                        staging.unlink(missing_ok=True)
        finally:
            lock.unlink(missing_ok=True)
        _preflight(workspace, artifacts, require_all=True)
    return {"mode": "write" if write else "check" if check else "dry_run",
            "source_kind": SOURCE_KIND, "document_count": 5, "created_files": created,
            "artifacts": [{"path": (OUTPUT / name).as_posix(), "size_bytes": len(payload),
                           "sha256": sha256(payload)} for name, payload in artifacts.items()]}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--write", action="store_true", help="generate the local fictional edition")
    action.add_argument("--check", action="store_true", help="verify existing output without writing")
    args = parser.parse_args(argv)
    try:
        print(json.dumps(generate(workspace=Path.cwd(), write=args.write, check=args.check), indent=2))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
