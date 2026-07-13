from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from core import views as core_views
from books import views as book_views
from papers import views as paper_views
from ai_assistant import views as ai_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', core_views.home, name='home'),
    path('books/', book_views.book_list, name='book_list'),
    path('books/upload/', book_views.upload_book, name='upload_book'),
    
    path('papers/', paper_views.paper_list, name='paper_list'),
    path('papers/upload/', paper_views.upload_paper, name='upload_paper'),
    path('lectures/', paper_views.lecture_list, name='lecture_list'),
    path('lectures/upload/', paper_views.upload_lecture, name='upload_lecture'),
    
    path('ai/', ai_views.ai_assistant, name='ai_assistant'),
    path('ai/query/', ai_views.ai_query, name='ai_query'),
    path('profile/', core_views.edit_profile, name='edit_profile'),
    path('dashboard/', core_views.analytics_dashboard, name='analytics_dashboard'),
    
    # Anonymous Chat
    path('chat/', core_views.chat_lobby, name='chat_lobby'),
    path('chat/messages/', core_views.get_chat_messages, name='get_chat_messages'),
    path('chat/send/', core_views.send_chat_message, name='send_chat_message'),
    path('chat/search/', core_views.search_shareable_materials, name='search_shareable_materials'),
    path('chat/upvote/<int:message_id>/', core_views.upvote_message, name='upvote_message'),
    path('chat/unread/', core_views.check_unread_messages, name='check_unread_messages'),
    
    # Fast Viewer
    path('viewer/<str:type>/<int:id>/', core_views.view_material, name='view_material'),
    
    # Collabo
    path('collabo/', core_views.collabo_home, name='collabo_home'),
    path('collabo/create/', core_views.create_group, name='create_group'),
    path('collabo/join/', core_views.join_group, name='join_group'),
    path('collabo/<int:pk>/', core_views.group_detail, name='group_detail'),
    path('collabo/<int:pk>/task/update/', core_views.group_task_update, name='group_task_update'),
    path('collabo/<int:pk>/doc/add/', core_views.group_add_doc, name='group_add_doc'),
    path('collabo/<int:pk>/messages/', core_views.group_messages, name='group_messages'),
    path('collabo/<int:pk>/leave/', core_views.group_leave, name='group_leave'),
    
    # Authentication
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('signup/', core_views.signup, name='signup'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)