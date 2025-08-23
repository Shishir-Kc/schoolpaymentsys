# 💳 Payment Integration with Khalti (Django)

![Logo](https://khaltibyime.khalti.com/wp-content/uploads/2025/07/Logo-for-Blog.png)

---

## 📚 Table of Contents

* [Acknowledgements](#-acknowledgements)
* [Quick Start](#-quick-start)
* [Installation](#-installation)
* [Project Configuration](#-project-configuration)
* [Custom User & Payment Models](#-custom-user--payment-models)
* [Admin Configuration](#-admin-configuration)
* [Templates](#-templates)
* [Views & Routing](#-views--routing)
* [Khalti Payment Integration](#-khalti-payment-integration)

  * [Initiating a Payment](#initiating-a-payment)
  * [Payment Verification](#payment-verification)
* [Generic Errors](#-generic-errors)
* [Example Project](#-example-project)

---

## 🙌 Acknowledgements

* [Official Khalti Documentation](https://docs.khalti.com/)

---

## ⚡ Quick Start

Integrating **Khalti with Django** is straightforward.
It might feel like a learning curve at first, but trust the process!

---

## ⚙️ Installation

### Create Virtual Environment

**Linux / Mac**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows**

```bash
python -m venv .venv
source .venv/Scripts/activate
```

### Install Django

```bash
pip install django
```

### Check Version

```bash
django-admin --version
```

### Create Project & App

```bash
django-admin startproject {project_name} .
django-admin startapp {app_name}
```

---

## 🔧 Project Configuration

### Add App to `INSTALLED_APPS`

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'home',   # your app
]
```

### Add Routing in `{project_name}/urls.py`

```python
from django.urls import path, include

urlpatterns = [
    path('', include('{app_name}.urls')),
]
```

📖 [Django Docs (v5.2)](https://docs.djangoproject.com/en/5.2/)

---

## 👤 Custom User & Payment Models

### Enable Custom User in `settings.py`

```python
AUTH_USER_MODEL = "home.Custom_user"
```

### Define Models (`{app_name}/models.py`)

```python
from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

class Custom_user(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    age = models.IntegerField(null=True, blank=True)
    contact = models.IntegerField(null=True, blank=True)


class Payment(models.Model):
    class Status(models.TextChoices):
        SUCCESS = "SUCCESS", "Success"
        PENDING = "PENDING", "Pending"
        FAILURE = "FAILURE", "Failure"
        INITIATED = "INITIATED", "Initiated"
        REFUNDED = "REFUNDED", "Refunded"

    user = models.ForeignKey(Custom_user, on_delete=models.CASCADE)
    purchase_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    purchase_order_name = models.CharField(max_length=255)
    purchase_status = models.CharField(choices=Status.choices, default=Status.INITIATED)
    purchase_amount = models.FloatField(null=True)
    initiated_at = models.DateTimeField(auto_now_add=True)

    # Khalti details
    pidx = models.CharField(max_length=255, editable=False)
    khalti_status = models.CharField(max_length=100, editable=False)
    khalti_transaction_id = models.CharField(max_length=255, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Transaction by {self.user.username} => {self.purchase_status}"
```

### Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 🛠️ Admin Configuration

```python
from django.contrib import admin
from .models import Custom_user, Payment

admin.site.register(Custom_user)

class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'purchase_id',
        'purchase_status',
        'purchase_amount',
        'khalti_status',
        'pidx',
        'khalti_transaction_id',
        'initiated_at',
        'updated_at',
    ]

admin.site.register(Payment, PaymentAdmin)
```

---

## 🗼️ Templates

Folder structure:

```
{app_name}/templates/home/home.html
{app_name}/templates/payment/payment.html
```

* [home.html Example](https://github.com/Shishir-Kc/schoolpaymentsys/blob/main/home/templates/home/home.html)
* [payment.html Example](https://github.com/Shishir-Kc/schoolpaymentsys/blob/main/home/templates/payment/payment.html)

---

## 🌐 Views & Routing

### Views (`{app_name}/views.py`)

```python
from django.shortcuts import render

def home(request):
    context = {
        'id': request.user.id
    }
    return render(request, 'home/home.html', context)
```

### Routes (`{app_name}/urls.py`)

```python
from django.urls import path
from . import views

app_name = "home"

urlpatterns = [
    path('', views.home, name='home'),
    path("payment/", views.payment_gate, name="payment_gate"),
    path('payment/validation/', views.payment_validation, name="payment_validation"),
]
```

---

## 💳 Khalti Payment Integration

### Initiating a Payment

* Endpoint: `POST /epayment/initiate/`
* Docs: [Khalti e-Payment](https://docs.khalti.com/khalti-epayment/)

Django Example:

```python
import json, requests
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.urls import reverse
from .models import Payment

def payment_gate(request):
    Debug = False

    if request.method == 'POST':
        amount = request.POST.get('payment_amount')
        purchase_name = request.POST.get('purchase_name')

        url = settings.KHALTI_URL
        AMOUNT = int(amount) * 100  # Convert to paisa

        payment_obj = Payment.objects.create(
            user=request.user,
            purchase_order_name=purchase_name,
            purchase_amount=amount
        )

        payload = json.dumps({
            "return_url": request.build_absolute_uri(reverse("home:payment_validation")),
            "website_url": request.build_absolute_uri('/'),
            "amount": AMOUNT,
            "purchase_order_id": str(payment_obj.purchase_id),
            "purchase_order_name": payment_obj.purchase_order_name,
            "customer_info": {
                "name": payment_obj.user.username,
                "email": payment_obj.user.email,
                "phone": payment_obj.user.contact,
            }
        })

        headers = {
            'Authorization': f'key {settings.SECRET_KEY}',
            'Content-Type': 'application/json',
        }

        response = requests.post(url, headers=headers, data=payload)

        if Debug:
            return JsonResponse(response.json(), safe=False)
        else:
            return redirect(response.json()['payment_url'])

    return render(request, 'payment/payment.html')
```

---

### Payment Verification

* Endpoint: `POST /epayment/lookup/`

```python
def payment_validation(request):
    import json, requests

    pidx = request.GET.get("pidx")

    url = f"{settings.KHALTI_BASE_URL}/epayment/lookup/"
    payload = json.dumps({"pidx": pidx})
    headers = {
        "Authorization": f"key {settings.SECRET_KEY}",
        "Content-Type": "application/json",
    }

    response = requests.post(url, headers=headers, data=payload)
    data = response.json()

    # Update Payment object in DB here

    return JsonResponse(data)
```

---

## ❌ Generic Errors

**Invalid Token**

```json
{ "detail": "Invalid token.", "status_code": 401 }
```

**Incorrect pidx**

```json
{ "detail": "Not found.", "error_key": "validation_error" }
```

**Missing Authorization**

```json
{ "detail": "Authentication credentials were not provided.", "status_code": 401 }
```

---

## 📂 Example Project

* 🔗 [Basic Payment Project Example](https://github.com/Shishir-Kc/schoolpaymentsys/)

---

✨ With this README, your Khalti integration guide is **structured, professional, and easy to navigate**.
