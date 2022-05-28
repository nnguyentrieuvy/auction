import pymongo
from django.conf import settings
from django.shortcuts import render, redirect

def permission(request, user, role):
    #user la mot document
    result = None
    try:
        usr = request.session.get('auction_account')['username']
        pwd = request.session.get('auction_account')['password']
        rl = request.session.get('auction_account')['role']
        if user is not None:
            if usr == user.id and pwd == user.password and rl == role:
                result = role
        return result
    except KeyError:
        return redirect('/login')
