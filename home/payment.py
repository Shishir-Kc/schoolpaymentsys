import requests
import json
from SCHOOL import settings


def payment(amount:float,name:str,order_id:str,order_name:str,email:str,phone:int,return_url:str,website_url:str) -> None:

    url = settings.KHALTI_URL

    payload = json.dumps({
    "return_url": return_url,
    "website_url": website_url,
    "amount": amount,
    "purchase_order_id": order_id,
    "purchase_order_name": order_name,
    "customer_info": {
    "name": name,
    "email": email,
    "phone": phone
    }
    })
    headers = {
     'Authorization': f'key {settings.SECRET_KEY}',
     'Content-Type': 'application/json',
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return response