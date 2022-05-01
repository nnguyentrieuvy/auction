from django.urls import path

from . import views
urlpatterns = [
    # path('signup', views.register_form),
    path('registration', views.registration),
    path('verify/<str:token>', views.verify),
    path('login', views.login),
    # path('verification', views.verification_form),
    ]