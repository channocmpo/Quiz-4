from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, DeleteView, UpdateView, CreateView
from django.http import Http404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from .models import Post
from .forms import PostForm
from django.utils.text import slugify


# Create your views here.
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('posts')
    else:
        form = PostForm()
    return render(request, 'posts/post_create.html', {'form': form})
class PostListView(ListView):
    model = Post
    template_name = 'posts/post_list.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('auth:signin')
        return super().dispatch(request, *args, **kwargs)

class PostDetailSlugView(DetailView):
    queryset = Post.objects.all()
    template_name = 'posts/post_detail.html'

class PostDeleteView(DeleteView):
    model = Post
    template_name = 'posts/post_confirm_delete.html'
    success_url = reverse_lazy('posts:post-list')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.user != self.request.user:
            raise PermissionDenied("You don't have permission to delete this post.")
        return obj

class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'posts/post_update.html'
    context_object_name = 'post'
    success_url = reverse_lazy('posts:post-list')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.user != self.request.user:
            raise PermissionDenied("You don't have permission to edit this post.")
        return obj

    def get_success_url(self):
        return reverse_lazy('posts:post-detail', kwargs={'slug': self.object.slug})

class PostCreateView(CreateView):
    form_class = PostForm
    template_name = 'posts/post_create.html'
    success_url = reverse_lazy('posts:post-list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        post = form.save(commit=False)
        post.slug = slugify(post.title)
        original_slug = post.slug
        counter = 1
        while Post.objects.filter(slug=post.slug).exists():
            post.slug = f"{original_slug}_{counter}"
            counter += 1
        post.user = self.request.user
        post.save()
        self.object = post
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('posts:post-detail', kwargs={'slug': self.object.slug})
