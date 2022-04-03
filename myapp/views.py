import re
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse, QueryDict, JsonResponse
from django.templatetags.static import static
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from .models import *
import os
from bs4 import BeautifulSoup
import html
from urllib.parse import quote
from urllib.parse import unquote
import base64
import sys
import zlib
from random import randint
import boto3
import magic
import gzip
import requests
import json
import zipfile
import shutil
import subprocess
import boto3.session

GLOBAL_URL = "https://htmlprefabs.herokuapp.com/"

SITE_PATH = os.getcwd()
APP_PATH = SITE_PATH + "/myapp"
TEMPLATE_PATH = SITE_PATH + "/myapp/templates"
PREFAB_PATH = SITE_PATH + "/myapp/templates/prefabs"
STATIC_PATH = SITE_PATH + "/myapp/static"

# aws S3 bucket
mime = magic.Magic(mime=True)
s3_client = boto3.client("s3")
ACCESS_ID = "AKIA4IIU3O5VQTIJIIWH"
ACCESS_KEY = "2bjcx0uF+bxxtTiR+Asz75qPuYQBj3wlOGxMtpuS"
BUCKET_NAME = "html-prefab-bucket"

s3 = boto3.resource('s3', aws_access_key_id=ACCESS_ID, aws_secret_access_key=ACCESS_KEY)
my_session = boto3.session.Session(aws_access_key_id=ACCESS_ID, aws_secret_access_key=ACCESS_KEY)
s3_session = my_session.client('s3')


CONTENT_TYPE = {
    "png" : "image/png",
    "jpg" : "image/jpeg",
    "jpeg" : "image/jpeg",
    "html" : "text/html",
    "css" : "text/css",
    "csv" : "text/csv",
    "js" : "text/javascript",
    "ttf" : "font/ttf",
    "zip" : "application/zip",
}

SEPARATOR = "/*s*/"

# utils
def jsError(error):
    return JsonResponse({"success":0, "error":error})

def is_user_exist(email):
    try:
        u = user.objects.get(email=email)
        return True
    except:
        return False

def array_to_str(array, separator=","):
    response = ""   
   
    for i in range(len(array)):
        if i == 0:
            response = str(array[i])
        else:
            response = response + separator + str(array[i]) 

    return response

def is_user_connected(request):
    is_con = 0
    try:
        r = request.session["logged"]
        if request.session["logged"] == 1:
            is_con = 1
        else:
            is_con = 0
    except:
        is_con = 0

    return is_con


def get_curr_user(request):
    if is_user_connected(request):
        u = user.objects.get(tocken=request.session["tocken"])
        return u
    else:
        return False



def get_file_extention(file):
    file = file.split(".")
    file = file[len(file)-1] 
    return file

def get_content_type(extention):
    try : return CONTENT_TYPE[extention]
    except: return "text/plain"
    

def get_file_content_type(file):
    extention = get_file_extention(file)
    return get_content_type(extention)

def upload_file(bucket_path, data="", path="", content_type=""):

    if data == "":
        data = open(path, "rb")
        content_type = mime.from_file(path)

    s3.Bucket(BUCKET_NAME).put_object(Key=bucket_path, Body=data, ContentType=content_type, ACL="public-read")


def create_compressed_file(file_path, destination_path):
    with gzip.open(destination_path + ".gz", 'wb') as f:
        with open(file_path, "rb") as file:
            f.write(file.read())


def create_uncompressed_file(file_path, destination_path):
    with gzip.open(file_path, 'rb') as file:
        with open(destination_path, "wb") as f:
            f.write(file.read())


def get_post_file_data(data):
    data = data.replace("/*0*/", "+")
    data = data.replace("/*1*/", "&")

    return data

# templates
def is_not_log(func):
    def wrapper(*args, **kwargs):
        is_connected = 0
        try: 
            if(args[0].session["logged"] == 1):
                is_connected = 1
            else:
                is_connected = 0
        except:
            is_connected = 0
            
        if is_connected == 1:
            return func(*args, **kwargs)
        else:
            return home(args[0], log={"logged":2})

    return wrapper

def is_not_log_json(func):
    def wrapper(*args, **kwargs):
        try:
            if args[0].session["logged"] == 1:
                return func(*args, **kwargs)
            else:
                return JsonResponse({"success" : 0})
        except:
            return JsonResponse({"success" : 0})

    return wrapper

