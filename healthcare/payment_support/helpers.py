from paypalrestsdk import Payment
from django.urls import reverse



#----------------helper functions-----------------------------------
def get_object_or_none(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return None

def prepare_payment_data(req, product_price, product_name):
    return Payment({
                "intent": "sale",
                "payer": {
                    "payment_method": "paypal",
                },
                "redirect_urls": {
                    "return_url": req.build_absolute_uri(reverse('payment_support:execute_payment')),
                    "cancel_url": req.build_absolute_uri(reverse('payment_support:payment_failed')),
                },
                "transactions": [
                    {
                        "amount": {
                            "total": str(product_price),
                            "currency": "USD",
                        },
                        "description": f" Payment for {product_name} ",

                    }
                ],
            })

#--------------------------------------------------------------------