from django import forms
from .models import UserProfile, Gender

class StudentForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control rounded-pill bg-light border-0', 'placeholder': 'Password'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control rounded-pill bg-light border-0', 'placeholder': 'Confirm'}))

    class Meta:
        model = UserProfile
        fields = ['username', 'email', 'gender', 'profile_picture', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control rounded-pill bg-light border-0', 'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control rounded-pill bg-light border-0', 'placeholder': 'Email'}),
            'gender': forms.Select(attrs={'class': 'form-select rounded-pill bg-light border-0'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control rounded-pill bg-light border-0'}),
        }