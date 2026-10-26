from django.contrib import admin

from .models import Attendance, AttendanceConfig

admin.site.register(Attendance)
admin.site.register(AttendanceConfig)
