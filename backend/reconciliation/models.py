
from django.db import models


class Location(models.Model):
    location_id = models.CharField(max_length=50, unique=True)
    org_id = models.CharField(max_length=50)
    location_name = models.CharField(max_length=150)

    def __str__(self):
        return f"{self.location_id} - {self.location_name}"


class SystemARecord(models.Model):
    record_id = models.CharField(max_length=50, unique=True)
    location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name="system_a_records"
    )

    # Preserve original CSV values
    raw_data = models.JSONField(default=dict)

    event_date = models.DateField(null=True, blank=True)
    category_code = models.CharField(max_length=50, blank=True)
    actor_id = models.CharField(max_length=50, blank=True)

    base_value_raw = models.CharField(max_length=100, blank=True)
    adjustment_raw = models.CharField(max_length=100, blank=True)
    total_value_raw = models.CharField(max_length=100, blank=True)

    base_value = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    adjustment = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    total_value = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )

    state = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.record_id


class SystemBEntry(models.Model):
    entry_id = models.CharField(max_length=50, unique=True)

    # Keep the original reference and its normalized version
    record_ref_raw = models.CharField(max_length=100, blank=True)
    normalized_record_ref = models.CharField(max_length=50, blank=True)

    location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name="system_b_entries"
    )

    recorded_on_raw = models.CharField(max_length=100, blank=True)
    recorded_on = models.DateField(null=True, blank=True)

    value_raw = models.CharField(max_length=100, blank=True)
    value = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )

    label = models.TextField(blank=True)
    raw_data = models.JSONField(default=dict)

    def __str__(self):
        return self.entry_id


class ImportIssue(models.Model):
    SOURCE_CHOICES = [
        ("A", "System A"),
        ("B", "System B"),
        ("LOC", "Locations"),
    ]

    source = models.CharField(max_length=10, choices=SOURCE_CHOICES)
    row_number = models.PositiveIntegerField()
    field_name = models.CharField(max_length=100)
    raw_value = models.TextField(blank=True)
    message = models.TextField()

    def __str__(self):
        return f"{self.source} row {self.row_number}: {self.field_name}"
