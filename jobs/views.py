from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import UpdateView, DeleteView
from django.contrib import messages
from django.views.generic.edit import CreateView
from .forms import JobForm
from .models import Job, JobApplicant

class JobCreateView(CreateView):
    model = Job
    form_class = JobForm
    template_name = 'jobs/job_create.html'
    success_url = reverse_lazy('jobs:job_list_view')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def handle_no_permission(self):
        return redirect('jobs:job_list_view')

    def test_func(self):
        return self.request.user.is_staff


def job_list_view(request):
    jobs = Job.objects.all()
    query = request.GET.get('q', None)
    if query is not None:
        jobs = jobs.filter(
            Q(job_title__icontains=query),
            Q(job_description__icontains=query),
            Q(location__icontains=query)
        )
    context = {
        'jobs': jobs,
    }
    return render(request, 'jobs/job_list.html', context)


def job_detail_view(request, pk):
    try:
        user = request.user
        job = Job.objects.get(pk=pk)

        if not user.is_authenticated:
            return render(request, 'auth/401.html', status=401)
    except Job.DoesNotExist:
        return render(request, 'auth/404.html', status=404)

    applicants = JobApplicant.objects.filter(job=job)
    has_applied = JobApplicant.objects.filter(job=job, user=user).exists() if user.is_authenticated else False

    context = {
        'job': job,
        'user': user,
        'applicants': applicants,
        'has_applied': has_applied,
    }
    return render(request, 'jobs/job_detail.html', context)


def job_apply(request, pk):
    job = get_object_or_404(Job, pk=pk)
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return render(request, 'auth/401.html', status=401)
        resume = request.FILES.get('resume')

        if not resume:
            messages.error(request, 'Please upload your resume.')
            return render(request, 'jobs/job_apply.html', {'job': job})

        JobApplicant.objects.create(job=job, user=request.user, resume=resume)
        messages.success(request, 'Application submitted successfully!')

        return redirect('jobs:job_detail_view', pk=job.pk)
    return render(request, 'jobs/job_apply.html', {'job': job})


class JobUpdateView(UpdateView):
    form_class = JobForm
    template_name = 'jobs/job_update.html'
    queryset = Job.objects.all()
    success_url = reverse_lazy('jobs:job_detail_view')

    def get_object(self, queryset=None):
        job = super().get_object(queryset)
        user = self.request.user
        if not user.is_authenticated:
            raise PermissionError("You do not have permission to edit this job.")
        return job

    def get_success_url(self):
        return reverse_lazy('jobs:job_detail_view', kwargs={'pk': self.object.pk})


class JobDeleteView(DeleteView):
    model = Job
    template_name = 'jobs/job_delete.html'
    success_url = reverse_lazy('jobs:job_list_view')

    def get_object(self, queryset=None):
        job = super().get_object(queryset)
        user = self.request.user
        if not user.is_authenticated:
            raise PermissionError("You do not have permission to delete this job.")
        return job