from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from drivers.models import Driver
from accounts.decorators import login_required_custom, role_required
from datetime import date
import csv


@login_required_custom
def driver_list(request):
    status_filter = request.GET.get('status', '')
    search = request.GET.get('search', '')
    sort = request.GET.get('sort', '-created_at')
    drivers = Driver.objects.all()
    if status_filter:
        drivers = drivers.filter(status=status_filter)
    if search:
        drivers = drivers.filter(name__icontains=search) | \
                  Driver.objects.filter(license_number__icontains=search)
    drivers = drivers.order_by(sort)

    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="drivers.csv"'
        writer = csv.writer(response)
        writer.writerow(['Name', 'License Number', 'Category', 'Expiry', 'Safety Score', 'Status'])
        for d in drivers:
            writer.writerow([d.name, d.license_number, d.license_category, d.license_expiry, d.safety_score, d.status])
        return response

    return render(request, 'drivers/list.html', {
        'drivers': drivers,
        'status_filter': status_filter,
        'search': search,
        'sort': sort,
        'today': date.today(),
    })


@login_required_custom
@role_required('fleet_manager', 'safety_officer')
def driver_add(request):
    if request.method == 'POST':
        lic = request.POST.get('license_number')
        if Driver.objects.filter(license_number=lic).exists():
            messages.error(request, f'Driver with license {lic} already exists!')
            return render(request, 'drivers/form.html', {'action': 'Add', 'post': request.POST})
        Driver.objects.create(
            name=request.POST.get('name'),
            license_number=lic,
            license_category=request.POST.get('license_category'),
            license_expiry=request.POST.get('license_expiry'),
            contact=request.POST.get('contact'),
            safety_score=request.POST.get('safety_score', 100),
            status='available',
        )
        messages.success(request, 'Driver added successfully!')
        return redirect('driver_list')
    return render(request, 'drivers/form.html', {'action': 'Add'})


@login_required_custom
def driver_detail(request, pk):
    driver = get_object_or_404(Driver, pk=pk)
    trips = driver.trip_set.all().order_by('-created_at')
    return render(request, 'drivers/detail.html', {'driver': driver, 'trips': trips})


@login_required_custom
@role_required('fleet_manager', 'safety_officer')
def driver_edit(request, pk):
    driver = get_object_or_404(Driver, pk=pk)
    if request.method == 'POST':
        driver.name = request.POST.get('name')
        driver.license_category = request.POST.get('license_category')
        driver.license_expiry = request.POST.get('license_expiry')
        driver.contact = request.POST.get('contact')
        driver.safety_score = request.POST.get('safety_score', 100)
        driver.status = request.POST.get('status')
        driver.save()
        messages.success(request, 'Driver updated!')
        return redirect('driver_list')
    return render(request, 'drivers/form.html', {'action': 'Edit', 'driver': driver})


@login_required_custom
@role_required('fleet_manager')
def driver_delete(request, pk):
    driver = get_object_or_404(Driver, pk=pk)
    if request.method == 'POST':
        driver.delete()
        messages.success(request, 'Driver deleted.')
        return redirect('driver_list')
    return render(request, 'drivers/confirm_delete.html', {'driver': driver})
