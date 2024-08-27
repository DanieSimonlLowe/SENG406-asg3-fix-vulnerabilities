from django.contrib import admin
from home.models import User, Assignment, AssignmentResult


# Register your models here.
admin.site.register(User)
admin.site.register(Assignment)
admin.site.register(AssignmentResult)

