from django.urls import path

from . import views
urlpatterns = [
    path('admin', views.login_form),
    path('admin/login', views.login),
    path('admin/logout', views.logout),
    path('admin/index', views.index),
    path('admin/signup', views.register_form),
    path('admin/changepassword_form', views.change_password_form),
    path('admin/changepassword', views.changepwd),
    path('admin/register', views.register),
    path('admin/category', views.category),
    path('admin/attribute_groups', views.attribute_groups),
    # path('admin/attribute_groups_add_form', views.attribute_groups_add_form),
    path('admin/attributes', views.attributes),
    ]