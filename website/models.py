# https://github.com/MongoEngine/django-mongoengine
from mongoengine import *
from django_mongoengine import fields, Document
# Create your models here.

class account(Document):
    account = fields.StringField(max_length=100, primary_key=True)
    password = fields.StringField(max_length=100)
    email = fields.StringField(max_length=100)
    phonenb = fields.StringField(max_length=100, null=True)
    address = fields.StringField(max_length=100)
    city = fields.StringField(max_length=300)
    district = fields.StringField(max_length=300)
    role = fields.StringField(max_length=100, blank=True)
    is_verify = fields.BooleanField(default=False, blank=True)
    token = fields.StringField(default=None, blank=True)
    image = fields.ImageField(upload_to='media/', blank=True)




