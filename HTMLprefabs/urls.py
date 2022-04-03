from django.contrib import admin
from django.urls import path
from myapp.views import *
from myapp.database import *

urlpatterns = [
   #templates
   path('', home, name='index'),
   path('index', home, name='index'),
   path('login', login, name='login'),
   path('signin', signin, name='signin'),
   path('home', home, name='home'),
   path('profile', profile, name='profile'),
   path('prefab', prefab, name='prefab'),
   path('addprefab', addprefab, name='addprefab'),
   path('category', category, name='category'),

   #post
   path('save_prefab', save_prefab, name='save_prefab'),
   path('db_add_user', db_add_user, name='db_add_user'),
   path('user_login', user_login, name='user_login'),
   path('download_prefab', download_prefab, name='download_prefab'),
   path('delete_prefab', delete_prefab, name='delete_prefab'),
   path('logout', logout, name='logout'),
   path('save_preview', save_preview, name='save_preview'),
   path('delete_preview', delete_preview, name='delete_preview'),
   path('preview', preview, name='preview'),
   path('set_username', set_username, name='set_username'),
   


   #database
   path('database', get_database, name='database'),
   path('delete_db_element', delete_db_element, name='delete_db_element'),

   #api
   path('api', con_api, name='api'),
]