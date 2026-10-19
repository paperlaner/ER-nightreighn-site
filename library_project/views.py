from urllib.parse import quote

from django import forms
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import TemplateView
from django.utils import timezone


class AboutPageView(TemplateView):
    template_name = "about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        image_path = quote("Новая папка/gladius-everdark-4-nightreign-full.jpg")
        context["about_image"] = f"{settings.MEDIA_URL}{image_path}"
        context["about_text"] = "интерактивная вики для элден ринг найтрейна"
        return context


class FeedbackForm(forms.Form):
    name = forms.CharField(label="Имя", max_length=120)
    message = forms.CharField(label="Сообщение", widget=forms.Textarea(attrs={"rows": 4}))


def hello(request):
    return HttpResponse("Привет, Django!")


def index_page(request, name="Гость"):
    return render(request, "index.html", {"name": name})


def feedback_view(request):
    if request.method == "POST":
        form = FeedbackForm(request.POST)
        if form.is_valid():
            request.session["feedback_name"] = form.cleaned_data["name"]
            request.session["feedback_message"] = form.cleaned_data["message"]
            return redirect("feedback_success")
    else:
        form = FeedbackForm()

    return render(request, "feedback.html", {"form": form})


def feedback_success(request):
    return render(
        request,
        "feedback_success.html",
        {
            "name": request.session.get("feedback_name", "Гость"),
            "message": request.session.get("feedback_message", ""),
        },
    )


def status_json(request):
    return JsonResponse({"status": "ok"})


def template_demo(request):
    context = {
        "headline": "шаблонный пример",
        "child_text": "Этот дочерний шаблон наследует base.html и вставляет свой текст.",
        "raw_text": "    строка с пробелами слева",
        "published_at": timezone.now(),
        "display_user": request.user,
    }
    return render(request, "template_demo.html", context)


def template_nested(request):
    return render(request, "template_nested.html", {"nested_text": "Задание по многоуровневому наследованию выполнено."})


def numeric_only_view(request, value):
    return HttpResponse(f"Числовой адрес: {value}")


def main_page_address(request):
    return HttpResponse(reverse("books:home"))


def custom_page_not_found(request, exception):
    return render(request, "404.html", status=404)


def preview_page_not_found(request):
    return render(request, "404.html", status=404)


def custom_page_not_found_fallback(request, unmatched=None):
    return render(request, "404.html", status=404)
