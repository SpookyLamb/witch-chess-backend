from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

# Register your models here.

from witch_chess_app.models import *

class ProfileAdmin(admin.ModelAdmin):
    pass

admin.site.register(Profile, ProfileAdmin)