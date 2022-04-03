import os 
appname = input('app name : ') 
print('creating app ...') 
os.system(f'python manage.py startapp {appname}') 
print('success') 
os.system(f"cd C:/Users/alkan/Desktop/django_create/HTMLprefabs/{appname} & mkdir templates")
with open(f'C:/Users/alkan/Desktop/django_create/HTMLprefabs/{appname}/templates/index.html', 'w') as f:
    f.write('<h1>index<h1>')
with open(f'C:/Users/alkan/Desktop/django_create/HTMLprefabs/{appname}/views.py', 'w') as f:
  f.write('from django.shortcuts import render\n\n')
  f.write('def index(request):\n')
  f.write("  return render(request, 'index.html')\n")

#ADD INDEX URL

with open(f'C:/Users/alkan/desktop/django_create/HTMLprefabs/HTMLprefabs/urls.py', 'w') as f:
   f.write('from django.contrib import admin\n')
   f.write('from django.urls import path\n')
   f.write(f'from {appname}.views import *\n\n')
   f.write("urlpatterns = [\n")
   f.write("   path('index', index, name='index'),\n]")
