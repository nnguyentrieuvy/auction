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
    path('seller/product', views.product),
    # path('seller/detail_product', views.detail_product),
    path('seller/detail_product/save', views.save_product),
    path('seller/detail_product_form', views.detail_product_form),
    path('seller/get_category', views.get_category),
    path('vd', views.vd),
    path('room/<str:id>', views.room_detail),
    path('bidder/bid', views.bid),
    path('get_next_bids', views.get_next_bids),
    # path('verification', views.verification_form),
    ]