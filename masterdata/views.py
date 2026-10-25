from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView

from .forms import StudentCreateForm
from .models import Student


class StudentListView(ListView):
    model = Student
    template_name = "masterdata/student_list.html"
    context_object_name = "students"
    queryset = Student.objects.select_related("section").order_by("usn")


class StudentCreateView(SuccessMessageMixin, CreateView):
    model = Student
    form_class = StudentCreateForm
    template_name = "masterdata/form.html"
    success_url = reverse_lazy("masterdata:student_list")
    success_message = "Student added."
    extra_context = {
        "title": "Add student",
        "cancel_url": reverse_lazy("masterdata:student_list"),
    }
