# https://github.com/MongoEngine/django-mongoengine
from mongoengine import *
from django_mongoengine import fields, Document
# Create your models here.

class auction_account(Document):
    account = fields.StringField(max_length=100)
    password = fields.StringField(max_length=100)



class account(Document):
    account = fields.StringField(max_length=100)
    password = fields.StringField(max_length=100)
    email = fields.StringField(max_length=100)
    address = fields.StringField(max_length=100)
    city = fields.StringField(max_length=100)
    district = fields.StringField(max_length=100)
    role = fields.StringField(max_length=100)
    is_verify = fields.BooleanField(default=False)
    token = fields.StringField(default=None)

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

class category(Document):
    id = fields.IntField(primary_key=True)
    catagory_parent = fields.IntField()
    name = fields.StringField(max_length=300)
    attributes_id = fields.ListField(ReferenceField('attributes', reverse_delete_rule=CASCADE))



