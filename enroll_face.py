#!/usr/bin/env python3
"""
Upload a portrait photo to POST /face/enroll so the server stores a Facenet512 embedding.

Prerequisites: backend running, student row exists (e.g. from POST /students or seed_database).

Examples (PowerShell):
  py -3.8 enroll_face.py --image C:\\Users\\you\\Pictures\\me.jpg --student-id 1
  py -3.8 enroll_face.py --image .\\photo.jpg --rfid-tag 584192787859

  $env:NOVA_SERVER="http://127.0.0.1:5001"
"""

import argparse
import base64
import json
import sys
from pathlib import Path

import requests


def main():
    p = argparse.ArgumentParser(description="Enroll a face image via NOVA /face/enroll")
    p.add_argument("--image", required=True, type=Path, help="Path to a JPG/PNG with one clear face")
    p.add_argument("--server", default=None, help="Base URL (default: NOVA_SERVER env or http://127.0.0.1:5001)")
    p.add_argument("--student-id", type=int, default=None)
    p.add_argument("--rfid-tag", default=None, help="Alternative to --student-id")
    args = p.parse_args()

    if not args.student_id and not args.rfid_tag:
        print("Provide --student-id or --rfid-tag", file=sys.stderr)
        sys.exit(1)

    import os
    base = (args.server or os.environ.get("NOVA_SERVER", "http://127.0.0.1:5001")).rstrip("/")
    raw = args.image.read_bytes()
    b64 = base64.b64encode(raw).decode("ascii")

    body = {"image_base64": b64}
    if args.student_id:
        body["student_id"] = args.student_id
    else:
        body["rfid_id"] = args.rfid_tag

    r = requests.post(f"{base}/face/enroll", json=body, timeout=120)
    print(r.status_code, r.text)
    if r.ok:
        try:
            print(json.dumps(r.json(), indent=2))
        except Exception:
            pass
        sys.exit(0)
    sys.exit(1)


if __name__ == "__main__":
    main()
