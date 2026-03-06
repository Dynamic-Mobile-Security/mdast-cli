# Примеры команд для скачивания приложений

Этот файл содержит примеры команд для тестирования скачивания приложений из всех поддерживаемых distribution systems.

## Общий формат

Все примеры используют флаг `--download_only` (или `-d`) для скачивания без запуска сканирования.

---

## 1. Local File (Локальный файл)

Скачивание не требуется - используется существующий файл.

```bash
# Просто проверка существования файла
mdast_cli -d \
  --distribution_system file \
  --file_path /path/to/your/app.apk
```

**Пример с реальным файлом:**
```bash
mdast_cli -d \
  --distribution_system file \
  --file_path ./my_app.apk
```

---

## 2. Google Play

### С использованием OAuth2 токена (первый запуск)

```bash
mdast_cli -d \
  --distribution_system google_play \
  --google_play_package_name com.instagram.android \
  --google_play_email your.email@gmail.com \
  --google_play_oauth2_token "YOUR_OAUTH2_TOKEN" \
  --google_play_file_name instagram_latest
```

### С использованием AAS токена (последующие запуски)

```bash
mdast_cli -d \
  --distribution_system google_play \
  --google_play_package_name com.instagram.android \
  --google_play_email your.email@gmail.com \
  --google_play_aas_token "YOUR_AAS_TOKEN" \
  --google_play_file_name instagram_latest
```

### С прокси

```bash
mdast_cli -d \
  --distribution_system google_play \
  --google_play_package_name com.whatsapp \
  --google_play_email your.email@gmail.com \
  --google_play_aas_token "YOUR_AAS_TOKEN" \
  --google_play_proxy "socks5://username:password@proxy.example.com:1080"
```

### Популярные пакеты для тестирования

```bash
# Instagram
mdast_cli -d \
  --distribution_system google_play \
  --google_play_package_name com.instagram.android \
  --google_play_email your.email@gmail.com \
  --google_play_aas_token "YOUR_AAS_TOKEN"

# WhatsApp
mdast_cli -d \
  --distribution_system google_play \
  --google_play_package_name com.whatsapp \
  --google_play_email your.email@gmail.com \
  --google_play_aas_token "YOUR_AAS_TOKEN"

# Telegram
mdast_cli -d \
  --distribution_system google_play \
  --google_play_package_name org.telegram.messenger \
  --google_play_email your.email@gmail.com \
  --google_play_aas_token "YOUR_AAS_TOKEN"

# VK
mdast_cli -d \
  --distribution_system google_play \
  --google_play_package_name com.vkontakte.android \
  --google_play_email your.email@gmail.com \
  --google_play_aas_token "YOUR_AAS_TOKEN"
```

---

## 3. AppStore

### С использованием App ID

```bash
mdast_cli -d \
  --distribution_system appstore \
  --appstore_app_id YOUR_APP_ID \
  --appstore_apple_id your.email@icloud.com \
  --appstore_password "YOUR_PASSWORD" \
  --appstore_2FA YOUR_2FA_CODE \
  --appstore_file_name my_app
```

### С использованием Bundle ID

```bash
mdast_cli -d \
  --distribution_system appstore \
  --appstore_bundle_id com.example.myapp \
  --appstore_apple_id your.email@icloud.com \
  --appstore_password "YOUR_PASSWORD" \
  --appstore_2FA YOUR_2FA_CODE \
  --appstore_file_name my_app
```

### Примеры популярных приложений

```bash
# Instagram (App ID: 389801252)
mdast_cli -d \
  --distribution_system appstore \
  --appstore_app_id 389801252 \
  --appstore_apple_id your.email@icloud.com \
  --appstore_password "YOUR_PASSWORD" \
  --appstore_2FA YOUR_2FA_CODE

# WhatsApp (App ID: 310633997)
mdast_cli -d \
  --distribution_system appstore \
  --appstore_app_id 310633997 \
  --appstore_apple_id your.email@icloud.com \
  --appstore_password "YOUR_PASSWORD" \
  --appstore_2FA YOUR_2FA_CODE
```

---

## 4. Firebase

### Android приложение (APK)

