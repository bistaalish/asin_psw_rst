from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import NewUserForm
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from payment_support.models import Product, Purchase, Order
from payment_support.helpers import get_object_or_none
from django.http import JsonResponse


def about_us_view(request):
    return render(request, 'basic/about_us.html')


def home(request):
    payment_status = request.session.pop('payment_status', None)
    print("\n==================orders===========================")

    try:
        orders = Order.objects.filter(customer=request.user)
        print("\n==================orders===========================")
        prev_purchase = [order.product.id for order in orders]
        print(prev_purchase)

        prev_purchase = Purchase.objects.get(buyer=request.user)
        prev_purchased_stages = [prev_purchase.stage1, prev_purchase.stage2, prev_purchase.stage3]
        prev_purchases = [i+1 for i, stage in enumerate(prev_purchased_stages) if stage]
        # print(prev_purchases)
    
        bought_all = sum(prev_purchased_stages) == len(prev_purchased_stages)
        # print(bought_all)

    except Exception as e:
        print(e)

        prev_purchases = []
        bought_all = False

    next_allow_product = len(prev_purchases) + 1   

    products = Product.objects.all()

    return render(request, 'basic/index.html', {'products': products, 
                                                "prev_purchases": prev_purchases,
                                                "bought_all": bought_all,
                                                "next_allow_product": next_allow_product,
                                                "payment_status": payment_status})


def register_request(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful.")
            # return render(request, 'homepage/index.html')
            return redirect("basic:home")
        messages.error(request, "Unsuccessful registration. Invalid information.")
        # need to send error msg to the front end 
                
    return redirect("basic:home")


def login_request(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')                                                               
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"Hello! welcome back {username}.")
                return redirect("basic:home")
            else:
                print("Invalid user name or password ")
                messages.error(request,"Invalid username or password.")
        else:
            print("invalid user name or password")
            messages.error(request,"Invalid username or password!!!!.")
        
    return redirect("basic:home")


# --- remove --
def buy_product_view(request, product_id):
    print("==================================== buy product view =========================================")
    prev_purchase = get_object_or_none(Purchase, buyer=request.user)
    
    # if already purchased once, skip buy product form
    if prev_purchase and product_id != 0:
        return redirect("payment_support:create_payment", product_id=product_id)
    
    elif prev_purchase and product_id == 0:
        return redirect("payment_support:create_allpayment")

    # else redirect to the buy product form
    # if single product
    # elif product_id != 0:
    #     selected_product = Product.objects.get(pk=product_id)
    #     return render(request, 'basic/buy_product.html', context={"product": selected_product})
    # # if buy all
    # else:
    #     product_price = sum([product.price for product in Product.objects.all()])
    #     return render(request, 'basic/buy_product.html', context={"product_price": product_price})



def get_product_price(request):
    product_id = int(request.GET.get('product_id'))
    
    if product_id == 0:
        product_price = sum([product.price for product in Product.objects.all()])
        return JsonResponse({'price': product_price})
    
    else:
        product = Product.objects.get(pk=product_id)
        return JsonResponse({'price': product.price})
