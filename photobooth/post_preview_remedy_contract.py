"""Public CASE status vocabulary; no backend/provider/custody imports."""

STATUSES=frozenset({'WAITING_PROVIDER','PAID_OWED_DELIVERY','PAID_OWED_REMEDY',
                    'REFUND_REVIEW_REQUIRED','PRINT_INSPECTION_REQUIRED','SERVICE_REVIEW_REQUIRED'})
