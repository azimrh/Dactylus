```text
dactylus/
├── apps/
│   ├── __init__.py
│   ├── api/
│   │   ├── v1/
│   │   │   └── ...
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── pagination.py
│   │   ├── permissions.py
│   │   ├── routers.py
│   │   └── urls.py
│   ├── dictionary/
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── lexical.py
│   │   │   └── semantic.py
│   │   ├── migrations/
│   │   │   ├── __init__.py
│   │   │   └── ...
│   │   ├── templatetags/
│   │   │   ├── __init__.py
│   │   │   └── custom_filters.py
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   └── users/
│       ├── migrations/
│       ├── models/
│       ├── __init__.py
│       ├── admin.py
│       ├── apps.py
│       └── signals.py
├── dactylus/
│   ├── __init__.py
│   ├── asgi.py
│   ├── wsgi.py
│   ├── urls.py
│   └── settings.py
├── logs/
├── static/
├── media/
├── templates/
│   └── dictionary/
│       ├── partials/
│       │   └── ...
│       └── ...
└── manage.py
```
