from django.shortcuts import render


def select_class(request):
    classes = [
        {"subject": "Sample Subject", "section": "Sample Section"},
    ]
    return render(request, "attendance/select_class.html", {"classes": classes})
