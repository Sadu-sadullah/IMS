import json
import requests
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import (HttpResponse, HttpResponseRedirect,
                              get_object_or_404, redirect, render)
from django.templatetags.static import static
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import UpdateView
from django.db.models import Count, Q

from .forms import *
from .models import *


def admin_home(request):
    total_staff = Staff.objects.all().count()
    total_interns = Intern.objects.all().count()
    tasks = Task.objects.all()
    total_task = tasks.count()
    total_department = Department.objects.all().count()
    attendance_list = Attendance.objects.filter(task__in=tasks)
    total_attendance = attendance_list.count()
    attendance_list = []
    task_list = []
    for task in tasks:
        attendance_count = Attendance.objects.filter(task=task).count()
        task_list.append(task.name[:7])
        attendance_list.append(attendance_count)

    # Total Tasks and interns in Each Department
    department_all = Department.objects.all()
    department_name_list = []
    task_count_list = []
    intern_count_list_in_department = []

    for department in department_all:
        tasks = Task.objects.filter(department_id=department.id).count()
        interns = Intern.objects.filter(department_id=department.id).count()
        department_name_list.append(department.name)
        task_count_list.append(tasks)
        intern_count_list_in_department.append(interns)
    
    task_all = Task.objects.all()
    task_list = []
    intern_count_list_in_task = []
    for task in task_all:
        department = Department.objects.get(id=task.department.id)
        intern_count = Intern.objects.filter(department_id=department.id).count()
        task_list.append(task.name)
        intern_count_list_in_task.append(intern_count)


    # For Interns
    intern_attendance_present_list=[]
    intern_attendance_leave_list=[]
    intern_name_list=[]
    intern_task_count_list={}
    completed_task_count_list= {}

    interns = Intern.objects.all()
    for intern in interns:
        
        attendance = AttendanceReport.objects.filter(intern_id=intern.id, status=True).count()
        absent = AttendanceReport.objects.filter(intern_id=intern.id, status=False).count()
        leave = LeaveReportIntern.objects.filter(intern_id=intern.id, status=1).count()
        intern_attendance_present_list.append(attendance)
        intern_attendance_leave_list.append(leave+absent)
        intern_name_list.append(intern.admin.first_name)
        task_count = Task.objects.filter(intern=intern).count()
        intern_task_count_list[intern.id] = task_count
        completed_task_count_list[intern.id] = Task.objects.filter(intern=intern, completed=True).count()

    context = {
        'page_title': "Administrative Dashboard",
        'total_interns': total_interns,
        'total_staff': total_staff,
        'total_department': total_department,
        'total_task': total_task,
        'task_list': task_list,
        'attendance_list': attendance_list,
        'intern_attendance_present_list': intern_attendance_present_list,
        'intern_attendance_leave_list': intern_attendance_leave_list,
        "intern_name_list": intern_name_list,
        "intern_count_list_in_task": intern_count_list_in_task,
        "intern_count_list_in_department": intern_count_list_in_department,
        "department_name_list": department_name_list,
        "intern_task_count_list": intern_task_count_list,
        "completed_task_count_list": completed_task_count_list,

    }
    return render(request, 'hod_template/home_content.html', context)


def add_staff(request):
    form = StaffForm(request.POST or None, request.FILES or None)
    context = {'form': form, 'page_title': 'Add Staff'}
    if request.method == 'POST':
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            address = form.cleaned_data.get('address')
            email = form.cleaned_data.get('email')
            gender = form.cleaned_data.get('gender')
            password = form.cleaned_data.get('password')
            department = form.cleaned_data.get('department')
            passport = request.FILES.get('profile_pic')
            fs = FileSystemStorage()
            filename = fs.save(passport.name, passport)
            passport_url = fs.url(filename)
            try:
                user = CustomUser.objects.create_user(
                    email=email, password=password, user_type=2, first_name=first_name, last_name=last_name, profile_pic=passport_url)
                user.gender = gender
                user.address = address
                user.staff.department = department
                user.save()
                messages.success(request, "Successfully Added")
                return redirect(reverse('add_staff'))

            except Exception as e:
                messages.error(request, "Could Not Add " + str(e))
        else:
            messages.error(request, "Please fulfil all requirements")

    return render(request, 'hod_template/add_staff_template.html', context)


