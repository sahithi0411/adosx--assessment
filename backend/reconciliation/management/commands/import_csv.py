
import csv
import re
from decimal import Decimal, InvalidOperation
from datetime import datetime
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from reconciliation.models import (
    Location,
    SystemARecord,
    SystemBEntry,
    ImportIssue,
)


def parse_decimal(raw_value):
    """Parse a number while preserving the original CSV value."""
    if raw_value is None or not raw_value.strip():
        return None

    cleaned = raw_value.strip().replace(",", "")

    try:
        return Decimal(cleaned)
    except InvalidOperation:
        return None


def parse_date(raw_value):
    if not raw_value or not raw_value.strip():
        return None

    try:
        return datetime.strptime(raw_value.strip(), "%Y-%m-%d").date()
    except ValueError:
        return None


def normalize_record_ref(raw_ref):
    """
    Convert REC-1034, rec1034, REC - 1034 and 1034
    into REC-1034.
    """
    cleaned = re.sub(r"[^A-Z0-9]", "", raw_ref.upper().strip())

    if cleaned.startswith("REC"):
        number = cleaned[3:]
    else:
        number = cleaned

    if number.isdigit():
        return f"REC-{int(number):04d}"

    return ""


class Command(BaseCommand):
    help = "Import locations, System A and System B CSV files"

    def add_arguments(self, parser):
        parser.add_argument(
            "--data-dir",
            type=str,
            required=True,
            help="Path to the folder containing the CSV files",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        data_dir = Path(options["data_dir"])

        required_files = [
            "locations.csv",
            "system_a.csv",
            "system_b.csv",
        ]

        for filename in required_files:
            if not (data_dir / filename).exists():
                raise CommandError(f"Missing file: {filename}")

        # Clear previous imported data before a fresh import.
        ImportIssue.objects.all().delete()
        SystemBEntry.objects.all().delete()
        SystemARecord.objects.all().delete()
        Location.objects.all().delete()

        self.import_locations(data_dir / "locations.csv")
        self.import_system_a(data_dir / "system_a.csv")
        self.import_system_b(data_dir / "system_b.csv")

        self.stdout.write(
            self.style.SUCCESS("CSV import completed successfully.")
        )

    def read_csv(self, file_path):
        with open(file_path, "r", encoding="utf-8-sig", newline="") as file:
            yield from csv.DictReader(file)

    def record_issue(self, source, row_number, field, raw, message):
        ImportIssue.objects.create(
            source=source,
            row_number=row_number,
            field_name=field,
            raw_value=raw or "",
            message=message,
        )

    def get_location(self, location_id, source, row_number):
        location = Location.objects.filter(
            location_id=location_id.strip()
        ).first()

        if not location:
            self.record_issue(
                source,
                row_number,
                "location_id",
                location_id,
                "Location does not exist. Row retained only if location can be resolved.",
            )

        return location

    def import_locations(self, file_path):
        for row_number, row in enumerate(
            self.read_csv(file_path), start=2
        ):
            try:
                Location.objects.create(
                    location_id=row["location_id"].strip(),
                    org_id=row["org_id"].strip(),
                    location_name=row["location_name"].strip(),
                )
            except Exception as error:
                self.record_issue(
                    "LOC",
                    row_number,
                    "row",
                    str(row),
                    f"Could not import location: {error}",
                )

        self.stdout.write("Locations imported.")

    def import_system_a(self, file_path):
        for row_number, row in enumerate(
            self.read_csv(file_path), start=2
        ):
            record_id = (row.get("record_id") or "").strip()
            location_id = row.get("location_id") or ""
            location = self.get_location(location_id, "A", row_number)

            raw_base = row.get("base_value") or ""
            raw_adjustment = row.get("adjustment") or ""
            raw_total = row.get("total_value") or ""
            raw_date = row.get("event_date") or ""

            base = parse_decimal(raw_base)
            adjustment = parse_decimal(raw_adjustment)
            total = parse_decimal(raw_total)
            event_date = parse_date(raw_date)

            for field, raw, parsed in [
                ("base_value", raw_base, base),
                ("adjustment", raw_adjustment, adjustment),
                ("total_value", raw_total, total),
            ]:
                if raw.strip() and parsed is None:
                    self.record_issue(
                        "A", row_number, field, raw,
                        "Invalid numeric value."
                    )

            if raw_date.strip() and event_date is None:
                self.record_issue(
                    "A", row_number, "event_date", raw_date,
                    "Invalid date."
                )

            if not location:
                # Preserve the full row as an issue rather than silently
                # discarding it when its foreign key cannot be resolved.
                self.record_issue(
                    "A", row_number, "row", str(row),
                    "System A row could not be linked to a known location."
                )
                continue

            try:
                SystemARecord.objects.create(
                    record_id=record_id,
                    location=location,
                    raw_data=row,
                    event_date=event_date,
                    category_code=row.get("category_code", ""),
                    actor_id=row.get("actor_id", ""),
                    base_value_raw=raw_base,
                    adjustment_raw=raw_adjustment,
                    total_value_raw=raw_total,
                    base_value=base,
                    adjustment=adjustment,
                    total_value=total,
                    state=row.get("state", ""),
                )
            except Exception as error:
                self.record_issue(
                    "A", row_number, "row", str(row),
                    f"Could not import record: {error}"
                )

        self.stdout.write("System A imported.")

    def import_system_b(self, file_path):
        for row_number, row in enumerate(
            self.read_csv(file_path), start=2
        ):
            entry_id = (row.get("entry_id") or "").strip()
            raw_ref = row.get("record_ref") or ""
            raw_location = row.get("location_id") or ""
            raw_value = row.get("value") or ""
            raw_date = row.get("recorded_on") or ""

            location = self.get_location(raw_location, "B", row_number)

            value = parse_decimal(raw_value)
            recorded_on = parse_date(raw_date)

            if raw_value.strip() and value is None:
                self.record_issue(
                    "B", row_number, "value", raw_value,
                    "Invalid numeric value."
                )

            if raw_date.strip() and recorded_on is None:
                self.record_issue(
                    "B", row_number, "recorded_on", raw_date,
                    "Invalid date."
                )

            if not location:
                self.record_issue(
                    "B", row_number, "row", str(row),
                    "System B row could not be linked to a known location."
                )
                continue

            try:
                SystemBEntry.objects.create(
                    entry_id=entry_id,
                    location=location,
                    record_ref_raw=raw_ref,
                    normalized_record_ref=normalize_record_ref(raw_ref),
                    recorded_on_raw=raw_date,
                    recorded_on=recorded_on,
                    value_raw=raw_value,
                    value=value,
                    label=row.get("label", ""),
                    raw_data=row,
                )
            except Exception as error:
                self.record_issue(
                    "B", row_number, "row", str(row),
                    f"Could not import entry: {error}"
                )

        self.stdout.write("System B imported.")
