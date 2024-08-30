import logging
import urllib.request
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from django.db import connection
from django.db.models import Q
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone

from django.contrib.auth import authenticate, login, logout, update_session_auth_hash

from django.http import Http404, FileResponse, HttpResponseForbidden, JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.dateparse import parse_datetime

from home.forms import LoginForm, RegistrationForm, AssignmentFileForm, CreateAssignmentForm, UpdateUserProfileForm, \
    GradeAssignmentForm, UpdatePasswordForm
from home.models import User, Assignment, AssignmentResult, AssignmentResultView

logger = logging.getLogger(__name__)


@login_required(login_url='/accounts/login_user')
def index(request):
    return redirect("/assignments/")


def register_user(request):
    logger.info("Registering new user")
    message = None
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if user_does_not_exist(form) and form.is_valid():
            user = form.save(commit=False)
            user.is_teacher = False
            user.save()
            login(request, user)
            return redirect("/")
        else:
            message = "Error(s) in form"
    else:
        form = RegistrationForm()
    return render(request, 'pages/auth-signup.html', context={'form': form, 'message': message})


def login_user(request):
    message = None
    if request.method == "POST":
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            if user is not None:
                login(request, user)
                return redirect('/')
            else:
                message = "Login failed: Username or password incorrect"
        else:
            message = "Error(s) in form"

    else:
        logger.info("Getting login page")
        form = LoginForm()

    return render(request, 'pages/auth-signin.html', context={'form': form, 'message': message})


def user_does_not_exist(form):
    input_username = form.data["username"]
    result = User.objects.filter(username=input_username).count()
    if result > 0:
        form.add_error("username", "Username already in use.")
    return result == 0


@login_required(login_url='/accounts/login_user')
def assignments(request):
    logger.info("Getting assignments")
    if request.user.is_teacher:
        assignment_list = Assignment.objects.all()
        return render(request, 'pages/assignment_list_teacher.html', context={'assignments': assignment_list})
    else:
        search_term = request.GET.get('search', '')
        if search_term.strip() != "":
            with connection.cursor() as cursor:
                query = f"""SELECT *
                FROM assignment_result_view
                WHERE title LIKE '%{search_term.strip()}%' AND (user_id = {request.user.id} OR user_id = -1)
                """
                cursor.execute(query)
                rows = cursor.fetchall()
                columns = [col[0] for col in cursor.description]
                assignment_results = []
                for row in rows:
                    row_dict = dict(zip(columns, row))
                    if 'submission_date' in row_dict:
                        row_dict['submission_date'] = parse_datetime(row_dict['submission_date'])
                    instance = AssignmentResultView(**row_dict)
                    assignment_results.append(instance)
            ids_to_remove = [x.assignment_id for x in assignment_results if x.assignment_result_id != -1]
            assignment_results = [x for x in assignment_results if x.assignment_id not in ids_to_remove or (x.assignment_id in ids_to_remove and x.assignment_result_id != -1)]
        else:
            submissions = AssignmentResultView.objects.filter(Q(user_id=request.user.id))
            excluded_ids = [x.assignment_id for x in submissions]
            others = AssignmentResultView.objects.filter(~Q(assignment_id__in=excluded_ids) & Q(user_id=-1))
            assignment_results = submissions.union(others)

        print(assignment_results)
        return render(request, 'pages/assignment_results_student.html',
                      context={'assignments': assignment_results, 'current_user': request.user, "search_query": search_term })


@login_required(login_url='/accounts/login_user')
def view_profile(request):
    logger.info("Viewing profile")
    user_profile = User.objects.get(username=request.user.username)
    return render(request, 'pages/profile.html', context={'user': user_profile})


@login_required(login_url='/accounts/login_user')
def update_profile(request):
    logger.info("Attempting to update profile")
    if request.method == "POST":
        form = UpdateUserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("view_profile")
    else:
        form = UpdateUserProfileForm(instance=request.user)
    return render(request, 'pages/update_profile.html', context={'form': form})


@login_required(login_url='/accounts/login_user')
def update_password(request):
    logger.info("Attempting to update password")
    message = None
    form = UpdatePasswordForm(request.POST, instance=request.user)
    if form.is_valid():
        try:
            password_validation.validate_password(form.cleaned_data['password'])
            if form.cleaned_data['password'] == form.cleaned_data['confirm_password']:
                user = form.save(commit=False)
                user.password = make_password(form.cleaned_data['password'])
                user.save()
                update_session_auth_hash(request, user)
                return redirect('view_profile')
            else:
                form.add_error('confirm_password', 'Passwords do not match')
        except ValidationError as e:
            form.add_error('password', e)

    else:
        message = 'Error(s) in form'
    return render(request, 'pages/update_password.html', context={'form': form, 'message': message})


