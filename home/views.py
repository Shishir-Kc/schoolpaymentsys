from django.shortcuts import render,redirect
from django.urls import reverse
from SCHOOL import settings
import json
import requests
from django.http import JsonResponse
from .models import Payment
from django.http import HttpResponse


def home(request):
    context = {
        'id':request.user.id
    }
    return render(request,'home/home.html',context)


def payment_gate(request):

    Debug = False

    if request.method == 'POST':
        amount=request.POST.get('payment_amount')
        purchse_name = request.POST.get('purchase_name')

        url = settings.KHALTI_URL
        AMOUNT = int(amount)*100

        payment_obj = Payment.objects.create(user=request.user,purchase_order_name=purchse_name,purchase_amount=amount)
     
        print("======================================ID========================================")
        
        payload = json.dumps({
        "return_url": request.build_absolute_uri(reverse("home:payment_validation")),
        "website_url":request.build_absolute_uri('/'),
        "amount": AMOUNT,
        "purchase_order_id": str(payment_obj.purchase_id),
        "purchase_order_name": payment_obj.purchase_order_name,
        "customer_info": {
        "name": payment_obj.user.username,
        "email": payment_obj.user.email,
        "phone": payment_obj.user.contact
         }
        })
        headers = {
            'Authorization': f'key {settings.SECRET_KEY}',
            'Content-Type': 'application/json',
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        print("=====================================================================")
        print(response)


        
        if Debug:
            return JsonResponse(response.json(), safe=False)
        else:
            return redirect(response.json()['payment_url'])
        
    else:
        return render(request,'payment/payment.html')
    
def payment_validation(request)->None:
    print("=======================================REQUEST===========================================")
    print(request)
    print("==============================================================================================")
    param = request.GET
    pidx = param.get("pidx")
    amount = param.get('total_amount')
    transaction_id = param.get('transaction_id')
    status = param.get('status')
    purchase_order_id = param.get('purchase_order_id')


    print("================================PIDX=======================================")
    print(pidx)
    print("================================AMOUNT=======================================")
    print(int(amount)/100)
    print("================================ORDER_ID=======================================")
    print(purchase_order_id)


    URL = f"{settings.KHALTI_BASE_URL}{settings.KHALTI_PAYMENT_VERIFICATION_URL}"



    payload = json.dumps({"pidx": pidx})

    headers = {
        "Authorization": f"key {settings.SECRET_KEY}",
        "Content-Type": "application/json",
    }

    response = requests.post(URL, headers=headers, data=payload)

    print("===============================RESPONSE========================================")
    print(" = = = == = = = > ", response)
    print("Status Code:", response.status_code)

    print("==========================================JSON======================================")
    
    data = response.json()

    print(data)
    print("=======================================================Amount===========================================================")
     
    print(int(amount)/100)
    try:
        purchase_obj = Payment.objects.get(purchase_id = purchase_order_id)
    except Exception:
        return HttpResponse("Payment has not been done ! ")

    amount_in_paisa = purchase_obj.purchase_amount
 
    
    if (data['total_amount'] == int(amount_in_paisa)*100) and (data['transaction_id']== transaction_id) and (data['status']==status) :
        print('data has been matched !')
        if data['status'] == 'Completed':
            status = 'Completed'
            purchase_state = purchase_obj.Status.SUCESS
        elif data['status'] in ('User canceled','Expired','Failed'):
            status = 'Failed'
            purchase_state = purchase_obj.Status.FAILURE
        else:
            status = 'Pending'
            purchase_state = purchase_obj.Status.PENDING

        purchase_obj.pidx = pidx
        purchase_obj.khalti_transaction_id = transaction_id
        purchase_obj.khalti_status = status
        purchase_obj.purchse_status = purchase_state
        purchase_obj.save()

        return HttpResponse('PAYMENT SUCESSFUL ! ')

    else:
        if data['status'] in ('User canceled','Expired','Failed'):
            status = 'Failed'
            purchase_state = purchase_obj.Status.FAILURE
        else:
            status = 'Pending'
            purchase_state = purchase_obj.Status.PENDING

        purchase_obj.pidx = pidx
        purchase_obj.khalti_transaction_id = transaction_id
        purchase_obj.khalti_status = status
        purchase_obj.purchse_status = purchase_state
        purchase_obj.save()
        return HttpResponse("PAYMENT FAILURE ! ")


