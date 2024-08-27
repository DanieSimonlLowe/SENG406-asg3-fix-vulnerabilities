from django.conf.urls.static import static
from django.urls import path
from djangoProject import settings as SETTINGS

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('accounts/register_user/', views.register_user, name='register_user'),
    path('accounts/login_user/', views.login_user, name='login_user'),
    path('accounts/logout_user/', views.logout_user, name='logout_user'),
    path('accounts/profile/', views.view_profile, name='view_profile'),
    path('accounts/profile/update/', views.update_profile, name='update_profile'),
    path('accounts/profile/update_password/', views.update_password, name='update_password'),
    path('assignments/', views.assignments, name='assignments'),
    path('assignments/<int:assignment_id>/results/', views.assignment_results_list, name='assignment_results'),
    path('assignments/<int:assignment_id>/download/<int:assignment_result_id>', views.download_assignment_file, name='download_assignment_result_file'),
    path('assignments/<int:assignment_id>/submission/', views.assignment_submission, name='assignment_submission'),
    path('assignments/create/', views.assignment_create, name='assignment_create'),
    path('assignments/grade/', views.assignments_grade, name='assignments_grade'),
    path('morale/', views.morale, name='morale'),
]

urlpatterns += static(SETTINGS.MEDIA_URL, document_root=SETTINGS.MEDIA_ROOT)
