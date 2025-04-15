from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('', views.home, name='home'),
    path('view-data/', views.view_data, name='view_data'),
    path('process-image/', views.process_image, name='process_image'),  # Add this line
]