from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse
from django.middleware.csrf import get_token
from .models import Student
from .forms import RegisterForm, StudentForm
import json
import re

# -------- Đăng nhập --------
def login_view(request):
    if request.method == 'POST':
        if request.headers.get('Content-Type') == 'application/json':
            try:
                data = json.loads(request.body)
                username = data.get('username', '').strip()
                password = data.get('password', '').strip()
            except json.JSONDecodeError:
                return JsonResponse({'errors': ['Dữ liệu không hợp lệ.']}, status=400)
        else:
            username = request.POST.get('username')
            password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({'message': 'Đăng nhập thành công.'}, status=200)
            return redirect('student_list')
        else:
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({'errors': ['Sai thông tin đăng nhập.']}, status=401)
            messages.error(request, "Sai thông tin đăng nhập!")

    return render(request, 'main/login.html')

# -------- Đăng ký --------
def register_view(request):
    if request.method == 'POST':
        if request.headers.get('Content-Type') == 'application/json':
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({'errors': ['Dữ liệu không hợp lệ.']}, status=400)
            form = RegisterForm(data)
        else:
            form = RegisterForm(request.POST)

        if form.is_valid():
            form.save()
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({'message': 'Đăng ký thành công!'}, status=200)
            messages.success(request, "Đăng ký thành công!")
            return redirect('login')
        else:
            if request.headers.get('Content-Type') == 'application/json':
                errors = []
                for field, errs in form.errors.items():
                    for err in errs:
                        errors.append(f"{field}: {err}")
                return JsonResponse({'errors': errors}, status=400)
            else:
                for field, errs in form.errors.items():
                    for err in errs:
                        messages.error(request, f"{field}: {err}")
    else:
        form = RegisterForm()

    return render(request, 'main/register.html', {'form': form})


# -------- Danh sách sinh viên --------
def student_list(request):
    if not request.user.is_authenticated:
        return redirect('login')
    students = Student.objects.all().order_by('id')
    return render(request, 'main/student_list.html', {'students': students})


# -------- Thêm / Chỉnh sửa sinh viên --------
def student_form(request, id=None):
    if not request.user.is_authenticated:
        if request.headers.get('Content-Type') == 'application/json':
            return JsonResponse({'error': 'Unauthorized'}, status=401)
        return redirect('login')

    student = None
    if id:
        student = get_object_or_404(Student, id=id)

    form_data = {
        'name': student.name if student else '',
        'age': student.age if student else '',
        'email': student.email if student else '',
        'phone': student.phone if student else '',
        'address': student.address if student else '',
    }

    if request.method == "POST":
        # Nếu từ Postman JSON
        if request.headers.get('Content-Type') == 'application/json':
            try:
                data = json.loads(request.body)
                name = data.get('name', '').strip()
                age = data.get('age', '').strip()
                email = data.get('email', '').strip()
                phone = data.get('phone', '').strip()
                address = data.get('address', '').strip()
            except json.JSONDecodeError:
                return JsonResponse({'errors': ['Dữ liệu không hợp lệ.']}, status=400)
        else:
            # Dữ liệu từ form
            name = request.POST.get('name', '').strip()
            age = request.POST.get('age', '').strip()
            email = request.POST.get('email', '').strip()
            phone = request.POST.get('phone', '').strip()
            address = request.POST.get('address', '').strip()

        form_data.update({
            'name': name,
            'age': age,
            'email': email,
            'phone': phone,
            'address': address,
        })

        # Kiểm tra hợp lệ thủ công
        errors = []
        if not name or '<script>' in name.lower():
            errors.append("Tên không được để trống hoặc chứa mã độc.")
        if not age.isdigit() or not (1 <= int(age) <= 120):
            errors.append("Tuổi phải là số từ 1 đến 120.")
        if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
            errors.append("Email không hợp lệ.")
        if Student.objects.filter(email=email).exclude(id=id).exists():
            errors.append("Email đã tồn tại.")
        if not phone.isdigit() or len(phone) != 10:
            errors.append("Số điện thoại phải gồm đúng 10 chữ số.")
        if Student.objects.filter(phone=phone).exclude(id=id).exists():
            errors.append("Số điện thoại đã tồn tại.")
        if not address or '<script>' in address.lower():
            errors.append("Địa chỉ không được để trống hoặc chứa mã độc.")

        if errors:
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({'errors': errors}, status=400)
            else:
                for error in errors:
                    messages.error(request, error)
                return render(request, 'main/student_form.html', {'form_data': form_data, 'student': student})

        # Nếu hợp lệ, lưu dữ liệu
        if student:
            student.name = name
            student.age = age
            student.email = email
            student.phone = phone
            student.address = address
            student.save()
            message = "Sinh viên đã được cập nhật."
        else:
            Student.objects.create(
                name=name,
                age=age,
                email=email,
                phone=phone,
                address=address
            )
            message = "Sinh viên đã được thêm mới."

        if request.headers.get('Content-Type') == 'application/json':
            return JsonResponse({'message': message}, status=200)
        else:
            messages.success(request, message)
            return redirect('student_list')

    return render(request, 'main/student_form.html', {'form_data': form_data, 'student': student})


# -------- Xóa sinh viên --------
def delete_student(request, id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    student = get_object_or_404(Student, id=id)
    student.delete()
    return JsonResponse({'message': 'Sinh viên đã được xóa.'}, status=200)


# -------- Đăng xuất --------
def logout_view(request):
    logout(request)
    return redirect('login')


# -------- Lấy CSRF token --------
def get_csrf_token(request):
    token = get_token(request)
    return JsonResponse({'csrf_token': token})
