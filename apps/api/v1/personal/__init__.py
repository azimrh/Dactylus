'''

GET /api/personal/ - список записей пользователя

POST /api/personal/ - создать новую запись

GET /api/personal/{id}/ - детали записи

PATCH /api/personal/{id}/ - обновить запись

DELETE /api/personal/{id}/ - удалить запись

GET /api/personal/statistics/ - статистика

GET /api/personal/by_status/?status=learning - фильтрация по статусу

POST /api/personal/{id}/mark_learned/ - отметить как выученное

POST /api/personal/{id}/reset_status/ - сбросить статус

'''