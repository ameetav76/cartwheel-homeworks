"""Local HW1 conversation viewer with editable observations. Uses no model API."""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
RECORDS = ROOT / "hw1-session.jsonl"
PAGE = Path(__file__).with_name("index.html")
ANALYSIS = ROOT / "reports" / "hw1-all-runs-analysis.json"
REPORT = ROOT / "reports" / "hw1-all-runs-analysis.md"


def read_analysis() -> dict:
    if not ANALYSIS.exists():
        return {"analysis": None, "report": "", "stale": False}
    analysis = json.loads(ANALYSIS.read_text(encoding="utf-8"))
    digest = hashlib.sha256(RECORDS.read_bytes()).hexdigest() if RECORDS.exists() else None
    return {
        "analysis": analysis,
        "report": REPORT.read_text(encoding="utf-8") if REPORT.exists() else "",
        "stale": analysis.get("source_sha256") != digest,
    }


def revision(record: dict) -> str:
    return hashlib.sha256(json.dumps(record, sort_keys=True).encode()).hexdigest()


def save_observation(line: int, expected_revision: str, observation: str) -> dict:
    if type(line) is not int or line < 1 or not isinstance(observation, str):
        raise ValueError("A valid line number and text observation are required")
    if len(observation) > 20000:
        raise ValueError("Observation must be at most 20,000 characters")
    with RECORDS.open("r+", encoding="utf-8") as stream:
        fcntl.flock(stream, fcntl.LOCK_EX)
        lines = stream.readlines()
        if line > len(lines):
            raise ValueError("Conversation no longer exists; refresh the page")
        record = json.loads(lines[line - 1])
        if revision(record) != expected_revision:
            raise FileExistsError("This conversation changed. Refresh before saving again.")
        record["observation"] = observation
        lines[line - 1] = json.dumps(record, ensure_ascii=False) + "\n"
        stream.seek(0)
        stream.writelines(lines)
        stream.truncate()
        stream.flush()
        os.fsync(stream.fileno())
    return {"record": record, "revision": revision(record)}


def read_records() -> dict:
    conversations, errors = [], []
    if not RECORDS.exists():
        return {"conversations": [], "errors": [], "source": RECORDS.name}
    for line_number, line in enumerate(RECORDS.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
            if not isinstance(record, dict):
                raise ValueError("expected a JSON object")
            conversations.append({"line": line_number, "record": record, "revision": revision(record)})
        except (ValueError, json.JSONDecodeError) as exc:
            errors.append(f"Line {line_number}: {exc}")
    return {"conversations": conversations, "errors": errors, "source": RECORDS.name}


class Handler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        if urlsplit(self.path).path != "/api/observation":
            self.send_error(404)
            return
        # Browser writes must originate from this local viewer.
        if self.headers.get("Origin") != f"http://127.0.0.1:{self.server.server_port}":
            self.send_error(403)
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= 100000 or self.headers.get_content_type() != "application/json":
                raise ValueError("Expected a JSON observation")
            data = json.loads(self.rfile.read(size))
            if not isinstance(data, dict):
                raise ValueError("Expected a JSON object")
            result = save_observation(data.get("line"), data.get("revision"), data.get("observation"))
        except FileExistsError as exc:
            self.send_json({"error": str(exc)}, 409)
        except (ValueError, TypeError) as exc:
            self.send_json({"error": str(exc)}, 400)
        except OSError:
            self.send_json({"error": "Unable to save observation"}, 500)
        else:
            self.send_json(result)

    def send_json(self, data: dict, status: int = 200) -> None:
        body = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        route = urlsplit(self.path).path
        if route == "/":
            body, content_type = PAGE.read_bytes(), "text/html; charset=utf-8"
        elif route == "/export.html":
            from hw1_review.export import build_export
            try:
                body = build_export().encode("utf-8")
            except (OSError, ValueError):
                self.send_error(500, "Unable to export review")
                return
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Disposition", 'attachment; filename="cartwheel-hw1-review.html"')
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
            return
        elif route == "/api/analysis":
            try:
                payload = read_analysis()
            except (OSError, ValueError):
                self.send_json({"error": "Unable to read saved analysis"}, 500)
                return
            self.send_json(payload)
            return
        elif route == "/api/conversations":
            try:
                body = json.dumps(read_records(), ensure_ascii=False).encode("utf-8")
            except OSError:
                self.send_error(500, "Unable to read conversation records")
                return
            content_type = "application/json; charset=utf-8"
        else:
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"HW1 conversation viewer: http://127.0.0.1:{args.port}", flush=True)
    print("Observations save to hw1-session.jsonl. Press Ctrl+C to stop.", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
