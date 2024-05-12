from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from django.contrib import messages
from .models import Task, Staff, Intern, InternResult
from .forms import EditResultForm
from django.urls import reverse


class EditResultView(View):
    def get(self, request, *args, **kwargs):
        resultForm = EditResultForm()
        staff = get_object_or_404(Staff, admin=request.user)
        resultForm.fields['task'].queryset = Task.objects.filter(staff=staff)
        context = {
            'form': resultForm,
            'page_title': "Edit Intern's Result"
        }
        return render(request, "staff_template/edit_intern_result.html", context)

    def post(self, request, *args, **kwargs):
        form = EditResultForm(request.POST)
        context = {'form': form, 'page_title': "Edit Intern's Result"}
        if form.is_valid():
            try:
                intern = form.cleaned_data.get('intern')
                task = form.cleaned_data.get('task')
                test = form.cleaned_data.get('test')
                exam = form.cleaned_data.get('exam')
                # Validating
                result = InternResult.objects.get(intern=intern, task=task)
                result.exam = exam
                result.test = test
                result.save()
                messages.success(request, "Result Updated")
                return redirect(reverse('edit_intern_result'))
            except Exception as e:
                messages.warning(request, "Result Could Not Be Updated")
        else:
            messages.warning(request, "Result Could Not Be Updated")
        return render(request, "staff_template/edit_intern_result.html", context)
