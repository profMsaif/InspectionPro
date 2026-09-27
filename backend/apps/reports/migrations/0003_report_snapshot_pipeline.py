from django.db import migrations, models


def migrate_report_statuses(apps, schema_editor):
    Report = apps.get_model("reports", "Report")
    mapping = {
        "Draft": "draft",
        "Generated": "generated",
        "On Review": "generated",
        "Approved": "approved",
        "Archived": "archived",
    }
    for report in Report.objects.all():
        report.status = mapping.get(report.status, "draft")
        if not report.generated_at and report.status in {"generated", "approved", "archived"}:
            report.generated_at = report.created_at
        report.save(update_fields=["status", "generated_at"])


class Migration(migrations.Migration):
    dependencies = [
        ("reports", "0002_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="report",
            name="generated_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="report",
            name="json_snapshot",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AlterField(
            model_name="report",
            name="status",
            field=models.CharField(
                choices=[
                    ("draft", "Draft"),
                    ("generated", "Generated"),
                    ("approved", "Approved"),
                    ("archived", "Archived"),
                ],
                default="draft",
                max_length=32,
            ),
        ),
        migrations.RunPython(migrate_report_statuses, migrations.RunPython.noop),
    ]
