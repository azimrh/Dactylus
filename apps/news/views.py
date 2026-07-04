from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.http import Http404

from .models import News
from .forms import NewsCreateForm


def page_news(request):
    """Страница списка новостей"""
    queryset = News.objects.filter(
        is_published=True
    ).select_related('author').order_by('-published_at')

    # Фильтр по статусу (для пользователей с правами можно показать черновики)
    status = request.GET.get('status')
    can_manage = request.user.has_perm('news.add_news') or request.user.has_perm('news.change_news')

    if can_manage:
        if status == 'archive':
            queryset = News.objects.all().order_by('-published_at')
        elif status == 'published':
            pass  # уже отфильтровано выше
    else:
        status = None  # обычные пользователи не могут фильтровать

    paginator = Paginator(queryset, 9)  # 9 новостей на страницу
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(request, 'news/list.html', {
        'news_list': page_obj,
        'page_obj': page_obj,
        'filter_status': status,
        'can_manage': can_manage,
    })


def news_detail(request, pk):
    """Страница конкретной новости"""
    news_item = get_object_or_404(
        News.objects.select_related('author'),
        pk=pk,
        is_published=True
    )

    # 3 последние новости, исключая текущую
    related = News.objects.filter(
        is_published=True
    ).exclude(
        id=news_item.id
    ).select_related('author').order_by('-published_at')[:3]

    can_manage = request.user.has_perm('news.delete_news')

    return render(request, 'news/detail.html', {
        'detail': news_item,
        'related': related,
        'can_manage': can_manage,
    })


@login_required
@permission_required('news.delete_news', raise_exception=True)
def news_delete(request, pk):
    """Удаление новости"""
    news_item = get_object_or_404(News, pk=pk)

    if request.method == 'POST':
        news_item.delete()
        return redirect('news')

    raise Http404("Метод не разрешен")


@login_required
@permission_required('news.add_news', raise_exception=True)
def news_create(request):
    """Создание новой новости"""
    if request.method == 'POST':
        form = NewsCreateForm(request.POST, request.FILES)
        if form.is_valid():
            news_item = form.save(commit=False)
            news_item.author = request.user
            # По умолчанию опубликовано, или можно добавить чекбокс is_published в форму
            news_item.is_published = True
            news_item.save()

            messages.success(request, 'Новость успешно создана!')
            return redirect('news_detail', pk=news_item.pk)
    else:
        form = NewsCreateForm()

    return render(request, 'news/create.html', {
        'form': form
    })