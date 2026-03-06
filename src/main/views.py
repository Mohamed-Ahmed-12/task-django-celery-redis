from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework import status
from rest_framework.views import APIView, Response
from rest_framework.pagination import PageNumberPagination
from .tasks import start_batch_processing 
from .serializers import BatchDetailSerializer, CreateBatchSerializer, CreateTransactionSerializer
from .models import Batch, Transaction


class BatchAPIView(APIView):
    pagination_class = PageNumberPagination
    def post(self, request):
        transactions=request.data.get('transactions', [])
        if len(transactions) == 0:
            return Response ({"detail":"list of Transactions must be exist"},status=status.HTTP_400_BAD_REQUEST,)
        with transaction.atomic():
            # 1. Validate and Create Batch
            serializer = CreateBatchSerializer(data={"client": request.user.id})
            serializer.is_valid(raise_exception=True)
            batch = serializer.save()
                
            # 2. Validate and Create Transactions
            tx_serializer = CreateTransactionSerializer(
                data=transactions,
                many=True
            )
            tx_serializer.is_valid(raise_exception=True)
            
            # Save returns the list of objects
            transaction_instances = tx_serializer.save(batch=batch)

            # 3. Queue tasks ONLY after the DB successfully commits
            transaction.on_commit(lambda: start_batch_processing.delay(batch.id))

        return Response(
            {"batch_id": batch.id}, 
            status=status.HTTP_202_ACCEPTED
        )  
    
    def get(self,request,pk=None):
        # List all batches for the authenticated client (pagination required)
        if pk is None:
            batches = Batch.objects.filter(client=request.user).prefetch_related('transactions')
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(batches, request)
            
            if page is not None:
                serializer = BatchDetailSerializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)

            serializer = BatchDetailSerializer(batches, many=True)
            return Response(serializer.data)
        
        # Retrieve the status and transactions of a specific batch.
        batch = get_object_or_404(Batch, id=pk,)
        serializer = BatchDetailSerializer(batch)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
class TransactionAPIView(APIView):
    def get(self, request, pk):
        # Retrieve the status of a single transaction.
        transaction = get_object_or_404(Transaction, id=pk)
        transaction = {
            # 'id': transaction.id,
            'status': transaction.status,
        }
        return Response(transaction, status=status.HTTP_200_OK)