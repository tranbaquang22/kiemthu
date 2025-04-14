from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse
from django.middleware.csrf import get_token
from .models import Student
from .forms import RegisterForm, StudentForm
import json
import re

from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
# -------- Đăng nhập --------

def login_view(request):
    if request.method == 'POST':
        is_json = 'application/json' in request.headers.get('Content-Type', '')
        
        if is_json:
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
            token, _ = Token.objects.get_or_create(user=user)

            if is_json:
                return JsonResponse({'message': 'Đăng nhập thành công.', 'token': token.key}, status=200)
            return redirect('student_list')
        else:
            if is_json:
                return JsonResponse({'errors': ['Sai thông tin đăng nhập.']}, status=401)
            messages.error(request, "Sai thông tin đăng nhập!")

    return render(request, 'main/login.html')

def get_user_from_token(request):
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Token '):
        token_key = auth_header.split('Token ')[1]
        try:
            token = Token.objects.get(key=token_key)
            return token.user
        except Token.DoesNotExist:
            return None
    return None

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
    is_json = request.headers.get('Content-Type') == 'application/json'
    user = get_user_from_token(request) if is_json else request.user

    if not user or not user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401) if is_json else redirect('login')

    students = Student.objects.all().order_by('id')

    if is_json or request.headers.get('Authorization'):
        student_data = []
        for student in students:
            student_data.append({
                'id': student.id,
                'name': student.name,
                'age': student.age,
                'email': student.email,
                'phone': student.phone,
                'address': student.address,
            })
        return JsonResponse({'students': student_data}, status=200)

    return render(request, 'main/student_list.html', {'students': students})

# -------- Thêm / Chỉnh sửa sinh viên --------
# -------- Thêm / Chỉnh sửa sinh viên --------
def student_form(request, id=None):
    is_json = request.headers.get('Content-Type') == 'application/json'

    if is_json:
        user = get_user_from_token(request)
        if not user:
            return JsonResponse({'error': 'Unauthorized'}, status=401)
        student = get_object_or_404(Student, id=id) if id else None
    else:
        if not request.user.is_authenticated:
            return redirect('login')
        student = get_object_or_404(Student, id=id) if id else None

    form_data = {
        'name': student.name if student else '',
        'age': student.age if student else '',
        'email': student.email if student else '',
        'phone': student.phone if student else '',
        'address': student.address if student else '',
    }

    if request.method in ["POST", "PUT"]:
        if is_json:
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

        # Kiểm tra hợp lệ
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
            if is_json:
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

        if is_json:
            return JsonResponse({'message': message}, status=200)
        else:
            messages.success(request, message)
            return redirect('student_list')

    # Nếu là GET hoặc chưa gửi dữ liệu: trả về dữ liệu form
    if is_json:
        if student:
            return JsonResponse({
                'id': student.id,
                'name': student.name,
                'age': student.age,
                'email': student.email,
                'phone': student.phone,
                'address': student.address,
            }, status=200)
        else:
            return JsonResponse({'message': 'Ready to create new student'}, status=200)

    return render(request, 'main/student_form.html', {'form_data': form_data, 'student': student})


# -------- Xóa sinh viên --------
def delete_student(request, id):
    if request.headers.get('Content-Type') == 'application/json':
        user = get_user_from_token(request)
        if not user:
            return JsonResponse({'error': 'Unauthorized'}, status=401)
    else:
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
