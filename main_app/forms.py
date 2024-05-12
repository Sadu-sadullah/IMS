from typing import OrderedDict
from django import forms
from django.forms.widgets import DateInput, TextInput, TimeInput
from django.core.exceptions import ObjectDoesNotExist

from .models import *


class FormSettings(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormSettings, self).__init__(*args, **kwargs)
        # Here make some changes such as:
        for field in self.visible_fields():
            field.field.widget.attrs['class'] = 'form-control'


class CustomUserForm(FormSettings):
    email = forms.EmailField(required=True)
    gender = forms.ChoiceField(choices=[('M', 'Male'), ('F', 'Female')])
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    address = forms.CharField(widget=forms.Textarea)
    password = forms.CharField(widget=forms.PasswordInput)
    widget = {
        'password': forms.PasswordInput(),
    }
    profile_pic = forms.ImageField()

    def __init__(self, *args, **kwargs):
        super(CustomUserForm, self).__init__(*args, **kwargs)

        if kwargs.get('instance'):
            instance = kwargs.get('instance').admin.__dict__
            self.fields['password'].required = False
            for field in CustomUserForm.Meta.fields:
                self.fields[field].initial = instance.get(field)
            if self.instance.pk is not None:
                self.fields['password'].widget.attrs['placeholder'] = "Fill this only if you wish to update password"

    def clean_email(self, *args, **kwargs):
        formEmail = self.cleaned_data['email'].lower()
        if self.instance.pk is None:  # Insert
            if CustomUser.objects.filter(email=formEmail).exists():
                raise forms.ValidationError(
                    "The given email is already registered")
        else:  # Update
            dbEmail = self.Meta.model.objects.get(
                id=self.instance.pk).admin.email.lower()
            if dbEmail != formEmail:  # There has been changes
                if CustomUser.objects.filter(email=formEmail).exists():
                    raise forms.ValidationError("The given email is already registered")

        return formEmail

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'gender',  'password','profile_pic', 'address' ]


class InternForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(InternForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Intern
        fields = CustomUserForm.Meta.fields + \
            ['department', 'shift', 'staff']


class AdminForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(AdminForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Admin
        fields = CustomUserForm.Meta.fields


class StaffForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(StaffForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Staff
        fields = CustomUserForm.Meta.fields + \
            ['department' ]


class DepartmentForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(DepartmentForm, self).__init__(*args, **kwargs)

    class Meta:
        fields = ['name']
        model = Department


class TaskForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)

        # Intern field (initial queryset for all interns)
        self.fields['intern'].queryset = Intern.objects.all()

    def clean(self):
        cleaned_data = super().clean()  # Call parent clean method
        intern = cleaned_data.get('intern')
        if intern:
            # Explicitly set department based on intern
            cleaned_data['department'] = intern.department
        return cleaned_data

    class Meta:
        model = Task
        fields = ['name', 'intern', 'department', 'description']

class StaffTaskForm(forms.Form):
    name = forms.CharField(required=True)
    description = forms.CharField(widget=forms.Textarea, required=True)

    def __init__(self, *args, **kwargs):
        current_user = kwargs.pop('user')
        try:
            department = current_user.staff.department
            interns = Intern.objects.filter(staff__admin=current_user)
        except (AttributeError, ObjectDoesNotExist):
            department = None
            interns = None

        super(StaffTaskForm, self).__init__(*args, **kwargs)
        self.initial['department'] = department
        self.initial['intern'] = None if interns else None


        if department:
            self.fields['department'] = forms.CharField(required=False, initial=department)
            self.fields['department'].disabled = True
        else:
            del self.fields['department'] 

        
        if interns:
            self.fields['intern'] = forms.ModelChoiceField(queryset=interns)
            if self.initial['intern']:
                self.fields['intern'].initial = self.initial['intern'].pk
        else:
            del self.fields['intern'] 

        self.fields = OrderedDict([
            ('name', self.fields['name']),
            ('department', self.fields.get('department', None)),
            ('intern', self.fields.get('intern', None)), 
            ('description', self.fields['description']),
        ])

        for field in self.visible_fields():
            field.field.widget.attrs['class'] = 'form-control'

class TaskUpdateForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(TaskUpdateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Task
        fields = ['completed', 'intern_feedback']

class EditTaskForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EditTaskForm, self).__init__(*args, **kwargs)
        for field in self.visible_fields():
            field.field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = Task
        fields = ['name', 'description']

class ShiftForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(ShiftForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Shift
        fields = '__all__'
        widgets = {
            'start_time': TimeInput(attrs={'type': 'time'}),
            'end_time': TimeInput(attrs={'type': 'time'}),
        }



class LeaveReportStaffForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(LeaveReportStaffForm, self).__init__(*args, **kwargs)

    class Meta:
        model = LeaveReportStaff
        fields = ['date', 'message']
        widgets = {
            'date': DateInput(attrs={'type': 'date'}),
        }


class FeedbackStaffForm(FormSettings):

    def __init__(self, *args, **kwargs):
        super(FeedbackStaffForm, self).__init__(*args, **kwargs)

    class Meta:
        model = FeedbackStaff
        fields = ['feedback']


class LeaveReportInternForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(LeaveReportInternForm, self).__init__(*args, **kwargs)

    class Meta:
        model = LeaveReportIntern
        fields = ['date', 'message']
        widgets = {
            'date': DateInput(attrs={'type': 'date'}),
        }


class FeedbackInternForm(FormSettings):

    def __init__(self, *args, **kwargs):
        super(FeedbackInternForm, self).__init__(*args, **kwargs)

    class Meta:
        model = FeedbackIntern
        fields = ['feedback']


class InternEditForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(InternEditForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Intern
        fields = CustomUserForm.Meta.fields 


class StaffEditForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(StaffEditForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Staff
        fields = CustomUserForm.Meta.fields


class EditResultForm(FormSettings):
    shift_list = Shift.objects.all()
    shift_year = forms.ModelChoiceField(
        label="Shift Year", queryset=shift_list, required=True)

    def __init__(self, *args, **kwargs):
        super(EditResultForm, self).__init__(*args, **kwargs)

    class Meta:
        model = InternResult
        fields = ['shift_year', 'task', 'intern', 'test', 'exam']