def add_intern(request):
    intern_form = InternForm(request.POST or None, request.FILES or None)
    context = {'form': intern_form, 'page_title': 'Add Intern'}
    if request.method == 'POST':
        if intern_form.is_valid():
            first_name = intern_form.cleaned_data.get('first_name')
            last_name = intern_form.cleaned_data.get('last_name')
            address = intern_form.cleaned_data.get('address')
            email = intern_form.cleaned_data.get('email')
            gender = intern_form.cleaned_data.get('gender')
            password = intern_form.cleaned_data.get('password')
            department = intern_form.cleaned_data.get('department')
            shift = intern_form.cleaned_data.get('shift')
            passport = request.FILES['profile_pic']
            fs = FileSystemStorage()
            filename = fs.save(passport.name, passport)
            passport_url = fs.url(filename)
            try:
                user = CustomUser.objects.create_user(
                    email=email, password=password, user_type=3, first_name=first_name, last_name=last_name, profile_pic=passport_url)
                user.gender = gender
                user.address = address
                user.intern.shift = shift
                user.intern.department = department
                user.save()
                messages.success(request, "Successfully Added")
                return redirect(reverse('add_intern'))
            except Exception as e:
                messages.error(request, "Could Not Add: " + str(e))
        else:
            messages.error(request, "Could Not Add: ")
    return render(request, 'hod_template/add_intern_template.html', context)


def add_department(request):
    form = DepartmentForm(request.POST or None)
    context = {
        'form': form,
        'page_title': 'Add Department'
    }
    if request.method == 'POST':
        if form.is_valid():
            name = form.cleaned_data.get('name')
            try:
                department = Department()
                department.name = name
                department.save()
                messages.success(request, "Successfully Added")
                return redirect(reverse('add_department'))
            except:
                messages.error(request, "Could Not Add")
        else:
            messages.error(request, "Could Not Add")
    return render(request, 'hod_template/add_department_template.html', context)


def add_task(request):
    form = TaskForm(request.POST or None)
    context = {
        'form': form,
        'page_title': 'Add Task'
    }
    if request.method == 'POST':
        if form.is_valid():
            task = form.save()  # Save directly as form is already validated
            messages.success(request, "Successfully Added")
            return redirect(reverse('add_task'))
        else:
            messages.error(request, "Fill Form Properly")

    return render(request, 'hod_template/add_task_template.html', context)


def manage_staff(request):
    allStaff = CustomUser.objects.filter(user_type=2)
    allIntern = Intern.objects.all()
    context = {
        'allStaff': allStaff,
        'allIntern': allIntern,
        'page_title': 'Manage Staff',
    }
    return render(request, "hod_template/manage_staff.html", context)

def manage_intern(request):
    interns = CustomUser.objects.filter(user_type=3)
    context = {
        'interns': interns,
        'page_title': 'Manage Interns'
    }
    return render(request, "hod_template/manage_intern.html", context)


def manage_department(request):
    departments = Department.objects.all()
    context = {
        'departments': departments,
        'page_title': 'Manage Departments'
    }
    return render(request, "hod_template/manage_department.html", context)


def manage_task(request):
    tasks = Task.objects.all()
    context = {
        'tasks': tasks,
        'page_title': 'Manage Tasks'
    }
    return render(request, "hod_template/manage_task.html", context)


def edit_staff(request, staff_id):
    staff = get_object_or_404(Staff, id=staff_id)
    form = StaffForm(request.POST or None, instance=staff)
    context = {
        'form': form,
        'staff_id': staff_id,
        'page_title': 'Edit Staff'
    }
    if request.method == 'POST':
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            address = form.cleaned_data.get('address')
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            gender = form.cleaned_data.get('gender')
            password = form.cleaned_data.get('password') or None
            department = form.cleaned_data.get('department')
            passport = request.FILES.get('profile_pic') or None
            try:
                user = CustomUser.objects.get(id=staff.admin.id)
                user.username = username
                user.email = email
                if password != None:
                    user.set_password(password)
                if passport != None:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    user.profile_pic = passport_url
                user.first_name = first_name
                user.last_name = last_name
                user.gender = gender
                user.address = address
                staff.department = department
                user.save()
                staff.save()
                messages.success(request, "Successfully Updated")
                return redirect(reverse('edit_staff', args=[staff_id]))
            except Exception as e:
                messages.error(request, "Could Not Update " + str(e))
        else:
            messages.error(request, "Please fil form properly")
    else:
        user = CustomUser.objects.get(id=staff_id)
        staff = Staff.objects.get(id=user.id)
        return render(request, "hod_template/edit_staff_template.html", context)


