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

## Холодная загрузка runtime

Живая первая подготовка превышает 25 минут; kernel ZIP entry читается flate-reader небольшими ReadAt, каждый порождает HTTP Range. Добавить только для kernel entry буфер 2 MiB перед распаковкой. Сохранить pinned compressed/uncompressed sizes, CRC ZIP, SHA256 итоговых assets и общий deadline. Проверить количество чтений на synthetic ZIP, повреждённый архив, превышение лимита, равенство распакованных байтов. Guarded patch применяется только к checksum-verified upstream. Это не разрешает менять TLS, источники или инфраструктуру.

Повтор на 256 KiB не уложился в отдельный пятиминутный тест kernel: около 126 последовательных Range. Увеличить только этот bounded sequential buffer до 2 MiB (около 16 запросов на pinned entry). Проверка synthetic 2 MiB ZIP допускает не более четырёх ReadAt с учётом заголовка. Дополнительная память буфера менее 2 MiB.

## Память native authentication

Живая CLI загрузка IPA успешна, но общий пик Python и helper составил 905504 KiB (около 884 MiB). Во время RP/SP provisioning остаётся открыт SAP signer и запускается второй emulator. Для Markea REST с limit 1Gi это оставляет мало запаса на HTTP-сервис.

Перед выпуском выполнять native identity/provisioning и SAP signing последовательно: signer открывается только на signed authentication request и закрывается до следующего identity operation. Legacy auth и формат persisted state не меняются. Приёмка: тест запрещает overlap signer/identity в успешном и ошибочном RP/SP flow; полный suite; новый живой вход с замером памяти. Повторная загрузка того же IPA не нужна, если download path не меняется и предыдущий архив прошёл проверку.
