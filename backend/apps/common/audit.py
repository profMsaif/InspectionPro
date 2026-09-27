from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from django.db.models.fields.files import FieldFile

from apps.audit.models import AuditLog


def _normalize_value(value):
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, FieldFile):
        return value.name
    return value


def build_model_snapshot(instance):
    snapshot = {}
    for field in instance._meta.fields:
        value = getattr(instance, field.name)
        if field.is_relation and value is not None:
            snapshot[field.name] = str(value.pk)
        else:
            snapshot[field.name] = _normalize_value(value)
    return snapshot


def log_audit_event(*, user, action, instance, old_value=None, new_value=None):
    AuditLog.objects.create(
        user=user if getattr(user, "is_authenticated", False) else None,
        action=action,
        entity_type=instance.__class__.__name__,
        entity_id=str(instance.pk),
        old_value=old_value,
        new_value=new_value,
    )
