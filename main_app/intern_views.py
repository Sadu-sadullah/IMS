import json
import math
from datetime import datetime

from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import (HttpResponseRedirect, get_object_or_404,
                              redirect, render)
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from .forms import *
from .models import *


def intern_home(request):
    intern = get_object_or_404(Intern, admin=request.user)
    total_task = Task.objects.filter(department=intern.department).count()
    total_attendance = AttendanceReport.objects.filter(intern=intern).count()
    total_present = AttendanceReport.objects.filter(intern=intern, status=True).count()
    if total_attendance == 0:  # Don't divide. DivisionByZero
        percent_absent = percent_present = 0
    else:
        percent_present = math.floor((total_present/total_attendance) * 100)
        percent_absent = math.ceil(100 - percent_present)
    task_name = []
    data_present = []
    data_absent = []
    tasks = Task.objects.filter(department=intern.department)
    for task in tasks:
        attendance = Attendance.objects.filter(task=task)
        present_count = AttendanceReport.objects.filter(
            attendance__in=attendance, status=True, intern=intern).count()
        absent_count = AttendanceReport.objects.filter(
            attendance__in=attendance, status=False, intern=intern).count()
        task_name.append(task.name)
        data_present.append(present_count)
        data_absent.append(absent_count)
    context = {
        'total_attendance': total_attendance,
        'percent_present': percent_present,
        'percent_absent': percent_absent,
        'total_task': total_task,
        'tasks': tasks,
        'data_present': data_present,
        'data_absent': data_absent,
        'data_name': task_name,
        'page_title': 'Intern Homepage'

    }
    return render(request, 'intern_template/home_content.html', context)


@ csrf_exempt
def intern_view_attendance(request):
    intern = get_object_or_404(Intern, admin=request.user)
    if request.method != 'POST':
        department = get_object_or_404(Department, id=intern.department.id)
        context = {
            'tasks': Task.objects.filter(department=department),
            'page_title': 'View Attendance'
        }
        return render(request, 'intern_template/intern_view_attendance.html', context)
    else:
        task_id = request.POST.get('task')
        start = request.POST.get('start_date')
        end = request.POST.get('end_date')
        try:
            task = get_object_or_404(Task, id=task_id)
            start_date = datetime.strptime(start, "%Y-%m-%d")
            end_date = datetime.strptime(end, "%Y-%m-%d")
            attendance = Attendance.objects.filter(
                date__range=(start_date, end_date), task=task)
            attendance_reports = AttendanceReport.objects.filter(
                attendance__in=attendance, intern=intern)
            json_data = []
            for report in attendance_reports:
                data = {
                    "date":  str(report.attendance.date),
                    "status": report.status
                }
                json_data.append(data)
            return JsonResponse(json.dumps(json_data), safe=False)
        except Exception as e:
            return None


def intern_apply_leave(request):
    form = LeaveReportInternForm(request.POST or None)
    intern = get_object_or_404(Intern, admin_id=request.user.id)
    context = {
        'form': form,
        'leave_history': LeaveReportIntern.objects.filter(intern=intern),
        'page_title': 'Apply for leave'
    }
    if request.method == 'POST':
        if form.is_valid():
            try:
                obj = form.save(commit=False)
                obj.intern = intern
                obj.save()
                messages.success(
                    request, "Application for leave has been submitted for review")
                return redirect(reverse('intern_apply_leave'))
            except Exception:
                messages.error(request, "Could not submit")
        else:
            messages.error(request, "Form has errors!")
    return render(request, "intern_template/intern_apply_leave.html", context)


def intern_feedback(request):
    form = FeedbackInternForm(request.POST or None)
    intern = get_object_or_404(Intern, admin_id=request.user.id)
    context = {
        'form': form,
        'feedbacks': FeedbackIntern.objects.filter(intern=intern),
        'page_title': 'Intern Feedback'

    }
    if request.method == 'POST':
        if form.is_valid():
            try:
                obj = form.save(commit=False)
                obj.intern = intern
                obj.save()
                messages.success(
                    request, "Feedback submitted for review")
                return redirect(reverse('intern_feedback'))
            except Exception:
                messages.error(request, "Could not Submit!")
        else:
            messages.error(request, "Form has errors!")
    return render(request, "intern_template/intern_feedback.html", context)


