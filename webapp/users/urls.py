from django.urls import path
from . import views
from documents import views as doc_views

urlpatterns = [
    path('pro_dashboard/', doc_views.pro_dashboard, name='pro_dashboard'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('upload/', doc_views.upload_document, name='upload_document'),
    path('documents/', doc_views.document_list, name='document_list'),
    path('create_formation/', doc_views.create_formation, name='create_formation'),
    path('formations/', doc_views.formation_list, name='formation_list'),
    path('logout/', doc_views.logout_view, name='logout'),
    path('formation/edit/<int:formation_id>/', doc_views.edit_formation, name='edit_formation'),
    path('formation/delete/<int:formation_id>/', doc_views.delete_formation, name='delete_formation'),
    path('chat/', views.chat, name='chatbot'),
    path('chat-api/<int:conversation_id>/', views.chat_api, name='chat_api'),
    path('chat/conversations/new/', views.new_conversation, name='new_conversation'),
    path('chat/conversations/<int:conversation_id>/', views.get_conversation, name='get_conversation'),

]
