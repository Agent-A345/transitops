from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from maintenance.models import MaintenanceLog
from vehicles.models import Vehicle
from accounts.decorators import login_required_custom, role_required


@login_required_custom
def maintenance_list(request):
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')
    logs = MaintenanceLog.objects.select_related('vehicle').order_by('-created_at')
    if status_filter:
        logs = logs.filter(status=status_filter)
    if priority_filter:
        logs = logs.filter(priority=priority_filter)
    return render(request, 'maintenance/list.html', {
        'logs': logs,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
    })


@login_required_custom
def maintenance_add(request):
    vehicles = Vehicle.objects.exclude(status='retired')
    if request.method == 'POST':
        vehicle = get_object_or_404(Vehicle, pk=request.POST.get('vehicle'))
        MaintenanceLog.objects.create(
            vehicle=vehicle,
            issue=request.POST.get('issue'),
            priority=request.POST.get('priority'),
            cost=request.POST.get('cost', 0),
            technician=request.POST.get('technician', ''),
            status='pending',
        )
        messages.success(request, 'Maintenance request raised!')
        return redirect('maintenance_list')
    return render(request, 'maintenance/form.html', {'vehicles': vehicles})


@login_required_custom
def maintenance_detail(request, pk):
    log = get_object_or_404(MaintenanceLog, pk=pk)
    return render(request, 'maintenance/detail.html', {'log': log})


@login_required_custom
@role_required('fleet_manager')
def maintenance_approve(request, pk):
    log = get_object_or_404(MaintenanceLog, pk=pk)
    if request.method == 'POST':
        log.status = 'in_progress'
        log.save()
        log.vehicle.status = 'in_shop'
        log.vehicle.save()
        messages.success(request, f'Approved! {log.vehicle.registration_number} is now In Shop.')
        return redirect('maintenance_list')
    return redirect('maintenance_detail', pk=pk)


@login_required_custom
@role_required('fleet_manager')
def maintenance_reject(request, pk):
    log = get_object_or_404(MaintenanceLog, pk=pk)
    if request.method == 'POST':
        log.status = 'rejected'
        log.save()
        messages.warning(request, 'Maintenance request rejected.')
        return redirect('maintenance_list')
    return redirect('maintenance_detail', pk=pk)


@login_required_custom
@role_required('fleet_manager')
def maintenance_resolve(request, pk):
    log = get_object_or_404(MaintenanceLog, pk=pk)
    if request.method == 'POST':
        log.status = 'resolved'
        log.cost = request.POST.get('cost', log.cost)
        log.resolved_at = timezone.now()
        log.save()
        log.vehicle.status = 'available'
        log.vehicle.save()
        messages.success(request, f'Resolved! {log.vehicle.registration_number} is now Available.')
        return redirect('maintenance_list')
    return render(request, 'maintenance/resolve_form.html', {'log': log})
