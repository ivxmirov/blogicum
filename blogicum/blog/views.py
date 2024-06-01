from datetime import datetime

from django.shortcuts import get_object_or_404, render
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)
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

class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm

    def form_valid(self, form):
        # Присвоить полю author объект пользователя из запроса.
        form.instance.author = self.request.user
        # Продолжить валидацию, описанную в форме.
        return super().form_valid(form)


class BirthdayDeleteView(OnlyAuthorMixin, DeleteView):
    model = Birthday
    success_url = reverse_lazy('birthday:list')


class BirthdayDetailView(DetailView):
    model = Birthday

    def get_context_data(self, **kwargs):
        # Получаем словарь контекста:
        context = super().get_context_data(**kwargs)
        # Добавляем в словарь новый ключ:
        context['birthday_countdown'] = calculate_birthday_countdown(
            # Дату рождения берём из объекта в словаре context:
            self.object.birthday
        )
        # Записываем в переменную form пустой объект формы.
        context['form'] = CongratulationForm()
        # Запрашиваем все поздравления для выбранного дня рождения.
        context['congratulations'] = (
            # Дополнительно подгружаем авторов комментариев,
            # чтобы избежать множества запросов к БД.
            self.object.congratulations.select_related('author')
        )
        # Возвращаем словарь контекста.
        return context


# Наследуем класс от встроенного ListView:
class BirthdayListView(ListView):
    # Указываем модель, с которой работает CBV...
    model = Birthday
    # ...сортировку, которая будет применена при выводе списка объектов:
    ordering = 'id'
    # ...и даже настройки пагинации:
    paginate_by = 10


class BirthdayUpdateView(OnlyAuthorMixin, UpdateView):
    model = Birthday
    form_class = BirthdayForm

    # Определяем метод test_func() для миксина UserPassesTestMixin:
    def test_func(self):
        # Получаем текущий объект.
        object = self.get_object()
        # Метод вернёт True или False.
        # Если пользователь - автор объекта, то тест будет пройден.
        # Если нет, то будет вызвана ошибка 403.
        return object.author == self.request.user


class CongratulationCreateView(LoginRequiredMixin, CreateView):
    birthday = None
    model = Congratulation
    form_class = CongratulationForm

    # Переопределяем dispatch()
    def dispatch(self, request, *args, **kwargs):
        self.birthday = get_object_or_404(Birthday, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    # Переопределяем form_valid()
    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.birthday = self.birthday
        return super().form_valid(form)

    # Переопределяем get_success_url()
    def get_success_url(self):
        return reverse('birthday:detail', kwargs={'pk': self.birthday.pk})
