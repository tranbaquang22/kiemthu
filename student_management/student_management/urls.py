from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),  # Thêm đường dẫn này để trỏ về các URL trong app 'main'
]
