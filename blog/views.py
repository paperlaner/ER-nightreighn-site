from django.http import HttpResponse


def index(request):
    return HttpResponse("Это раздел blog, подключенный через include.")


def post_detail(request, post_id):
    return HttpResponse(f"Пост блога #{post_id}")
