from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404

from apps.news.models import News


def page_news(request):
    """Единая страница новостей: список или деталь в зависимости от ?id=..."""
    news_id = request.GET.get('id')

    # === DETAIL VIEW ===
    if news_id:
        detail = get_object_or_404(
            News.objects.select_related('author'),
            pk=news_id,
            is_published=True
        )
        # 3 последние новости, исключая текущую
        related = News.objects.filter(
            is_published=True
        ).exclude(
            id=detail.id
        ).select_related('author').order_by('-published_at')[:3]

        return render(request, 'news/home.html', {
            'detail': detail,
            'related': related,
        })

    # === LIST VIEW ===
    queryset = News.objects.filter(
        is_published=True
    ).select_related('author').order_by('-published_at')

    # Фильтр по статусу (для админов/модераторов можно показать черновики)
    status = request.GET.get('status')
    if request.user.is_staff or request.user.groups.filter(name__in=['moderator', 'admin']).exists():
        if status == 'archive':
            queryset = News.objects.all().order_by('-published_at')
        elif status == 'published':
            pass  # уже отфильтровано выше
    else:
        status = None  # обычные пользователи не могут фильтровать

    paginator = Paginator(queryset, 9)  # 9 новостей на страницу
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(request, 'news/home.html', {
        'news_list': page_obj,
        'page_obj': page_obj,
        'filter_status': status,
    })