def is_log(func):
    def wrapper(*args, **kwargs):
        try:
            if args[0].session["logged"] == 1:
                return home(args[0])
            else:
                return func(*args, **kwargs)
        except:
            return func(*args, **kwargs)

    return wrapper


def is_log_json(func):
    def wrapper(*args, **kwargs):
        try:
            if args[0].session["logged"] == 1:
                return JsonResponse({"success" : 0})
            else:
                return func(*args, **kwargs)
        except:
            return func(*args, **kwargs)

    return wrapper


@is_log
def index(request):
    return render(request, 'index.html')

@is_log
def login(request):
    return render(request, 'login.html')

@is_log
def signin(request):
    return render(request, 'signin.html')


@is_not_log
def profile(request):
    u = get_curr_user(request)
    if u != False:
        p_array = []
        for p_files_name in u.prefabs.split("/*s*/"):
            try: 
                p = prefabdata.objects.get(file_name=p_files_name) 
                p_array.append(p)
            except: 
                pass
            

        return render(request, 'profile.html', {"user_prefabs":p_array, "u_tocken": u.tocken, "user":u})


def website(request):
    return render(request, 'website.html')


def home(request, *args, **kwargs):
    curr_user = get_curr_user(request)
    cat_dict = {"categories": categories.objects.all()}
    data = {**cat_dict, **kwargs}

    if curr_user != False:
        return render(request, 'home.html', data)
    else:
        data["log"] = {}
        data["log"]["logged"] = 2
        return render(request, 'home.html', data)


#prefabs
def get_prefabs_from_category(category, order="r"):
    response = []
    if order == "r": order = "id"
    if order == "v": order = "view"
    if order == "l": order = "like"
    for obj in prefabdata.objects.order_by(order, "id"):
        if obj.category == category:
            response.append(obj)
    return response

def find_in_array(element, array):
    for index, obj in enumerate(array):
        if obj == element:
            return index

def get_next_prefab(prefab, order="r"):
    prefabs = get_prefabs_from_category(prefab.category, order)
    index = find_in_array(prefab, prefabs)
    return prefabs[index-1]



def prefab(request, file=''):
    if file == '': file = request.GET.get('file', '')
    sort = request.GET.get('s', 'r')

    db_object = prefabdata.objects.get(file_name=file)
    db_object_user = user.objects.get(email=db_object.user)
    category = db_object.category
    file_name = db_object.file_name
    static_file_names = db_object.static_file_names

    u = get_curr_user(request)
    path = f"prefabs/{category}/{db_object_user.tocken}/{file}/html_file.html"
    bucket_path = static(f"prefabs/{category}/{db_object_user.tocken}/{file}/")
    url = static(path)
    try:
        if str(u.id) in db_object.user_like_putin.split('/*s*/'): is_liked = 1
        else: is_liked = 0
    except:
        is_liked = 0

    #get next prefab
    next = get_next_prefab(db_object, sort)
    
    #get bucket data
    r = requests.get(url)
    file_content = quote(r.content)
    return render(request, "prefab.html", {
        "file": file, 
        "url": url, 
        "file_content": file_content,
        "bucket_path":bucket_path, 
        "static_file_names": static_file_names, 
        "file_id":db_object.id, 
        "file_name":file_name,
        "is_liked":is_liked,
        "sort":sort,
        "next":next.file_name,
        "category":category,
    })

@is_not_log
def addprefab(request):
    return render(request, 'addprefab.html', {"categories": categories.objects.order_by("id")})

