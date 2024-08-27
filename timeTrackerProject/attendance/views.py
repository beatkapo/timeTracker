from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta, time
from .models import Employee, Attendance
import calendar
# Create your views here.

def index(request):
    return redirect('login')


@login_required
def home(request):
    if not request.user.is_authenticated:
        print('No autenticado')
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']
            print(request.POST['username'])
            print(request.POST['password'])
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                auth_login(request, user)
                
                return render(request, 'home.html')
            else:
                return redirect('home')
            
        return redirect('login')
    else:
        print('Autenticado')
        user = request.user
        
        employee = Employee.objects.get(user_id=user.id)  # Obtener 

        
        if request.method == 'POST':
            if 'entrar_trabajo' in request.POST:
                if not employee.is_working:
                    employee.is_working = True
                    # Crear una nueva sesión de trabajo
                    Attendance.objects.create(employee=employee, check_in=timezone.localtime(timezone.now()))
                    employee.save()
                    messages.success(request, 'Has entrado a trabajar.')
                else:
                    messages.warning(request, 'Ya estás trabajando actualmente.')

            elif 'salir_trabajo' in request.POST:
                if employee.is_working:
                    employee.is_working = False
                    
                    # Completar la sesión de trabajo actual
                    work_session = Attendance.objects.filter(employee=employee, check_out__isnull=True).latest('check_in')
                    now = timezone.localtime(timezone.now())
                    check_in = timezone.localtime(work_session.check_in)
                    # Si pasa de las 00:00, guardarlo a las 23:59 y crear otro.
                    if now.time() < check_in.time():
                        fin = datetime.combine(check_in.date(), time(23, 59))
                        fin_aware = timezone.make_aware(fin)
                        work_session.check_out = timezone.localtime(fin_aware)
                        
                        inicio = datetime.combine(now.date(), time(0, 0))
                        inicio_aware = timezone.make_aware(inicio)
                        Attendance.objects.create(employee=employee, check_in=timezone.localtime(inicio_aware), check_out=now)
                        
                    else:
                        work_session.check_out = now
                    
                    work_session.save()
                    employee.save()
                    messages.success(request, 'Has salido de trabajar.')
                else:
                    messages.warning(request, 'No estás trabajando actualmente.')

            return redirect('home')
        
        # Obtener el último registro de asistencia para el empleado
        ultima_fichada = Attendance.objects.filter(employee=employee).latest('check_in')

        # Calcular el tiempo transcurrido desde el último check_in
        tiempo_transcurrido = timezone.now() - ultima_fichada.check_in

        # Para mostrar el tiempo transcurrido en días, horas, minutos y segundos
        dias = tiempo_transcurrido.days
        horas, resto = divmod(tiempo_transcurrido.seconds, 3600)
        minutos, segundos = divmod(resto, 60)
        
        context = {
            'firstname': employee.first_name,
            'is_working': employee.is_working,
            
            'dias': dias,
            'horas': horas,
            'minutos': minutos,
            'segundos': segundos,
        }

        return render(request, 'home.html', context)

@login_required
def week(request):
    user = request.user
    employee = Employee.objects.get(user_id=user.id)
    
    # Obtener las fichadas del empleado
    attendances = Attendance.objects.filter(employee_id=employee.id).order_by('check_in')
    
    # Obtener la semana desde el parámetro de la URL, por defecto será la semana actual
    week_offset = int(request.GET.get('week', 0))
    
    # Guardar el día de la semana que es hoy
    today = timezone.localtime(timezone.now())
    
    
    # Calcular el lunes de la semana seleccionada
    start_of_week = today - timedelta(days=today.weekday())  # Lunes de la semana actual
    print(start_of_week)
    current_week_start = start_of_week + timedelta(weeks=week_offset)
    print(current_week_start)
    current_week_start = datetime.combine(current_week_start.date(), time(0, 0))
    current_week_end = current_week_start + timedelta(days=6)
    
    # Obtener las Attendance desde el último lunes
    week_attendances = attendances.filter(check_in__gte=current_week_start, check_in__lt=current_week_start + timedelta(days=7))
    
    print(week_attendances)
    
    # Separar los días
    days_of_week = [{"day": i, "ranges": []} for i in range(7)]
    day_names_es = ['L', 'M', 'X', 'J', 'V', 'S', 'D']
    for day in days_of_week:
        day_index = (day["day"] + 1) % 7 + 1  # Convertir de 0-6 (lunes-domingo) a 1-7 (domingo-sábado)
        day_name = day_names_es[day["day"]]  # Obtener la inicial del nombre del día en español
        day["name"] = day_name
        attendances_day = week_attendances.filter(check_in__week_day=day_index)
        for attendance in attendances_day:
            check_in = timezone.localtime(attendance.check_in)
            check_out = timezone.localtime(attendance.check_out) if attendance.check_out else None
            now = timezone.localtime(timezone.now())
            
            
            
            if check_out is None or check_out.time() < check_in.time() :
                if check_out is None:
                    check_out = now
                    
                else:
                    new_check_in = datetime.combine(now.date(), time(0, 0))
                    new_check_out = check_out
                    check_out = datetime.combine(check_in.date(), time(23, 59))
                    new_left_value = calculate_percentage(new_check_in)
                    new_width_value = calculate_percentage(new_check_out) - new_left_value
                
                    new_range = {
                        'check_in': new_left_value,
                        'check_out': new_width_value
                    }
                
                    if(day["day"] != 6):
                        days_of_week[(day["day"] + 1) % 7]["ranges"].append(new_range)
            
            left_value = calculate_percentage(check_in)
            width_value = calculate_percentage(check_out) - left_value
            range_entry = {
                'check_in': left_value,
                'check_out': width_value
            } 
            day["ranges"].append(range_entry)
    dotted_line_positions = [(i + 0.5) * (100 / 24) for i in range(24)]
    context = {
        'days_of_week': days_of_week,
        'week_offset': week_offset,
        'current_week_start': current_week_start,
        'current_week_end': current_week_end,
        'dotted_line_positions': dotted_line_positions,
    }
    
    return render(request, 'week.html', context)


def calculate_percentage(datetime_obj):
    total_minutes = 24 * 60
    minutes_since_midnight = datetime_obj.hour * 60 + datetime_obj.minute
    return (minutes_since_midnight / total_minutes) * 100

def login(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('login')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html')

def logout(request):
    auth_logout(request)
    return redirect('index')

