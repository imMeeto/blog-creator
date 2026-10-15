# Рабочий шаблон слайда

Сохранить как `template.html` рядом с папкой `fonts/`. Открывается в браузере как превью и им же пользуется скрипт рендера — обе ветки зовут одну функцию `renderSlide`.

Раскладка папки:

```
project/
  template.html
  slides.json
  render.js
  fonts/GolosText-Regular.woff2  GolosText-Bold.woff2  GolosText-Black.woff2
  out/
```

## template.html

```html
<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<title>slide</title>
<style>
/* ---- шрифты: только локальные файлы, никакого CDN в момент рендера ---- */
@font-face{font-family:"Golos Text";src:url("./fonts/GolosText-Regular.woff2") format("woff2");font-weight:400;font-display:block}
@font-face{font-family:"Golos Text";src:url("./fonts/GolosText-Bold.woff2")    format("woff2");font-weight:700;font-display:block}
@font-face{font-family:"Golos Text";src:url("./fonts/GolosText-Black.woff2")   format("woff2");font-weight:900;font-display:block}

/* ---- ТЕМА: единственное место, которое меняется под бренд ---- */
:root{
  --bg:#0E1116;
  --surface:#171C24;
  --text:#F2F5F9;
  --text-muted:#A3AEBE;
  --accent:#FFB01F;
  --accent-dim:#FFC966;
  --font-head:"Golos Text", system-ui, sans-serif;
  --font-body:"Golos Text", system-ui, sans-serif;

  --w:1080px; --h:1350px;   /* размер слайда — один источник правды */
  --pad:64px;               /* безопасное поле, минимум 40px */
  --radius:0px;             /* скругления только если это решение темы */
}

*{margin:0;padding:0;box-sizing:border-box}
body{background:var(--bg);display:flex;align-items:flex-start;justify-content:center}

/* ---- слайд ---- */
.slide{
  width:var(--w); height:var(--h);
  container-type:size;            /* включает cqw / cqh внутри слайда */
  padding:var(--pad);
  background:var(--bg); color:var(--text);
  font-family:var(--font-body);
  display:flex; flex-direction:column; justify-content:space-between; gap:min(4cqh,48px);
  overflow:hidden;                /* видимая обрезка лучше невидимого выезда */
}

/* ---- типографика: двойное ограничение по ширине И по высоте ---- */
.h1  {font-family:var(--font-head);font-weight:900;line-height:1.03;letter-spacing:-.015em;
      font-size:min(9.2cqw,7.4cqh);text-wrap:balance}
.h2  {font-family:var(--font-head);font-weight:700;line-height:1.1;
      font-size:min(6.4cqw,5.1cqh);text-wrap:balance}
.body{font-size:min(5.0cqw,4.0cqh);line-height:1.32}                          /* ≈54px, ступень body 52–60 */
.small{font-size:min(4.07cqw,3.26cqh);line-height:1.35;color:var(--text-muted)} /* ≈44px, ступень small 42–44; 54/44 = 1,23 при пороге 1,15 */
.meta{font-size:min(3.0cqw,2.4cqh);color:var(--text-muted);   /* служебное: хэндл и номер слайда */
      display:flex;justify-content:space-between;align-items:center}
.accent{color:var(--accent)}
.num{font-family:var(--font-head);font-weight:900;line-height:.9;
     font-size:min(26cqw,20cqh);color:var(--accent)}

/* ---- блоки ---- */
.stack{display:flex;flex-direction:column;gap:min(2.4cqh,28px)}
.row{display:flex;gap:min(3cqw,32px)}
.row>*{flex:1 1 0}
.card{background:var(--surface);padding:min(4cqw,44px);border-radius:var(--radius)}
.item{display:flex;gap:min(2.4cqw,26px);align-items:baseline}
.item .marker{font-family:var(--font-head);font-weight:900;color:var(--accent);
              font-size:min(6.11cqw,4.89cqh);min-width:min(7cqw,80px)} /* ≈66px: маркер стоит рядом с .body, отношение 66/54 = 1,22 */
.rule{height:min(.8cqh,8px);background:var(--accent);width:min(16cqw,180px)}
.img{width:100%;height:min(52cqh,700px);object-fit:cover;border-radius:var(--radius);display:block}
.cta{background:var(--accent);color:var(--bg);padding:min(4cqw,44px);
     font-family:var(--font-head);font-weight:800;font-size:min(6.4cqw,5.1cqh);
     border-radius:var(--radius)}
/* текст на акцентной плашке — цветом фона: акцент обычно не проходит контраст с --text */

/* ---- превью: масштаб ТОЛЬКО снаружи слайда ---- */
#stage{transform-origin:top center}
</style>
</head>
<body>
  <div id="stage"><div class="slide" id="slide"></div></div>

<script>
/* ЕДИНСТВЕННАЯ функция оборачивания. Её зовёт и превью, и экспорт.
   Второй такой функции в проекте быть не должно. */
const esc = s => String(s ?? '').replace(/[&<>]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));
const li  = (arr, marked) => (arr || []).map((t,i) =>
  `<div class="item">${marked ? `<span class="marker">${i+1}</span>` : '<span class="marker">—</span>'}
   <span class="body">${esc(t)}</span></div>`).join('');

const BODY = {
  hook:    d => `<div class="stack"><div class="rule"></div>
                 <div class="h1">${esc(d.title)}</div>
                 ${d.sub ? `<div class="small">${esc(d.sub)}</div>` : ''}</div>`,
  thesis:  d => `<div class="stack"><div class="h2">${esc(d.title)}</div>
                 ${d.text ? `<div class="body">${esc(d.text)}</div>` : ''}</div>`,
  list:    d => `<div class="stack"><div class="h2">${esc(d.title)}</div>
                 <div class="stack">${li(d.items,false)}</div></div>`,
  steps:   d => `<div class="stack"><div class="h2">${esc(d.title)}</div>
                 <div class="stack">${li(d.items,true)}</div></div>`,
  check:   d => `<div class="stack"><div class="h2">${esc(d.title)}</div>
                 <div class="stack">${(d.items||[]).map(t =>
                   `<div class="item"><span class="marker">☑</span>
                    <span class="body">${esc(t)}</span></div>`).join('')}</div></div>`,
  number:  d => `<div class="stack"><div class="num">${esc(d.value)}</div>
                 <div class="body">${esc(d.text)}</div>
                 <div class="small">Источник: ${esc(d.source)} · ${esc(d.date)}</div></div>`,
  quote:   d => `<div class="stack card"><div class="h2">«${esc(d.text)}»</div>
                 <div class="small">${esc(d.author)}${d.source ? ' · ' + esc(d.source) : ''}</div></div>`,
  compare: d => `<div class="stack"><div class="h2">${esc(d.title)}</div>
                 <div class="row">
                   <div class="card"><div class="small">${esc(d.leftTitle)}</div>
                        <div class="body">${esc(d.left)}</div></div>
                   <div class="card"><div class="small accent">${esc(d.rightTitle)}</div>
                        <div class="body">${esc(d.right)}</div></div></div></div>`,
  image:   d => `<div class="stack"><img class="img" src="${esc(d.src)}" alt="">
                 ${d.caption ? `<div class="small">${esc(d.caption)}</div>` : ''}</div>`,
  cta:     d => `<div class="stack"><div class="h2">${esc(d.title)}</div>
                 <div class="cta">${esc(d.action)}</div></div>`
};

function renderSlide(d){
  const el = document.getElementById('slide');
  const body = (BODY[d.type] || BODY.thesis)(d);
  el.innerHTML = `
    <div class="meta"><span>${esc(d.brand || '')}</span><span>${esc(d.kicker || '')}</span></div>
    ${body}
    <div class="meta"><span>${esc(d.footer || '')}</span>
      <span>${d.n ? esc(d.n) + '/' + esc(d.total) : ''}</span></div>`;
  return el;
}
window.renderSlide = renderSlide;

/* превью в браузере: масштабируется ОБЁРТКА, слайд внутри не трогается */
function fitPreview(){
  const s = Math.min(1, (window.innerHeight - 40) / 1350);
  document.getElementById('stage').style.transform = `scale(${s})`;
}
window.addEventListener('resize', fitPreview); fitPreview();

/* демо-слайд, чтобы страница не была пустой при открытии руками */
if (!window.__noDemo) renderSlide({
  type:'hook', brand:'BRAND', kicker:'каркас: обучающая',
  title:'Заявки есть. Денег нет', sub:'разбираю, где теряется путь клиента',
  n:1, total:9, footer:''
});
</script>
</body>
</html>
```

