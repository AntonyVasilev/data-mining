# data-mining

Задача: Источник Интсаграмм. На вход программе подяется 2 имени пользователя. Задача программы найти самую короткую цепоччку рукопожатий между этими пользователями. Рукопожатием считаем только взаимоподписанных пользовтаелей.

Стек: scrapy, networkx, pymongo

Решение: Использован scrapy для сбора данных о пользователях. Данные сохраняются в БД MongoDB. Поиск цепочки рукопожатий реализован через создание направленного графа, в котором вершины - id пользователей. После добавления каждого нового пользователя происходить поиск наличия пути между двумя начальными вершинами графа (заданными пользователями). Если такой путь найден и он существует в обе стороны, то цепочка рукопожатий найдена.
