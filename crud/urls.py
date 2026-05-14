from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_list, name='user_list'),
    path('edit/<int:pk>/', views.edit_user, name='edit_user'),
    path('delete/<int:pk>/', views.delete_user, name='delete_user'),
    path('edit-gender/<int:pk>/', views.edit_gender, name='edit_gender'),
    path('delete-gender/<int:pk>/', views.delete_gender, name='delete_gender'),
    path('archive/', views.archive_list, name='archive_list'),
    path('vault-action/', views.vault_action, name='vault_action'),
    path('export/', views.export_students, name='export_students'),
    path('check-email/', views.check_email_exists, name='check_email_exists'),
]