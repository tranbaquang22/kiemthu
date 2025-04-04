from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.http import HttpResponse
import re
from .models import Student
from .forms import RegisterForm
from django.http import JsonResponse
from django.middleware.csrf import get_token
# Hàm đăng nhập
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('student_list')
        else:
            return HttpResponse('Sai thông tin đăng nhập!', status=400)

    return render(request, 'main/login.html')

# Hàm đăng ký
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Đăng ký thành công!")
            return redirect('login')
        else:
            # In lỗi form ra console để kiểm tra
            print(form.errors)  #
            messages.error(request, "Đăng ký thất bại. Vui lòng kiểm tra lại.")
    else:
        form = RegisterForm()
    return render(request, 'main/register.html', {'form': form})


# Hàm hiển thị danh sách sinh viên
def student_list(request):
    if not request.user.is_authenticated:
        return redirect('login')  # Chuyển hướng nếu chưa đăng nhập
    students = Student.objects.all()

    # Đảm bảo ID bắt đầu từ 1 sau khi xóa
    students = students.order_by('id')  # Sắp xếp lại theo ID

    return render(request, 'main/student_list.html', {'students': students})

# Hàm thêm hoặc chỉnh sửa sinh viên
# Hàm thêm hoặc chỉnh sửa sinh viên
def student_form(request, id=None):
    if not request.user.is_authenticated:
        return redirect('login')  # Chuyển hướng nếu chưa đăng nhập

    if id:
        student = get_object_or_404(Student, id=id)
    else:
        student = None

    if request.method == "POST":
        name = request.POST.get('name', '').strip()  # Sử dụng default là chuỗi rỗng
        age = request.POST.get('age', '').strip()  # Sử dụng default là chuỗi rỗng
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()

        # Kiểm tra xem các trường có phải là chuỗi không và xử lý regex cho email
        if not isinstance(email, str) or not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
            messages.error(request, "Địa chỉ email không hợp lệ.")
            return render(request, 'main/student_form.html', {
                'student': student,
                'name': name,
                'email': email,
                'age': age,
                'phone': phone,
                'address': address
            })

        if not isinstance(phone, str) or (phone and len(phone) != 10):
            messages.error(request, "Số điện thoại phải có 10 chữ số.")
            return render(request, 'main/student_form.html', {
                'student': student,
                'name': name,
                'email': email,
                'age': age,
                'phone': phone,
                'address': address
            })

        # Kiểm tra email trùng (ngoại trừ bản ghi đang chỉnh sửa)
        if Student.objects.filter(email=email).exclude(id=id).exists():
            messages.error(request, "Email này đã tồn tại. Vui lòng sử dụng email khác.")
            return render(request, 'main/student_form.html', {
                'student': student,
                'name': name,
                'email': email,
                'age': age,
                'phone': phone,
                'address': address
            })

        if student:
            # Cập nhật sinh viên
            student.name = name
            student.age = age
            student.email = email
            student.phone = phone
            student.address = address
            student.save()
            messages.success(request, "Sinh viên đã được cập nhật.")
        else:
            # Thêm mới sinh viên
            new_student = Student(
                name=name,
                age=age,
                email=email,
                phone=phone,
                address=address
            )
            new_student.save()
            
            messages.success(request, "Sinh viên đã được thêm mới.")

        return redirect('student_list')  # Quay lại danh sách sinh viên

    return render(request, 'main/student_form.html', {'student': student})



# Hàm xóa sinh viên
def delete_student(request, id):
    if not request.user.is_authenticated:
        return redirect('login')

    student = get_object_or_404(Student, id=id)
    student.delete()
    messages.success(request, "Sinh viên đã được xóa.")
    return redirect('student_list')

# Hàm đăng xuất
def logout_view(request):
    logout(request)
    return redirect('login')  # Chuyển hướng về trang đăng nhập sau khi đăng xuất


def get_csrf_token(request):
    token = get_token(request)
    return JsonResponse({'csrf_token': token})