## slides.json

Порядок массива = порядок публикации. Поле `type` берётся из таксономии типов слайдов (`cp-carousel`).

```json
[
  {"type":"hook","title":"Заявки есть. Денег нет","sub":"где теряется путь клиента","n":1,"total":9,"brand":"BRAND"},
  {"type":"hook","title":"Если считаешь заявки, а не сделки — это тебе","n":2,"total":9,"brand":"BRAND"},
  {"type":"thesis","title":"Заявка — не результат","text":"Результат — оплата. Всё между ними нужно измерить.","n":3,"total":9,"brand":"BRAND"},
  {"type":"steps","title":"Как посчитать","items":["Разбей путь на пять точек","Посчитай, сколько проходит каждую","Найди точку с потерей больше половины"],"n":4,"total":9,"brand":"BRAND"},
  {"type":"number","value":"5","text":"точек достаточно, чтобы увидеть провал","source":"собственный замер","date":"04.08.2026","n":5,"total":9,"brand":"BRAND"},
  {"type":"compare","title":"Как не надо и как надо","leftTitle":"Обычно","left":"Чиним всё сразу","rightTitle":"Работает","right":"Одна правка, две недели замера","n":6,"total":9,"brand":"BRAND"},
  {"type":"check","title":"Проверь у себя","items":["Точки описаны","Цифры собраны","Правка одна","Срок замера назначен"],"n":7,"total":9,"brand":"BRAND"},
  {"type":"quote","text":"Порог — собственная медиана, а не чужой бенчмарк","author":"правило пака","source":"context/07-evidence.md","n":8,"total":9,"brand":"BRAND"},
  {"type":"cta","title":"Забери себе","action":"Сохрани — пригодится на планёрке","n":9,"total":9,"brand":"BRAND"}
]
```