```bash
mdast_cli -d \
  --distribution_system firebase \
  --firebase_project_number YOUR_PROJECT_NUMBER \
  --firebase_app_id "YOUR_FIREBASE_APP_ID" \
  --firebase_account_json_path /path/to/service_account.json \
  --firebase_file_extension apk \
  --firebase_file_name my_android_app
```

### iOS приложение (IPA)

```bash
mdast_cli -d \
  --distribution_system firebase \
  --firebase_project_number YOUR_PROJECT_NUMBER \
  --firebase_app_id "YOUR_FIREBASE_APP_ID" \
  --firebase_account_json_path /path/to/service_account.json \
  --firebase_file_extension ipa \
  --firebase_file_name my_ios_app
```

### Без указания имени файла (используется версия из Firebase)

```bash
mdast_cli -d \
  --distribution_system firebase \
  --firebase_project_number YOUR_PROJECT_NUMBER \
  --firebase_app_id "YOUR_FIREBASE_APP_ID" \
  --firebase_account_json_path ./service_account.json \
  --firebase_file_extension apk
```

---

## 5. Nexus Repository (Nexus 3.x)

```bash
mdast_cli -d \
  --distribution_system nexus \
  --nexus_url https://nexus.example.com \
  --nexus_login YOUR_NEXUS_USERNAME \
  --nexus_password YOUR_NEXUS_PASSWORD \
  --nexus_repo_name releases \
  --nexus_group_id com.example \
  --nexus_artifact_id myapp \
  --nexus_version 1.0.0
```

### Пример с локальным Nexus

```bash
mdast_cli -d \
  --distribution_system nexus \
  --nexus_url http://localhost:8081 \
  --nexus_login YOUR_NEXUS_USERNAME \
  --nexus_password YOUR_NEXUS_PASSWORD \
  --nexus_repo_name maven-releases \
  --nexus_group_id com.mycompany \
  --nexus_artifact_id mobile-app \
  --nexus_version 2.5.1
```

---

## 6. Nexus2 Repository

```bash
mdast_cli -d \
  --distribution_system nexus2 \
  --nexus2_url http://nexus:8081/nexus/ \
  --nexus2_login YOUR_NEXUS_USERNAME \
  --nexus2_password YOUR_NEXUS_PASSWORD \
  --nexus2_repo_name releases \
  --nexus2_group_id com.example \
  --nexus2_artifact_id myapp \
  --nexus2_version 1.337 \
  --nexus2_extension apk \
  --nexus2_file_name my_app_from_nexus2
```

### Пример с кастомным именем файла

```bash
mdast_cli -d \
  --distribution_system nexus2 \
  --nexus2_url http://nexus.example.com:8081/nexus/ \
  --nexus2_login YOUR_NEXUS_USERNAME \
  --nexus2_password YOUR_NEXUS_PASSWORD \
  --nexus2_repo_name snapshots \
  --nexus2_group_id org.myproject \
  --nexus2_artifact_id android-app \
  --nexus2_version 1.0.0-SNAPSHOT \
  --nexus2_extension apk \
  --nexus2_file_name production_build
```

---

## 7. RuStore

```bash
mdast_cli -d \
  --distribution_system rustore \
  --rustore_package_name ru.example.app
```

### Примеры популярных приложений из RuStore

```bash
# VK
mdast_cli -d \
  --distribution_system rustore \
  --rustore_package_name com.vkontakte.android

# Яндекс.Браузер
mdast_cli -d \
  --distribution_system rustore \
  --rustore_package_name com.yandex.browser

# Сбербанк Онлайн
mdast_cli -d \
  --distribution_system rustore \
  --rustore_package_name ru.sberbank.sberbankid
```

---

## 8. AppGallery (Huawei)

```bash
mdast_cli -d \
  --distribution_system appgallery \
  --appgallery_app_id C101184875 \
  --appgallery_file_name huawei_app
```

### Примеры популярных приложений

```bash
# Instagram в AppGallery
mdast_cli -d \
  --distribution_system appgallery \
  --appgallery_app_id C101184875 \
  --appgallery_file_name instagram_huawei

# WhatsApp в AppGallery
mdast_cli -d \
  --distribution_system appgallery \
  --appgallery_app_id C100000001 \
  --appgallery_file_name whatsapp_huawei
```

**Примечание:** App ID можно найти на странице приложения в AppGallery в URL.

---

## 9. RuMarket

