import json

from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import (HttpResponseRedirect, get_object_or_404,redirect, render)
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q

from .forms import *
from .models import *


def staff_home(request):
    staff = get_object_or_404(Staff, admin=request.user)
    total_interns = Intern.objects.filter(department=staff.department).count()
    total_leave = LeaveReportStaff.objects.filter(staff=staff).count()

    # Filter tasks assigned to interns in the staff's department
    tasks = Task.objects.filter(intern__department=staff.department)
    total_task = tasks.count()

    # Calculate total attendance (assuming a model named Attendance with a foreign key to Task)
    attendance_list = Attendance.objects.filter(task__in=tasks)
    total_attendance = attendance_list.count()

    # Existing logic to create separate lists for task names and attendance counts (might not be required for the bar chart)
    attendance_list = []
    task_list = []
    for task in tasks:
        attendance_count = Attendance.objects.filter(task=task).count()
        task_list.append(task.name)
        attendance_list.append(attendance_count)

    # Data for bar chart (assuming Intern model has a foreign key relationship with Task)
    intern_list = list(tasks.values_list('intern__admin__first_name', flat=True).distinct())  # Get unique intern names
    intern_list_json = json.dumps(intern_list)
    # completed_task_count_list = list(tasks.filter(completed=True).values('intern').annotate(count=Count('id')).order_by('intern').values_list('count', flat=True))
    # completed_task_count_list_json = json.dumps(completed_task_count_list)

    total_task_per_intern = list(tasks.values('intern__admin__first_name').annotate(count=Count('id')).order_by('intern__admin__first_name').values_list('count', flat=True))
    total_task_per_intern_json = json.dumps(total_task_per_intern)

    task_counts_per_intern = list(tasks.values('intern__admin__first_name').annotate(total_tasks=Count('id'), completed_tasks=Count('id', filter=Q(completed=True))).order_by('intern__admin__first_name'))

    completed_task_count_list = list(tasks.values('intern__admin__first_name').annotate(count=Count('id', filter=Q(completed=True))).order_by('intern__admin__first_name').values_list('count', flat=True))

    completed_task_count_list_json = json.dumps(completed_task_count_list)

    context = {
        'page_title': 'Staff Panel - ' + str(staff.admin.last_name) + ' (' + str(staff.department) + ')',
        'total_interns': total_interns,
        'total_attendance': total_attendance,
        'total_leave': total_leave,
        'total_task': total_task,
        'task_list': task_list,  # Might not be required for this chart
        'attendance_list': attendance_list,  # Might not be required for this chart
        'intern_list_json': intern_list_json,
        'completed_task_count_list': completed_task_count_list,
        'total_task_per_intern_json': total_task_per_intern_json,
    }
    return render(request, 'staff_template/home_content.html', context)


def staff_take_attendance(request):
    staff = get_object_or_404(Staff, admin=request.user)
    tasks = Task.objects.all()
    shifts = Shift.objects.all()
    context = {
        'tasks': tasks,
        'shifts': shifts,
        'page_title': 'Take Attendance'
    }

    return render(request, 'staff_template/staff_take_attendance.html', context)


@csrf_exempt
def get_interns(request):
    task_id = request.POST.get('task')
    shift_id = request.POST.get('shift')
    try:
        task = get_object_or_404(Task, id=task_id)
        shift = get_object_or_404(Shift, id=shift_id)
        interns = Intern.objects.filter(
            department_id=task.department.id, shift=shift)
        intern_data = []
        for intern in interns:
            data = {
                    "id": intern.id,
                    "name": intern.admin.last_name + " " + intern.admin.first_name
                    }
            intern_data.append(data)
        return JsonResponse(json.dumps(intern_data), content_type='application/json', safe=False)
    except Exception as e:
        return e


@csrf_exempt
def save_attendance(request):
    intern_data = request.POST.get('intern_ids')
    date = request.POST.get('date')
    task_id = request.POST.get('task')
    shift_id = request.POST.get('shift')
    interns = json.loads(intern_data)
    try:
        shift = get_object_or_404(Shift, id=shift_id)
        task = get_object_or_404(Task, id=task_id)
        attendance = Attendance(shift=shift, task=task, date=date)
        attendance.save()

        for intern_dict in interns:
            intern = get_object_or_404(Intern, id=intern_dict.get('id'))
            attendance_report = AttendanceReport(intern=intern, attendance=attendance, status=intern_dict.get('status'))
            attendance_report.save()
    except Exception as e:
        return None

    return HttpResponse("OK")