def assignment_results_list(request, assignment_id):
    if getattr(request.user, 'is_teacher', True):
        logger.info("Getting assignment results list")
        assignment_results = get_object_or_404(Assignment, pk=assignment_id)
        data = list(assignment_results.assignmentresult_set.all().values('grade'))
        return render(request, 'pages/assignment_results_list.html',
                      context={'assignment': assignment_results, 'data': data})
    else:
        return HttpResponseForbidden('<h1>403 Forbidden</h1>')


@login_required(login_url='/accounts/login_user')
def download_assignment_file(request, assignment_id, assignment_result_id):
    logger.info("Downloading assignment")
    assignment = get_object_or_404(AssignmentResult, pk=assignment_result_id)
    file_path = assignment.file.path
    try:
        return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=assignment.file.name)
    except FileNotFoundError:
        raise Http404("File not found")


@login_required(login_url='/accounts/login_user')
def assignment_submission(request, assignment_id):
    logger.info("Submitting assignment")
    assignment = get_object_or_404(Assignment, pk=assignment_id)
    if not request.user.is_teacher:
        message = None
        if request.method == 'POST':
            form = AssignmentFileForm(request.POST, request.FILES)
            if form.is_valid():
                assignment_result = form.save(commit=False)
                assignment_result.assignment = assignment
                assignment_result.user = request.user
                assignment_result.submission_date = timezone.now()
                assignment_result.save()
                return redirect(reverse('assignments'))
            else:
                message = "Invalid submission"
        else:
            form = AssignmentFileForm()

        return render(request, 'pages/assignment_submission.html',
                      context={'form': form, 'assignment': assignment, "message": message})
    else:
        return render(request, 'pages/assignment_submission_no_submit.html', context={"assignment": assignment})


@login_required(login_url='/accounts/login_user')
def assignment_create(request):
    logger.info("Creating assignment")
    if request.user.is_teacher:
        message = None
        if request.method == "POST":
            form = CreateAssignmentForm(request.POST)
            if form.is_valid():
                created_assignment = form.save(commit=False)
                # any other values that need to be saved?
                created_assignment.save()
                return redirect(reverse('assignments'))
            else:
                message = "Error(s) in form"
        else:
            form = CreateAssignmentForm()
        return render(request, 'pages/assignment_create.html', context={'form': form, 'message': message})
    else:
        return HttpResponseForbidden('<h1>403 Forbidden</h1>')


@login_required(login_url='/accounts/login_user')
def logout_user(request):
    logger.info("Logging out")
    logout(request)
    return redirect("/accounts/login_user")


@login_required(login_url='/accounts/login_user')
def assignments_grade(request):
    logger.info("Grading assignments")
    if request.user.is_teacher:
        if request.method == "POST":
            form = GradeAssignmentForm(request.POST)
            if form.is_valid():
                try:
                    assignment_result_id = form.cleaned_data['assignment_result_id']
                    grade = form.cleaned_data['grade']
                    assignment_result = get_object_or_404(AssignmentResult, pk=assignment_result_id)
                    assignment_result.grade = grade
                    assignment_result.save()
                    context = {'assignment_result': assignment_result, 'assignment': assignment_result.assignment}
                    row_html = render_to_string('partials/assignment_result_row.html', context, request=request)
                    return JsonResponse({'success': True, 'row_html': row_html})
                except Exception as e:
                    print(f"Error in submit_grade: {e}")
                    return JsonResponse({'success': False, 'error': str(e)}, status=500)
        else:
            return JsonResponse({'success': False})
    else:
        return HttpResponseForbidden('<h1>403 Forbidden</h1>')


@login_required(login_url='/accounts/login_user')
def morale(request):
    logger.info("Boosting morale")
    if request.method == "GET":
        return render(request, "pages/morale.html")
    else:
        try:
            with urllib.request.urlopen(request.POST['api_url']) as f:
                file_content = f.read().decode()
                return HttpResponse(file_content)
        except Exception:
            logger.exception("Can't load " + request.POST['api_url'])
            return render(request, "pages/morale.html")
