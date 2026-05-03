# MCP серверы проекта

Все MCP настроены глобально в `~/.claude.json`.
Эта папка содержит документацию по каждому серверу.

## Установленные MCP

| Сервер | Тип | Статус | Файл |
|--------|-----|--------|------|
| context7 | stdio | ✅ Подключён | [context7.md](context7.md) |
| fs | stdio | ✅ Подключён | [filesystem.md](filesystem.md) |
| notion | HTTP | ⚠️ Нужна авторизация | [notion.md](notion.md) |
| figma | HTTP | ⚠️ Нужна авторизация | [figma.md](figma.md) |
| github | HTTP | ❌ Не подключён | [github.md](github.md) |

## Добавить MCP

```bash
claude mcp add --scope user <имя> -- npx -y <пакет>@<версия>
```

⚠️ Всегда фиксировать версию — никогда `@latest`
