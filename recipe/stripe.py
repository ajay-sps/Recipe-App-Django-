import stripe
from django.shortcuts import redirect
from recipe.settings import STRIPE_SECRET_KEY 
from django.http import JsonResponse
from django.views import View
from adminuser.models import User,Payments
from django.contrib.auth.mixins import LoginRequiredMixin
from decouple import config

stripe.api_key = STRIPE_SECRET_KEY

# Create a Checkout Session
class CreateCheckoutSessionView(LoginRequiredMixin,View):
     def post(self, request, *args, **kwargs):
        try:
            amount=int(request.POST.get("amount","50"))*100
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": "INR",
                            "unit_amount": amount,  # Amount in cents (e.g., $20.00)
                            "product_data": {
                                "name": "Donate a coffee",
                                "images": ["https://img.icons8.com/?size=512&id=4HBoNoTgzJzF&format=png"],
                            },
                        },
                        "quantity": 1,
                    }
                ],
                
                mode="payment",
                success_url=f"{config('site_base_url')}/payment/success/",
                cancel_url=f"{config('site_base_url')}/home/",
            )
            intent=stripe.PaymentIntent.create(
            setup_future_usage='off_session',
            amount=amount,
            currency='INR',
            automatic_payment_methods={
                'enabled': True,
            })
            Payments.objects.create(user=request.user,Amount=amount/100,payment_intent=intent["id"])
            return redirect(checkout_session.url)

        except Exception as e:
            print(str(e))
            return redirect('/home')