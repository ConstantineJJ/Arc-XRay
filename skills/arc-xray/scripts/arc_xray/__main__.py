import argparse
import hashlib
import json
from pathlib import Path
import sys

from . import __version__
from .assess import assess, require_complete
from .model import enrich, safe_relative, validate
from .render import render
from .scan import scan


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def main(argv=None):
    parser = argparse.ArgumentParser(prog="arc-xray", description="Independent, read-only architecture atlas. No MCP/server required.")
    parser.add_argument("--version", action="version", version=__version__)
    commands = parser.add_subparsers(dest="command", required=True)
    audit = commands.add_parser("audit", help="Inventory source and generate the canonical blue viewer; this starts a survey")
    audit.add_argument("project", type=Path)
    audit.add_argument("--out", type=Path, required=True)
    audit.add_argument("--name")
    audit.add_argument("--language", choices=("en", "ru"), default="en")
    audit.add_argument("--max-files", type=int, default=2000)
    audit.add_argument("--exclude", action="append", default=[])
    audit.add_argument("--enrichment", type=Path)
    audit.add_argument("--finalize", action="store_true")
    review = commands.add_parser("review", help="Apply agent source review to an existing atlas using the same renderer")
    review.add_argument("atlas", type=Path)
    review.add_argument("--project", type=Path, required=True)
    review.add_argument("--review-file", type=Path, required=True)
    review.add_argument("--out", type=Path)
    review.add_argument("--language", choices=("en", "ru"), default="en")
    review.add_argument("--finalize", action="store_true")
    preview = commands.add_parser("render", help="Render an existing atlas model for browser or host HTML preview")
    preview.add_argument("atlas", type=Path)
    preview.add_argument("--out", type=Path, required=True)
    preview.add_argument("--language", choices=("en", "ru"), default="en")
    preview.add_argument("--finalize", action="store_true")
    check = commands.add_parser("validate", help="Check references, evidence hashes and optional completion")
    check.add_argument("atlas", type=Path)
    check.add_argument("--project", type=Path)
    check.add_argument("--require-complete", action="store_true")
    commands.add_parser("doctor", help="Report runtime without reading a project")
    args = parser.parse_args(argv)
    try:
        if args.command == "doctor":
            print(json.dumps({"version": __version__, "python": sys.version.split()[0], "runtime_dependencies": "Python standard library", "mcp_required": False,
                              "viewer_id": "arc-xray-blue-v1", "host_preview": "Open the same generated index.html in the host HTML preview"}))
            return 0
        if args.command == "audit":
            if args.out.resolve() == args.project.resolve():
                raise ValueError("Output must be separate from the project root")
            data = scan(args.project, name=args.name, max_files=args.max_files, exclude=args.exclude, output=args.out)
            if args.enrichment:
                data = enrich(data, read_json(args.enrichment), args.project)
        elif args.command == "review":
            data = enrich(validate(read_json(args.atlas)), read_json(args.review_file), args.project)
            args.out = args.out or args.atlas.parent
        else:
            data = validate(read_json(args.atlas))
        if args.command == "validate":
            if args.project:
                for path, digest in {a["path"]: a["sha256"] for a in data["evidence"].values()}.items():
                    if hashlib.sha256(safe_relative(args.project, path).read_bytes()).hexdigest() != digest:
                        raise ValueError("Source hash mismatch: " + path)
            if args.require_complete:
                require_complete(data)
            print(json.dumps({"status": "PASS", "source_hashes_checked": bool(args.project), "evidence": len(data["evidence"]), "review": assess(data)}))
        else:
            if args.finalize:
                require_complete(data)
            result = render(data, args.out, language=args.language)
            result.update({"components": len(data["nodes"]), "relationships": len(data["edges"]), "findings": len(data["findings"]), "review": assess(data)})
            print(json.dumps(result, ensure_ascii=False))
        return 0
    except (ValueError, OSError, KeyError, TypeError) as error:
        print("Arc-XRay: " + str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
