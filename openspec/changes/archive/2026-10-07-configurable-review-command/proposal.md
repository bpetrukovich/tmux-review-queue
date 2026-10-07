# Proposal

## Why

Команда ревью зашита в домен жёстко (`nvim +'DiffviewOpen <base>..<ref>'` в спеке и коммите; в рабочей директории — незакоммиченный эксперимент `nvim +'CodeDiff <base>  <ref>'`). Чтобы сменить диф-тул (например, на `nvim codediff`), приходится править код. Нужен конфиг в духе `multi-sessionizer`: файл в `~/.config`, шаблон команды с плейсхолдерами под `base` и `ref`.

## What Changes

- **Новый обязательный конфиг** `~/.config/tmux-review-queue/config.toml` (путь переопределяется `TMUX_REVIEW_QUEUE_CONFIG`), по конвенциям msz. Файл обязателен: при его отсутствии печатаем скелет-пример и выходим с ненулевым кодом, ничего не регистрируя. **BREAKING**: `add` теперь требует конфиг.
- **Ключ `[review].command`** — shell-шаблон команды ревью с плейсхолдерами `{base}` и `{ref}`. Подстановка — из полей каждого репозитория task-документа.
- **Валидация конфига**: команда обязательна и непуста; обязательны **оба** плейсхолдера `{base}` и `{ref}`; неизвестные плейсхолдеры вида `{...}` — ошибка. Список проблем печатается целиком, регистрация не выполняется.
- **Поддержка только `{base}`/`{ref}`** — никаких `{repo}`, `{path}` и т.п.; остальное приходит только из API (task JSON).
- **Генерация workspace** (требование «Review workspace generation») меняется: вместо зашитой команды — подстановка из конфига.
- **Разрешение рассинхрона**: незакоммиченная правка `CodeDiff` в `workspaces.py` устаревает — команда переезжает в конфиг.

## Capabilities

### New Capabilities
- `review-queue-config`: обязательный TOML-конфиг — путь и переопределение через env, чтение, скелет при отсутствии, валидация шаблона команды (`[review].command`, плейсхолдеры `{base}`/`{ref}`).

### Modified Capabilities
- `review-queue`: требование «Review workspace generation» — команда в workspace становится конфигурируемой (`[review].command` с подстановкой `{base}`/`{ref}` вместо зашитой `nvim +'DiffviewOpen <base>..<ref>'`).

## Impact

- `src/tmux_review_queue/domain/workspaces.py` — `workspace_yaml`/`group_yaml` принимают команду; новый чистый `render_command`.
- Новый `infrastructure/config_loader.py` (чтение TOML через `tomllib`, stdlib 3.12).
- App-слой: DTO `Config` + `ConfigError`, проброс команды через `FlowDeps` (`app/ports.py`, `app/flows.py`).
- `main.py` — композиция корня: загрузка конфига до `add_flow`.
- Тесты: `workspaces` (подстановка), новые `config_loader`/`flows` (валидация, скелет).
- Зависимости: без новых — `tomllib` в stdlib (Python >=3.12).