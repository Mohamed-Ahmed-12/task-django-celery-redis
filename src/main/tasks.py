from django.db import transaction
import requests
from .models import Batch, BatchStatus, Transaction, TransactionStatus
from project import celery_app as app
from celery.exceptions import MaxRetriesExceededError


@app.task
def check_batch_completion(batch_id):
    """
    Check if all transactions in a batch are finished.
    If none are left in PENDING/PROCESSING, mark batch as COMPLETED.
    """
    with transaction.atomic():
        batch = Batch.objects.select_for_update().get(id=batch_id)
        finished_statuses = [TransactionStatus.COMPLETED, TransactionStatus.FAILED]

        # Skip if batch already finalized
        if batch.status in finished_statuses:
            return

        # Look for unfinished transactions
        unfinished = batch.transactions.exclude(status__in=finished_statuses).exists()

        if not unfinished:
            # Check if any children failed
            has_failures = batch.transactions.filter(status=TransactionStatus.FAILED).exists()
            
            if has_failures:
                batch.status = BatchStatus.FAILED
            else:
                batch.status = BatchStatus.COMPLETED
            
            batch.save(update_fields=["status"])

@app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=10,
    queue="transactions"
)
def process_transaction_task(self, transaction_id):
    """
    Process a single transaction:
    - Mark as PROCESSING
    - Call external validator
    - Retry on transient errors with exponential backoff
    - Mark FAILED after max retries
    - Always trigger batch completion check
    """
    tx = Transaction.objects.select_related("batch").get(id=transaction_id)
    tx.status = TransactionStatus.PROCESSING
    tx.save(update_fields=["status"])

    try:
        # web not localhost because localhost point to celery here not django so web point to django (web service)
        response = requests.post("http://web:8000/api/mock-validate/", json={"payload": tx.payload}, timeout=10 )
        
        if response.status_code == 200:
            tx.result = response.json()
            tx.status = TransactionStatus.COMPLETED
            tx.save(update_fields=["status", "result"])
            
            # Trigger only on success
            check_batch_completion.delay(tx.batch_id)
        else:
            # Trigger the retry logic because it wasn't a 200 OK
            raise Exception(f"Provider returned {response.status_code}")
    except Exception as exc:
        tx.result = {"detail": str(exc), "retry": self.request.retries}
        tx.save(update_fields=["result"])

        try:
            # Re-queue for later
            countdown = self.default_retry_delay * (2 ** self.request.retries)
            raise self.retry(exc=exc, countdown=countdown)
        except MaxRetriesExceededError:
            # Final failure path
            tx.status = TransactionStatus.FAILED
            tx.save(update_fields=["status", "result"])
            
            # Trigger only on final failure
            check_batch_completion.delay(tx.batch_id)


@app.task
def start_batch_processing(batch_id):
    """
    Kick off processing for all transactions in a batch.
    Each transaction is queued individually.
    """
    tx_ids = list(
        Transaction.objects.filter(batch_id=batch_id).values_list("id", flat=True)
    )
    print(f"Starting batch {batch_id} with transactions: {tx_ids}")
    for tx_id in tx_ids:
        process_transaction_task.delay(tx_id)
