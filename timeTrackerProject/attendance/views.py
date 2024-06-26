from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Employee, Attendance
# Create your views here.

def index(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'index.html')


@login_required
def home(request):
    if not request.user.is_authenticated:
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                auth_login(request, user)
                
                return render(request, 'home.html')
            else:
                return redirect('home')
        return render(request, 'login.html')
    else:
        user = request.user
        
        employee = Employee.objects.get(user_id=user.id)  # Obtener 

        
        if request.method == 'POST':
            if 'entrar_trabajo' in request.POST:
                if not employee.is_working:
                    employee.is_working = True
                    employee.save()
                    # Crear una nueva sesión de trabajo
                    Attendance.objects.create(employee=employee, check_in=timezone.now())
                    messages.success(request, 'Has entrado a trabajar.')
                else:
                    messages.warning(request, 'Ya estás trabajando actualmente.')

            elif 'salir_trabajo' in request.POST:
                if employee.is_working:
                    employee.is_working = False
                    employee.save()
                    # Completar la sesión de trabajo actual
                    work_session = Attendance.objects.filter(employee=employee, check_out__isnull=True).latest('check_in')
                    work_session.check_out = timezone.now()
                    work_session.save()
                    messages.success(request, 'Has salido de trabajar.')
                else:
                    messages.warning(request, 'No estás trabajando actualmente.')

            return redirect('home')   
        
        context = {
            'firstname': employee.first_name,
            'is_working': employee.is_working,
        }

        return render(request, 'home.html', context)

@login_required
def ver_horas_trabajadas(request):
    user = request.user
    employee = Employee.objects.get(user_id=user.id)
    
    # Obtener la semana a mostrar desde los parámetros GET
    week_offset = int(request.GET.get('week', 0))
    
    # Guardar el día de la semana que es hoy
    day_of_week = timezone.now().weekday()
    
    # Calcular el último lunes con el offset
    last_monday = timezone.now() - timedelta(days=day_of_week + 7 * week_offset)
    
    # Calcular el final de la semana
    week_start = last_monday
    week_end = last_monday + timedelta(days=6)
    
    # Formatear las fechas para mostrarlas
    week_start_str = week_start.strftime("%d/%m/%Y")
    week_end_str = week_end.strftime("%d/%m/%Y")
    
    # Obtener las fichadas del empleado desde el último lunes
    attendances = Attendance.objects.filter(employee_id=employee.id, check_in__gte=week_start, check_in__lt=week_end + timedelta(days=1)).order_by('check_in')
    
    days_of_week = [{"day": i, "ranges": []} for i in range(7)]
    
    for day in days_of_week:
        day_index = (day["day"] + 1) % 7 + 1  # Convertir de 0-6 (lunes-domingo) a 1-7 (domingo-sábado)
        attendances_day = attendances.filter(check_in__week_day=day_index)
        for attendance in attendances_day:
            check_in = timezone.localtime(attendance.check_in)
            check_out = timezone.localtime(attendance.check_out)
            
            if check_out is None:
                check_out = timezone.now()
            
            left_value = calculate_percentage(check_in)
            width_value = calculate_percentage(check_out)
            range_entry = {
                'check_in': left_value,
                'check_out': width_value - left_value
            }
            day["ranges"].append(range_entry)
    
    context = {
        'days_of_week': days_of_week,
        'week_offset': week_offset,
        'week_start': week_start_str,
        'week_end': week_end_str,
    }
    
    return render(request, 'days.html', context)

def calculate_percentage(datetime_obj):
    total_minutes = 24 * 60
    minutes_since_midnight = datetime_obj.hour * 60 + datetime_obj.minute
    return (minutes_since_midnight / total_minutes) * 100


def logout(request):
    auth_logout(request)
    return redirect('index')