def intern_view_profile(request):
    intern = get_object_or_404(Intern, admin=request.user)
    form = InternEditForm(request.POST or None, request.FILES or None,
                           instance=intern)
    context = {'form': form,
               'page_title': 'View/Edit Profile'
               }
    if request.method == 'POST':
        try:
            if form.is_valid():
                first_name = form.cleaned_data.get('first_name')
                last_name = form.cleaned_data.get('last_name')
                password = form.cleaned_data.get('password') or None
                address = form.cleaned_data.get('address')
                gender = form.cleaned_data.get('gender')
                passport = request.FILES.get('profile_pic') or None
                admin = intern.admin
                if password != None:
                    admin.set_password(password)
                if passport != None:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    admin.profile_pic = passport_url
                admin.first_name = first_name
                admin.last_name = last_name
                admin.address = address
                admin.gender = gender
                admin.save()
                intern.save()
                messages.success(request, "Profile Updated!")
                return redirect(reverse('intern_view_profile'))
            else:
                messages.error(request, "Invalid Data Provided")
        except Exception as e:
            messages.error(request, "Error Occured While Updating Profile " + str(e))

    return render(request, "intern_template/intern_view_profile.html", context)


@csrf_exempt
def intern_fcmtoken(request):
    token = request.POST.get('token')
    intern_user = get_object_or_404(CustomUser, id=request.user.id)
    try:
        intern_user.fcm_token = token
        intern_user.save()
        return HttpResponse("True")
    except Exception as e:
        return HttpResponse("False")


def intern_view_notification(request):
    intern = get_object_or_404(Intern, admin=request.user)
    notifications = NotificationIntern.objects.filter(intern=intern)
    context = {
        'notifications': notifications,
        'page_title': "View Notifications"
    }
    return render(request, "intern_template/intern_view_notification.html", context)


def intern_view_result(request):
    intern = get_object_or_404(Intern, admin=request.user)
    results = InternResult.objects.filter(intern=intern)
    context = {
        'results': results,
        'page_title': "View Results"
    }
    return render(request, "intern_template/intern_view_result.html", context)

@login_required
def view_task(request):
    # Get the logged-in user (intern)
    logged_in_user = request.user

    try:
        intern_object = Intern.objects.get(admin__email=logged_in_user.email)
    except Intern.DoesNotExist:
        messages.error(request, "Error Intern could not be found ")

    if intern_object:
        intern_id = intern_object.id
        # Filter tasks assigned to the logged-in user (assuming 'intern' is a foreign key field)
        tasks = Task.objects.filter(intern=intern_id)  # Filter by logged-in user's intern field

    context = {
        'tasks': tasks,
        'page_title': 'View Tasks',
    }
    return render(request, "intern_template/intern_view_task.html", context)

def update_tasks(request, task_id):
    if request.method == 'POST':
        form = TaskUpdateForm(request.POST)
        if form.is_valid():
            task = Task.objects.get(pk=task_id)  # Retrieve the existing task object
            task.completed = form.cleaned_data['completed']
            task.intern_feedback = form.cleaned_data['intern_feedback']
            task.save()  # Save the updated object (required after modifying attributes)
            messages.success(request, "Task Updated")
            return redirect('intern_view_task')
    else:
        try:
            task = Task.objects.get(pk=task_id)
        except Task.DoesNotExist:
            messages.error(request, "Task not found")
            task = None
        form = TaskUpdateForm(instance=task)  # Pre-populate form with task data (if available)

    context = {'task': task, 'form': form}
    return render(request, 'intern_template/intern_update_task.html', context)
