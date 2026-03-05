from .models import Batch, Transaction
from rest_framework import serializers

# Serializers for Transaction models
class CreateTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'status', 'created_at', 'updated_at', 'payload','result']
        read_only_fields = ['id', 'status', 'created_at', 'updated_at','result']


# Serializers for Batch
class CreateBatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Batch
        fields = ['id', 'client', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'status', 'created_at', 'updated_at']
        
        
class BatchDetailSerializer(serializers.ModelSerializer):
    transactions = CreateTransactionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Batch
        fields = ['id', 'client', 'status', 'created_at', 'updated_at', 'transactions']
        read_only_fields = ['id', 'status', 'created_at', 'updated_at', 'transactions']