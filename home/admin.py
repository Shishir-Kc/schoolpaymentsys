from django.contrib import admin
from .models import Custom_user,Payment

admin.site.register(Custom_user)
class PAYMENT_ADMIN(admin.ModelAdmin):
    list_display=[
        'user',
        'purchase_id',
        'purchse_status',
        'purchase_amount',
        'khalti_status',
        'pidx',
        'khalti_transaction_id',
        'initiated_at',
        'updated_at'
    ]
admin.site.register(Payment,PAYMENT_ADMIN)
