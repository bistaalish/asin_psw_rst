from django.conf import settings
from django.urls import path
from . import views
from django.conf.urls.static import static

app_name = 'payment_support'

urlpatterns = [
    path('execute_payment/', views.execute_payment, name='execute_payment'),
    path('payment-failed/', views.payment_failed, name='payment_failed'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('create-payment/<int:product_id>/', views.create_payment, name='create_payment'),
    path('create-allpayment/', views.create_allpayment, name='create_allpayment'),

]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)