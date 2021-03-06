from django.contrib.auth import logout, login
from django.contrib.auth.views import LoginView
from django.http import HttpResponse, HttpResponseNotFound, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls.base import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator

from .forms import *
from .models import *
from .utils import *


# ------------index----------------
class DecorationHome(DataMixin, ListView):
    """
    Класс отвечает за отображение главной страницы
    """
    model = Decoration
    template_name = 'decoration/index.html'
    context_object_name = 'posts'

    # extra_context = {'title': 'Главная страница'}

    def get_context_data(self, *, object_list=None, **kwargs):
        """
        Создание 2-х словарей и их объединение
        :return:
        """
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title="Главная страница")
        return dict(list(context.items()) + list(c_def.items()))

    def get_queryset(self):
        """
        Отображение только отмеченных публикаций
        :return: elect_related жадный запрос
        """
        return Decoration.objects.filter(is_published=True).select_related('cat')


# def index(request):
#     posts = Decoration.objects.all()

#     context = {
#         'posts': posts,
#         'menu': menu,
#         'title': 'Главная страница',
#         'cat_selected': 0,
#     }

#     return render(request, 'decoration/index.html', context=context)


def about(request):
    contact_list = Decoration.objects.all()
    paginator = Paginator(contact_list, 3)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'decoration/about.html', {'page_obj': page_obj, 'menu': menu, 'title': 'О сайте'})


# -------------addpage---------------
class AddPage(LoginRequiredMixin, DataMixin, CreateView):
    form_class = AddPostForm
    template_name = 'decoration/addpage.html'
    success_url = reverse_lazy('home')
    login_url = reverse_lazy('home')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title="Добавить отзыв")
        return dict(list(context.items()) + list(c_def.items()))


# def addpage(request):
#     if request.method == 'POST':
#         form = AddPostForm(request.POST, request.FILES)
#         if form.is_valid():
#             # print(form.cleaned_data)
#             form.save()
#             return redirect('home')
#     else:
#         form = AddPostForm()

#     return render(request, 'decoration/addpage.html', {'form': form, 'menu': menu, 'title': 'Добавление украшение'})


# def contact(request):
#     return HttpResponse("Обратная связь")


class ContactFormView(DataMixin, FormView):
    form_class = ContactForm
    template_name = 'decoration/contact.html'
    success_url = reverse_lazy('home')

    def get_context_data(self, *, object_list=None,  **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title="Заказать украшение")
        return dict((list(context.items()) + list(c_def.items())))

    def form_valid(self, form):
        print(form.cleaned_data)
        return redirect('home')



# def login(request):
#     return HttpResponse("Авторизация")


def pageNotFound(request, exception):
    return HttpResponseNotFound('<h1>Страница не найдена</h1>')


# -------------show_post---------------
class ShowPost(DataMixin, DetailView):
    model = Decoration
    template_name = 'decoration/post.html'
    slug_url_kwarg = 'post_slug'
    context_object_name = 'post'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title=context['post'])
        return dict(list(context.items()) + list(c_def.items()))


# def show_post(request, post_slug):
#     post = get_object_or_404(Decoration, slug=post_slug)

#     context = {
#         'post': post,
#         'menu': menu,
#         'title': post.title,
#         'cat_selected': post.cat_id,
#     }

#     return render(request, 'decoration/post.html', context=context)


# -----------show_category------------
class DecorationCategory(DataMixin, ListView):
    model = Decoration
    template_name = 'decoration/index.html'
    context_object_name = 'posts'
    allow_empty = False

    def get_queryset(self):
        return Decoration.objects.filter(cat__slug=self.kwargs['cat_slug'], is_published=True).select_related('cat')

    def get_context_data(self, *, object_list=None, **kwargs):
        """
        :param object_list:
        :param kwargs:
        :return:
        """
        context = super().get_context_data(**kwargs)
        c = Category.objects.get(slug=self.kwargs['cat_slug'])
        c_def = self.get_user_context(title='Категория - ' + str(c.name),
                                      cat_selected=c.pk)
        return dict(list(context.items()) + list(c_def.items()))


# def show_category(request, cat_id):
#     posts = Decoration.objects.filter(cat_id=cat_id)

#     if len(posts) == 0:
#         raise Http404()

#     context = {
#         'posts': posts,
#         'menu': menu,
#         'title': 'Отображение по рубрикам',
#         'cat_selected': cat_id,
#     }

#     return render(request, 'decoration/index.html', context=context)


class RegisterUser(DataMixin, CreateView):
    form_class = RegisterUserForm
    template_name = 'decoration/register.html'
    success_url = reverse_lazy('login')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title="Регистрация")
        return dict(list(context.items()) + list(c_def.items()))

    def form_valid(self, form):
        """
        Метод автоматически авторизует после регистрации пользователя
        :param form:
        :return:
        """
        user = form.save()
        login(self.request, user)
        return redirect('home')


class LoginUser(DataMixin, LoginView):
    form_class = LoginUserForm
    template_name = 'decoration/login.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        """
        Отображение формы Авторизации.
        Формирование контекста для шаблона Login
        :return:
        """
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title="Авторизация")
        return dict(list(context.items()) + list(c_def.items()))

    def get_success_url(self):
        """
        Метод возвращает пользователя на главную страницу,
        если он правильно авторизовался
        :return:
        """
        return reverse_lazy('home')


def logout_user(request):
    """
    Выход из авторизации
    :param request:
    :return:
    """
    logout(request)
    return redirect('login')
