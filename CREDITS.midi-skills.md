# Источники

Пак собран не с нуля. Перед сборкой изучены открытые наборы скиллов и первоисточники по площадкам, метрикам и российскому праву. Ни один скилл не скопирован: методики переписаны под русский язык, российские площадки и правило доказательности пака.

## Что взято как метод

| Источник | Что переиспользовано | Где живёт |
|---|---|---|
| [charlie947/social-media-skills](https://github.com/charlie947/social-media-skills) | паттерн «файлы голоса как фундамент, от которого зависят все остальные скиллы»; правило выбора «вёрстка против генерации»; лимит 15 слов на слайд; числовой порог качества как ворота | `cp-voice`, `cp-carousel`, `cp-image-prompt`, `cp-video-score` |
| [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills) | архитектура hub-and-spoke: единый контекстный корень, который читают все скиллы; матрица «пиллар × формат» с 8 форматами; скоринг приоритизации тем; разделение searchable против shareable | `context/08-brand-profile.md`, `cp-content-plan`, `AUTHORING.md` |
| [realkimbarrett/advertising-skills](https://github.com/realkimbarrett/advertising-skills) | уровни осознанности и уровни искушённости рынка как вход в выбор хука и оффера; идея механизма; QA-слой как отдельная ступень конвейера | `cp-audience`, `cp-offer`, конвейер качества |
| [obra/superpowers](https://github.com/obra/superpowers) | процессный слой: уточнение задачи диалогом до производства, план до исполнения, отдельная ступень ревью | оркестратор, конвейер качества |
| [anthropics/skills](https://github.com/anthropics/skills) | формат SKILL.md и прогрессивное раскрытие через `references/`; модель темы «палитра плюс пара шрифтов» | `AUTHORING.md`, `cp-design-system` |
| [aaron-he-zhu/seo-geo-claude-skills](https://github.com/aaron-he-zhu/seo-geo-claude-skills) | чек-листы качества контента и доверия к домену как проверяемые списки, работающие без платных API | `cp-seo` |
| [AgriciDaniel/claude-seo](https://github.com/AgriciDaniel/claude-seo) | схема аудита «наблюдение → зависимость → что делать → чем проверить»; разделение находок по серьёзности; трекинг изменений от базовой линии | `cp-seo`, `cp-web`, `cp-audit` |
| [zubair-trabzada/geo-seo-claude](https://github.com/zubair-trabzada/geo-seo-claude) | оценка цитируемости и анализ логов на предмет ИИ-краулеров | `cp-geo` |
| [ericosiu/ai-marketing-skills](https://github.com/ericosiu/ai-marketing-skills) | детекция аутлаеров от медианы канала и разбор их общих признаков; окна валидации 24 ч / 7 д / 28 д; дисциплина «паттерн не подтверждён, пока не проверен постфактум» | `cp-analytics`, `cp-analytics-cross` |
| [AgriciDaniel/claude-shorts](https://github.com/AgriciDaniel/claude-shorts) | взвешенная рубрика оценки сегмента с порогом включения | `cp-video-score`, `cp-clip` |
| [blader/humanizer](https://github.com/blader/humanizer) | идея каталога признаков машинного письма и двухпроходной переписки с аудитом | `cp-humanizer` — каталог собран заново под русский язык, логика перевёрнута: неровности речи сохраняются |
| [wondelai/skills](https://github.com/wondelai/skills) | уравнение ценности оффера; «работа, на которую нанимают продукт»; правила интервью без наводящих вопросов | `cp-offer`, `cp-audience` |
| [CosmoBlk/email-marketing-bible](https://github.com/CosmoBlk/email-marketing-bible) | блок доставляемости: аутентификация домена, прогрев, сегментация по вовлечённости, пошаговая диагностика | `cp-email` |
| [Hainrixz/open-carrusel](https://github.com/Hainrixz/open-carrusel) | правило WYSIWYG: превью и экспорт через одну функцию оборачивания слайда | `cp-carousel-render` |
| [lewislulu/html-ppt-skill](https://github.com/lewislulu/html-ppt-skill) | архитектура «тема — один файл токенов»; headless-экспорт в PNG | `cp-design-system`, `cp-carousel-render` |
| [op7418/guizang-ppt-skill](https://github.com/op7418/guizang-ppt-skill) (AGPL — взяты только идеи, не код) | закреплённые лейауты и валидатор вёрстки; правило «только пресетные палитры»; двойное ограничение размера текста | `cp-carousel-render`, `context/06-design.md` |
| [itchernetski/threads-carousel-claude-skill](https://github.com/itchernetski/threads-carousel-claude-skill) | таксономия типов слайдов; оси стиля вместо «придумай дизайн» | `cp-carousel` |
| [sergebulaev/instagram-skills](https://github.com/sergebulaev/instagram-skills) | каркас хук → польза → оплата обещания | `cp-carousel`, `cp-caption` |
| [czlonkowski/n8n-skills](https://github.com/czlonkowski/n8n-skills) | архитектура сценария автоматизации и обязательный блок обработки ошибок | `cp-automation` |
| [aaaronmiller/create-viral-content](https://github.com/aaaronmiller/create-viral-content) | идея адверсарного ревью независимыми персонами; чёрный список маркеров машинного письма | конвейер качества, `cp-humanizer` |

## Что изучено и не взято

| Источник | Почему |
|---|---|
| Каталоги-агрегаторы скиллов ([ComposioHQ](https://github.com/ComposioHQ/awesome-claude-skills), [VoltAgent](https://github.com/VoltAgent/awesome-agent-skills), [jqueryscript](https://github.com/jqueryscript/awesome-claude-code)) | это списки ссылок, а не скиллы. Использованы как навигация |
| [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) | значительная часть — переимпорт другого набора без атрибуции. Взято из первоисточника |
| [nowork-studio/toprank](https://github.com/nowork-studio/toprank) | вся телеметрия завязана на Google Ads, Meta Ads и Search Console — для России почти неприменимо. Взята только логика аудита по фиксированным измерениям |
| [skainguyen1412/social-media-research-skill](https://github.com/skainguyen1412/social-media-research-skill) | требует платных ключей и работает только по англоязычным Reddit и X |
| [SamurAIGPT/Generative-Media-Skills](https://github.com/SamurAIGPT/Generative-Media-Skills) | целиком зависит от платного шлюза к моделям |
| [nexu-io/open-design](https://github.com/nexu-io/open-design) | репозиторий целиком — десктопное приложение с демоном. Из скиллов взята только идея разделять оформление и содержание; в самих скиллах ни одной проверяемой цифры |
| [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) | это агентный фреймворк, то есть то, что запускает скиллы. Другой класс инструмента |
| [borghei/Claude-Skills](https://github.com/borghei/Claude-Skills) | содержит зашитые «стоимости лайка» и категории ROI без источника — образец того, чего пак избегает |
| Мобильные наборы (React Native, Flutter, iOS) | сильного набора в 2026 не обнаружено, все найденные маргинальны по качеству |
| Дефолтные шрифты всех перечисленных дизайн-скиллов | Inter забракован по качеству кириллического набора |

## Первоисточники фактуры

Фактическая часть — не из скиллов, а из первоисточников: справка и блог для вебмастеров Яндекса, справка Дзена, документация Telegram Bot API и статистики каналов, справка и документация YouTube, документация Meta для разработчиков, центр прозрачности TikTok, справка RuTube, документация краулеров OpenAI и Google Search, тексты законов и разъяснения регуляторов, замеры аудитории от независимого измерителя, исследования на выборках в миллионы публикаций с раскрытой методологией.

Все они процитированы внутри файлов `context/` с указанием уровня достоверности и даты. Там же — списки того, что устаревает и требует перепроверки.

## Про цифры

Ни один бенчмарк из англоязычных источников не перенесён напрямую. Пороги удержания, нормы вовлечённости, «оптимальные частоты публикаций» и стоимости контакта вычищены намеренно: они либо не имеют раскрытой методологии, либо получены на выборках, несопоставимых с российским рынком. Правило записано в `AUTHORING.md` и `context/07-evidence.md` и продублировано в красных линиях скиллов.

## Лицензии

Источники распространяются под MIT и Apache-2.0; один — под AGPL, и из него взяты только идеи, не код. Этот репозиторий — MIT. Поскольку переиспользованы методы и подходы, а не текст, прямых производных файлов здесь нет; ссылки выше даны как признание авторства идей.
