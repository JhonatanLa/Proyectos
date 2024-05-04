from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),  # Add this line
    path('upload/', views.upload_file, name='upload_file'),
    path('view-data/', views.view_data, name='view_data'),
    path('view-results/', views.view_results, name='view_results'),
    path('delete_data/', views.delete_data, name='delete_data'),
    path('base_generic/', views.base_generic, name='base_generic'),
]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)