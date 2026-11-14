import argparse
import hashlib
import json
from pathlib import Path
import sys

from . import __version__
from .model import enrich, safe_relative, validate
from .render import render
from .scan import scan


def main(argv=None):
    parser = argparse.ArgumentParser(prog="arc-xray", description="Create a read-only, source-backed interactive architecture atlas.")
    parser.add_argument("--version", action="version", version=__version__)
    commands = parser.add_subparsers(dest="command", required=True)
    audit = commands.add_parser("audit", help="Inspect source without executing it and generate atlas files")
    audit.add_argument("project", type=Path)
    audit.add_argument("--out", type=Path, required=True, help="New/empty directory, or an existing Arc-XRay output directory")
    audit.add_argument("--name")
    audit.add_argument("--language", choices=("en", "ru"), default="en")
    audit.add_argument("--max-files", type=int, default=2000)
    audit.add_argument("--exclude", action="append", default=[], help="Project-relative glob; repeat as needed")
    audit.add_argument("--enrichment", type=Path, help="Agent-authored semantic review JSON")
    check = commands.add_parser("validate", help="Check graph references and optional source hashes")
    check.add_argument("atlas", type=Path)
    check.add_argument("--project", type=Path)
    server = commands.add_parser("mcp", help="Run the local MCP server over stdio")
    server.add_argument("--data-dir", type=Path)
    server.add_argument("--allow-root", type=Path, action="append", default=[])
    commands.add_parser("doctor", help="Report local prerequisites without inspecting a project")
    args = parser.parse_args(argv)
    try:
        if args.command == "audit":
            if args.out.resolve() == args.project.resolve():
                raise ValueError("Output must be separate from the project root")
            data = scan(args.project, name=args.name, max_files=args.max_files, exclude=args.exclude, output=args.out)
            if args.enrichment:
                patch = json.loads(args.enrichment.read_text(encoding="utf-8-sig"))
                data = enrich(data, patch, args.project)
            result = render(data, args.out, language=args.language)
            result.update({"components": len(data["nodes"]), "relationships": len(data["edges"]),
                           "findings": len(data["findings"]), "truncated": data["coverage"]["truncated"]})
            print(json.dumps(result, ensure_ascii=False))
        elif args.command == "validate":
            data = validate(json.loads(args.atlas.read_text(encoding="utf-8-sig")))
            if args.project:
                for anchor in data["evidence"].values():
                    path = safe_relative(args.project, anchor["path"])
                    if hashlib.sha256(path.read_bytes()).hexdigest() != anchor["sha256"]:
                        raise ValueError("Source hash mismatch: " + anchor["path"])
            print(json.dumps({"status": "PASS", "source_hashes_checked": bool(args.project), "evidence": len(data["evidence"])}))
        elif args.command == "doctor":
            print(json.dumps({"version": __version__, "python": sys.version.split()[0], "runtime_dependencies": "Python standard library",
                "project_execution": False, "host_preview": "MCP Apps client required; file:// HTML works independently"}))
        else:
            from .server import serve
            serve(data_dir=args.data_dir, allowed_roots=args.allow_root)
        return 0
    except (ValueError, OSError, KeyError, TypeError, json.JSONDecodeError) as error:
        print("Arc-XRay: " + str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
