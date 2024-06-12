from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_document, name='upload_document'),
    path('create_formation/', views.create_formation, name='create_formation'),
    path('formations/', views.formation_list, name='formation_list'),
    path('pro_dashboard/', views.pro_dashboard, name='pro_dashboard'),
    path('documents/', views.document_list, name='document_list'),
    path('documents/<int:document_id>/view/', views.view_document, name='view_document'),
    path('documents/<int:document_id>/delete/', views.delete_document, name='delete_document'),
    path('documents/<path:path>', views.serve_pdf, name='serve_pdf'),


]
