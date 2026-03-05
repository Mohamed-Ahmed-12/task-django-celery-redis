from django.db import models
import uuid
from django.contrib.auth.models import User

class BatchStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    PROCESSING = 'PROCESSING', 'Processing'
    COMPLETED = 'COMPLETED', 'Completed'
    FAILED = 'FAILED', 'Failed'

class TransactionStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    PROCESSING = 'PROCESSING', 'Processing'
    COMPLETED = 'COMPLETED', 'Completed'
    FAILED = 'FAILED', 'Failed'
     
class Batch(models.Model):
    client = models.ForeignKey(User, on_delete=models.PROTECT, related_name='batches')
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)#Batch ID  returned to the user when a batch is created
    status = models.CharField(max_length=255, choices=BatchStatus.choices,default=BatchStatus.PENDING,db_index=True)
    created_at = models.DateTimeField(auto_now_add=True,db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Batch {self.id} - {self.status}"
    class Meta:
        ordering = ['-created_at']
    
class Transaction(models.Model):
    batch = models.ForeignKey(Batch, related_name='transactions', on_delete=models.CASCADE)
    status = models.CharField(max_length=255, choices=TransactionStatus.choices,default=TransactionStatus.PENDING,db_index=True)
    created_at = models.DateTimeField(auto_now_add=True,db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    payload = models.JSONField()
    result = models.JSONField(
        null=True, 
        blank=True, 
        help_text="The raw response or error details from the 3rd party service."
    )
    
    def __str__(self):
        return self.status
    class Meta:
        ordering = ['-created_at']
