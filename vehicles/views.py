from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from vehicles.models import Vehicle, VehicleDocument
from drivers.models import Driver
from trips.models import Trip
from accounts.decorators import login_required_custom, role_required
import csv
from datetime import date, timedelta


@login_required_custom
def dashboard(request):
    total_vehicles = Vehicle.objects.count()
    available_vehicles = Vehicle.objects.filter(status='available').count()
    in_maintenance = Vehicle.objects.filter(status='in_shop').count()
    on_trip_vehicles = Vehicle.objects.filter(status='on_trip').count()
    active_trips = Trip.objects.filter(status='dispatched').count()
    pending_trips = Trip.objects.filter(status='draft').count()
    completed_trips = Trip.objects.filter(status='completed').count()
    drivers_on_duty = Driver.objects.filter(status='on_trip').count()
    available_drivers = Driver.objects.filter(status='available').count()
    total_drivers = Driver.objects.count()
    fleet_utilization = round((on_trip_vehicles / total_vehicles * 100) if total_vehicles > 0 else 0)
    recent_trips = Trip.objects.select_related('vehicle', 'driver').order_by('-created_at')[:8]
    expiring_soon = Driver.objects.filter(
        license_expiry__lte=date.today() + timedelta(days=30),
        license_expiry__gte=date.today()
    )
    expired = Driver.objects.filter(license_expiry__lt=date.today())

    # Expiring documents alert
    expiring_docs = VehicleDocument.objects.filter(
        expiry_date__lte=date.today() + timedelta(days=30),
        expiry_date__gte=date.today()
    ).select_related('vehicle')
    expired_docs = VehicleDocument.objects.filter(
        expiry_date__lt=date.today()
    ).select_related('vehicle')

    return render(request, 'dashboard.html', {
        'total_vehicles': total_vehicles,
        'available_vehicles': available_vehicles,
        'in_maintenance': in_maintenance,
        'active_trips': active_trips,
        'pending_trips': pending_trips,
        'completed_trips': completed_trips,
        'drivers_on_duty': drivers_on_duty,
        'available_drivers': available_drivers,
        'total_drivers': total_drivers,
        'fleet_utilization': fleet_utilization,
        'recent_trips': recent_trips,
        'expiring_soon': expiring_soon,
        'expired': expired,
        'expiring_docs': expiring_docs,
        'expired_docs': expired_docs,
    })


@login_required_custom
def vehicle_list(request):
    status_filter = request.GET.get('status', '')
    type_filter = request.GET.get('type', '')
    search = request.GET.get('search', '')
    sort = request.GET.get('sort', '-created_at')

    vehicles = Vehicle.objects.all()
    if status_filter:
        vehicles = vehicles.filter(status=status_filter)
    if type_filter:
        vehicles = vehicles.filter(type=type_filter)
    if search:
        vehicles = vehicles.filter(registration_number__icontains=search) | \
                   Vehicle.objects.filter(name__icontains=search)
    vehicles = vehicles.order_by(sort)

    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="vehicles.csv"'
        writer = csv.writer(response)
        writer.writerow(['Reg Number', 'Name', 'Type', 'Capacity (kg)', 'Odometer (km)', 'Acquisition Cost', 'Status'])
        for v in vehicles:
            writer.writerow([v.registration_number, v.name, v.type, v.max_load_capacity, v.odometer, v.acquisition_cost, v.status])
        return response

    status_counts = {
        'available': Vehicle.objects.filter(status='available').count(),
        'on_trip': Vehicle.objects.filter(status='on_trip').count(),
        'in_shop': Vehicle.objects.filter(status='in_shop').count(),
        'retired': Vehicle.objects.filter(status='retired').count(),
    }
    return render(request, 'vehicles/list.html', {
        'vehicles': vehicles,
        'status_filter': status_filter,
        'type_filter': type_filter,
        'search': search,
        'sort': sort,
        'status_counts': status_counts,
    })


@login_required_custom
@role_required('fleet_manager')
def vehicle_add(request):
    if request.method == 'POST':
        reg = request.POST.get('registration_number')
        if Vehicle.objects.filter(registration_number=reg).exists():
            messages.error(request, f'Vehicle {reg} already exists!')
            return render(request, 'vehicles/form.html', {'action': 'Add', 'post': request.POST})
        Vehicle.objects.create(
            registration_number=reg,
            name=request.POST.get('name'),
            type=request.POST.get('type'),
            max_load_capacity=request.POST.get('max_load_capacity'),
            odometer=request.POST.get('odometer', 0),
            acquisition_cost=request.POST.get('acquisition_cost'),
            status='available',
        )
        messages.success(request, 'Vehicle registered successfully!')
        return redirect('vehicle_list')
    return render(request, 'vehicles/form.html', {'action': 'Add'})


@login_required_custom
def vehicle_detail(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    trips = Trip.objects.filter(vehicle=vehicle).order_by('-created_at')
    maintenance = vehicle.maintenancelog_set.all().order_by('-created_at')
    fuel_logs = vehicle.fuellog_set.all().order_by('-date')
    documents = vehicle.documents.all().order_by('-uploaded_at')
    return render(request, 'vehicles/detail.html', {
        'vehicle': vehicle, 'trips': trips,
        'maintenance': maintenance, 'fuel_logs': fuel_logs,
        'documents': documents,
    })


@login_required_custom
@role_required('fleet_manager')
def vehicle_edit(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    if request.method == 'POST':
        vehicle.name = request.POST.get('name')
        vehicle.type = request.POST.get('type')
        vehicle.max_load_capacity = request.POST.get('max_load_capacity')
        vehicle.odometer = request.POST.get('odometer', 0)
        vehicle.acquisition_cost = request.POST.get('acquisition_cost')
        vehicle.status = request.POST.get('status')
        vehicle.save()
        messages.success(request, 'Vehicle updated!')
        return redirect('vehicle_list')
    return render(request, 'vehicles/form.html', {'action': 'Edit', 'vehicle': vehicle})


@login_required_custom
@role_required('fleet_manager')
def vehicle_delete(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    if request.method == 'POST':
        vehicle.delete()
        messages.success(request, 'Vehicle deleted.')
        return redirect('vehicle_list')
    return render(request, 'vehicles/confirm_delete.html', {'vehicle': vehicle})


# ── Document views ──────────────────────────────────────────

@login_required_custom
@role_required('fleet_manager')
def document_upload(request, vehicle_pk):
    vehicle = get_object_or_404(Vehicle, pk=vehicle_pk)
    if request.method == 'POST':
        doc_type = request.POST.get('doc_type')
        title = request.POST.get('title')
        expiry_date = request.POST.get('expiry_date') or None
        file = request.FILES.get('file')
        if not file:
            messages.error(request, 'Please select a file to upload.')
            return redirect('vehicle_detail', pk=vehicle_pk)
        VehicleDocument.objects.create(
            vehicle=vehicle,
            doc_type=doc_type,
            title=title,
            file=file,
            expiry_date=expiry_date,
        )
        messages.success(request, f'Document "{title}" uploaded successfully!')
        return redirect('vehicle_detail', pk=vehicle_pk)
    return render(request, 'vehicles/document_upload.html', {'vehicle': vehicle})


@login_required_custom
@role_required('fleet_manager')
def document_delete(request, pk):
    doc = get_object_or_404(VehicleDocument, pk=pk)
    vehicle_pk = doc.vehicle.pk
    if request.method == 'POST':
        doc.file.delete(save=False)
        doc.delete()
        messages.success(request, 'Document deleted.')
    return redirect('vehicle_detail', pk=vehicle_pk)
