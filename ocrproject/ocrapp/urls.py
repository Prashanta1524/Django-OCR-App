from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('process/', views.process_image, name='process_image'),
    path('view-data/', views.view_data, name='view_data'),
] 