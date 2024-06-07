from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)
from django.urls import reverse

from .forms import CommentForm, PostForm, UserForm
from .models import Category, Comment, Post, User
from core.consts import POSTS_ON_PAGE


class ProfileListView(ListView):
    model = User
    template_name = 'blog/profile.html'
    paginate_by = POSTS_ON_PAGE

    def get_object(self):
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_queryset(self):
        if self.request.user == self.get_object():
            page_obj = Post.objects.filter(
                author=self.get_object()
            )
        else:
            page_obj = Post.objects.filter(
                author=self.get_object(),
                category__is_published=True,
                is_published=True,
                pub_date__lte=datetime.now()
            )
        return page_obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.get_object()
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = 'blog/user.html'

    def get_object(self):
        return self.request.user

    def handle_no_permission(self):
        return redirect('login')

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
        return get_object_or_404(
            Category,
            is_published=True,
            slug=self.kwargs['slug']
        )

    def get_queryset(self):
        page_obj = Post.objects.filter(
            category=self.get_object(),
            is_published=True,
            pub_date__lte=datetime.now()
        )
        return page_obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.get_object()
        return context


class PostListView(ListView):
    model = Post
    paginate_by = POSTS_ON_PAGE
    template_name = 'blog/index.html'

    def get_queryset(self):
        page_obj = Post.objects.filter(
            category__is_published=True,
            is_published=True,
            pub_date__lte=datetime.now()
        )
        return page_obj


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


class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user

    def handle_no_permission(self):
        return redirect('blog:post_detail', post_id=self.kwargs['post_id'])


class PostMixin:
    model = Post
    form_class = PostForm
    pk_url_kwarg = 'post_id'

    def get_object(self):
        return get_object_or_404(
            Post,
            pk=self.kwargs['post_id']
        )

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostDetailView(DetailView):
    model = Post
    form_class = PostForm
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_object(self):
        post_instance = get_object_or_404(
            Post,
            pk=self.kwargs['post_id']
        )
        if post_instance.author == self.request.user:
            return post_instance
        else:
            return get_object_or_404(
                Post,
                pk=self.kwargs['post_id'],
                is_published=True,
                pub_date__lte=datetime.now()
            )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = self.get_object()
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.select_related('author')
        return context


class PostUpdateView(PostMixin, OnlyAuthorMixin, UpdateView):
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class PostDeleteView(PostMixin, OnlyAuthorMixin, DeleteView):
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    post_instance = None
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        self.post_instance = get_object_or_404(Post, pk=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.post_instance
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.post_instance.pk}
        )


class CommentMixin:
    model = Comment
    form_class = CommentForm
    pk_url_kwarg = ['comment_id', 'post_id']
    template_name = 'blog/comment.html'

    def get_object(self):
        return get_object_or_404(Comment, pk=self.kwargs['comment_id'])

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class CommentUpdateView(CommentMixin, OnlyAuthorMixin, UpdateView):
    pass


class CommentDeleteView(CommentMixin, OnlyAuthorMixin, DeleteView):
    pass
