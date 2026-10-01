# apkeep для Стинга

Upstream apkeep 1.0.0 и gpapi 6.1.0 закреплены SHA256 в `upstream.json`.
Патч воспроизводимо добавляет профиль `sting_x86_64` на основе телефона `px_9a`:
Идентичность устройства берётся из upstream `google_kiwi_x86_64`, возможности телефона и SDK из `px_9a`. С идентичностью Pixel Google возвращает ARM даже при объявленной единственной ABI x86_64; профиль kiwi без возможностей телефона ограничивает доступность приложений.
Единственная ABI первого профиля: x86_64. Профиль используется по умолчанию.
ARM используется только при отдельной повторной попытке исходным профилем px_9a; фактическая ABI проверяется в CLI.

Дополнительно ошибки Google Play печатаются в stderr без зависимости от TTY,
отказ выдачи имеет маркер `STING_APP_UNAVAILABLE`, неудачная загрузка возвращает
код 3. CLI делает один повтор с исходным ARM-профилем только при этом маркере,
а не при ошибках сети, авторизации или повреждённом APK.

Подготовка источников и сборка macOS ARM64:

```sh
python tools/apkeep/build.py --directory /tmp/sting-apkeep --name apkeep-darwin-arm64
```

Для macOS Intel добавить `--target x86_64-apple-darwin --name apkeep-darwin-x86_64`.
Для Linux собрать подготовленные источники с musl в rust:1.91-alpine,
с установленными build-base, cmake, perl, pkgconf, openssl-dev,
openssl-libs-static, protobuf-dev и linux-headers; задать OPENSSL_STATIC=1.
`cargo build --release --locked` не обновляет upstream зависимости.
Host-архитектура бинарника независима от ABI скачиваемого Android-приложения.

Готовый бинарник включается в пакет командой `build.py --directory ... --install
<binary> --name apkeep-linux-x86_64` (либо `apkeep-linux-arm64`). Команда записывает
SHA256 в `mdast_cli/bin/apkeep-manifest.json`. Linux-сборки должны быть статическими,
чтобы работать в Alpine Markea и Debian монолита. В wheel/sdist входят бинарники,
manifest и MIT-лицензии apkeep/gpapi. Код CLI проверяет manifest, SHA256 и версию
бинарника до передачи credentials.

Проверка 30.09.2026 (STG-5356): реальная загрузка Firefox с этим профилем содержит split `config.x86_64.apk` и библиотеки `lib/x86_64`. Изменение только Platforms при сохранении идентичности Pixel возвращало ARM64. Контроль ошибки CDN возвращает DOWNLOAD_FAILED, без перехода на ARM. Локальные проверки CLI: 304 passed.

Изменение 01.10.2026: `1.0.0-sting.2` включает reqwest feature `socks` для всех
платформ. Внутренние повторы apkeep удалены: CLI повторяет только ошибку с
`STING_DOWNLOAD_ERROR`, в новом временном каталоге и в пределах общего timeout.
Поддержка proxy не меняет x86_64-профиль и правила ARM fallback.

Исправление TLS macOS 01.10.2026: `1.0.0-sting.3` оставляет native-tls-no-alpn
только для платформ кроме macOS. На macOS весь reqwest, включая загрузчик APK,
использует rustls со штатной проверкой сертификатов и системного доверия.
Запросы gpapi явно используют HTTP/1.1 поверх HTTPS, сохраняя поведение прежнего
native-tls-no-alpn; HTTP/2 приводит к PROTOCOL_ERROR на запросе авторизации.
На Linux TLS-backend и создание клиента не меняются. Python-зависимости не обновляются.
