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
    
    path('ai/', ai_views.ai_assistant, name='ai_assistant'),
    path('ai/query/', ai_views.ai_query, name='ai_query'),
    path('profile/', core_views.edit_profile, name='edit_profile'),
    
    # Authentication
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('signup/', core_views.signup, name='signup'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)