def edit_intern(request, intern_id):
    intern = get_object_or_404(Intern, id=intern_id)
    form = InternForm(request.POST or None, instance=intern)
    context = {
        'form': form,
        'intern_id': intern_id,
        'page_title': 'Edit Intern'
    }
    if request.method == 'POST':
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            address = form.cleaned_data.get('address')
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            gender = form.cleaned_data.get('gender')
            password = form.cleaned_data.get('password') or None
            department = form.cleaned_data.get('department')
            shift = form.cleaned_data.get('shift')
            passport = request.FILES.get('profile_pic') or None
            try:
                user = CustomUser.objects.get(id=intern.admin.id)
                if passport != None:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    user.profile_pic = passport_url
                user.username = username
                user.email = email
                if password != None:
                    user.set_password(password)
                user.first_name = first_name
                user.last_name = last_name
                intern.shift = shift
                user.gender = gender
                user.address = address
                intern.department = department
                user.save()
                intern.save()
                messages.success(request, "Successfully Updated")
                return redirect(reverse('edit_intern', args=[intern_id]))
            except Exception as e:
                messages.error(request, "Could Not Update " + str(e))
        else:
            messages.error(request, "Please Fill Form Properly!")
    else:
        return render(request, "hod_template/edit_intern_template.html", context)


def edit_department(request, department_id):
    instance = get_object_or_404(Department, id=department_id)
    form = DepartmentForm(request.POST or None, instance=instance)
    context = {
        'form': form,
        'department_id': department_id,
        'page_title': 'Edit Department'
    }
    if request.method == 'POST':
        if form.is_valid():
            name = form.cleaned_data.get('name')
            try:
                department = Department.objects.get(id=department_id)
                department.name = name
                department.save()
                messages.success(request, "Successfully Updated")
            except:
                messages.error(request, "Could Not Update")
        else:
            messages.error(request, "Could Not Update")

    return render(request, 'hod_template/edit_department_template.html', context)


def edit_task(request, task_id):
    instance = get_object_or_404(Task, id=task_id)
    form = TaskForm(request.POST or None, instance=instance)
    context = {
        'form': form,
        'task_id': task_id,
        'page_title': 'Edit Task'
    }
    if request.method == 'POST':
        if form.is_valid():
            name = form.cleaned_data.get('name')
            department = form.cleaned_data.get('department')
            try:
                task = Task.objects.get(id=task_id)
                task.name = name
                task.department = department
                task.save()
                messages.success(request, "Successfully Updated")
                return redirect(reverse('edit_task', args=[task_id]))
            except Exception as e:
                messages.error(request, "Could Not Add " + str(e))
        else:
            messages.error(request, "Fill Form Properly")
    return render(request, 'hod_template/edit_task_template.html', context)


def add_shift(request):
    form = ShiftForm(request.POST or None)
    context = {'form': form, 'page_title': 'Add Shift'}
    if request.method == 'POST':
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Shift Created")
                return redirect(reverse('add_shift'))
            except Exception as e:
                messages.error(request, 'Could Not Add ' + str(e))
        else:
            messages.error(request, 'Fill Form Properly ')
    return render(request, "hod_template/add_shift_template.html", context)


def manage_shift(request):
    shifts = Shift.objects.all()
    context = {'shifts': shifts, 'page_title': 'Manage Shifts'}
    return render(request, "hod_template/manage_shift.html", context)


def edit_shift(request, shift_id):
    instance = get_object_or_404(Shift, id=shift_id)
    form = ShiftForm(request.POST or None, instance=instance)
    context = {'form': form, 'shift_id': shift_id,
               'page_title': 'Edit Shift'}
    if request.method == 'POST':
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Shift Updated")
                return redirect(reverse('edit_shift', args=[shift_id]))
            except Exception as e:
                messages.error(
                    request, "Shift Could Not Be Updated " + str(e))
                return render(request, "hod_template/edit_shift_template.html", context)
        else:
            messages.error(request, "Invalid Form Submitted ")
            return render(request, "hod_template/edit_shift_template.html", context)

    else:
        return render(request, "hod_template/edit_shift_template.html", context)


@csrf_exempt
def check_email_availability(request):
    email = request.POST.get("email")
    try:
        user = CustomUser.objects.filter(email=email).exists()
        if user:
            return HttpResponse(True)
        return HttpResponse(False)
    except Exception as e:
        return HttpResponse(False)


