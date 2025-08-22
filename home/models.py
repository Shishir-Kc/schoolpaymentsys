from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

class Custom_user(AbstractUser):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    age = models.IntegerField(null=True,blank=True)
    contact = models.IntegerField(null=True,blank=True)


class Payment(models.Model):
    
    # saving purchase details from our side ! 
    
    class Status(models.TextChoices):
        SUCESS = "SUCESS","Sucess"
        PENDING = "PENDNG","Pending"
        FAILURE = "FAILURE","Failure"
        INITIATED = "INITIATED", "Initiated"
        REFUNDED =  "REFUNDED",'Refunded'
                
    user = models.ForeignKey(Custom_user,on_delete=models.CASCADE)
    purchase_id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    purchase_order_name = models.CharField(verbose_name='purchase_order_name')
    purchse_status = models.CharField(choices=Status.choices,default=Status.INITIATED)
    purchase_amount = models.FloatField(null=True)
    initiated_at = models.DateTimeField(auto_now_add=True)

    # saving purchase Details from Khalti Side ! 

    pidx = models.CharField(verbose_name='pidx',editable=False)
    khalti_status = models.CharField(verbose_name='Status From Khalti ',editable=False)
    khalti_transaction_id = models.CharField(verbose_name='Khati Transation ID' ,  editable=False)
    updated_at  = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Transaction of user {self.user.username} = > Status : {self.purchse_status}"