"""
Importer giúp đọc CSV giá dịch vụ và đẩy vào DB directory.

CSV cần các cột:
hospital_id,service_code,service_name,unit,category_name,payer_type,price,currency,effective_from,effective_to,notes,status

Script sẽ:
- Tạo/đồng bộ danh mục (ServiceCategory) theo category_name + hospital_id.
- Tạo/đồng bộ dịch vụ (Service) theo service_code + hospital_id, cập nhật name/description nếu thay đổi.
- Tạo/đồng bộ ServicePrice theo (service_id, hospital_id, payer_type, area_tag, effective_from, effective_to).
"""

import argparse
import csv
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Dict, Optional, Tuple

from sqlalchemy.orm import Session

# Bổ sung sys.path để chạy script trực tiếp từ repo root
import sys

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from app.directory.db import SessionLocal  # noqa: E402
from app.directory import models  # noqa: E402


def parse_decimal(value: str) -> Decimal:
    cleaned = (value or "").replace(",", "").strip()
    if cleaned == "":
        raise ValueError("empty price")
    try:
        return Decimal(cleaned)
    except InvalidOperation as exc:
        raise ValueError(f"invalid price '{value}'") from exc


def parse_date(value: str):
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()


def get_or_create_category(db: Session, hospital_id: int, name: str, cache: Dict[Tuple[int, str], models.ServiceCategory]):
    key = (hospital_id, name)
    if key in cache:
        return cache[key]

    category = (
        db.query(models.ServiceCategory)
        .filter(
            models.ServiceCategory.hospital_id == hospital_id,
            models.ServiceCategory.name == name,
        )
        .first()
    )
    if not category:
        category = models.ServiceCategory(
            hospital_id=hospital_id,
            name=name,
            status=1,
        )
        db.add(category)
        db.flush()
    cache[key] = category
    return category


def get_or_create_service(
    db: Session,
    hospital_id: int,
    code: str,
    name: str,
    category: Optional[models.ServiceCategory],
):
    service = (
        db.query(models.Service)
        .filter(
            models.Service.hospital_id == hospital_id,
            models.Service.code == code,
        )
        .first()
    )
    if not service:
        service = models.Service(
            hospital_id=hospital_id,
            code=code,
            name=name,
            status=1,
        )
        if category:
            service.categories.append(category)
        db.add(service)
        db.flush()
        return service

    # cập nhật tên nếu thay đổi, và gắn category nếu chưa có
    if name and service.name != name:
        service.name = name
    if category and category not in service.categories:
        service.categories.append(category)
    return service


def upsert_price(
    db: Session,
    service: models.Service,
    row: dict,
):
    price = parse_decimal(row["price"])
    payer_type = row.get("payer_type") or None
    area_tag = row.get("area_tag") or None
    effective_from = parse_date(row.get("effective_from"))
    effective_to = parse_date(row.get("effective_to"))
    unit = (row.get("unit") or "").strip()
    extra_notes = (row.get("notes") or "").strip()
    notes = extra_notes
    if unit:
        notes = f"{notes} | ĐVT: {unit}" if notes else f"ĐVT: {unit}"

    existing = (
        db.query(models.ServicePrice)
        .filter(
            models.ServicePrice.service_id == service.service_id,
            models.ServicePrice.hospital_id == row["hospital_id"],
            models.ServicePrice.payer_type == payer_type,
            models.ServicePrice.area_tag == area_tag,
            models.ServicePrice.effective_from == effective_from,
            models.ServicePrice.effective_to == effective_to,
        )
        .first()
    )
    if existing:
        existing.price = price
        existing.currency = row.get("currency") or "VND"
        existing.notes = notes
        existing.status = row.get("status") or 1
        return existing

    new_price = models.ServicePrice(
        service_id=service.service_id,
        hospital_id=row["hospital_id"],
        payer_type=payer_type,
        area_tag=area_tag,
        price=price,
        currency=row.get("currency") or "VND",
        effective_from=effective_from,
        effective_to=effective_to,
        notes=notes,
        status=row.get("status") or 1,
    )
    db.add(new_price)
    return new_price


def import_csv(csv_path: Path, default_hospital_id: Optional[int] = None) -> int:
    session = SessionLocal()
    created_prices = 0
    category_cache: Dict[Tuple[int, str], models.ServiceCategory] = {}

    try:
        with csv_path.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if not row.get("service_code") or not row.get("service_name"):
                    continue

                hospital_id = default_hospital_id or int(row["hospital_id"])
                row["hospital_id"] = hospital_id

                category_name = (row.get("category_name") or "").strip() or None
                category = None
                if category_name:
                    category = get_or_create_category(session, hospital_id, category_name, category_cache)

                service = get_or_create_service(
                    session,
                    hospital_id=hospital_id,
                    code=row["service_code"].strip(),
                    name=row["service_name"].strip(),
                    category=category,
                )
                upsert_price(session, service, row)
                created_prices += 1

        session.commit()
        return created_prices
    finally:
        session.close()


def main():
    parser = argparse.ArgumentParser(description="Import service prices CSV into directory DB")
    parser.add_argument("--csv", type=Path, required=True, help="Path to service_price CSV")
    parser.add_argument("--hospital-id", type=int, help="Override hospital_id for all rows")
    args = parser.parse_args()

    total = import_csv(args.csv, default_hospital_id=args.hospital_id)
    print(f"Imported/updated {total} price records from {args.csv}")


if __name__ == "__main__":
    main()
