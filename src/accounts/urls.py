from django.urls import path

from accounts.views import CustomAuthToken
urlpatterns = [
    path('login/', CustomAuthToken.as_view(), name='login'),
]