from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from app import views
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

urlpatterns = [
    path('', lambda request: redirect('dashboard'), name='home'),
    path('login/', views.CustomLoginView.as_view(template_name='auth/login.html'), name='login'),
    path("logout/", views.logout, name="logout"),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('status/live/', views.live_status, name='live_status'),
    path('orders/', views.orders_partial, name='orders_partial'),
    path('order/<int:pk>/', views.order_detail, name='order_detail'),  # para detalhar depois
    path('order/<int:pk>/upload-photos/', views.upload_photos, name='upload_photos'),
    path('order/<int:pk>/sign/', views.sign_order, name='sign_order'),
    path('orders/create/', views.create_service_order, name='create_service_order'),
    path('order/<int:pk>/download-pdf/', views.generate_order_pdf, name='generate_order_pdf'),
    path("reports/", views.reports, name="reports"),
    path("clients/", views.see_clients, name="see_clients"),
    path("clients/<int:client_id>/orders/", views.client_orders, name="client_orders"),
    path("portfolio", views.portfolio, name="portfolio"),
    path("profile/", views.my_profile, name="my_profile"),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
