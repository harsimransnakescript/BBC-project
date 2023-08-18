from django.shortcuts import render
from django.http import StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from get_news_query import  QA
import openai, os
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.environ.get('OPENAI_API_KEY')

def index(request):
    return render(request, 'index.html')



@csrf_exempt
def get_query(request):
    if request.method == "POST":
        search_key = request.POST.get("search")
        
        prompts = [
        {
            'role': 'system',
            'content': f'You are a helpful AI news assistant. Get information and fetch news based on the information with working and complete images links. Fetch me the latest news articles and images links.  Use the following parameters:\n\nAPI Endpoint: https://newsapi.org/v2/everything\nAPI Key: {os.environ.get("NEWS_API_KEY")}\nQ: {search_key}\nSort Order: latest\nNumber of Articles: 5'
        },
        {
            'role': 'user',
            'content': search_key
        }
    ]
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=prompts,
            temperature=0.0,
            stream=True,
            top_p=1.0,
        )
        test = []
        def generate_response():
            for chunk in response:
                chunk_message = chunk['choices'][0]['delta']
                test.append(chunk_message.get("content", ''))
                print(chunk_message.get("content", ''))
                yield chunk_message.get("content", '')

       
        # use Django's StreamingHttpResponse to send the response messages as a stream to the frontend
        return StreamingHttpResponse(generate_response(), headers={'X-Accel-Buffering': 'no'}, content_type="application/json")
    
