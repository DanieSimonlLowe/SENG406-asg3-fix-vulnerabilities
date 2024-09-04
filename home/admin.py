from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from django import forms
from django.contrib.auth.models import Permission, Group

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


class CustomGroupAdmin(admin.ModelAdmin):

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if not request.user.is_superuser:
            # Get the IDs of permissions the user has
            user_permission_ids = {perm.id for perm in get_permissions(request.user)}
            # Get the IDs of groups that have permissions that are a subset of the user's permissions
            allowed_group_ids = [
                group.id for group in queryset
                if set(group.permissions.values_list('id', flat=True)).issubset(set(user_permission_ids))
            ]
            queryset = queryset.filter(id__in=allowed_group_ids)
        return queryset

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not request.user.is_superuser:
            # Limit permissions to the user's own permissions
            user_permissions = {perm.id for perm in get_permissions(request.user)}
            form.base_fields['permissions'].queryset = Permission.objects.filter(id__in=user_permissions)
        return form


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

admin.site.unregister(Group)
admin.site.register(Group, CustomGroupAdmin)
