# aggregator
Web-application to search it-vacancies

Приложение разрабатываются с помощью итеративного подхода. Благодаря этому можно гораздо быстрее получить первые результаты и менять требования по ходу разработки. Требования на первую итерацию отражены на схеме:

![requirements](https://github.com/Nutrymaco/aggregator/blob/master/Screenshot1.png)

Текущая схема приложения выглядит вот так:

![schema](https://github.com/Nutrymaco/aggregator/blob/master/Screenshot3.png)

Некоторые пояснения:
  1) Приложения разрабатывается с помощью фреймворка Django.
  2) Использование Redis обусловлено тем, что она хранит данные в основной памяти, что дает быстрый доступ к ним. Для хранения данных в Redis используется встроенная структура данных хэши, она позволяет получить значение хэша со сложностью O(1). Данные, хранящиеся в Redis выглядит так: hash:"key word" field:"vacancy id" value:"count key word in vacancy". На данной итерации подсчет слов не используется, но на ближайших итерациях планируется ввести метрику TF-IDF, как хорошо себя зарекомендовавшую для ранжирования ключевых слов в тексте и при этом простую в реализации.
  3) В конце предыдущего пункта была затронута тема ранжирования, на данной итерации эта задача не ставится, так как необходимо проверить как справится данная архитектура с нагрузкой.
  4) Для того, чтобы работа скраперов не блокировала работу приложения используется Celery, так как это самое удобная реализация асинхронных задач для Django. 
  5) Обработка текста производится путем разбиения на слова, отбросом не несущих смысла частей речи (предлогов, союзов и т. д.), а затем лемматизации - приведения их в начальную форму.
