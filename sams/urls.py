from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('masterdata/', include('masterdata.urls')),
    path('attendance/', include('attendance.urls')),
    path('analytics/', include('analytics.urls')),
]
