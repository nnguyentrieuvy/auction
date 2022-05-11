import pymongo
from django.conf import settings

def permission(request, user, role):
    #user la mot document
    result = None
    usr = request.session.get('auction_account')['username']
    pwd = request.session.get('auction_account')['password']
    rl = request.session.get('auction_account')['role']
    if user is not None:
        if usr == user.account and pwd == user.password and rl == role:
            result = role
    return result