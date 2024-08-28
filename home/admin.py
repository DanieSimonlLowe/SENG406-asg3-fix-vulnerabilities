from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from django import forms

from home.models import User, Assignment, AssignmentResult

# Register your models here.
admin.site.register(User)
admin.site.register(Assignment)
admin.site.register(AssignmentResult)


class CustomUserChangeForm(UserChangeForm):
    def clean(self):
        cleaned_data = super().clean()
        user_permissions = set(cleaned_data.get("user_permissions"))
        is_superuser = cleaned_data.get('is_superuser')

        if self.instance.pk:
            admin_user = self.request.user
            admin_permissions = set(admin_user.get_all_permissions())

            if not admin_user.is_superuser:
                if not user_permissions.issubset(admin_permissions) or is_superuser:
                    raise forms.ValidationError("You can only assign permissions that you have.")

                original_permissions = set(self.instance.get_all_permissions())
                if not original_permissions.issubset(admin_permissions) or self.instance.is_superuser:
                    raise forms.ValidationError("You can only modify users with a subset of your permissions.")

        return cleaned_data


class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm

    def has_change_permission(self, request, obj=None):
        if not obj:
            return True
        admin_user = request.user
        if admin_user.is_superuser:
            return True
        admin_permissions = set(admin_user.get_all_permissions())
        user_permissions = set(obj.get_all_permissions())

        return user_permissions.issubset(admin_permissions)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.request = request
        return form


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