@is_not_log_json
def save_prefab(request):
    input_error = 0
    picture = 0
    u = get_curr_user(request)

    #title
    title = u.username #request.POST.get('title', '')
    #title = get_post_file_data(title)

    #category (div title button ...)
    category = request.POST.get('category', '')
    custom_category = request.POST.get('custom', '').lower()


    try:  
        if custom_category != "":
            custom_category = get_post_file_data(custom_category) 
    except:pass

    #data html
    data = request.POST.get('data', '')
    data = get_post_file_data(data)

    #description
    description = "desc" #request.POST.get('description', '')
    #description = get_post_file_data(description)
    
    #static files
    data_static = request.POST.get('data_static', '')
    data_static = get_post_file_data(data_static)
    static_files_data = data_static.split("/*s*/")

    #static files name
    data_static_files_names = request.POST.get('data_static_files_names', '')
    data_static_files_names_data_string = "/*d*/default"

    if data_static_files_names != "":
        data_static_files_names = get_post_file_data(data_static_files_names)
        data_static_files_names_data = data_static_files_names.split("/*s*/")
        data_static_files_names_data_string = array_to_str(data_static_files_names_data, "/*s*/")

    #picture
    data_pic = request.POST.get('data_pic', '')
    if data_pic != "": picture = 1
    data_pic = get_post_file_data(data_pic)
    data_pic = base64.b64decode(data_pic)
    data_pic_name = request.POST.get('pic_file_name', '')

    data_pic_extention = get_file_extention(data_pic_name)


    if data == "": return JsonResponse({"success": 0, "error":"Html file empty"})
    if category == "": return JsonResponse({"success": 0, "error":"Category field empty"})

    try:
        if category == "custom":
            if custom_category != "": 
                add_category(custom_category)
                category = custom_category
    except:pass

    file_name = title + "_" + str(randint(0, 1000000))

    if len(data) != 0:
        path = f"prefabs/{category}/{u.tocken}/{file_name}/"
        bucket_path = static(path)

        upload_file(path+"html_file.html", data=data, content_type="text/html")
        
        upload_file(path+f"picture.{data_pic_extention}", data=data_pic, content_type=get_file_content_type(data_pic_name))
   
        if data_static_files_names != "":
            for i in range(len(static_files_data)):

                file_name_static = data_static_files_names_data[i]
                file_data = base64.b64decode(static_files_data[i])
                content_type = get_file_content_type(file_name_static)


                upload_file(path+file_name_static, data=file_data, content_type=content_type)

                
        user = get_curr_user(request)

        db_add_prefab(title, file_name, picture, data_pic_extention, data_static_files_names_data_string , category, like=0, view=0 ,user=user.email, path=bucket_path, description=description)
        
        
        if user.prefabs == "":
            user.prefabs += file_name
        else:
            user.prefabs += "/*s*/"+file_name

        user.save()


        c = categories.objects.get(name=category)
        c.count += 1
        c.save()
        return JsonResponse({"success": 1})
    else:
      return JsonResponse({"success": 0})


def download_prefab(request):
    
    path = request.POST.get("bucket_path", "")
    rel_path = path.split("https://html-prefab-bucket.s3.amazonaws.com/")[1][:-1]
    statics_file_path = request.POST.get("statics", "")
    file_name = request.POST.get("file_name", "")

    if path != "":
        picture_path = path+"picture"
        html_path = path+"html_file"

        if file_name+".zip" in os.listdir("myapp/static/zip_prefab/"):
            return JsonResponse({"success": 1})

        try : os.makedirs(f"temporary_zip_prefabs/{file_name}")
        except : pass

        s3.Bucket(BUCKET_NAME).download_file(f"{rel_path}/html_file.html", f'temporary_zip_prefabs/{file_name}/html_file.html')

        if statics_file_path != "":
            statics_file_path = statics_file_path.split("/*s*/")
            for f in statics_file_path:
                s3.Bucket(BUCKET_NAME).download_file(f"{rel_path}/{f}", f'temporary_zip_prefabs/{file_name}/{f}')
    
        shutil.make_archive(f"myapp/static/zip_prefab/{file_name}", "zip", f"temporary_zip_prefabs/{file_name}")
        shutil.rmtree(f'temporary_zip_prefabs/{file_name}')

        return JsonResponse({"success": 1})
    else:
        return JsonResponse({"success": 0})

@is_not_log_json
def delete_prefab(request):
    p_id = int(request.POST.get("p_id", ""))
    prefab = prefabdata.objects.get(id=p_id)
    prefab_user = prefab.user
    p_user = user.objects.get(email=prefab_user)
    u = get_curr_user(request)
    path = f"prefabs/{prefab.category}/{u.tocken}/{prefab.file_name}"
    

    if p_id != "":
        if u != False:
            if request.session["tocken"] == p_user.tocken:

                #delete on count
                c = categories.objects.get(name=prefab.category)
                c.count -= 1
                c.save()


                # delete on user
                u_prefabs = u.prefabs.split("/*s*/")
                u_prefabs.remove(prefab.file_name)
                u.prefabs = array_to_str(u_prefabs, SEPARATOR)
                u.save()



                # delete on db
                prefab.delete()

                # delete on cloud
                obj_list = s3_session.list_objects_v2(Bucket=BUCKET_NAME, StartAfter=path, Prefix=path)["Contents"]
                for obj in obj_list: 
                    obj_path = obj["Key"]
                    r = s3_session.delete_object(Bucket=BUCKET_NAME, Key=obj_path)

                return JsonResponse({"success" : 1})
            else:
                return JsonResponse({"success" : 0})
        else:
            return JsonResponse({"success" : 0})
    else: 
        return JsonResponse({"success" : 0})

