from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from get_news_query import  QA
# Create your views here.


def index(request):
    return render(request, 'index.html')

@csrf_exempt
def get_query(request):
    if request.method == "POST":
        search_key = request.POST.get("search")
        qa = QA(search_key)
        response_data = {
            "message": "Search successful",
            "search_key": search_key,
        }
        return JsonResponse(response_data)
    else:
        return JsonResponse({"message": "Invalid request"}, status=400)