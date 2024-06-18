from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

# Register your models here.

from witch_chess_app.models import *

class ProfileAdmin(admin.ModelAdmin):
    pass

class ClientAdmin(admin.ModelAdmin):
    pass

class LobbyAdmin(admin.ModelAdmin):
    pass

class GameSetAdmin(admin.ModelAdmin):
    pass

admin.site.register(Profile, ProfileAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(Lobby, LobbyAdmin)
admin.site.register(GameSet, GameSetAdmin)