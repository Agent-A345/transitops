from django.shortcuts import render
from django.http import HttpResponse
from vehicles.models import Vehicle
from drivers.models import Driver
from trips.models import Trip
from fuel.models import FuelLog, Expense
from maintenance.models import MaintenanceLog
from accounts.decorators import login_required_custom
import json
import csv


@login_required_custom
def analytics(request):
    vehicles = Vehicle.objects.all()
    trips = Trip.objects.all()
    completed_trips = trips.filter(status='completed')

    fleet_status = {
        'available': vehicles.filter(status='available').count(),
        'on_trip': vehicles.filter(status='on_trip').count(),
        'in_shop': vehicles.filter(status='in_shop').count(),
        'retired': vehicles.filter(status='retired').count(),
    }
    trip_status = {
        'draft': trips.filter(status='draft').count(),
        'dispatched': trips.filter(status='dispatched').count(),
        'completed': trips.filter(status='completed').count(),
        'cancelled': trips.filter(status='cancelled').count(),
    }

    fuel_data = []
    for v in vehicles:
        v_trips = Trip.objects.filter(vehicle=v, status='completed').exclude(fuel_consumed=None).exclude(fuel_consumed=0)
        if v_trips.exists():
            total_dist = sum(t.planned_distance for t in v_trips)
            total_fuel = sum(t.fuel_consumed for t in v_trips)
            efficiency = round(total_dist / total_fuel, 2) if total_fuel > 0 else 0
            fuel_data.append({'label': v.registration_number, 'value': efficiency})

    cost_data = []
    for v in vehicles:
        cost = v.total_operational_cost()
        if cost > 0:
            cost_data.append({'label': v.registration_number, 'value': round(cost, 2)})

    driver_trips = []
    for d in Driver.objects.all():
        count = Trip.objects.filter(driver=d, status='completed').count()
        if count > 0:
            driver_trips.append({'label': d.name, 'value': count, 'score': d.safety_score})
    driver_trips.sort(key=lambda x: x['value'], reverse=True)

    total_revenue = sum(t.revenue for t in completed_trips if t.revenue)
    total_fuel_cost = sum(f.cost for f in FuelLog.objects.all())
    total_maint_cost = sum(m.cost for m in MaintenanceLog.objects.filter(status='resolved'))
    total_expense = sum(e.amount for e in Expense.objects.all())
    total_cost = total_fuel_cost + total_maint_cost + total_expense
    profit = total_revenue - total_cost

    total_v = vehicles.count()
    on_trip_v = vehicles.filter(status='on_trip').count()
    utilization = round((on_trip_v / total_v * 100) if total_v > 0 else 0)

    eff_trips = completed_trips.exclude(fuel_consumed=None).exclude(fuel_consumed=0)
    avg_efficiency = 0
    if eff_trips.exists():
        total_d = sum(t.planned_distance for t in eff_trips)
        total_f = sum(t.fuel_consumed for t in eff_trips)
        avg_efficiency = round(total_d / total_f, 2) if total_f > 0 else 0

    # ROI per vehicle
    roi_data = []
    for v in vehicles:
        roi = v.roi()
        roi_data.append({'label': v.registration_number, 'value': roi})

    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="analytics_report.csv"'
        writer = csv.writer(response)
        writer.writerow(['Metric', 'Value'])
        writer.writerow(['Fleet Utilization (%)', utilization])
        writer.writerow(['Avg Fuel Efficiency (km/L)', avg_efficiency])
        writer.writerow(['Total Revenue (₹)', total_revenue])
        writer.writerow(['Total Cost (₹)', total_cost])
        writer.writerow(['Net Profit (₹)', profit])
        writer.writerow(['Completed Trips', completed_trips.count()])
        writer.writerow([])
        writer.writerow(['Vehicle', 'ROI (%)', 'Operational Cost (₹)', 'Revenue (₹)'])
        for v in vehicles:
            writer.writerow([v.registration_number, v.roi(), v.total_operational_cost(), v.total_revenue()])
        return response

    return render(request, 'analytics/index.html', {
        'fleet_status': json.dumps(fleet_status),
        'trip_status': json.dumps(trip_status),
        'fuel_data': json.dumps(fuel_data),
        'cost_data': json.dumps(cost_data),
        'driver_trips': json.dumps(driver_trips[:8]),
        'roi_data': json.dumps(roi_data),
        'total_revenue': total_revenue,
        'total_cost': total_cost,
        'profit': profit,
        'utilization': utilization,
        'avg_efficiency': avg_efficiency,
        'completed_trips_count': completed_trips.count(),
        'total_fuel_cost': total_fuel_cost,
        'total_maint_cost': total_maint_cost,
    })
