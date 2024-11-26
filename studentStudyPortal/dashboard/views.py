from django.shortcuts import render, redirect, HttpResponseRedirect
from django.contrib import messages
from .models import Notes, Homework, Todo
from .forms import NotesForm, HomeworkForm, DashboardForm, TodoForm, UserRegistrationForm
from django.contrib.auth import authenticate, login, logout
from django.views import generic
from youtubesearchpython import VideosSearch
import requests
import wikipedia
from django.contrib.auth.decorators import login_required

# Create your views here.
def home(request):
    if request.user.is_authenticated:
        return render(request,'dashboard/home.html', {'name':request.user})
    else:
        return render(request,'dashboard/home.html')

@login_required
def notes(request):
    if request.method == 'POST':
        form = NotesForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            description = form.cleaned_data['description']

            notes = Notes(user=request.user, title=title, description=description)
            # notes = Notes(user=request.user, title=request.POST['title'], description=request.POST['description'])
            # notes = Notes(user=request.user, title=form.cleaned_data['title'], description=form.cleaned_data['description'])

            notes.save()

        form = NotesForm()
        messages.success(request,f"Notes Added from {request.user.username} Successfully !")

    else:
        form = NotesForm()
    notes = Notes.objects.filter(user = request.user)
    context = {'notes':notes, 'form':form}
    return render(request,'dashboard/notes.html', context)

@login_required
def delete_note(request, pk=None):
    Notes.objects.get(id=pk).delete()
    return redirect("notes")

class NotesDetailView(generic.DetailView):
    model = Notes

@login_required
def homework(request):
    if request.method == 'POST':
        form = HomeworkForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            title = form.cleaned_data['title']
            description = form.cleaned_data['description']
            due = form.cleaned_data['due']

            try:
                finished = form.cleaned_data['is_finished']
                if finished == 'on':
                    finished = True
                else:
                    finished = False
            except:
                finished = False
        homeworks = Homework(user=request.user, subject=subject, title=title, description=description, due=due, is_finished=finished)
        homeworks.save()
        messages.success(request,f"Homework Added from {request.user.username} Successfully !")
        return redirect('homework')

    else:
        form = HomeworkForm()
    homework = Homework.objects.filter(user = request.user)
    if len(homework) == 0:
        homework_done = True
    else:
        homework_done = False
    context = {'homeworks':homework, 'homeworks_done':homework_done, 'form':form}
    return render(request, 'dashboard/homework.html', context)

@login_required
def update_homework(request, pk=None):
    homework = Homework.objects.get(id=pk)
    if homework.is_finished == True:
        homework.is_finished = False
    else:
        homework.is_finished = True
    homework.save()
    return redirect('homework')

@login_required
def delete_homework(request, pk=None):
   Homework.objects.get(id=pk).delete()
   return redirect('homework')

def youtube(request):
    if request.method == 'POST':
        form = DashboardForm(request.POST)
        # text = form.cleaned_data['text']
        text = request.POST['text']
        video = VideosSearch(text, limit=10)
        result_list = []
        for i in video.result()['result']:
            result_dict = {
                'input':text,
                'title':i['title'],
                'duration':i['duration'],
                'thumbnail':i['thumbnails'][0]['url'],
                'channel':i['channel']['name'],
                'link':i['link'],
                'views':i['viewCount']['short'],
                'published':i['publishedTime'],
            }
            desc = ''
            if i.get('descriptionSnippet'):
                for j in i['descriptionSnippet']:
                    desc += j['text']
            result_dict['description'] = desc
            result_list.append(result_dict)
            context = {'form':form, 'results':result_list}
        
        return render(request, 'dashboard/youtube.html', context)

    else:
        form = DashboardForm()
    context = {'form':form}
    return render(request, 'dashboard/youtube.html', context)

@login_required
def todo(request):
    if request.method == 'POST':
        form = TodoForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']

            try:
                finished = request.POST['is_finished']
                if finished == 'on':
                    finished = True
                else:
                    finished = False
            except:
                finished = False
        todos = Todo(user=request.user, title=title, is_finished=finished)
        todos.save()
        messages.success(request,f"Todo Added from {request.user.username} Successfully !")
        return redirect('todo')
    else:
        form = TodoForm()
    todo = Todo.objects.filter(user=request.user)
    if len(todo) == 0:
        todos_done = True
    else:
        todos_done = False
    context = {'todos':todo, 'form':form, 'todos_done':todos_done}
    return render(request, 'dashboard/todo.html', context)

@login_required
def update_todo(request, pk=None):
    todo = Todo.objects.get(id=pk)
    if todo.is_finished == True:
        todo.is_finished = False
    else:
        todo.is_finished = True
    todo.save()
    return redirect('todo')

@login_required
def delete_todo(request, pk=None):
   Todo.objects.get(id=pk).delete()
   return redirect('todo')

