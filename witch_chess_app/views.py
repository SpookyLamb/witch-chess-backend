from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status

from .models import *
from .serializers import *

# user creation

@api_view(['POST'])
@permission_classes([])
def create_user(request):
    user = User.objects.create(
        username = request.data['username'],
    )
    user.set_password(request.data['password'])
    user.save()
    
    profile = Profile.objects.create(
        user = user,
        email = request.data['email'],
    )
    profile.save()
    profile_serialized = ProfileSerializer(profile)
    return Response(profile_serialized.data)

# profile CRUD

@api_view(['GET'])
def get_profile(request):
    user = request.user
    profile = user.profile
    serialized_profile = ProfileSerializer(profile)
    return Response(serialized_profile.data)

# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def get_userID(request):
#     user = request.user
#     userID = user.id
#     return Response({"id": userID})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_lobbies(request):
    user = request.user

    lobbies = Lobby.objects.all()
    lobbies_serialized = {}

    for lobby in lobbies:
        lobby_serialized = LobbySerializer(lobby)
        data = lobby_serialized.data
        lobbies_serialized[str(lobby_serialized.data["id"])] = data #add to dictionary

    return Response(lobbies_serialized)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_win(request):
    user = request.user
    profile = user.profile

    profile.wins += 1
    profile.save()

    return Response()

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_wins(request):
    user = request.user
    profile = user.profile

    return Response(profile.wins)