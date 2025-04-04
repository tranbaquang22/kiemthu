from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Student

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_password2(self):
        pass1 = self.cleaned_data.get('password1')
        pass2 = self.cleaned_data.get('password2')
        if pass1 and pass2 and pass1 != pass2:
            raise forms.ValidationError("Mật khẩu không khớp")
        return pass2

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'age', 'email', 'phone', 'address']