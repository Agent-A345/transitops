from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from fuel.models import FuelLog, Expense
from vehicles.models import Vehicle
from accounts.decorators import login_required_custom, role_required
import csv


@login_required_custom
def fuel_list(request):
    vehicle_filter = request.GET.get('vehicle', '')
    fuel_logs = FuelLog.objects.select_related('vehicle').order_by('-date')
    expenses = Expense.objects.select_related('vehicle').order_by('-date')
    vehicles = Vehicle.objects.all()

    if vehicle_filter:
        fuel_logs = fuel_logs.filter(vehicle_id=vehicle_filter)
        expenses = expenses.filter(vehicle_id=vehicle_filter)

    total_fuel_cost = sum(f.cost for f in fuel_logs)
    total_expense = sum(e.amount for e in expenses)
    total_operational = total_fuel_cost + total_expense

    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="fuel_expenses.csv"'
        writer = csv.writer(response)
        writer.writerow(['Type', 'Vehicle', 'Amount', 'Date', 'Notes'])
        for f in fuel_logs:
            writer.writerow(['Fuel', f.vehicle.registration_number, f.cost, f.date, f'{f.liters}L'])
        for e in expenses:
            writer.writerow([e.type, e.vehicle.registration_number, e.amount, e.date, e.note])
        return response

    return render(request, 'fuel/list.html', {
        'fuel_logs': fuel_logs, 'expenses': expenses,
        'vehicles': vehicles, 'vehicle_filter': vehicle_filter,
        'total_fuel_cost': total_fuel_cost,
        'total_expense': total_expense,
        'total_operational': total_operational,
    })


@login_required_custom
@role_required('fleet_manager', 'financial_analyst')
def fuel_add(request):
    vehicles = Vehicle.objects.all()
    if request.method == 'POST':
        vehicle = get_object_or_404(Vehicle, pk=request.POST.get('vehicle'))
        FuelLog.objects.create(
            vehicle=vehicle,
            liters=request.POST.get('liters'),
            cost=request.POST.get('cost'),
            date=request.POST.get('date'),
            odometer_at_fill=request.POST.get('odometer_at_fill', 0),
            notes=request.POST.get('notes', ''),
        )
        messages.success(request, 'Fuel log added!')
        return redirect('fuel_list')
    return render(request, 'fuel/fuel_form.html', {'vehicles': vehicles})


@login_required_custom
@role_required('fleet_manager', 'financial_analyst')
def fuel_delete(request, pk):
    log = get_object_or_404(FuelLog, pk=pk)
    if request.method == 'POST':
        log.delete()
        messages.success(request, 'Fuel log deleted.')
    return redirect('fuel_list')


@login_required_custom
@role_required('fleet_manager', 'financial_analyst')
def expense_add(request):
    vehicles = Vehicle.objects.all()
    if request.method == 'POST':
        vehicle = get_object_or_404(Vehicle, pk=request.POST.get('vehicle'))
        Expense.objects.create(
            vehicle=vehicle,
            type=request.POST.get('type'),
            amount=request.POST.get('amount'),
            date=request.POST.get('date'),
            note=request.POST.get('note', ''),
        )
        messages.success(request, 'Expense added!')
        return redirect('fuel_list')
    return render(request, 'fuel/expense_form.html', {'vehicles': vehicles})


@login_required_custom
@role_required('fleet_manager', 'financial_analyst')
def expense_delete(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    if request.method == 'POST':
        expense.delete()
        messages.success(request, 'Expense deleted.')
    return redirect('fuel_list')
