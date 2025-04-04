from django.urls import path
from . import views
from .views import get_csrf_token

urlpatterns = [
    path('', views.login_view, name='student_l'),  # Đặt trang đăng nhập làm trang chủ
    path('login/', views.login_view, name='login'),  # Đăng nhập
    path('register/', views.register_view, name='register'),  # Đăng ký
    path('students/', views.student_list, name='student_list'),  # Danh sách sinh viên
    path('student/', views.student_list),
    path('students/add/', views.student_form, name='student_add'),  # Thêm sinh viên
    path('students/edit/<int:id>/', views.student_form, name='student_edit'),  # Chỉnh sửa sinh viên
    path('students/delete/<int:id>/', views.delete_student, name='student_delete'),  # Xóa sinh viên
    path('logout/', views.logout_view, name='logout'),  # Đăng xuất
    path('get-csrf-token/', get_csrf_token, name='get_csrf_token'),
]
