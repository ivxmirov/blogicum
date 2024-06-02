from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import get_object_or_404, render
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)
from django.urls import reverse, reverse_lazy

from .forms import CommentForm, PostForm
from .models import Category, Comment, Post
from core.consts import POSTS_ON_MAIN


def posts_filter():
    return Post.objects.filter(
        pub_date__lte=datetime.now(),
        is_published=True,
        category__is_published=True
    )


def index(request):
    post_list = posts_filter().order_by('-pub_date')[:POSTS_ON_MAIN]
    return render(request, 'blog/index.html', {'post_list': post_list})


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category.objects.filter(
            is_published=True,
            slug=category_slug
        )
    )
    post_list = posts_filter().filter(category=category)
    return render(
        request,
        'blog/category.html',
        {'category': category, 'post_list': post_list}
    )


def post_detail(request, post_id):
    post = get_object_or_404(posts_filter(), pk=post_id)
    return render(request, 'blog/detail.html', {'post': post})


class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostDeleteView(OnlyAuthorMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('Post:list')


class PostDetailView(DetailView):
    model = Post


class PostListView(ListView):
    model = Post
    ordering = 'id'
    paginate_by = 10


class PostUpdateView(OnlyAuthorMixin, UpdateView):
    model = Post
    form_class = PostForm

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user


class CommentCreateView(LoginRequiredMixin, CreateView):
    Post = None
    model = Comment
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        self.Post = get_object_or_404(Post, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.Post = self.Post
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('Post:detail', kwargs={'pk': self.Post.pk})


class CommentDeleteView(OnlyAuthorMixin, DeleteView):
    Post = None
    model = Comment
    form_class = CommentForm


class CommentUpdateView(OnlyAuthorMixin, UpdateView):
    Post = None
    model = Comment
    form_class = CommentForm
