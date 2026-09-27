from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter

from apps.audit.views import AuditLogViewSet
from apps.defects.views import DefectViewSet
from apps.dictionaries.views import DictionaryItemViewSet
from apps.elements.views import StructuralElementViewSet
from apps.files.views import InspectionFileViewSet
from apps.inspections.views import InspectionProjectViewSet, TechnicalTaskViewSet, WorkProgramViewSet
from apps.measurements.views import MeasurementViewSet
from apps.notifications.views import NotificationViewSet
from apps.objects.views import BuildingObjectViewSet
from apps.reports.views import ReportTemplateBlockViewSet, ReportTemplateViewSet, ReportViewSet
from apps.users.views import AuthMeView, LogoutView, UserViewSet

router = DefaultRouter()
router.register("users", UserViewSet, basename="users")
router.register("objects", BuildingObjectViewSet, basename="objects")
router.register("projects", InspectionProjectViewSet, basename="projects")
router.register("technical-tasks", TechnicalTaskViewSet, basename="technical-tasks")
router.register("work-programs", WorkProgramViewSet, basename="work-programs")
router.register("elements", StructuralElementViewSet, basename="elements")
router.register("defects", DefectViewSet, basename="defects")
router.register("measurements", MeasurementViewSet, basename="measurements")
router.register("reports", ReportViewSet, basename="reports")
router.register("report-templates", ReportTemplateViewSet, basename="report-templates")
router.register("report-template-blocks", ReportTemplateBlockViewSet, basename="report-template-blocks")
router.register("files", InspectionFileViewSet, basename="files")
router.register("audit", AuditLogViewSet, basename="audit")
router.register("notifications", NotificationViewSet, basename="notifications")
router.register("dictionaries/items", DictionaryItemViewSet, basename="dictionary-items")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/auth/", include("apps.users.urls")),
    path("api/auth/me/", AuthMeView.as_view(), name="auth-me"),
    path("api/auth/logout/", LogoutView.as_view(), name="auth-logout"),
    path("api/", include(router.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
