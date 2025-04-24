from django.urls import path
from . import views
from crawler_app import views
urlpatterns = [
    path('', views.index, name='home'),   # Ánh xạ trang 'home'
    path('demo1/dist/apps/user-management/users/view.html', views.view, name='view'),  # Ánh xạ trang 'view'
    path('create-task/', views.create_task, name='create_task'), 
    path('action-task/<int:task_id>/', views.action_task, name='action_task'),
]
