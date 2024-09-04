from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from django import forms
from django.contrib.auth.models import Permission

from home.models import User, Assignment, AssignmentResult

# Register your models here.
admin.site.register(User)
admin.site.register(Assignment)
admin.site.register(AssignmentResult)


def get_permissions(user):
    individual_permissions = set(user.user_permissions.all())
    group_permissions = set(Permission.objects.filter(group__user=user))
    all_permissions = individual_permissions.union(group_permissions)
    return all_permissions


class CustomUserChangeForm(UserChangeForm):
    def clean(self):
        cleaned_data = super().clean()
        user_permissions = set(cleaned_data.get("user_permissions"))
        is_superuser = cleaned_data.get('is_superuser')

        if self.instance.pk:
            admin_user = self.request.user
            admin_permissions = get_permissions(admin_user)

            if not admin_user.is_superuser:
                if not user_permissions.issubset(admin_permissions) or is_superuser:
                    raise forms.ValidationError("You can only assign permissions that you have.")

                original_permissions = get_permissions(self.instance)
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
        admin_permissions = get_permissions(admin_user)
        user_permissions = get_permissions(obj)

        return user_permissions.issubset(admin_permissions)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.request = request
        return form

    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('is_teacher',)}),
    )


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
