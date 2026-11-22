
from collections import defaultdict

from reconciliation.models import SystemARecord, SystemBEntry


def compare_systems():
    disagreements = []

    # Fetch all records
    a_records = SystemARecord.objects.select_related(
        "location"
    ).all()

    b_entries = SystemBEntry.objects.select_related(
        "location"
    ).all()

    # Index System A by organization and record ID
    a_index = {}

    for record in a_records:
        org_id = record.location.org_id

        a_index[(org_id, record.record_id)] = record

    # Group System B entries by organization and normalized reference
    b_index = defaultdict(list)

    for entry in b_entries:
        org_id = entry.location.org_id
        record_ref = entry.normalized_record_ref

        if record_ref:
            b_index[(org_id, record_ref)].append(entry)

    # Compare System A records with System B entries
    for (org_id, record_id), a_record in a_index.items():

        matching_entries = b_index.get(
            (org_id, record_id), []
        )

        # Type 1: Record missing in System B
        if not matching_entries:
            disagreements.append({
                "reason": "missing_in_b",
                "record_id": record_id,
                "organization": org_id,
                "system_a_value": str(a_record.total_value)
                if a_record.total_value is not None else None,
                "system_b_value": None,
                "location": a_record.location.location_name,
                "entry_id": None,
            })

            continue

        # Type 2: Duplicate entries in System B
        if len(matching_entries) > 1:
            for entry in matching_entries:
                disagreements.append({
                    "reason": "duplicate_in_b",
                    "record_id": record_id,
                    "organization": org_id,
                    "system_a_value": str(a_record.total_value)
                    if a_record.total_value is not None else None,
                    "system_b_value": str(entry.value)
                    if entry.value is not None else None,
                    "location": a_record.location.location_name,
                    "entry_id": entry.entry_id,
                })

        # Type 3: Different monetary values
        for entry in matching_entries:
            if (
                a_record.total_value is not None
                and entry.value is not None
                and a_record.total_value != entry.value
            ):
                disagreements.append({
                    "reason": "value_mismatch",
                    "record_id": record_id,
                    "organization": org_id,
                    "system_a_value": str(a_record.total_value),
                    "system_b_value": str(entry.value),
                    "location": a_record.location.location_name,
                    "entry_id": entry.entry_id,
                })

    # Type 4: System B references an unknown A record
    for (org_id, record_ref), entries in b_index.items():

        if (org_id, record_ref) not in a_index:
            for entry in entries:
                disagreements.append({
                    "reason": "orphan_in_b",
                    "record_id": record_ref,
                    "organization": org_id,
                    "system_a_value": None,
                    "system_b_value": str(entry.value)
                    if entry.value is not None else None,
                    "location": entry.location.location_name,
                    "entry_id": entry.entry_id,
                })

    return disagreements
