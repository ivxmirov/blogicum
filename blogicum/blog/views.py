from datetime import datetime

from django.shortcuts import get_object_or_404, render

from .models import Post, Category
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
