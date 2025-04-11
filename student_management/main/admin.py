from django.contrib import admin
from .models import Student

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'age', 'email', 'phone', 'address', 'created_at')  # Các cột hiển thị
    search_fields = ('name', 'email', 'phone')  # Cho phép tìm kiếm
    list_filter = ('age', 'created_at')  # Bộ lọc
    ordering = ('id',)  # Sắp xếp theo ID tăng dần
