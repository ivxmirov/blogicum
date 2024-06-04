from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import get_object_or_404
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)
from django.urls import reverse, reverse_lazy
from django.utils import timezone

from .forms import CommentForm, PostForm
from .models import Category, Comment, Post, User
from core.consts import POSTS_ON_PAGE


class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user


class ProfileListView(ListView):
    model = User
    template_name = 'blog/profile.html'
    paginate_by = POSTS_ON_PAGE

    def get_object(self):
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_queryset(self):
        if self.request.user == self.get_object():
            page_obj = Post.objects.filter(author=self.get_object().id)
        else:
            page_obj = Post.objects.filter(
                author=self.get_object().id,
                is_published=True,
                pub_date__lte=timezone.now()
            )
        return page_obj

    def get_context_data(self, **kwargs):
        # paginator = Paginator(self.get_queryset(), POSTS_ON_PAGE)
        # page_number = self.request.GET.get('page')
        # page_obj = paginator.get_page(page_number)
        context = super().get_context_data(**kwargs)
        context['profile'] = self.get_object()
        # context['page_obj'] = page_obj
        return context


class ProfileUpdateView(UpdateView):
    model = User
    template_name = 'blog/user.html'

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class CategoryListView(ListView):
    model = Category
    paginate_by = POSTS_ON_PAGE
    template_name = 'blog/category.html'

    def get_object(self):
        return get_object_or_404(Category, slug=self.kwargs['slug'])

    def get_queryset(self):
        page_obj = Post.objects.filter(
            category=self.get_object(),
            is_published=True,
            pub_date__lte=timezone.now()
        )
        return page_obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.get_object()
        return context


class PostMixin:
    model = Post
    pk_url_kwarg = 'post_id'


class PostListView(ListView):
    model = Post
    ordering = 'pub_date'
    paginate_by = POSTS_ON_PAGE
    template_name = 'blog/index.html'


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class PostDetailView(PostMixin, DetailView):
    template_name = 'blog/detail.html'


class PostUpdateView(PostMixin, OnlyAuthorMixin, UpdateView):
    form_class = PostForm
    template_name = 'blog/detail.html'

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.object.id})


class PostDeleteView(PostMixin, OnlyAuthorMixin, DeleteView):
    template_name = 'blog/detail.html'
    success_url = reverse_lazy('blog:profile')


class CommentMixin:
    model = Comment
    pk_url_kwarg = 'post_id'


class CommentCreateView(LoginRequiredMixin, CreateView):
    post = None
    model = Comment
    form_class = CommentForm
    template_name = 'includes/comments.html'

    def dispatch(self, request, *args, **kwargs):
        self.post = get_object_or_404(Post, pk=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.post
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.post.pk})


class CommentUpdateView(CommentMixin, OnlyAuthorMixin, UpdateView):
    Post = None
    form_class = CommentForm


class CommentDeleteView(CommentMixin, OnlyAuthorMixin, DeleteView):
    Post = None
    form_class = CommentForm
