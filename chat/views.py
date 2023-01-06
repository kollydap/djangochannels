from django.shortcuts import render
from.models import Room, Message

def index(request):
    return render(request,'index.html',{'rooms':Room.objects.all()})

# def room(request,room_name):
#     return render(request,'chatroom.html',{
#         'room_name':room_name
#     })

def room(request, room_name):
    chat_room, created = Room.objects.get_or_create(name=room_name)
    return render(request, 'chatroom.html', {"room_name": chat_room})