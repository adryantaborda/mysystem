from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser


# Usuário base (técnico ou gestor)
class User(AbstractUser):
    ROLE_CHOICES = (
        ('technician', 'Technician'),
        ('manager', 'Manager'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    full_name = models.CharField(max_length=150)

    def __str__(self):
        return self.full_name


# Cliente atendido pela OS
class Client(models.Model):
    name = models.CharField(max_length=150)
    address = models.CharField(max_length=255)
    contact = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name


# Ordem de serviço
class ServiceOrder(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('finished', 'Finished'),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_orders')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_orders')

    def __str__(self):
        return f"OS #{self.id} - {self.client.name}"


# Fotos tiradas no serviço
class ServiceOrderPhoto(models.Model):
    service_order = models.ForeignKey(ServiceOrder, on_delete=models.CASCADE, related_name="photos")
    image = models.ImageField(upload_to="service_photos/")
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"OS Photo #{self.service_order.id}"


# Assinatura final da OS
class ServiceOrderSignature(models.Model):
    service_order = models.OneToOneField(ServiceOrder, on_delete=models.CASCADE, related_name="signature")
    signed_by = models.CharField(max_length=100)  # Nome digitado ou técnico
    signed_at = models.DateTimeField(auto_now_add=True)

    image = models.ImageField(upload_to="signatures/", blank=True, null=True)  # imagem da assinatura
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"Signature OS #{self.service_order.id}"
