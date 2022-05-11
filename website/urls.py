from django.urls import path

from . import views
urlpatterns = [
    path('registration', views.registration),
    path('verify/<str:token>', views.verify),
    path('login', views.login),
    path('logout', views.logout),
    path('usr/0/information', views.information),
    path('usr/0/information/update', views.update),
    path('home', views.home),
    path('category', views.category_select),
    path('seller/detail_product', views.detail_product),
    path('seller/detail_product_form', views.detail_product_form),
    # path('verification', views.verification_form),
    ]