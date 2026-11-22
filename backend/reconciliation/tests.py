from django.test import TestCase

# Create your tests here.

from decimal import Decimal
from reconciliation.models import Location, SystemARecord, SystemBEntry
from reconciliation.comparison import compare_systems


class ReconciliationTests(TestCase):

    def setUp(self):
        self.location = Location.objects.create(
            location_id="LOC-TEST",
            org_id="ORG-TEST",
            location_name="Test Location",
        )

        self.record = SystemARecord.objects.create(
            record_id="REC-1001",
            location=self.location,
            total_value=Decimal("100.00"),
        )

    def create_b_entry(self, entry_id, record_ref, value):
        return SystemBEntry.objects.create(
            entry_id=entry_id,
            record_ref_raw=record_ref,
            normalized_record_ref=record_ref,
            location=self.location,
            value=Decimal(value) if value is not None else None,
        )

    def test_missing_in_b(self):
        results = compare_systems()

        self.assertTrue(
            any(
                item["reason"] == "missing_in_b"
                and item["record_id"] == "REC-1001"
                for item in results
            )
        )

    def test_orphan_in_b(self):
        self.create_b_entry("ENTRY-1", "REC-9999", "50.00")

        results = compare_systems()

        self.assertTrue(
            any(
                item["reason"] == "orphan_in_b"
                and item["record_id"] == "REC-9999"
                for item in results
            )
        )

    def test_duplicate_in_b(self):
        self.create_b_entry("ENTRY-1", "REC-1001", "100.00")
        self.create_b_entry("ENTRY-2", "REC-1001", "100.00")

        results = compare_systems()

        duplicates = [
            item for item in results
            if item["reason"] == "duplicate_in_b"
        ]

        self.assertEqual(len(duplicates), 2)

    def test_value_mismatch(self):
        self.create_b_entry("ENTRY-1", "REC-1001", "90.00")

        results = compare_systems()

        self.assertTrue(
            any(
                item["reason"] == "value_mismatch"
                and item["record_id"] == "REC-1001"
                for item in results
            )
        )
