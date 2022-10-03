from django.urls import path
from .views import *

urlpatterns = [
  path('signup', signup, name='signup'),
  path('activate/<uidb64>/<token>/', activate, name='activate'),
  
  path('login', login_user, name='login_user'),
  path('logout', logout_user, name='logout_user'),

  path('reset-password', reset_password, name='reset_password'),
  path('reset-password/confirm/<uidb64>/<token>', reset_password_confirm, name='reset_password_confirm'),
]
