from django.conf import settings
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static

app_name = 'basic'

urlpatterns = [
    path('', views.home, name='home'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path("register", views.register_request, name="register"),
    path("login", views.login_request, name="login"),
    path('buy-product/<int:product_id>/', views.buy_product_view, name='buy_product'),
    path("get_product_price", views.get_product_price, name="get_product_price"),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)