from django.contrib.auth.models import AbstractUser
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

from djangoProject import settings


class User(AbstractUser):
    profile_image = models.FileField(upload_to="profile_images", blank=True, null=True)
    is_teacher = models.BooleanField(default=False)

    def __str__(self):
        return self.first_name + " " + self.last_name


class Assignment(models.Model):
    title = models.CharField(max_length=100, blank=False, null=False)
    description = models.CharField(max_length=500)
    due_date = models.DateTimeField()

    def __str__(self):
        return self.title


class AssignmentResult(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    submission_date = models.DateTimeField()
    file = models.FileField(upload_to="assignments", null=True)
    grade = models.FloatField(default=0, validators=[MinValueValidator(0.0), MaxValueValidator(100.0)])

    def __str__(self):
        return f"{self.user.username} submission for '{self.assignment.title}'"

    def get_letter_grade(self):
        if 90 <= self.grade <= 100:
            return "A+"
        elif 85 <= self.grade < 90:
            return "A"
        elif 80 <= self.grade < 85:
            return "A-"
        elif 75 <= self.grade < 80:
            return "B+"
        elif 70 <= self.grade < 75:
            return "B"
        elif 65 <= self.grade < 70:
            return "B-"
        elif 60 <= self.grade < 65:
            return "C+"
        elif 55 <= self.grade < 60:
            return "C"
        elif 50 <= self.grade < 55:
            return "C-"
        elif 40 <= self.grade < 50:
            return "D"
        elif 0 <= self.grade < 40:
            return "E"
        else:
            return "Invalid percentage"


class AssignmentResultViewQuerySet(models.QuerySet):
    def get_by_custom_fields(self, assignment_id, assignment_result_id):
        return self.filter(
            assignment_id=assignment_id,
            assignment_result_id=assignment_result_id
        )

    def get_unique_results(self):
        return self.distinct()


class AssignmentResultView(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    assignment_id = models.IntegerField()
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    due_date = models.DateTimeField()
    assignment_result_id = models.IntegerField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    submission_date = models.DateTimeField()
    file = models.FileField(upload_to="assignments", blank=True, null=True)
    grade = models.FloatField()

    class Meta:
        managed = False  # No migrations will be created for this model
        db_table = 'assignment_result_view'  # Name of the database view

    objects = AssignmentResultViewQuerySet.as_manager()

    def get_letter_grade(self):
        if 90 <= self.grade <= 100:
            return "A+"
        elif 85 <= self.grade < 90:
            return "A"
        elif 80 <= self.grade < 85:
            return "A-"
        elif 75 <= self.grade < 80:
            return "B+"
        elif 70 <= self.grade < 75:
            return "B"
        elif 65 <= self.grade < 70:
            return "B-"
        elif 60 <= self.grade < 65:
            return "C+"
        elif 55 <= self.grade < 60:
            return "C"
        elif 50 <= self.grade < 55:
            return "C-"
        elif 40 <= self.grade < 50:
            return "D"
        elif 0 <= self.grade < 40:
            return "E"
        else:
            return "Invalid percentage"

    def get_status(self):
        time_difference = self.submission_date - self.due_date
        total_seconds = abs(time_difference.total_seconds())
        days = total_seconds // (24 * 3600)
        total_seconds %= (24 * 3600)
        hours = total_seconds // 3600
        total_seconds %= 3600
        minutes = total_seconds // 60

        if self.submission_date < self.due_date:
            status = "early"
        else:
            status = "late"

        return f"Submitted for grading<br>{int(days)} days {int(hours)} hours {int(minutes)} minutes {status}"

    def get_status_color(self):
        if self.submission_date < self.due_date:
            return "green"
        else:
            return "red"