@csrf_exempt
def intern_feedback_message(request):
    if request.method != 'POST':
        feedbacks = FeedbackIntern.objects.all()
        context = {
            'feedbacks': feedbacks,
            'page_title': 'Intern Feedback Messages'
        }
        return render(request, 'hod_template/intern_feedback_template.html', context)
    else:
        feedback_id = request.POST.get('id')
        try:
            feedback = get_object_or_404(FeedbackIntern, id=feedback_id)
            reply = request.POST.get('reply')
            feedback.reply = reply
            feedback.save()
            return HttpResponse(True)
        except Exception as e:
            return HttpResponse(False)


@csrf_exempt
def staff_feedback_message(request):
    if request.method != 'POST':
        feedbacks = FeedbackStaff.objects.all()
        context = {
            'feedbacks': feedbacks,
            'page_title': 'Staff Feedback Messages'
        }
        return render(request, 'hod_template/staff_feedback_template.html', context)
    else:
        feedback_id = request.POST.get('id')
        try:
            feedback = get_object_or_404(FeedbackStaff, id=feedback_id)
            reply = request.POST.get('reply')
            feedback.reply = reply
            feedback.save()
            return HttpResponse(True)
        except Exception as e:
            return HttpResponse(False)


@csrf_exempt
def view_staff_leave(request):
    if request.method != 'POST':
        allLeave = LeaveReportStaff.objects.all()
        context = {
            'allLeave': allLeave,
            'page_title': 'Leave Applications From Staff'
        }
        return render(request, "hod_template/staff_leave_view.html", context)
    else:
        id = request.POST.get('id')
        status = request.POST.get('status')
        if (status == '1'):
            status = 1
        else:
            status = -1
        try:
            leave = get_object_or_404(LeaveReportStaff, id=id)
            leave.status = status
            leave.save()
            return HttpResponse(True)
        except Exception as e:
            return False


@csrf_exempt
def view_intern_leave(request):
    if request.method != 'POST':
        allLeave = LeaveReportIntern.objects.all()
        context = {
            'allLeave': allLeave,
            'page_title': 'Leave Applications From Interns'
        }
        return render(request, "hod_template/intern_leave_view.html", context)
    else:
        id = request.POST.get('id')
        status = request.POST.get('status')
        if (status == '1'):
            status = 1
        else:
            status = -1
        try:
            leave = get_object_or_404(LeaveReportIntern, id=id)
            leave.status = status
            leave.save()
            return HttpResponse(True)
        except Exception as e:
            return False


def admin_view_attendance(request):
    tasks = Task.objects.all()
    shifts = Shift.objects.all()
    context = {
        'tasks': tasks,
        'shifts': shifts,
        'page_title': 'View Attendance'
    }

    return render(request, "hod_template/admin_view_attendance.html", context)


@csrf_exempt
def get_admin_attendance(request):
    task_id = request.POST.get('task')
    shift_id = request.POST.get('shift')
    attendance_date_id = request.POST.get('attendance_date_id')
    try:
        task = get_object_or_404(Task, id=task_id)
        shift = get_object_or_404(Shift, id=shift_id)
        attendance = get_object_or_404(
            Attendance, id=attendance_date_id, shift=shift)
        attendance_reports = AttendanceReport.objects.filter(
            attendance=attendance)
        json_data = []
        for report in attendance_reports:
            data = {
                "status":  str(report.status),
                "name": str(report.intern)
            }
            json_data.append(data)
        return JsonResponse(json.dumps(json_data), safe=False)
    except Exception as e:
        return None


def admin_view_profile(request):
    admin = get_object_or_404(Admin, admin=request.user)
    form = AdminForm(request.POST or None, request.FILES or None,
                     instance=admin)
    context = {'form': form,
               'page_title': 'View/Edit Profile'
               }
    if request.method == 'POST':
        try:
            if form.is_valid():
                first_name = form.cleaned_data.get('first_name')
                last_name = form.cleaned_data.get('last_name')
                password = form.cleaned_data.get('password') or None
                passport = request.FILES.get('profile_pic') or None
                custom_user = admin.admin
                if password != None:
                    custom_user.set_password(password)
                if passport != None:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    custom_user.profile_pic = passport_url
                custom_user.first_name = first_name
                custom_user.last_name = last_name
                custom_user.save()
                messages.success(request, "Profile Updated!")
                return redirect(reverse('admin_view_profile'))
            else:
                messages.error(request, "Invalid Data Provided")
        except Exception as e:
            messages.error(
                request, "Error Occured While Updating Profile " + str(e))
    return render(request, "hod_template/admin_view_profile.html", context)


