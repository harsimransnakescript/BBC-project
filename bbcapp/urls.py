from django.urls import path
from .views import *

urlpatterns = [
    path('', index),
    path('get-query', get_query, name='get-query'),
]
