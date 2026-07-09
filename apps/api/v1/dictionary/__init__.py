"""
GET /api/v1/categories/ — список корневых категорий (с counts слов и жестов)

GET /api/v1/categories/{slug}/ — детали категории (с родителем, детьми, путём и counts)

GET /api/v1/categories/tree/ — полное дерево категорий (вложенная структура)

GET /api/v1/categories/{slug}/children/ — прямые дочерние категории указанной категории

GET /api/v1/text-lexemes/ — список текстовых лексем (краткий формат: id, text, slug)

GET /api/v1/text-lexemes/{id}/ — детали текстовой леммы (полный формат)

GET /api/v1/meanings/ — список значений (денотатов) с фильтрацией по статусу модерации (?status=approved/pending/rejected)

GET /api/v1/meanings/{pk}/ — детали значения (с автором, текстовыми и жестовыми лексемами через триплеты)

GET /api/v1/meanings/approved/ — только одобренные значения

GET /api/v1/meanings/{pk}/lexemes/ — все лексемы (текстовые и жестовые), связанные с данным значением через одобренные триплеты
"""