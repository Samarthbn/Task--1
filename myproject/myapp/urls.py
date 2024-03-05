from django.urls import path
from . import views


urlpatterns = [

    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('get-random-question/', views.get_random_question, name='get_random_question'),

]