```bash
mdast_cli -d \
  --distribution_system rumarket \
  --rumarket_package_name com.example.app
```

### Примеры

```bash
# Любое приложение по package name
mdast_cli -d \
  --distribution_system rumarket \
  --rumarket_package_name ru.play.market.app
```

---

## Полезные опции

### Указание кастомной директории для скачивания

```bash
mdast_cli -d \
  --distribution_system google_play \
  --google_play_package_name com.example.app \
  --google_play_email your.email@gmail.com \
  --google_play_aas_token "YOUR_TOKEN" \
  --download_path /custom/path/to/downloads
```

### Проверка вывода (для CI/CD)

```bash
# Команда выведет DOWNLOAD_PATH=/path/to/app.apk
mdast_cli -d \
  --distribution_system google_play \
  --google_play_package_name com.example.app \
  --google_play_email your.email@gmail.com \
  --google_play_aas_token "YOUR_TOKEN" \
  | grep DOWNLOAD_PATH
```

### Использование переменных окружения

```bash
# Установите переменные
export GOOGLE_PLAY_EMAIL="your.email@gmail.com"
export GOOGLE_PLAY_AAS_TOKEN="your_token_here"

# Используйте в команде
mdast_cli -d \
  --distribution_system google_play \
  --google_play_package_name com.example.app \
  --google_play_email "$GOOGLE_PLAY_EMAIL" \
  --google_play_aas_token "$GOOGLE_PLAY_AAS_TOKEN"
```

---

## Тестирование всех систем

### Скрипт для тестирования всех distribution systems

```bash
#!/bin/bash
set -e

DOWNLOAD_DIR="./test_downloads"
mkdir -p "$DOWNLOAD_DIR"

echo "Testing all distribution systems..."

# 1. Local File
echo "1. Testing Local File..."
mdast_cli -d \
  --distribution_system file \
  --file_path ./test.apk \
  --download_path "$DOWNLOAD_DIR" || echo "  ⚠️  Local file test skipped (file not found)"

# 2. Google Play
echo "2. Testing Google Play..."
if [ -n "$GOOGLE_PLAY_AAS_TOKEN" ]; then
  mdast_cli -d \
    --distribution_system google_play \
    --google_play_package_name com.instagram.android \
    --google_play_email "$GOOGLE_PLAY_EMAIL" \
    --google_play_aas_token "$GOOGLE_PLAY_AAS_TOKEN" \
    --download_path "$DOWNLOAD_DIR" && echo "  ✅ Google Play OK"
else
  echo "  ⚠️  Google Play skipped (no token)"
fi

# 3. AppStore
echo "3. Testing AppStore..."
if [ -n "$APPSTORE_PASSWORD" ]; then
  mdast_cli -d \
    --distribution_system appstore \
    --appstore_app_id YOUR_APP_ID \
    --appstore_apple_id "$APPSTORE_APPLE_ID" \
    --appstore_password "$APPSTORE_PASSWORD" \
    --appstore_2FA "$APPSTORE_2FA" \
    --download_path "$DOWNLOAD_DIR" && echo "  ✅ AppStore OK"
else
  echo "  ⚠️  AppStore skipped (no credentials)"
fi

# 4. Firebase
echo "4. Testing Firebase..."
if [ -f "$FIREBASE_SERVICE_ACCOUNT" ]; then
  mdast_cli -d \
    --distribution_system firebase \
    --firebase_project_number "$FIREBASE_PROJECT_NUMBER" \
    --firebase_app_id "$FIREBASE_APP_ID" \
    --firebase_account_json_path "$FIREBASE_SERVICE_ACCOUNT" \
    --firebase_file_extension apk \
    --download_path "$DOWNLOAD_DIR" && echo "  ✅ Firebase OK"
else
  echo "  ⚠️  Firebase skipped (no service account)"
fi

# 5. Nexus
echo "5. Testing Nexus..."
if [ -n "$NEXUS_URL" ]; then
  mdast_cli -d \
    --distribution_system nexus \
    --nexus_url "$NEXUS_URL" \
    --nexus_login "$NEXUS_LOGIN" \
    --nexus_password "$NEXUS_PASSWORD" \
    --nexus_repo_name "$NEXUS_REPO_NAME" \
    --nexus_group_id "$NEXUS_GROUP_ID" \
    --nexus_artifact_id "$NEXUS_ARTIFACT_ID" \
    --nexus_version "$NEXUS_VERSION" \
    --download_path "$DOWNLOAD_DIR" && echo "  ✅ Nexus OK"
else
  echo "  ⚠️  Nexus skipped (no configuration)"
fi

# 6. Nexus2
echo "6. Testing Nexus2..."
if [ -n "$NEXUS2_URL" ]; then
  mdast_cli -d \
    --distribution_system nexus2 \
    --nexus2_url "$NEXUS2_URL" \
    --nexus2_login "$NEXUS2_LOGIN" \
    --nexus2_password "$NEXUS2_PASSWORD" \
    --nexus2_repo_name "$NEXUS2_REPO_NAME" \
    --nexus2_group_id "$NEXUS2_GROUP_ID" \
    --nexus2_artifact_id "$NEXUS2_ARTIFACT_ID" \
    --nexus2_version "$NEXUS2_VERSION" \
    --nexus2_extension apk \
    --download_path "$DOWNLOAD_DIR" && echo "  ✅ Nexus2 OK"
else
  echo "  ⚠️  Nexus2 skipped (no configuration)"
fi

# 7. RuStore
echo "7. Testing RuStore..."
mdast_cli -d \
  --distribution_system rustore \
  --rustore_package_name com.vkontakte.android \
  --download_path "$DOWNLOAD_DIR" && echo "  ✅ RuStore OK"

# 8. AppGallery
echo "8. Testing AppGallery..."
mdast_cli -d \
  --distribution_system appgallery \
  --appgallery_app_id C101184875 \
  --download_path "$DOWNLOAD_DIR" && echo "  ✅ AppGallery OK"

# 9. RuMarket
echo "9. Testing RuMarket..."
mdast_cli -d \
  --distribution_system rumarket \
  --rumarket_package_name com.example.app \
  --download_path "$DOWNLOAD_DIR" && echo "  ✅ RuMarket OK"

echo ""
echo "✅ Testing completed! Check $DOWNLOAD_DIR for downloaded files"
```

