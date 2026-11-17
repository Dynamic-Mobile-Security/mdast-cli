# App Store: восстановление native authentication

## Проблема и границы

Контрольные загрузки 17.11.2026 на dev монолита и Kubernetes не проходят авторизацию Apple: старый Configurator 2.17 получает HTTP 204/404/301. В upstream ipatool исправление 001d889896fcb118546443c5dfe0997d11b74f56 поддерживает Configurator 2.21, native endpoint и Store AMD proof. Разрешённый scope: CLI, продуктовые потребители, MR и dev; production не обновлять.

## Решение

- Обновить checksum-pinned native helper до указанного upstream commit, сохранить проверку TLS, целостности assets и поддержку временного runtime cache.
- Сохранить точный native endpoint из Apple bag; не переписывать его в legacy path. Credentials и proof разрешены только на проверенных Apple endpoints.
- Добавить ограниченные операции helper для локальной machine identity, RP/SP provisioning и Store AMD proof. Пароли остаются в Python, helper получает только identity/challenge. Не использовать внешний anisette provider.
- Сохранить opaque provisioning state в существующей сессии аккаунта; старые сессии без этого поля читаются. Не вводить PVC, новые сервисы или shared identity между аккаунтами.
- Ограничить RP/SP переходы; не повторять неизвестный challenge или ошибку credentials. 2FA остаётся явным входом пользователя.
- Проверить потребность AMD в download endpoints; не посылать эти заголовки на CDN и произвольные redirect destinations.

## Приёмка

- Unit: native bag path, запрет постороннего host/path, RP/SP/success, неизвестный challenge, ограничение повторов, сохранение state, отсутствие секретов в ошибках.
- Build helper для поддерживаемых платформ; проверить старые sign/kbsync операции.
- Полный CLI CI, Markea unit/component/contract CI.
- Живая загрузка ранее доступного бесплатного приложения, валидный IPA. При требовании свежей 2FA зафиксировать реальный challenge и запросить код через локальный защищённый ввод.
- Нагрузку нового helper сначала измерять локально/изолированно. Не запускать диагностический helper в Markea REST с лимитом 256 MiB. Изменение ресурсов только через отдельный одобренный MR.

## Источники

- https://github.com/majd/ipatool/issues/642
- https://github.com/majd/ipatool/commit/001d889896fcb118546443c5dfe0997d11b74f56

## Проверка кандидата

Полный набор: 523 passed. Сборка helper с unit-проверкой allowlist выполнена для Linux/macOS/Windows amd64 и arm64. Живой cold start пока выполняется, успешный вход и IPA не подтверждены. Версия кандидата 2026.11.5, публикация после живой приёмки.
