from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Student
import re
from django.core.exceptions import ValidationError

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email đã được sử dụng.")
        return email

    def clean_password2(self):
        pass1 = self.cleaned_data.get('password1')
        pass2 = self.cleaned_data.get('password2')
        if pass1 and pass2 and pass1 != pass2:
            raise forms.ValidationError("Mật khẩu không khớp.")
        return pass2


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'age', 'email', 'phone', 'address']

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name or re.search(r'<script.*?>', name, re.IGNORECASE):
            raise forms.ValidationError("Tên không được chứa mã độc hoặc để trống.")
        return name

    def clean_address(self):
        address = self.cleaned_data.get('address')
        if not address or re.search(r'<script.*?>', address, re.IGNORECASE):
            raise forms.ValidationError("Địa chỉ không được chứa mã độc hoặc để trống.")
        return address

    def clean_age(self):
        age = self.cleaned_data.get('age')
        if not (1 <= age <= 120):
            raise forms.ValidationError("Tuổi phải nằm trong khoảng từ 1 đến 120.")
        return age

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not re.fullmatch(r'\d{10}', phone or ''):
            raise forms.ValidationError("Số điện thoại phải đúng 10 chữ số.")
        elif Student.objects.filter(phone=phone).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Số điện thoại đã tồn tại.")
        return phone


    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Student.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Email đã tồn tại.")
        return email
