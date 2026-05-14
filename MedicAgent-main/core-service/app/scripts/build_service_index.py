"""
Build FAISS index for service catalog (name + aliases + categories).
Usage:
    python core-service/app/scripts/build_service_index.py [--hospital-id 1]
"""

import argparse
import sys
from pathlib import Path

from sqlalchemy.orm import Session

# Ensure app package import works when running from repo root
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from app.directory.db import SessionLocal  # noqa: E402
from app.embeddings.service_index import build_index  # noqa: E402


def main(hospital_id: int | None):
    session: Session = SessionLocal()
    try:
        count, index_path, metadata_path = build_index(session, hospital_id=hospital_id)
        print(f"Indexed {count} services -> {index_path}, {metadata_path}")
    finally:
        session.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build FAISS index for services")
    parser.add_argument("--hospital-id", type=int, help="Filter services by hospital_id (optional)")
    args = parser.parse_args()
    main(args.hospital_id)
