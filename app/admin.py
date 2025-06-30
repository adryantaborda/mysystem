from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import User, Client, ServiceOrder, ServiceOrderPhoto, ServiceOrderSignature
from django.contrib.auth.admin import UserAdmin


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('email', 'full_name', 'role', 'is_active', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role', 'full_name')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('role', 'full_name')}),
    )


class ServiceOrderPhotoInline(admin.TabularInline):
    model = ServiceOrderPhoto
    extra = 1


class ServiceOrderSignatureInline(admin.StackedInline):
    model = ServiceOrderSignature
    extra = 0
    readonly_fields = ('signed_at', 'ip_address', 'image')


@admin.register(ServiceOrder)
class ServiceOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'status', 'created_at', 'assigned_to')
    list_filter = ('status',)
    search_fields = ('client__name', 'description')
    inlines = [ServiceOrderPhotoInline, ServiceOrderSignatureInline]


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'address')
    search_fields = ('name',)


@admin.register(ServiceOrderPhoto)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('service_order', 'uploaded_by', 'uploaded_at')


@admin.register(ServiceOrderSignature)
class SignatureAdmin(admin.ModelAdmin):
    list_display = ('service_order', 'signed_by', 'signed_at', 'ip_address')