---

## Docker примеры

### Google Play через Docker

```bash
docker run -it \
  -v $(pwd)/downloads:/mdast/downloads \
  mobilesecurity/mdast_cli:latest \
  -d \
  --distribution_system google_play \
  --google_play_package_name com.instagram.android \
  --google_play_email your.email@gmail.com \
  --google_play_aas_token "YOUR_TOKEN" \
  --download_path /mdast/downloads
```

### Firebase через Docker

```bash
docker run -it \
  -v $(pwd)/service_account.json:/mdast/service_account.json \
  -v $(pwd)/downloads:/mdast/downloads \
  mobilesecurity/mdast_cli:latest \
  -d \
  --distribution_system firebase \
  --firebase_project_number YOUR_PROJECT_NUMBER \
  --firebase_app_id "YOUR_FIREBASE_APP_ID" \
  --firebase_account_json_path /mdast/service_account.json \
  --firebase_file_extension apk \
  --download_path /mdast/downloads
```

---

## Отладка

### Включение подробных логов

```bash
# Python logging level
export PYTHONUNBUFFERED=1

mdast_cli -d \
  --distribution_system google_play \
  --google_play_package_name com.example.app \
  --google_play_email your.email@gmail.com \
  --google_play_aas_token "YOUR_TOKEN" \
  2>&1 | tee download.log
```

### Проверка только синтаксиса команды

```bash
# Проверка без выполнения (если поддерживается)
mdast_cli --help | grep -A 5 "google_play"
```

---

## Примечания

1. **Безопасность**: Никогда не коммитьте токены, пароли или ключи в репозиторий
2. **Переменные окружения**: Используйте переменные окружения для чувствительных данных
3. **Таймауты**: Большие файлы могут требовать больше времени для скачивания
4. **Права доступа**: Убедитесь, что у вас есть права на запись в `--download_path`
5. **Сеть**: Некоторые distribution systems могут требовать стабильного интернет-соединения

---

## Быстрая справка

```bash
# Показать все доступные опции
mdast_cli --help

# Показать help для конкретной distribution system
mdast_cli --distribution_system google_play --help 2>&1 | head -20
```

