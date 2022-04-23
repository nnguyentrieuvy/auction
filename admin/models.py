# https://github.com/MongoEngine/django-mongoengine
from mongoengine import *
from django_mongoengine import fields, Document
# Create your models here.

class auction_account(Document):
    account = fields.StringField(max_length=100)
    password = fields.StringField(max_length=100)



class account(Document):
    account = StringField(max_length=100)
    password = StringField(max_length=100)
    auth_password = StringField(max_length=100)
    email = StringField(max_length=100)
    auth_email = StringField(max_length=100)
    role = StringField(max_length=100)

class category(Document):
    id = fields.IntField(primary_key=True)
    catagory_parent = fields.StringField()
    name = fields.StringField(max_length=300)

class attribute_groups(Document):
    id = fields.IntField(primary_key=True)
    name = fields.StringField(max_length=300)

class attributes(Document):
    attr_groups_list = []
    for c in attribute_groups.objects:
        attr_groups = (str(c.id), c.name)
        attr_groups_list.append(attr_groups)
    id = fields.IntField(primary_key=True)
    name = fields.StringField(max_length=300)
    # attribute_groups_id = fields.IntField(choices=attr_groups_list)
    # atrg is refe..field in model so it just saves _id of corresponding attribute_groups documenent. (see attributes in view)
    attribute_groups_id = fields.ReferenceField('attribute_groups',reverse_delete_rule=CASCADE)
