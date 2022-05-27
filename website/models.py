# https://github.com/MongoEngine/django-mongoengine
import datetime

from mongoengine import *
from django_mongoengine import fields, Document
from django.core.files.storage import FileSystemStorage
from django.conf import settings
# Create your models here.

class account(Document):
    account = fields.StringField(max_length=100, primary_key=True)
    password = fields.StringField(max_length=100)
    email = fields.StringField(max_length=100)
    phonenb = fields.StringField(max_length=100, blank=True)
    address = fields.StringField(max_length=100)
    city = fields.StringField(max_length=300)
    district = fields.StringField(max_length=300)
    role = fields.StringField(max_length=100, blank=True)
    is_verify = fields.BooleanField(default=False, blank=True)
    token = fields.StringField(default=None, blank=True)
    image = fields.ImageField(upload_to='account', blank=True)
    img_url = fields.StringField(default=None, blank=True)
    # image = fields.ImageField(upload_to='media', default=content_file_name, blank=True)


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
    category_parent = fields.IntField()
    name = fields.StringField(max_length=300)
    attributes_id = fields.ListField(ReferenceField('attributes', reverse_delete_rule=CASCADE))


class OneImage(EmbeddedDocument):
    image = fields.ImageField(upload='product')
    url = fields.StringField()


# class item_specifics(EmbeddedDocument):
#     attributes = ReferenceField('attributes', reverse_delete_rule=CASCADE)
#     content = fields.StringField(max_length=500)


class product(Document):
    # usr = account.objects(pk='hhh').first()
    name = fields.StringField(max_length=300)
    category = fields.ReferenceField('category', reverse_delete_rule=CASCADE)
    decription = fields.StringField(max_length=500)
    quantity = fields.IntField(default=1)
    address = fields.StringField(max_length=200)
    city = fields.StringField(max_length=300)
    district = fields.StringField(max_length=300)
    image = fields.EmbeddedDocumentListField(OneImage)
    startingbid = fields.FloatField()
    duration = fields.StringField()
    condition = fields.StringField()
    # specifics = fields.EmbeddedDocumentListField(item_specifics)
    seller = fields.ReferenceField('account', reverse_delete_rule=CASCADE)


class product_attributes(Document):
    product_id = fields.ReferenceField('product', reverse_delete_rule=CASCADE)
    attributes = fields.ReferenceField('attributes', reverse_delete_rule=CASCADE)
    content = fields.StringField(max_length=500)


class room(Document):
    # Title = fields.StringField(max_length=500)
    product_id = fields.ReferenceField('product', reverse_delete_rule=CASCADE)
    total = fields.FloatField()
    start = fields.DateTimeField(default=datetime.datetime.utcnow)
    end = fields.DateTimeField()
    seller_id = fields.ReferenceField('account', reverse_delete_rule=CASCADE)
    quantity_of_bidder = fields.IntField()
    bidders = fields.ListField(ReferenceField('account', reverse_delete_rule=CASCADE), blank=True)
    highestbidder = fields.ReferenceField('account', reverse_delete_rule=CASCADE, blank=True)
    current_bid = fields.FloatField()
    status = fields.StringField(max_length=10)
    winner = fields.ReferenceField('account', reverse_delete_rule=CASCADE, blank=True)




