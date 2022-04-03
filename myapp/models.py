from django.db import models


DATABASES_NAMES = ["user", "prefabdata", "categories"]

class user(models.Model):
    email = models.CharField(max_length=255)
    username = models.CharField(max_length=255, default="")
    password = models.CharField(max_length=255)
    tocken = models.CharField(max_length=255)
    prefabs = models.TextField(default="")


class prefabdata(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(default="")
    picture = models.IntegerField(default=0)
    picture_extention = models.CharField(max_length=255, default="png")
    file_name = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    static_file_names = models.TextField(default="")
    user = models.CharField(max_length=255, default="default_user")
    like = models.IntegerField(default=0)
    view = models.IntegerField(default=0)
    path = models.TextField(default="")
    user_like_putin = models.TextField(default="10")

class categories(models.Model):
    name = models.CharField(max_length=255)
    count = models.IntegerField(default=0)