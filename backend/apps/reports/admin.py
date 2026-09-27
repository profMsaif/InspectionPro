from django.contrib import admin

from apps.reports.models import Report, ReportTemplate, ReportTemplateBlock

admin.site.register(Report)
admin.site.register(ReportTemplate)
admin.site.register(ReportTemplateBlock)