def db_add_prefab(title, file_name, picture, picture_extention, static_file_names , category, like, view ,user, path, description=""):
    p = prefabdata(title=title, file_name=file_name, picture=picture, picture_extention=picture_extention, category=category, like=like, view=view ,user=user, static_file_names=static_file_names, path=path, description=description)
    p.save()

def next_prefab(request):
    p_id = request.GET.get("p_id", "")
    return JsonResponse({"success":1, "path":0})

def back_prefab(request):
    next_prefab_filename = request.GET.get("next_prefab_filename", "")
    return prefab(request, next_prefab_filename)



#preview
@is_not_log_json
def save_preview(request):
    input_error = 0
    picture = 0
    u = get_curr_user(request)



    #data html
    data = request.POST.get('data', '')
    data = get_post_file_data(data)

    category = "preview"

    #static files
    data_static = request.POST.get('data_static', '')
    data_static = get_post_file_data(data_static)
    static_files_data = data_static.split("/*s*/")

    #static files name
    data_static_files_names = request.POST.get('data_static_files_names', '')
    data_static_files_names_data_string = "/*d*/default"

    if data_static_files_names != "":
        data_static_files_names = get_post_file_data(data_static_files_names)
        data_static_files_names_data = data_static_files_names.split("/*s*/")
        data_static_files_names_data_string = array_to_str(data_static_files_names_data, "/*s*/")



    if data == "":
      return JsonResponse({"success": 0})


    if len(data) != 0:
        path = f"prefabs/preview/{u.tocken}/"
        bucket_path = static(path)

        upload_file(path+"htmlfile.html", data=data, content_type="text/html")
        
        if data_static_files_names != "":
            for i in range(len(static_files_data)):

                file_name_static = data_static_files_names_data[i]
                file_data = base64.b64decode(static_files_data[i])
                content_type = get_file_content_type(file_name_static)


                upload_file(path+file_name_static, data=file_data, content_type=content_type)

     

        return JsonResponse({"success": 1})
    else:
      return JsonResponse({"success": 0})

@is_not_log_json
def delete_preview(request):
    u = get_curr_user(request)

    if u != False:
        path = f"prefabs/preview/{u.tocken}/"
        obj_list = s3_session.list_objects_v2(Bucket=BUCKET_NAME, StartAfter=path, Prefix=path)["Contents"]
        for obj in obj_list: 
            obj_path = obj["Key"]
            r = s3_session.delete_object(Bucket=BUCKET_NAME, Key=obj_path)
    
    return JsonResponse({"success":1})

@is_not_log
def preview(request):
    u = get_curr_user(request)
   
    if u != False:
        path = f"prefabs/preview/{u.tocken}/"
        obj_list = s3_session.list_objects_v2(Bucket=BUCKET_NAME, StartAfter=path, Prefix=path)["Contents"]
        static_file_names = ""

        for obj in obj_list:
            if str(u.tocken) in obj["Key"]:
                s_obj = obj["Key"].split("/")
                s_obj = s_obj[len(s_obj)-1]
                
                if s_obj != "htmlfile.html":
                    static_file_names += s_obj+"/*s*/"

        if static_file_names.endswith("/*s*/"):
            static_file_names = static_file_names[0:len(static_file_names)-5]

        if static_file_names == "":
            static_file_names = "/*d*/default"
        

        file_content = quote(requests.get(static(f"prefabs/preview/{u.tocken}/htmlfile.html")).content)

        data = {
            "file_content":file_content,
            "user":u,
            "bucket_path": static(path),
            "static_file_names":static_file_names,
        }

        return render(request, "preview.html", data)


