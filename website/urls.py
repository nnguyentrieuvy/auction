from django.urls import path

from . import views
urlpatterns = [
    path('registration', views.registration),
    path('verify/<str:token>', views.verify),
    path('login', views.login),
    path('logout', views.logout),
    path('usr/0/information', views.information),
    # path('verification', views.verification_form),
    ]