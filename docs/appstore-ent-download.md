# App Store: восстановление скачивания через ent/download

Релиз `mdast-cli 2026.11.1` основан на проверенном кандидате 2026.11.1rc1 и main `84e9756`. Он предназначен для последующего включения в release Стинга 2026.11. Публикация CLI согласована в STG-5536; MR монолита и Markea готовятся отдельно, без изменения стендов.

## Причина и исправление

05.11.2026 установленная версия 2026.10.3 на двух стендах успешно авторизуется, но legacy `volumeStoreDownloadProduct` возвращает пустой `songList`, а `/r/redownload` отвечает HTTP 403. Результат одинаков при свежей сессии и на контрольном приложении. Историческое успешное скачивание на prod не подтверждает работоспособность текущего протокола.

После пустого legacy-ответа клиент использует объявленный Apple bag endpoint `/WebObjects/DownloadDispatch.woa/wa/ent/download`. Новая операция существующего SAP helper генерирует `kbsync`, данные, привязанные к устройству и числовому идентификатору аккаунта DSID. Запрос также передаёт `serialNumber` и точную `externalVersionId`. Реализация закреплена на ipatool v2.7.0 с проверкой Go module checksum; лицензия сохранена.

Проверяются endpoint, HTTPS, отсутствие redirect, App Store ID, версия, bundle ID и URL файла. Отказ Apple не превращается в успех по HTTP 200. `authorized=false` сам по себе не считается отказом, поскольку Apple возвращает его и с рабочим файлом. Credentials и kbsync не выводятся; отдельный helper получает данные через stdin. Успешный legacy-путь и fallback при отсутствии нового endpoint сохраняются.

Это подтверждает исправление совместимости клиента с текущим протоколом Apple. Конкретную внутреннюю причину отказа старого endpoint со стороны Apple определить по его ответам нельзя.

## Сборка и проверка

```sh
python tools/sap/build.py --target all --go /path/to/go
python -m pytest -q
python -m build --no-isolation
python tools/sap/verify_artifacts.py
```

Нужны Python 3.12+, зависимости проекта и сборки, Go из требования закреплённого upstream. В wheel и sdist включаются шесть SAP helpers: Linux, macOS, Windows для amd64/arm64. Runtime assets при первом использовании скачиваются upstream по закреплённым SHA256. Для изолированного кеша задаётся абсолютный `MDAST_SAP_CACHE_DIR`.

Спецификация и критерии: `specs/appstore-ent-download-20261105/spec.md`. Результаты реальных скачиваний фиксируются отдельно от mocked unit tests. Проверка CLI не заменяет будущую приёмку UI/REST/Celery после подключения пакета к релизу.

Существующий код загрузки байтов IPA использует отдельный `requests.get` без account headers и с `verify=False`; это поведение до данной правки, в её scope не меняется. Новый запрос получения download metadata всегда использует `verify=True`.

## Источники

- [Upstream: kbsync и новый download flow](https://github.com/majd/ipatool/commit/3411d57f451f5111ae115641c22f7ed17bbd5fbe).
- [Закреплённый upstream v2.7.0](https://github.com/majd/ipatool/tree/4484b55d366e177ae6c89758c61588712c572fad).
