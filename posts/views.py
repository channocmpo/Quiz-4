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
    success_url = 'posts:post-list'
    
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
        if not form.instance.slug:
            base_slug = slugify(form.instance.title)
        slug = base_slug
        num = 1
        while Post.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{num}"
        num += 1
        form.instance.slug = slug

        return super().form_valid(form)