def admin_notify_staff(request):
    staff = CustomUser.objects.filter(user_type=2)
    context = {
        'page_title': "Send Notifications To Staff",
        'allStaff': staff
    }
    return render(request, "hod_template/staff_notification.html", context)


def admin_notify_intern(request):
    intern = CustomUser.objects.filter(user_type=3)
    context = {
        'page_title': "Send Notifications To Interns",
        'interns': intern
    }
    return render(request, "hod_template/intern_notification.html", context)


@csrf_exempt
def send_intern_notification(request):
    id = request.POST.get('id')
    message = request.POST.get('message')
    intern = get_object_or_404(Intern, admin_id=id)
    try:
        url = "https://fcm.googleapis.com/fcm/send"
        body = {
            'notification': {
                'title': "Intern Management System",
                'body': message,
                'click_action': reverse('intern_view_notification'),
                'icon': static('dist/img/AdminLTELogo.png')
            },
            'to': intern.admin.fcm_token
        }
        headers = {'Authorization':
                   'key=AAAA3Bm8j_M:APA91bElZlOLetwV696SoEtgzpJr2qbxBfxVBfDWFiopBWzfCfzQp2nRyC7_A2mlukZEHV4g1AmyC6P_HonvSkY2YyliKt5tT3fe_1lrKod2Daigzhb2xnYQMxUWjCAIQcUexAMPZePB',
                   'Content-Type': 'application/json'}
        data = requests.post(url, data=json.dumps(body), headers=headers)
        notification = NotificationIntern(intern=intern, message=message)
        notification.save()
        return HttpResponse("True")
    except Exception as e:
        return HttpResponse("False")


@csrf_exempt
def send_staff_notification(request):
    id = request.POST.get('id')
    message = request.POST.get('message')
    staff = get_object_or_404(Staff, admin_id=id)
    try:
        url = "https://fcm.googleapis.com/fcm/send"
        body = {
            'notification': {
                'title': "Intern Management System",
                'body': message,
                'click_action': reverse('staff_view_notification'),
                'icon': static('dist/img/AdminLTELogo.png')
            },
            'to': staff.admin.fcm_token
        }
        headers = {'Authorization':
                   'key=AAAA3Bm8j_M:APA91bElZlOLetwV696SoEtgzpJr2qbxBfxVBfDWFiopBWzfCfzQp2nRyC7_A2mlukZEHV4g1AmyC6P_HonvSkY2YyliKt5tT3fe_1lrKod2Daigzhb2xnYQMxUWjCAIQcUexAMPZePB',
                   'Content-Type': 'application/json'}
        data = requests.post(url, data=json.dumps(body), headers=headers)
        notification = NotificationStaff(staff=staff, message=message)
        notification.save()
        return HttpResponse("True")
    except Exception as e:
        return HttpResponse("False")


def delete_staff(request, staff_id):
    staff = get_object_or_404(CustomUser, staff__id=staff_id)
    staff.delete()
    messages.success(request, "Staff deleted successfully!")
    return redirect(reverse('manage_staff'))


def delete_intern(request, intern_id):
    intern = get_object_or_404(CustomUser, intern__id=intern_id)
    intern.delete()
    messages.success(request, "Intern deleted successfully!")
    return redirect(reverse('manage_intern'))


def delete_department(request, department_id):
    department = get_object_or_404(Department, id=department_id)
    try:
        department.delete()
        messages.success(request, "Department deleted successfully!")
    except Exception:
        messages.error(
            request, "Sorry, some interns are assigned to this department already. Kindly change the affected intern department and try again")
    return redirect(reverse('manage_department'))


def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.delete()
    messages.success(request, "Task deleted successfully!")
    return redirect(reverse('manage_task'))


def delete_shift(request, shift_id):
    shift = get_object_or_404(Shift, id=shift_id)
    try:
        shift.delete()
        messages.success(request, "Shift deleted successfully!")
    except Exception:
        messages.error(
            request, "There are interns assigned to this shift. Please move them to another shift.")
    return redirect(reverse('manage_shift'))
