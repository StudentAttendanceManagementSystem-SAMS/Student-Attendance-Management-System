from django.urls import path

from . import views

app_name = "attendance"

urlpatterns = [
    path("select-class/", views.SelectClassView.as_view(), name="select_class"),
]
