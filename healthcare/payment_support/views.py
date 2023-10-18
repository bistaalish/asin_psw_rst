from django.shortcuts import redirect
import paypalrestsdk
from django.conf import settings
from .models import Product, Purchase, Order
from .forms import ProductForm
from .helpers import get_object_or_none, prepare_payment_data


paypalrestsdk.configure({
    "mode": "sandbox",  # Change to "live" for production
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_SECRET,
})



def create_allpayment(request):
    prev_purchase = get_object_or_none(Purchase, buyer=request.user)

    if prev_purchase:
        prev_purchased_stages = [prev_purchase.stage1, prev_purchase.stage2, prev_purchase.stage3]
        prev_purchases = [i+1 for i, stage in enumerate(prev_purchased_stages) if stage]
        
        product_price = sum([product.price for product in Product.objects.all() if product.id not in prev_purchases])
        product_name = " + ".join([product.name for product in Product.objects.all() if product.id not in prev_purchases])

        stages = {
            "stage1": True,
            "stage2": True,
            "stage3": True
        }
        purchase_method = Purchase.ALL_PRODUCT


        purchase_data = {
            "buyer_name": prev_purchase.buyer_name,
            "email": prev_purchase.email,
            # "buyer_id": buyer_id,
            "product_id": 0,
            "method": purchase_method,
            "stage1" : stages["stage1"],
            "stage2": stages["stage2"],
            "stage3": stages["stage3"]
        }

        request.session['purchase_data'] = purchase_data

        payment = prepare_payment_data(request, product_price, product_name)

        if payment.create():
            return redirect(payment.links[1].href)
            # Redirect to PayPal for payment

    
    elif request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            
            # Get the buyer_name and email from the form
            buyer_name = form.cleaned_data['buyer_name']
            email = form.cleaned_data['email']

            # no previous purchases
            prev_purchases = []
            product_price = sum([product.price for product in Product.objects.all() if product.id not in prev_purchases])
            product_name = " + ".join([product.name for product in Product.objects.all() if product.id not in prev_purchases])

            stages = {
                "stage1": True,
                "stage2": True,
                "stage3": True
            }

            purchase_method = Purchase.ALL_PRODUCT

            purchase_data = {
                "buyer_name": buyer_name,
                "email": email,
                # "buyer_id": buyer_id,
                "product_id": 0,
                "method": purchase_method,
                "stage1" : stages["stage1"],
                "stage2": stages["stage2"],
                "stage3": stages["stage3"]
            }
            request.session['purchase_data'] = purchase_data

            payment = prepare_payment_data(request, product_price, product_name)


            if payment.create():
                # Redirect to PayPal for payment
                return redirect(payment.links[1].href)
            
    return redirect("payment_support:payment_failed")


def create_payment(request, product_id):
    prev_purchase = get_object_or_none(Purchase, buyer=request.user)
    if prev_purchase:
        product = Product.objects.get(pk=product_id)
        product_price = product.price
        product_name = product.name

        stages = {
            "stage1": prev_purchase.stage1 or product_id == 1,
            "stage2": prev_purchase.stage2 or product_id == 2,
            "stage3": prev_purchase.stage3 or product_id ==3
        }

        purchase_method = Purchase.SINGLE_PRODUCT

        purchase_data = {
            "buyer_name": prev_purchase.buyer_name,
            "email": prev_purchase.email,
            # "buyer_id": buyer_id,
            "product_id": product_id,
            "method": purchase_method,
            "stage1" : stages["stage1"],
            "stage2": stages["stage2"],
            "stage3": stages["stage3"]
        }

        request.session['purchase_data'] = purchase_data

        payment = prepare_payment_data(request, product_price, product_name)

        if payment.create():
            return redirect(payment.links[1].href)
            # Redirect to PayPal for payment
           
    elif request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            # Get the buyer_name and email from the form
            buyer_name = form.cleaned_data['buyer_name']
            email = form.cleaned_data['email']

            product = Product.objects.get(pk=product_id)
            product_price = product.price
            product_name = product.name
            
            stages = {
                "stage1" : product_id == 1,
                "stage2": product_id == 2,
                "stage3": product_id ==3
            }
            purchase_method = Purchase.SINGLE_PRODUCT

            purchase_data = {
                "buyer_name": buyer_name,
                "email": email,
                # "buyer_id": buyer_id,
                "product_id": product_id,
                "method": purchase_method,
                "stage1" : stages["stage1"],
                "stage2": stages["stage2"],
                "stage3": stages["stage3"]
            }

            request.session['purchase_data'] = purchase_data


            payment = prepare_payment_data(request, product_price, product_name)

            if payment.create():
                # Redirect to PayPal for payment
                return redirect(payment.links[1].href)
            
    return redirect("payment_support:payment_failed")    

      
    
def execute_payment(request):
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')

    payment = paypalrestsdk.Payment.find(payment_id)

    if payment.execute({"payer_id": payer_id}):
        try:
            prev_purchase = Purchase.objects.get(buyer=request.user)
        except Exception:
            prev_purchase = None

        purchase_data = request.session.get('purchase_data')

        buyer = request.user

        # -------------------- save order info ---------------------------------------
        if purchase_data.get("product_id") == 0:
            prev_purchase = get_object_or_none(Purchase, buyer=request.user)

            if prev_purchase:
                prev_purchased_stages = [prev_purchase.stage1, prev_purchase.stage2, prev_purchase.stage3]
                prev_purchases = [i+1 for i, stage in enumerate(prev_purchased_stages) if stage]

            else:
                prev_purchases = []
                
            current_purchase = [product for product in Product.objects.all() if product.id not in prev_purchases]
            orders_to_save = [ Order( customer= buyer, product = product) for product in current_purchase ]
            Order.objects.bulk_create(orders_to_save)

        else:
            order = Order(
                customer=buyer,
                product = Product.objects.get(pk=purchase_data.get("product_id"))
            )

            order.save()
        # ------------------------------------------------------------------------------

        #----------------save purchase info ----------------------------------------
        if not prev_purchase:
            purchase = Purchase(
                        buyer_name=purchase_data.get("buyer_name"),
                        email=purchase_data.get("email"),
                        buyer = buyer,
                        method= purchase_data.get("method"),
                        stage1 = purchase_data.get("stage1"),
                        stage2 = purchase_data.get("stage2"),
                        stage3 = purchase_data.get("stage3"),
                    )
            purchase.save()

        else:
            prev_purchase.method = purchase_data.get("method")
            prev_purchase.stage1 = purchase_data.get("stage1")
            prev_purchase.stage2 = purchase_data.get("stage2")
            prev_purchase.stage3 = purchase_data.get("stage3")
            prev_purchase.save()


        del request.session['purchase_data']

        return redirect("payment_support:payment_success") 
    
    else:
        return redirect("payment_support:payment_failed") 



def payment_success(request):
    request.session['payment_status'] = "success"
    return redirect("basic:home")


def payment_failed(request):
    request.session['payment_status'] = "fail"
    return redirect("basic:home")

