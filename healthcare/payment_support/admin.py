from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Order, Purchase



@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("index", 'name', 'description', 'price')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('customer', 'product', 'timestamp', 'custom_is_pending_display')
    list_filter = ('is_pending',)
    actions = ['mark_as_completed']

    def mark_as_completed(self, request, queryset):
        queryset.update(is_pending=False)
    mark_as_completed.short_description = "Mark selected orders as completed"

    def custom_is_pending_display(self, obj):
        if obj.is_pending:
            return format_html('<span style="color: red;">{}</span>', 'Pending')
        else:
            return format_html('<span style="color: green;">{}</span>', 'Completed')

    custom_is_pending_display.short_description = 'Is Pending'


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    # list_display = ('buyer_name', 'email', 'package_name', 'custom_payment_method_display', 'stage1', 'stage2', 'stage3', 'score_result_1', 'score_result_2', 'score_result_3', 'diagnosis')
    list_display = ('buyer_name', 'email', 'buyer', 'method', 'stage1', 'stage2', 'stage3', 'score_result_1', 'score_result_2', 'score_result_3', 'diagnosis')
    def custom_payment_method_display(self, obj):
        if obj.payment_method == 'single package':
            return format_html('<span style="color: green;">{}</span>', obj.payment_method)
        else:
            return format_html('<span style="color: red;">{}</span>', obj.payment_method)
    
    custom_payment_method_display.short_description = 'Payment Method'
    
    fieldsets = (
        ('Purchase Information', {
            'fields': ('buyer_name', 'email', 'buyer' ,'method'),
        }),
        ('Bought Packages', {
            'fields': ('stage1', 'stage2', 'stage3'),
            # You can remove the 'classes' option to display the Payment Stages section by default
        }),
        ('Score Results', {
            'fields': ('score_result_1', 'score_result_2', 'score_result_3'),
        }),
        ('Diagnosis', {
            'fields': ('diagnosis',),
        }),
    )

    # Override save_model to set stage fields based on payment method
    def save_model(self, request, obj, form, change):
        if obj.payment_method != 'all package':
            obj.stage1 = False
            obj.stage2 = False
            obj.stage3 = False
        super().save_model(request, obj, form, change)
