from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UsernameField

from django.forms import FileField, ModelForm
from django.utils.translation import gettext_lazy as _

from home.models import AssignmentResult, User, Assignment


class RegistrationForm(UserCreationForm):
    username = forms.CharField(
            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Username'})
    )
    email = forms.CharField(
            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Email Address'})
    )
    first_name = forms.CharField(
            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'})
    )
    is_teacher = forms.IntegerField(
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'style': 'display: none;'})
    )
    password1 = forms.CharField(
            label=_("Password"),
            widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
    )
    password2 = forms.CharField(
            label=_("Confirm Password"),
            widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}),
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label=_("Your Username"),
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Username"})
    )
    password = forms.CharField(
            label=_("Your Password"),
            strip=False,
            widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Password"}),
    )

    class Meta:
        fields = ('username', 'password')


class UpdateUserProfileForm(forms.ModelForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Username'})
    )
    email = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Email Address'})
    )
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'})
    )
    profile_image = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ('profile_image', 'username', 'email', 'first_name', 'last_name')


class UpdatePasswordForm(forms.ModelForm):
    current_password = forms.CharField(
        label=_('Current Password'),
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Current Password'})
    )
    password = forms.CharField(
        label=_('New Password'),
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'New Password'})
    )
    confirm_password = forms.CharField(
        label=_('Confirm New Password'),
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm New Password'})
    )

    class Meta:
        model = User
        fields = ('current_password', 'password', 'confirm_password')


class AssignmentFileForm(ModelForm):
    class Meta:
        model = AssignmentResult
        fields = ["file"]


class CreateAssignmentForm(ModelForm):
    title = forms.CharField(label=_("Assignment title"), widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Title"}))
    description = forms.CharField(label=_("Assignment description"), widget=forms.Textarea(attrs={"rows": 3, "class": "form-control", "placeholder": "Description"}))
    due_date = forms.DateTimeField(label=_("Assignment due date"), widget=forms.TextInput(attrs={"class": "form-control", "type": 'datetime-local'}))

    class Meta:
        model = Assignment
        fields = ["title", "description", "due_date"]


class GradeAssignmentForm(ModelForm):
    assignment_result_id = forms.IntegerField(widget=forms.HiddenInput())
    grade = forms.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        model = AssignmentResult
        fields = ["grade"]