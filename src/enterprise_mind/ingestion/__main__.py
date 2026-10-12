"""CLI: validate a manifest or plan/execute an explicitly selected collection."""

import argparse
import json
import sys
from pathlib import Path

from enterprise_mind.ingestion.collector import CollectionError, collect
from enterprise_mind.ingestion.manifest import ManifestError, blocked_reasons, load_manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    validate = commands.add_parser("validate", help="validate metadata offline")
    validate.add_argument("--manifest", type=Path, default=Path("data/sources.yaml"))
    collection = commands.add_parser("collect", help="dry-run unless --download is supplied")
    collection.add_argument("--manifest", type=Path, default=Path("data/sources.yaml"))
    collection.add_argument("--source", action="append", required=True, dest="source_ids")
    collection.add_argument("--output", type=Path, default=Path("data/raw"))
    collection.add_argument("--timeout-seconds", type=float, default=15)
    collection.add_argument("--max-bytes", type=int, default=5 * 1024 * 1024)
    collection.add_argument("--download", action="store_true",
                            help="requires recorded approval and exact allowlist")
    args = parser.parse_args(argv)
    try:
        manifest = load_manifest(args.manifest)
        if args.command == "validate":
            report = {"manifest_sha256": manifest.sha256, "source_count": len(manifest.sources),
                      "sources": [{"source_id": source.source_id, "category": source.category,
                                   "blocked_reasons": blocked_reasons(source, manifest)}
                                  for source in manifest.sources]}
        else:
            report = {"mode": "download" if args.download else "dry_run", "results": collect(
                manifest, args.source_ids, workspace=Path.cwd(), output=args.output,
                download=args.download, timeout=args.timeout_seconds, max_bytes=args.max_bytes)}
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0
    except (ManifestError, CollectionError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
