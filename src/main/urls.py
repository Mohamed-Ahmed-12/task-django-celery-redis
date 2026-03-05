from .views import BatchAPIView, TransactionAPIView
from django.urls import path, include
urlpatterns = [
    path('batches/', BatchAPIView.as_view(), name='batch'),
    path('batches/<uuid:pk>/', BatchAPIView.as_view(), name='batch-detail'),
    path('transactions/<int:pk>/', TransactionAPIView.as_view(), name='transaction-detail'),
]