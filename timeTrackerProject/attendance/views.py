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
    
    # Obtener las fichadas del empleado
    attendances = Attendance.objects.filter(employee_id=employee.id).order_by('check_in')
    
    #Separar los días. Tener en cuenta los días que hay turno de noche, como de 22:00 a 6:00.
    days_of_week = range(7)
    #Guardar el dia de la semana que es hoy
    
    day_of_week = datetime.now().weekday()
    #Guardar el ultimo lunes
    last_monday = datetime.now() - timedelta(days=day_of_week)
    
    #Guardar las Attendance desde el último lunes
    
    attendances = attendances.filter(check_in__gte=last_monday)
    for day in days_of_week:
        attendances_day = attendances.filter(check_in__week_day=day)
        if attendances_day is not None:
            check_in = attendances_day.first().check_in
            check_out = attendances_day.last().check_out
        
            left_value = calculate_percentage(check_in)
            width_value = calculate_percentage(check_out)
        
        
        
        days_of_week[day] = {
            'left' : check_in_percentage,
            'width' : checkout_percentage - check_in_percentage
        }
    #Para cada día, almacenar los rangos en una lista. Un día será una lista de rangos
    
    
    
    context = {
        'days_of_week' : range(7)
    }
    
    return render(request, 'days.html', context)

def calculate_percentage(datetime_obj):
    total_minutes = 24 * 60
    minutes_since_midnight = datetime_obj.hour * 60 + datetime_obj.minute
    return (minutes_since_midnight / total_minutes) * 100


def logout(request):
    auth_logout(request)
    return redirect('index')
