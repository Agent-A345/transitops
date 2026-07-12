from django.shortcuts import render
from vehicles.models import Vehicle
from drivers.models import Driver
from trips.models import Trip

def dashboard(request):
    total_vehicles = Vehicle.objects.count()
    available_vehicles = Vehicle.objects.filter(status='available').count()
    in_maintenance = Vehicle.objects.filter(status='in_shop').count()
    active_trips = Trip.objects.filter(status='dispatched').count()
    pending_trips = Trip.objects.filter(status='draft').count()
    drivers_on_duty = Driver.objects.filter(status='on_trip').count()
    available_drivers = Driver.objects.filter(status='available').count()
    fleet_utilization = round((active_trips / total_vehicles * 100) if total_vehicles > 0 else 0)
    recent_trips = Trip.objects.select_related('vehicle', 'driver').order_by('-created_at')[:5]

    return render(request, 'dashboard.html', {
        'total_vehicles': total_vehicles,
        'available_vehicles': available_vehicles,
        'in_maintenance': in_maintenance,
        'active_trips': active_trips,
        'pending_trips': pending_trips,
        'drivers_on_duty': drivers_on_duty,
        'available_drivers': available_drivers,
        'fleet_utilization': fleet_utilization,
        'recent_trips': recent_trips,
    })

def vehicle_list(request):
    vehicles = Vehicle.objects.all().order_by('-created_at')
    return render(request, 'vehicles/list.html', {'vehicles': vehicles})