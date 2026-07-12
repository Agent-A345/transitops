from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse
from trips.models import Trip
from vehicles.models import Vehicle
from drivers.models import Driver
from accounts.decorators import login_required_custom, role_required
import csv


@login_required_custom
def trip_list(request):
    status_filter = request.GET.get('status', '')
    search = request.GET.get('search', '')
    trips = Trip.objects.select_related('vehicle', 'driver').order_by('-created_at')
    if status_filter:
        trips = trips.filter(status=status_filter)
    if search:
        trips = trips.filter(source__icontains=search) | \
                Trip.objects.select_related('vehicle', 'driver').filter(destination__icontains=search)

    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="trips.csv"'
        writer = csv.writer(response)
        writer.writerow(['ID', 'Source', 'Destination', 'Vehicle', 'Driver', 'Cargo (kg)', 'Distance (km)', 'Revenue', 'Status', 'Date'])
        for t in trips:
            writer.writerow([t.id, t.source, t.destination, t.vehicle.registration_number, t.driver.name, t.cargo_weight, t.planned_distance, t.revenue, t.status, t.created_at.date()])
        return response

    return render(request, 'trips/list.html', {'trips': trips, 'status_filter': status_filter, 'search': search})


@login_required_custom
@role_required('fleet_manager', 'dispatcher')
def trip_add(request):
    available_vehicles = Vehicle.objects.filter(status='available')
    available_drivers = Driver.objects.filter(status='available')
    if request.method == 'POST':
        vehicle_id = request.POST.get('vehicle')
        driver_id = request.POST.get('driver')
        cargo_weight = float(request.POST.get('cargo_weight', 0))
        vehicle = get_object_or_404(Vehicle, pk=vehicle_id)
        driver = get_object_or_404(Driver, pk=driver_id)
        errors = []
        if vehicle.status != 'available':
            errors.append(f'Vehicle {vehicle.registration_number} is not available ({vehicle.status})')
        if driver.status != 'available':
            errors.append(f'Driver {driver.name} is not available ({driver.status})')
        if not driver.is_license_valid():
            errors.append(f'Driver {driver.name} has an expired license!')
        if driver.status == 'suspended':
            errors.append(f'Driver {driver.name} is suspended!')
        if cargo_weight > vehicle.max_load_capacity:
            errors.append(f'Cargo {cargo_weight}kg exceeds vehicle capacity {vehicle.max_load_capacity}kg!')
        if errors:
            for e in errors:
                messages.error(request, e)
            return render(request, 'trips/form.html', {
                'available_vehicles': available_vehicles,
                'available_drivers': available_drivers,
                'post': request.POST,
            })
        Trip.objects.create(
            source=request.POST.get('source'),
            destination=request.POST.get('destination'),
            vehicle=vehicle, driver=driver,
            cargo_weight=cargo_weight,
            planned_distance=request.POST.get('planned_distance'),
            revenue=request.POST.get('revenue', 0),
            notes=request.POST.get('notes', ''),
            status='draft',
        )
        messages.success(request, 'Trip created!')
        return redirect('trip_list')
    return render(request, 'trips/form.html', {
        'available_vehicles': available_vehicles,
        'available_drivers': available_drivers,
    })


@login_required_custom
def trip_detail(request, pk):
    trip = get_object_or_404(Trip, pk=pk)
    return render(request, 'trips/detail.html', {'trip': trip})


@login_required_custom
@role_required('fleet_manager', 'dispatcher')
def trip_dispatch(request, pk):
    trip = get_object_or_404(Trip, pk=pk)
    if trip.status != 'draft':
        messages.error(request, 'Only draft trips can be dispatched!')
        return redirect('trip_detail', pk=pk)
    trip.vehicle.status = 'on_trip'
    trip.vehicle.save()
    trip.driver.status = 'on_trip'
    trip.driver.save()
    trip.status = 'dispatched'
    trip.dispatched_at = timezone.now()
    trip.save()
    messages.success(request, f'Trip dispatched! {trip.vehicle.registration_number} & {trip.driver.name} are On Trip.')
    return redirect('trip_detail', pk=pk)


@login_required_custom
@role_required('fleet_manager', 'dispatcher')
def trip_complete(request, pk):
    trip = get_object_or_404(Trip, pk=pk)
    if trip.status != 'dispatched':
        messages.error(request, 'Only dispatched trips can be completed!')
        return redirect('trip_detail', pk=pk)
    if request.method == 'POST':
        trip.final_odometer = request.POST.get('final_odometer')
        trip.fuel_consumed = request.POST.get('fuel_consumed')
        trip.status = 'completed'
        trip.completed_at = timezone.now()
        trip.save()
        if trip.final_odometer:
            trip.vehicle.odometer = float(trip.final_odometer)
        trip.vehicle.status = 'available'
        trip.vehicle.save()
        trip.driver.status = 'available'
        trip.driver.save()
        messages.success(request, 'Trip completed! Vehicle and driver are now available.')
        return redirect('trip_detail', pk=pk)
    return render(request, 'trips/complete_form.html', {'trip': trip})


@login_required_custom
@role_required('fleet_manager', 'dispatcher')
def trip_cancel(request, pk):
    trip = get_object_or_404(Trip, pk=pk)
    if trip.status not in ['draft', 'dispatched']:
        messages.error(request, 'Cannot cancel this trip.')
        return redirect('trip_detail', pk=pk)
    if request.method == 'POST':
        if trip.status == 'dispatched':
            trip.vehicle.status = 'available'
            trip.vehicle.save()
            trip.driver.status = 'available'
            trip.driver.save()
        trip.status = 'cancelled'
        trip.save()
        messages.success(request, 'Trip cancelled.')
        return redirect('trip_list')
    return render(request, 'trips/confirm_cancel.html', {'trip': trip})
