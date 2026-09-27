from rest_framework import viewsets

from apps.common.audit import build_model_snapshot, log_audit_event


class AuditedModelViewSet(viewsets.ModelViewSet):
    audit_create_action = "created"
    audit_update_action = "updated"
    audit_delete_action = "deleted"

    def perform_create(self, serializer):
        instance = serializer.save()
        log_audit_event(
            user=self.request.user,
            action=self.audit_create_action,
            instance=instance,
            new_value=build_model_snapshot(instance),
        )

    def perform_update(self, serializer):
        old_value = build_model_snapshot(serializer.instance)
        instance = serializer.save()
        log_audit_event(
            user=self.request.user,
            action=self.audit_update_action,
            instance=instance,
            old_value=old_value,
            new_value=build_model_snapshot(instance),
        )

    def perform_destroy(self, instance):
        old_value = build_model_snapshot(instance)
        log_audit_event(
            user=self.request.user,
            action=self.audit_delete_action,
            instance=instance,
            old_value=old_value,
        )
        instance.delete()

