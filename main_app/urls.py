"""college_management_system URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path

from main_app.EditResultView import EditResultView

from . import hod_views, staff_views, intern_views, views

urlpatterns = [
    path("", views.login_page, name='login_page'),
    path("get_attendance", views.get_attendance, name='get_attendance'),
    path("firebase-messaging-sw.js", views.showFirebaseJS, name='showFirebaseJS'),
    path("doLogin/", views.doLogin, name='user_login'),
    path("logout_user/", views.logout_user, name='user_logout'),
    path("admin/home/", hod_views.admin_home, name='admin_home'),
    path("staff/add", hod_views.add_staff, name='add_staff'),
    path("department/add", hod_views.add_department, name='add_department'),
    path("send_intern_notification/", hod_views.send_intern_notification,
         name='send_intern_notification'),
    path("send_staff_notification/", hod_views.send_staff_notification,
         name='send_staff_notification'),
    path("add_shift/", hod_views.add_shift, name='add_shift'),
    path("admin_notify_intern", hod_views.admin_notify_intern,
         name='admin_notify_intern'),
    path("admin_notify_staff", hod_views.admin_notify_staff,
         name='admin_notify_staff'),
    path("admin_view_profile", hod_views.admin_view_profile,
         name='admin_view_profile'),
    path("check_email_availability", hod_views.check_email_availability,
         name="check_email_availability"),
    path("shift/manage/", hod_views.manage_shift, name='manage_shift'),
    path("shift/edit/<int:shift_id>",
         hod_views.edit_shift, name='edit_shift'),
    path("intern/view/feedback/", hod_views.intern_feedback_message,
         name="intern_feedback_message",),
    path("staff/view/feedback/", hod_views.staff_feedback_message,
         name="staff_feedback_message",),
    path("intern/view/leave/", hod_views.view_intern_leave,
         name="view_intern_leave",),
    path("staff/view/leave/", hod_views.view_staff_leave, name="view_staff_leave",),
    path("attendance/view/", hod_views.admin_view_attendance,
         name="admin_view_attendance",),
    path("attendance/fetch/", hod_views.get_admin_attendance,
         name='get_admin_attendance'),
    path("intern/add/", hod_views.add_intern, name='add_intern'),
    path("task/add/", hod_views.add_task, name='add_task'),
    path("staff/manage/", hod_views.manage_staff, name='manage_staff'),
    path("intern/manage/", hod_views.manage_intern, name='manage_intern'),
    path("department/manage/", hod_views.manage_department, name='manage_department'),
    path("task/manage/", hod_views.manage_task, name='manage_task'),
    path("staff/edit/<int:staff_id>", hod_views.edit_staff, name='edit_staff'),
    path("staff/delete/<int:staff_id>",
         hod_views.delete_staff, name='delete_staff'),

    path("department/delete/<int:department_id>",
         hod_views.delete_department, name='delete_department'),

    path("task/delete/<int:task_id>",
         hod_views.delete_task, name='delete_task'),

    path("shift/delete/<int:shift_id>",
         hod_views.delete_shift, name='delete_shift'),

    path("intern/delete/<int:intern_id>",
         hod_views.delete_intern, name='delete_intern'),
    path("intern/edit/<int:intern_id>",
         hod_views.edit_intern, name='edit_intern'),
    path("department/edit/<int:department_id>",
         hod_views.edit_department, name='edit_department'),
    path("task/edit/<int:task_id>",
         hod_views.edit_task, name='edit_task'),


    # Staff
    path("staff/home/", staff_views.staff_home, name='staff_home'),
    path("staff/apply/leave/", staff_views.staff_apply_leave,
         name='staff_apply_leave'),
    path("staff/feedback/", staff_views.staff_feedback, name='staff_feedback'),
    path("staff/view/profile/", staff_views.staff_view_profile,
         name='staff_view_profile'),
    path("staff/attendance/take/", staff_views.staff_take_attendance,
         name='staff_take_attendance'),
    path("staff/attendance/update/", staff_views.staff_update_attendance,
         name='staff_update_attendance'),
    path("staff/get_interns/", staff_views.get_interns, name='get_interns'),
    path("staff/attendance/fetch/", staff_views.get_intern_attendance,
         name='get_intern_attendance'),
    path("staff/attendance/save/",
         staff_views.save_attendance, name='save_attendance'),
    path("staff/attendance/update/",
         staff_views.update_attendance, name='update_attendance'),
    path("staff/fcmtoken/", staff_views.staff_fcmtoken, name='staff_fcmtoken'),
    path("staff/view/notification/", staff_views.staff_view_notification,
         name="staff_view_notification"),
    path("staff/result/add/", staff_views.staff_add_result, name='staff_add_result'),
    path("staff/result/edit/", EditResultView.as_view(),
         name='edit_intern_result'),
    path('staff/result/fetch/', staff_views.fetch_intern_result,
         name='fetch_intern_result'),
     path("staff/task/add/", staff_views.staff_add_task, name='staff_add_task'),
     path("staff/task/edit/<int:task_id>",
         staff_views.staff_edit_task, name='staff_edit_task'),
     path("staff/task/manage/", staff_views.staff_manage_task, name='staff_manage_task'),
     path("staff/task/delete/<int:task_id>",
         staff_views.staff_delete_task, name='staff_delete_task'),



    # Intern
    path("intern/home/", intern_views.intern_home, name='intern_home'),
    path("intern/view/attendance/", intern_views.intern_view_attendance,
         name='intern_view_attendance'),
    path("intern/apply/leave/", intern_views.intern_apply_leave,
         name='intern_apply_leave'),
    path("intern/feedback/", intern_views.intern_feedback,
         name='intern_feedback'),
    path("intern/view/profile/", intern_views.intern_view_profile,
         name='intern_view_profile'),
    path("intern/fcmtoken/", intern_views.intern_fcmtoken,
         name='intern_fcmtoken'),
    path("intern/view/notification/", intern_views.intern_view_notification,
         name="intern_view_notification"),
    path('intern/view/result/', intern_views.intern_view_result,
         name='intern_view_result'),
     path('intern/view/tasks', intern_views.view_task, name='intern_view_task'),
     path('intern/update/tasks', intern_views.update_tasks, name='update_tasks'),
     path("intern/update/tasks/<int:task_id>",
         intern_views.update_tasks, name='update_tasks')
]