#user connection
@is_not_log_json
def logout(request):
    request.session["email"] = ""
    request.session["logged"] = 0
    del request.session["tocken"] 
    return home(request)

@is_log_json
def db_add_user(request):
    email = request.POST.get("email", "")
    password = request.POST.get("password", "")

    if is_user_exist(email) == False:
        if email != "" and password != "":
            tocken = str(randint(0, 100000000000000))
            u = user(email=email, password=password, tocken=tocken)
            u.save()
            request.session["logged"] = 1
            request.session["tocken"] = u.tocken
            return JsonResponse({"success": 1})

        else:
            request.session["logged"] = 0
            return JsonResponse({"success": 0, "error": "fields empty"})
    else:
        return JsonResponse({"success": 0, "error": "email already exist"})

@is_log_json
def user_login(request):
    email = request.POST.get("email", "")
    password = request.POST.get("password", "")

    if email != "" and password != "":
        if is_user_exist(email):
            u = user.objects.get(email=email)
            if u.password == password:
                request.session["logged"] = 1
                request.session["tocken"] = u.tocken 
                return JsonResponse({"success": 1})
            else:
                request.session["logged"] = 0
                return JsonResponse({"success": 0, "error": "wrong password"})
        else:
            return JsonResponse({"success": 0, "error": "email not found"})
    else:
        return JsonResponse({"success": 0, "error": "fields empty"})

def set_username(request):
    username = request.POST.get("username")
    if username == "": return jsError("field empty")
    if len(username) >= 255: return jsError("username too big")

    try : 
        if request.session["tocken"] == 1: pass
    except: return JsonResponse({"success":0})
    for us in user.objects.all():
        if us.username == username:
            return jsError("username already exist")
    u = user.objects.get(tocken=request.session["tocken"])
    u.username = username
    u.save()

    return JsonResponse({"success": 1})


#category
def category(request):
    cat = request.GET.get("cat")
    prefab_array = []
    for prefab in prefabdata.objects.order_by("-id"):
        if prefab.category == cat:
            prefab_array.append(prefab)
    return render(request, "category.html", {"title": cat, "prefab_array": prefab_array})

def add_category(name):
    all_cat = categories.objects.all()
    already_exist = 0

    name = name.lower()

    for i, cat in enumerate(all_cat):
        if cat.name == name:
            already_exist = 1
    
    if already_exist == 0:
        c = categories(name=name, count=0)
        c.save()


#api
def con_api(request):
    
    try : f = request.GET.get("f", "")
    except : pass

    @is_not_log_json
    def like(request):
        file_id = request.GET.get("file_id", "")
        if file_id != "":
            try: file_id = int(file_id)
            except: return JsonResponse({"success": 0})

            obj = prefabdata.objects.get(id=file_id)
            
            u = get_curr_user(request)
            already_liked = obj.user_like_putin.split("/*s*/")
            if str(u.id) not in already_liked:
                obj.user_like_putin += f"/*s*/{u.id}"
                obj.like += 1

            obj.save()

            return JsonResponse({"success": 1})
        else:
            return JsonResponse({"success": 0})

    @is_not_log_json
    def unlike(request):
        file_id = request.GET.get("file_id", "")
        if file_id != "":
            try: file_id = int(file_id)
            except: return JsonResponse({"success": 0})

            uid = str(get_curr_user(request).id)
            obj = prefabdata.objects.get(id=file_id)

            if uid in obj.user_like_putin.split(SEPARATOR):
                already_like = obj.user_like_putin.split(SEPARATOR)
                already_like.remove(uid)
                obj.user_like_putin = array_to_str(already_like, SEPARATOR)

                obj.like -= 1
                obj.save()

            return JsonResponse({"success": 1})
        else:
            return JsonResponse({"success": 0})

    def view(request):
        file_id = request.GET.get("file_id", "")
        if file_id != "":
            try: file_id = int(file_id)
            except: return JsonResponse({"success": 0})

            obj = prefabdata.objects.get(id=file_id)
            obj.view += 1
            obj.save()

            return JsonResponse({"success": 1})
        else:
            return JsonResponse({"success": 0})
    

    def debug(request):
        pass

    if f == "like":
        like(request)

    if f == "unlike":
        unlike(request)

    if f == "view":
        view(request)

    if f == "debug":
        debug(request)

    return JsonResponse({"success" : 1})

