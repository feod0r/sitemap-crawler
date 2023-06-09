# Sitemap crawler python

## ТЗ

Написать скрипт на Python, который делает карту любого сайта. Запрещено использование сторонних библиотек, разрешено использование встроенных в Python библиотек.

Требования:
 - Предпочтительно объектно-ориентированный стиль программирования;
 - Многопоточная обработка с Python средствами (Multiprocessing, Threading, etc..) или потоки из-под языка Си (захват/освобождение GIL);
 - Итераторы/Генераторы для обхода структуры (в глубину/ширину);
 - Залить на Github;
 - Опционально: сейв карты в базу или рисовать с помощью matplotlib.
 - Построить карты сайтов из списка ниже. Результаты занести в таблицу. URL сайтов для таблицы:
 - - http://crawler-test.com/ 
 - - http://google.com/ 
 - - https://vk.com 
 - - https://dzen.ru 
 - - https://stackoverflow.com
 - В рамках карты сайта нужно учитывать все каталоги сайта. Например, "https://www.google.com/search/howsearchworks/?fg=1" относится к карте сайта www.google.com

## Реализовано

### Описание
Программа, осуществляющая получение кода страниц сайта, собирающая ссылки с этих страниц, проверяющая их на работоспособность. 

### Алгоритм

Создан класс ссылки, содержащий саму ссылку, код ответа, сайт, заголовок страницы. 

```
class endpoint:
    def __init__(self, site, link, status, title):
        self.site = site
        self.link = link
        self.status = status
        self.title = title
```

В классе краулера содержится 2 поля: хранящее массив ссылок, которые находятся при парсинге страниц. И второе поле хранит словарь формата "ключ" - "класс ссылки". Храниние готовых ссылок в словаре исключает дублирование ссылок, позволяет хранить полную информацию о ней: включая код ответа и заголовок страницы. 

В первую очередь, собирается в однопотоке первоначальный список ссылок, необходимый для запуска автономных рабочих. Затем создается n рабочих (50), которые посещают ссылку, получают код ответа, заголовок страницы, из тела самой html страницы достают все ссылки, которые расположены на этой странице. 

Ссылка помещается в список посещенных при условиях: возникла сетевая ошибка при посещении, либо же если она успешно была изучена. 

Когда рабочий получает очередную ссылку из массива, он сначала проверяет не была ли уже эта ссылка посещена его коллегами-потоками. Не происходит повторное посещение ссылки, если она уже была изучена. 

Условия для прекращения исследования сайта: все ссылки были изучены- т.е. массив ссылок равен 0. Достигнута заданная глубина изучения- собрано удовлетворяющее колчество ссылок. Это количество настраивается в коде программы. 

```
max_depth = 10000
```

Для изменения глубины исследования сайта предусмотрена настройка, разрешающая при сканировании страниц посещать субдомены относительно текущей стартовой страницы. 

```
use_subdomains = False
```

После составления карты сайта, она сохраняется в csv и записывается в базу данных mysql. 

## Использованные библиотеки

| Библиотека    | Обоснование    |
| ----------- | ----------- |
| requests | Основная библиотека для работы краулера- получение сайта и ссылок идет через нее |
| re | Регулярные выражения. Вычленение ссылок, заголовков и полезной информации из ссылок |
| time | Замер времени сбора ссылок |
| pandas | Сохранение собранных данных в csv и базу данных. Не то чтобы она нужна, просто это дополнительная и не принципиальная задача |
| threading | реализация многопоточной работы идет через эту библиотеку |
| sqlalchemy | коннектор к базе данных |

## Известные проблемы

 1. В проекте не реализована работа с прокси- отсюда сайты, с защитой от сканирования не дают программе выполнить сканирование. 
 2. Нет браузерного движка- сайты, строящие свою работу на js не могут быть изучены. 
 3. Программа воспринимает схожие ссылки как разные, пусть и ведущие на один ресурс. 
 4. Время сканирования зависит от времени ответа сервера в большей степени, чем хотелось. 
 

## Результаты работы 




| url сайта    | время работы сек    | количество исследованных ссылок | Имя файла с результатом |
| ----------- | ----------- | ----------- | ----------- |
| http://crawler-test.com/  | 70-90 | 1266 | crawler-test.csv |
| http://google.com/ | 2017 | 10023 | google.com.csv |
| https://vk.com | 3896 | 10016 | vk.com.csv |
| https://dzen.ru | 0 | 0 | |
| https://stackoverflow.com | 0 | 0 | |



