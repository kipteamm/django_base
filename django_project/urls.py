from django.urls import path, include
from .views import *

urlpatterns = [
    # Home
    path('', index, name='index'),

    # Authentication
    path('', include('auth.urls')),

    # Application
    path('', include('app.urls')),
]
