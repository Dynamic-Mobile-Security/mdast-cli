import logging
import os
import zipfile

import requests

from mdast_cli.helpers.file_utils import ensure_download_dir, cleanup_file

logger = logging.getLogger(__name__)


def get_app_info(package_name):
    """
    Обработка метаданных приложения RuStore и получение URL-адреса для прямой загрузки.
    Изменения по сравнению с исходной реализацией:
    - Добавлены явные заголовки (User-Agent, Accept) и таймауты ко всем HTTP-вызовам.
    - Проверяется структура JSON-ответов (проверяется наличие «body» и «apkUrl»).
    - Исправлена ошибка, при которой статус POST проверялся по предыдущему ответу GET.
    - Предоставляются подробные сообщения об ошибках со статусом и фрагментом ответа.
    """
    common_headers = {
        'User-Agent': 'mdast-cli/1.0 (+https://stingray-tech.ru)',
        'Accept': 'application/json'
    }

    req = requests.get(
        f'https://backapi.rustore.ru/applicationData/overallInfo/{package_name}',
        headers=common_headers,
        timeout=30
    )
    if req.status_code == 200:
        body = req.json()
        if 'body' not in body:
            raise RuntimeError('Rustore - Invalid response for overallInfo: missing body field')
        body_info = body['body']
        logger.info(f"Rustore - Successfully found app with package name: {package_name},"
                    f" version:{body_info['versionName']}, company: {body_info['companyName']}")
    else:
        raise RuntimeError(
            f"Rustore - Failed to get application info. Status: {req.status_code}, body: {req.text[:500]}"
        )

    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        **common_headers
    }
    body = {
        'appId': body_info['appId'],
        'firstInstall': True
    }
    download_link_resp = requests.post(
        'https://backapi.rustore.ru/applicationData/download-link',
        headers=headers,
        json=body,
        timeout=30
    )
    if download_link_resp.status_code == 200:
        dl_json = download_link_resp.json()
        if 'body' not in dl_json or 'apkUrl' not in dl_json['body']:
            raise RuntimeError(
                f"Rustore - Invalid response for download-link: {download_link_resp.text[:500]}"
            )
        download_link = dl_json['body']['apkUrl']
    else:
        raise RuntimeError(
            f"Rustore - Failed to get application download link. Status: {download_link_resp.status_code}, "
            f"body: {download_link_resp.text[:500]}"
        )

    return {
        'integration_type': 'rustore',
        'download_url': download_link,
        'package_name': body_info['packageName'],
        'version_name': body_info['versionName'],
        'version_code': body_info['versionCode'],
        'min_sdk_version': body_info['minSdkVersion'],
        'max_sdk_version': body_info['maxSdkVersion'],
        'target_sdk_version': body_info['targetSdkVersion'],
        'file_size': body_info['fileSize'],
        'icon_url': body_info['iconUrl']
    }


def rustore_download_app(package_name, download_path):
    """
    Загрузка APK из RuStore с поддержкой как прямых ссылок на APK, так и ZIP-контейнеров.

    Изменения по сравнению с исходной реализацией:
    - Потоковая загрузка во временный файл для предотвращения частичной записи
    - Обнаружение ZIP по URL или Content-Type и извлечение встроенного APK
    - Проверка конечного артефакта на наличие ZIP-контейнера (формат APK) перед возвратом
    - Использует ensure_download_dir() и os.path.join для кроссплатформенных путей
    - Запись в временные файлы
    """
    app_info = get_app_info(package_name)
    logger.info('Rustore - Start downloading application')

    download_headers = {
        'User-Agent': 'mdast-cli/1.0 (+https://stingray-tech.ru)',
        'Accept': '*/*'
    }

    r = requests.get(
        app_info['download_url'],
        headers=download_headers,
        stream=True,
        allow_redirects=True,
        timeout=120
    )
    if r.status_code != 200:
        raise RuntimeError(
            f"Rustore - Failed to download application. Status: {r.status_code}, "
            f"content-type: {r.headers.get('Content-Type')}, body: {r.text[:500]}"
        )

    ensure_download_dir(download_path)
    file_path = os.path.join(download_path, f"{app_info['package_name']}-{app_info['version_name']}.apk")
    tmp_download_path = file_path + '.download'
    tmp_apk_path = file_path + '.part'

    # Save network payload to a temp file first to avoid creating a locked/partial target file
    try:
        with open(tmp_download_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=512 * 1024):
                if chunk:
                    f.write(chunk)
    except Exception as e:
        # Cleanup partial file on error
        cleanup_file(tmp_download_path)
        raise RuntimeError(f'Rustore - Failed to write downloaded file: {e}')

    content_type = r.headers.get('Content-Type', '')
    url_looks_like_zip = app_info['download_url'].endswith('.zip')

    if url_looks_like_zip or 'zip' in content_type.lower():
        # Response is a zip archive containing an apk. Extract the apk inside.
        try:
            with zipfile.ZipFile(tmp_download_path, 'r') as zip_ref:
                file_list = zip_ref.namelist()
                apk_candidates = [p for p in file_list if p.lower().endswith('.apk')]
                target_in_zip = apk_candidates[0] if apk_candidates else file_list[0]
                with zip_ref.open(target_in_zip) as source_file:
                    with open(tmp_apk_path, 'wb') as target_file:
                        target_file.write(source_file.read())
            logger.info('Rustore - Extracted apk from zip package')
        except zipfile.BadZipFile:
            raise RuntimeError('Rustore - Downloaded file reported as zip, but it is not a valid zip')
        finally:
            try:
                os.remove(tmp_download_path)
            except OSError:
                pass
        working_path = tmp_apk_path
    else:
        # Treat as direct APK; the temp download is the working APK file.
        working_path = tmp_download_path

    # Validate that resulting file looks like an APK (which is a zip file)
    if not zipfile.is_zipfile(working_path):
        # Read small prefix for diagnostics
        try:
            with open(working_path, 'rb') as f:
                head = f.read(64)
        except Exception:
            head = b''
        # Cleanup invalid file before raising error
        cleanup_file(working_path)
        raise RuntimeError(
            f"Rustore - Downloaded file is not a valid APK/ZIP. Content-Type: {content_type}, "
            f"first-bytes: {head[:16]}"
        )

    # Atomically place the APK to the final path (Linux; no Windows lock retries needed)
    os.replace(working_path, file_path)

    logger.info(f'Rustore - Apk was downloaded from rustore to {file_path}')

    return file_path
