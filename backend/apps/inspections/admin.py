from django.contrib import admin

from apps.inspections.models import InspectionProject, TechnicalTask, WorkProgram

admin.site.register(InspectionProject)
admin.site.register(TechnicalTask)
admin.site.register(WorkProgram)

