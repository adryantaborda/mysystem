from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.utils.timezone import now
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
from django.template.loader import render_to_string
from django.http import HttpResponse, FileResponse
from django.conf import settings
from datetime import timedelta
import base64, tempfile
from weasyprint import HTML

from .models import ServiceOrder, ServiceOrderPhoto, ServiceOrderSignature, Client, User


def is_demo_user(user):
    return user.username == "demo"


class CustomLoginView(LoginView):
    template_name = 'auth/login.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        user = self.request.user
        if user.role == 'manager':
            return '/dashboard/'
        elif user.role == 'technician':
            return '/dashboard/'
        return super().get_success_url()
    
from django.contrib.auth import logout as auth_logout
from django.shortcuts import redirect

def logout(request):
    auth_logout(request)
    return redirect('login')



@login_required
def dashboard(request):
    orders = ServiceOrder.objects.all().order_by("-created_at")

    # Se demo, também trazer ordens em sessão (só visuais)
    demo_orders = request.session.get("demo_orders", []) if is_demo_user(request.user) else []

    return render(request, 'dashboard.html', {
        "orders": orders,
        "demo_orders": demo_orders,
        "demo": is_demo_user(request.user)
    })




def live_status(request):
    return HttpResponse(f"<p>Last updated: {now().strftime('%H:%M:%S')}</p>")


def orders_partial(request):
    status = request.GET.get("status")
    if status:
        orders = ServiceOrder.objects.filter(status=status)
    else:
        orders = ServiceOrder.objects.all()
    return render(request, "partials/orders_list.html", {"orders": orders})


from django.contrib import messages
from django.utils.safestring import mark_safe

@login_required
def upload_photos(request, pk):
    order = get_object_or_404(ServiceOrder, pk=pk)

    if is_demo_user(request.user) and order.created_by.username != "demo":
        msg = mark_safe(
            'You cannot upload photos to real orders in demo mode. '
            'Create your own order <a href="/orders/create/" class="underline text-violet-700">here</a>.'
        )
        messages.warning(request, msg)
        return redirect("order_detail", pk=pk)

    if request.method == "POST":
        for file in request.FILES.getlist("photos"):
            ServiceOrderPhoto.objects.create(
                service_order=order,
                image=file,
                uploaded_by=request.user
            )
        messages.success(request, "Photos uploaded successfully.")
        return redirect("order_detail", pk=pk)

    return render(request, "orders/upload_photos.html", {"order": order})



@login_required
def order_detail(request, pk):
    order = get_object_or_404(ServiceOrder, pk=pk)
    return render(request, 'orders/order_detail.html', {'order': order})


@login_required
def sign_order(request, pk):
    order = get_object_or_404(ServiceOrder, pk=pk)

    if is_demo_user(request.user):
        return redirect("order_detail", pk=pk)

    if request.method == "POST":
        data_url = request.POST.get("signature_data_url")
        name = request.POST.get("signed_by")

        format, imgstr = data_url.split(';base64,')
        ext = format.split('/')[-1]
        file_data = ContentFile(base64.b64decode(imgstr), name=f'signature_{pk}.{ext}')

        ServiceOrderSignature.objects.create(
            service_order=order,
            signed_by=name,
            image=file_data,
            ip_address=request.META.get('REMOTE_ADDR')
        )
        return redirect('order_detail', pk=pk)

    return render(request, 'orders/sign_order.html', {'order': order})


@login_required
def create_service_order(request):
    if is_demo_user(request.user):
        if request.method == "POST":
            demo_orders = request.session.get("demo_orders", [])
            demo_orders.append({
                "id": len(demo_orders) + 1,
                "client": {"name": "Demo Client"},
                "description": request.POST.get("description"),
                "status": "open",
                "assigned_to": {"full_name": "Demo Technician"} if request.POST.get("assigned_to") else None
            })
            request.session["demo_orders"] = demo_orders
            return redirect("dashboard")

        clients = Client.objects.all()
        technicians = User.objects.filter(role='technician')
        return render(request, 'orders/create_service_order.html', {
            'clients': clients,
            'technicians': technicians,
            'demo': True
        })

    if request.method == "POST":
        client_id = request.POST.get("client")
        description = request.POST.get("description")
        assigned_to_id = request.POST.get("assigned_to")

        ServiceOrder.objects.create(
            client_id=client_id,
            description=description,
            created_by=request.user,
            assigned_to_id=assigned_to_id if assigned_to_id else None
        )
        return redirect('dashboard')

    clients = Client.objects.all()
    technicians = User.objects.filter(role='technician')
    return render(request, 'orders/create_service_order.html', {
        'clients': clients,
        'technicians': technicians
    })


def portfolio(request):
    return render(request, 'portfolio/portfolio.html')


@login_required
def generate_order_pdf(request, pk):
    order = get_object_or_404(ServiceOrder, pk=pk)

    html = render_to_string("orders/pdf_order.html", {"order": order})
    temp = tempfile.NamedTemporaryFile(delete=True, suffix=".pdf")

    HTML(string=html, base_url=settings.BASE_DIR).write_pdf(temp.name)

    return FileResponse(open(temp.name, 'rb'), content_type='application/pdf', filename=f"order_{order.id}.pdf")


@login_required
def reports(request):
    status = request.GET.get("status")
    technician_id = request.GET.get("technician")

    orders = ServiceOrder.objects.all()

    if status:
        orders = orders.filter(status=status)
    if technician_id:
        orders = orders.filter(assigned_to_id=technician_id)

    total_orders = orders.count()
    completed_this_month = orders.filter(
        status='finished',
        updated_at__month=now().month,
        updated_at__year=now().year
    ).count()

    context = {
        "orders": orders.order_by("-created_at"),
        "total_orders": total_orders,
        "completed_this_month": completed_this_month,
    }
    return render(request, "reports/reports.html", context)


def see_clients(request):
    clients = Client.objects.all()
    image_map = {
        1: "clients/image1.jpeg",
        2: "clients/image2.jpeg",
        3: "clients/image3.jpeg",
        4: "clients/image4.jpeg",
        5: "clients/image5.jpeg",
        6: "clients/image6.jpeg",
        7: "clients/image7.jpeg",
    }

    for client in clients:
        client.display_photo = image_map.get(client.id, "clients/default.jpg")

    return render(request, "clients/see_clients.html", {"clients": clients})


def client_orders(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    orders = ServiceOrder.objects.filter(client=client)

    return render(request, "clients/client_orders.html", {
        "client": client,
        "orders": orders
    })

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def my_profile(request):
    return render(request, "profile/my_profile.html", {
        "user": request.user
    })