## Что менять под другую площадку

Только `--w`, `--h` и при необходимости `--pad`. Кегли пересчитаются сами, потому что заданы в `cqw` и `cqh`.

| Площадка | `--w` | `--h` | `--pad` |
|---|---|---|---|
| Карусель и пост Instagram | 1080px | 1350px | 64px |
| Квадрат ВК, универсальный | 1080px | 1080px | 64px |
| Сторис | 1080px | 1920px | 80px, плюс безопасная зона (см. ниже) |
| Превью YouTube | 1280px | 720px | 56px, правый нижний угол свободен под таймкод |
| Карточка VK Рекламы | 600px | 600px | 40px, важное вне 10% сверху и по бокам |
| Страница PDF, A4 150 dpi | 1240px | 1754px | 96px |

**Безопасная зона вертикального кадра 1080×1920.** Подтверждено только для ВК: отступы **200 px** сверху и снизу (уровень C, вторичный источник). У остальных площадок официальных чисел нет — зона проверяется тестовым кадром на реальном устройстве. Субтитры — не ниже **20% высоты от низа** (уровень C, ремесленная практика).

В `render.js` viewport выставляется тем же числом, что `--w` и `--h`, иначе элемент не поместится в кадр и скриншот придётся прокручивать.

## Проверка шаблона за две минуты

1. Открыть `template.html` в обычном браузере — виден демо-слайд, шрифт не системный.
2. В консоли: `document.fonts.check('900 96px "Golos Text"')` → `true`.
3. `renderSlide({type:'list',title:'Проверка длинной кириллической строки в заголовке',items:['раз','два','три']})` — ничего не выехало за рамку.
4. Запустить `render.js` на трёх слайдах, открыть PNG как файлы.
5. Сверить PNG с превью: расхождение означает, что где-то появилась вторая функция оборачивания.
