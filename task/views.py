from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from .models import Task
from .forms import TaskForm
from django.utils import timezone
from django.contrib.auth.decorators import login_required
# SuperUser cuenta: matiasz password: 21204650

# Create your views here.
def home(request):
    return render(request, 'home.html')

     # Esta funcion nos sirve para poder registarnos a la pagina con la ayuda de django con un username y una password
def signup(request):
    
    if request.method == 'GET':
        return render(request, 'signup.html',{'form': UserCreationForm})
    else:
        if request.POST['password1'] == request.POST['password2']:
            # Register user 
            try:
                user = User.objects.create_user(username=request.POST['username'], password=request.POST['password1'])
                user.save
                login(request, user)
                return redirect(tasks)# este lo manda al nombre de la urls en nuestro caso tasks
            except IntegrityError:
                return render(request, 'signup.html',{'form': UserCreationForm, 'error': 'Username alredy exist'})
        return render(request, 'signup.html',{'form': UserCreationForm, 'error':'password do not match'})

     # Esta funcion nos sirve para mostrar las tareas de un usuario registrado en el sistema     
@login_required
def tasks(request):
    tasks = Task.objects.filter(user=request.user, datecompleted__isnull = True)
    # Esta funcion sirve para que filtre por usuario las tarea si se usa Task.objects.all() te muestra todas las tareas como un ADMIN 
    return render(request, 'tasks.html', {'tasks': tasks, 'title':'Task Pending'})

     # Esta funcion nos sirve para cerrar sesion 
@login_required
def signout(request):
    logout(request)
    return redirect('home')

     # Esta funcion nos sirve para logearnos en la pagina 
def signin(request):
    if request.method == 'GET':
        return render(request,'signin.html',{
        'form' : AuthenticationForm
        })
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        
        if user is None:
            return render(request,'signin.html',{'form' : AuthenticationForm, 'error':'Username or password is incorrect'})
        
        else:
            login(request, user) 
            return redirect('tasks') 

     # Esta funcion nos sirve para crear tasks   
@login_required         
def create_task(request):

    if request.method == 'GET':
         return render(request, 'create_task.html',{
        'form': TaskForm
        })
    else:
        try:
            form = TaskForm(request.POST)
            new_task = form.save(commit=False)
            new_task.user = request.user
            new_task.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'create_task.html',{
            'form': TaskForm, 'error':'Please provide valida data'
            })

      # Esta funcion nos sirve para editar las tasks    
@login_required   
def task_detealt(request, task_id):
    if request.method == 'GET':      
        task = get_object_or_404(Task, pk = task_id, user = request.user)
        form = TaskForm(instance=task)
        return render(request, 'task_detail.html',{'task': task, 'form': form})
    else:
        try:
             # Obtengo la tarea (Task) y le digo que solo el usuario podra modificar sus tareas con el codigo 'user = request.user'
            task = get_object_or_404(Task, pk = task_id, user = request.user )
            # Con este actualizo la tarea con la id que encontre en task y luego cambio los datos en la base de datos 
            form = TaskForm(request.POST, instance=task) 
            # Y con este guardo los cambios 
            form.save()
            return redirect('tasks')

        except ValueError:
            return render(request, 'task_detail.html',{'task': task, 'form': form, 'error':'Error updating task'})
   
     # Esta funcion sirve para completar una tarea de un usuario x
@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.datecompleted = timezone.now()
        task.save()
        return redirect('tasks')
        
     # Esta funcion elimina una tarea de un usuario x
@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('tasks')
        
     # Esta funcion nos sirve para mostrar las tareas de un usuario registrado en el sistema // Solo las tareas que esten completas y las muestra con la
     # ordenada de forma decendente 
@login_required   
def tasks_completed(request):
    tasks = Task.objects.filter(user=request.user, datecompleted__isnull = False).order_by('-datecompleted')
    # Esta funcion sirve para que filtre por usuario las tarea si se usa Task.objects.all() te muestra todas las tareas como un ADMIN 
    return render(request, 'tasks.html', {'tasks': tasks, 'title':'Task Completadas'})

 