def books(request):
    if request.method == 'POST':
        form = DashboardForm(request.POST)
        # text = form.cleaned_data['text']
        text = request.POST['text']
        url = "https://www.googleapis.com/books/v1/volumes?q="+text
        r = requests.get(url)
        answer = r.json()
        result_list = []


        if 'items' in answer:
            for i in range(min(10, len(answer['items']))):  # Limit to available items
                volume_info = answer['items'][i]['volumeInfo']

                result_dict = {
                    'title': volume_info.get('title', 'No Title Available'),
                    'subtitle': volume_info.get('subtitle', 'No Subtitle'),
                    'description': volume_info.get('description', 'No Description Available'),
                    'count': volume_info.get('pageCount', 'N/A'),
                    'categories': volume_info.get('categories', ['Uncategorized']),
                    'rating': volume_info.get('averageRating', 'No Rating'),
                    'thumbnail': volume_info.get('imageLinks', {}).get('thumbnail', ''),
                    'preview': volume_info.get('previewLink', '#'),
                }
                result_list.append(result_dict)

        # for i in range(10):
        #     result_dict = {
        #         'title':answer['items'][i]['volumeInfo']['title'],
        #         'subtitle':answer['items'][i]['volumeInfo'].get('subtitle'),
        #         'description':answer['items'][i]['volumeInfo'].get('description'),
        #         'count':answer['items'][i]['volumeInfo'].get('paeCount'),
        #         'categories':answer['items'][i]['volumeInfo'].get('categories'),
        #         'rating':answer['items'][i]['volumeInfo'].get('pageRating'),
        #         'thumbnail':answer['items'][i]['volumeInfo'].get('imageLinks').get('thumbnail'),
        #         'preview':answer['items'][i]['volumeInfo'].get('previewLink'),      
        #     }
        #     result_list.append(result_dict)

        context = {'form':form, 'results':result_list}
        return render(request, 'dashboard/books.html', context)
    else:
        form = DashboardForm()
    context = {'form':form}
    return render(request, 'dashboard/books.html', context)

def dictionary(request):
    if request.method == 'POST':
        form = DashboardForm(request.POST)
        # text = form.cleaned_data['text']
        text = request.POST['text']
        url = "https://api.dictionaryapi.dev/api/v2/entries/en_US/"+text
        r = requests.get(url)
        answer = r.json()
        try:
            phonetics = answer[0]['phonetics'][0].get('text', 'No phonetics available')
            audio = answer[0]['phonetics'][0].get('audio', '')
            definition = answer[0]['meanings'][0]['definitions'][0].get('definition', 'No definition available')
            example = answer[0]['meanings'][0]['definitions'][0].get('example', 'No example available')
            # synonyms = answer[0]['meanings'][0]['definitions'][0].get('synonyms', [])
            synonyms_list = answer[0]['meanings'][0]['definitions'][0].get('synonyms', [])
            synonyms = ', '.join(synonyms_list) if synonyms_list else 'No synonyms available'


            # phonetics = answer[0]['phonetics'][0]['text']
            # audio = answer[0]['phonetics'][0]['audio']
            # definition = answer[0]['meanings'][0]['definitions'][0]['definition']
            # example = answer[0]['meanings'][0]['definitions'][0]['example']
            # synonyms = answer[0]['meanings'][0]['definitions'][0]['synonyms']
            context = {'form':form, 'input':text, 'phonetics':phonetics, 'audio':audio, 'definition':definition, 'example':example, 'synonyms':synonyms}
        except:
            context = {'form':form, 'input':text, 'error':'No data found for the entered word.'}
        return render(request, 'dashboard/dictionary.html', context)
        
    else:
        form = DashboardForm()
    context = {'form':form}
    return render(request, 'dashboard/dictionary.html', context)


def wiki(request):
    if request.method == 'POST':
        text = request.POST['text']
        form = DashboardForm(request.POST)
        search = wikipedia.page(text)
        context = {'form':form, 'title':search.title, 'link':search.url, 'details':search.summary}
        return render(request, 'dashboard/wiki.html', context)
    else:
        form = DashboardForm()
    context = {'form':form}
    return render(request, 'dashboard/wiki.html', context)


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            messages.success(request,f"Congratulations!! {username}, you are Successfully Created on your Account") 
            return redirect('login')

    else:
        form = UserRegistrationForm()
    context = {'form':form}
    return render(request, 'dashboard/register.html', context)

@login_required
def profile(request):
    homeworks = Homework.objects.filter(is_finished=False, user=request.user)
    todos = Todo.objects.filter(is_finished=False, user=request.user)

    if len(homeworks) == 0:
        homework_done = True
    else:
        homework_done = False

    if len(todos) == 0:
        todos_done = True
    else:
        todos_done = False

    context = {
        'homeworks':homeworks,
        'todos':todos,
        'homework_done':homework_done,
        'todos_done':todos_done
    }

    return render(request, 'dashboard/profile.html', context)


def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/')