def staff_update_attendance(request):
    staff = get_object_or_404(Staff, admin=request.user)
    tasks = Task.objects.all()
    shifts = Shift.objects.all()
    context = {
        'tasks': tasks,
        'shifts': shifts,
        'page_title': 'Update Attendance'
    }

    return render(request, 'staff_template/staff_update_attendance.html', context)


@csrf_exempt
def get_intern_attendance(request):
    attendance_date_id = request.POST.get('attendance_date_id')
    try:
        date = get_object_or_404(Attendance, id=attendance_date_id)
        attendance_data = AttendanceReport.objects.filter(attendance=date)
        intern_data = []
        for attendance in attendance_data:
            data = {"id": attendance.intern.admin.id,
                    "name": attendance.intern.admin.last_name + " " + attendance.intern.admin.first_name,
                    "status": attendance.status}
            intern_data.append(data)
        return JsonResponse(json.dumps(intern_data), content_type='application/json', safe=False)
    except Exception as e:
        return e


@csrf_exempt
def update_attendance(request):
    intern_data = request.POST.get('intern_ids')
    date = request.POST.get('date')
    interns = json.loads(intern_data)
    try:
        attendance = get_object_or_404(Attendance, id=date)

        for intern_dict in interns:
            intern = get_object_or_404(
                Intern, admin_id=intern_dict.get('id'))
            attendance_report = get_object_or_404(AttendanceReport, intern=intern, attendance=attendance)
            attendance_report.status = intern_dict.get('status')
            attendance_report.save()
    except Exception as e:
        return None

    return HttpResponse("OK")


def staff_apply_leave(request):
    form = LeaveReportStaffForm(request.POST or None)
    staff = get_object_or_404(Staff, admin_id=request.user.id)
    context = {
        'form': form,
        'leave_history': LeaveReportStaff.objects.filter(staff=staff),
        'page_title': 'Apply for Leave'
    }
    if request.method == 'POST':
        if form.is_valid():
            try:
                obj = form.save(commit=False)
                obj.staff = staff
                obj.save()
                messages.success(
                    request, "Application for leave has been submitted for review")
                return redirect(reverse('staff_apply_leave'))
            except Exception:
                messages.error(request, "Could not apply!")
        else:
            messages.error(request, "Form has errors!")
    return render(request, "staff_template/staff_apply_leave.html", context)


def staff_feedback(request):
    form = FeedbackStaffForm(request.POST or None)
    staff = get_object_or_404(Staff, admin_id=request.user.id)
    context = {
        'form': form,
        'feedbacks': FeedbackStaff.objects.filter(staff=staff),
        'page_title': 'Add Feedback'
    }
    if request.method == 'POST':
        if form.is_valid():
            try:
                obj = form.save(commit=False)
                obj.staff = staff
                obj.save()
                messages.success(request, "Feedback submitted for review")
                return redirect(reverse('staff_feedback'))
            except Exception:
                messages.error(request, "Could not Submit!")
        else:
            messages.error(request, "Form has errors!")
    return render(request, "staff_template/staff_feedback.html", context)


def staff_view_profile(request):
    staff = get_object_or_404(Staff, admin=request.user)
    form = StaffEditForm(request.POST or None, request.FILES or None,instance=staff)
    context = {'form': form, 'page_title': 'View/Update Profile'}
    if request.method == 'POST':
        try:
            if form.is_valid():
                first_name = form.cleaned_data.get('first_name')
                last_name = form.cleaned_data.get('last_name')
                password = form.cleaned_data.get('password') or None
                address = form.cleaned_data.get('address')
                gender = form.cleaned_data.get('gender')
                passport = request.FILES.get('profile_pic') or None
                admin = staff.admin
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
                staff.save()
                messages.success(request, "Profile Updated!")
                return redirect(reverse('staff_view_profile'))
            else:
                messages.error(request, "Invalid Data Provided")
                return render(request, "staff_template/staff_view_profile.html", context)
        except Exception as e:
            messages.error(
                request, "Error Occured While Updating Profile " + str(e))
            return render(request, "staff_template/staff_view_profile.html", context)

    return render(request, "staff_template/staff_view_profile.html", context)


