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
    path('admin/category/edit', views.category_edit),
    path('admin/category/update', views.category_update),
    path('admin/category/delete=<int:id>', views.delete_category),
    path('admin/category/attributes_attrgroups', views.attributes_attrgroups),
    path('admin/attribute_groups', views.attribute_groups),
    path('admin/attribute_groups/delete=<int:id>', views.delete_attribute_groups),
    path('admin/attribute_groups/update=<int:id>', views.update_attribute_groups),
    path('admin/attributes', views.attributes),
    path('admin/attributes/delete=<int:id>', views.delete_attributes),
    path('admin/attributes/update=<int:id>', views.update_attributes),

    ]