@csrf_exempt
def staff_fcmtoken(request):
    token = request.POST.get('token')
    try:
        staff_user = get_object_or_404(CustomUser, id=request.user.id)
        staff_user.fcm_token = token
        staff_user.save()
        return HttpResponse("True")
    except Exception as e:
        return HttpResponse("False")


def staff_view_notification(request):
    staff = get_object_or_404(Staff, admin=request.user)
    notifications = NotificationStaff.objects.filter(staff=staff)
    context = {
        'notifications': notifications,
        'page_title': "View Notifications"
    }
    return render(request, "staff_template/staff_view_notification.html", context)


def staff_add_result(request):
    staff = get_object_or_404(Staff, admin=request.user)
    tasks = Task.objects.all()
    shifts = Shift.objects.all()
    context = {
        'page_title': 'Result Upload',
        'tasks': tasks,
        'shifts': shifts
    }
    if request.method == 'POST':
        try:
            intern_id = request.POST.get('intern_list')
            task_id = request.POST.get('task')
            test = request.POST.get('test')
            exam = request.POST.get('exam')
            intern = get_object_or_404(Intern, id=intern_id)
            task = get_object_or_404(Task, id=task_id)
            try:
                data = InternResult.objects.get(
                    intern=intern, task=task)
                data.exam = exam
                data.test = test
                data.save()
                messages.success(request, "Scores Updated")
            except:
                result = InternResult(intern=intern, task=task, test=test, exam=exam)
                result.save()
                messages.success(request, "Scores Saved")
        except Exception as e:
            messages.warning(request, "Error Occured While Processing Form")
    return render(request, "staff_template/staff_add_result.html", context)


@csrf_exempt
def fetch_intern_result(request):
    try:
        task_id = request.POST.get('task')
        intern_id = request.POST.get('intern')
        intern = get_object_or_404(Intern, id=intern_id)
        task = get_object_or_404(Task, id=task_id)
        result = InternResult.objects.get(intern=intern, task=task)
        result_data = {
            'exam': result.exam,
            'test': result.test
        }
        return HttpResponse(json.dumps(result_data))
    except Exception as e:
        return HttpResponse('False')

@login_required
def staff_add_task(request):
    form = StaffTaskForm(request.POST or None, user=request.user)
    context = {
        'form': form,
        'page_title': 'Add Task'
    }
    if request.method == 'POST':
        if form.is_valid():
            name = form.cleaned_data.get('name')
            department_name = form.cleaned_data.get('department')
            try:
                department = Department.objects.get(name=department_name)
            except Department.DoesNotExist:
                messages.error(request, f"Department '{department_name}' not found!")
                return redirect(reverse('add_task'))
            description = form.cleaned_data.get('description')
            intern = form.cleaned_data.get('intern')  # No change here

            try:
                task = Task()
                task.name = name
                task.department = department
                task.description = description
                task.intern = intern
                task.save()
                messages.success(request, "Successfully Added")
                return redirect(reverse('staff_manage_task'))

            except Exception as e:
                messages.error(request, "Could Not Add " + str(e))
        else:
            messages.error(request, "Fill Form Properly")

    return render(request, 'staff_template/staff_add_task_template.html', context)

def staff_edit_task(request, task_id):
    instance = get_object_or_404(Task, id=task_id)
    form = EditTaskForm(request.POST or None, instance=instance)
    context = {
        'form': form,
        'task_id': task_id,
        'page_title': 'Edit Task'
    }
    if request.method == 'POST':
        if form.is_valid():
            form.save()  # Save directly as instance is already provided
            messages.success(request, "Successfully Updated")
            return redirect(reverse('staff_edit_task', args=[task_id]))
        else:
            messages.error(request, "Fill Form Properly")
    return render(request, 'staff_template/staff_edit_task_template.html', context)

def staff_manage_task(request):
    current_user= request.user
    interns = Intern.objects.filter(staff__admin=current_user)
    tasks = Task.objects.filter(intern__in=interns)
    context = {
        'tasks': tasks,
        'page_title': 'Manage Tasks'
    }
    return render(request, "staff_template/staff_manage_task.html", context)

def staff_delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.delete()
    messages.success(request, "Task deleted successfully!")
    return redirect(reverse('staff_manage_task'))