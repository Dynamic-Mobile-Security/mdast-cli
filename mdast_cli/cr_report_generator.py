import json
import sys
import os
import zipfile
from datetime import datetime
import requests
import logging
import urllib3

from mdast_cli_core.api import mDastAPI as mDast

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - [%(levelname)s] - %(message)s'
)
logger = logging.getLogger(__name__)
logging.getLogger("urllib3").setLevel(logging.CRITICAL)


APPS_RESULT_COMPARE = "stack_trace_compare_result.zip"


class stingrayAPI(mDast):
    def __init__(self, base_url, username, password, use_ldap=False, authority_server=None):
        self.use_ldap = use_ldap
        self.authority_server = authority_server

        super().__init__(base_url, username, password)

    def _auth(self):
        """
        Переопределяем логику аутентификации:
         - при use_ldap делаем LDAP‑логин,
         - иначе — обычный.
        """
        self.headers['Content-Type'] = 'application/json'

        if self.use_ldap:
            payload = {
                'username': self.username,
                'password': self.password,
                'authority_server': self.authority_server,
                'authority_type': self._get_authority_type_ldap_id()
            }
        else:
            payload = {
                'username': self.username,
                'password': self.password
            }

        resp = requests.post(
            f'{self.url}/login/',
            headers=self.headers,
            data=json.dumps(payload, indent=4),
            verify=False
        )
        resp.raise_for_status()
        token = resp.json().get('access')
        self.headers['Authorization'] = f'Bearer {token}'

    def _get_authority_type_ldap_id(self):
        authority_types = requests.get(
            f'{self.url}/authority/types',
            headers=self.headers,
            verify=False)

        if authority_types.status_code != 200:
            logger.error(
                f"Не удалось загрузить список типов аутентификации. Код ответа: {authority_types.status_code}, "
                f"Текст ошибки: {authority_types.text}"
            )
            return None

        for type_auth in authority_types.json():
            if type_auth["value"] in ('LDAP сервер', 'LDAP Server'):
                return type_auth["id"]

    def download_artifact(self, dast_id, artifact_id):
        """
        Загрузка артефакта анализа из Stingray.
        """
        logger.info(f"Начало загрузки артефакта {artifact_id} для DAST-сканирования {dast_id}.")
        try:
            report = requests.get(
                f'{self.url}/dasts/{dast_id}/data/?result={artifact_id}',
                allow_redirects=True,
                headers=self.headers,
                verify=False
            )
            if report.status_code != 200:
                logger.error(
                    f"Не удалось загрузить артефакт. Код ответа: {report.status_code}, "
                    f"Текст ошибки: {report.text}"
                )
                return None
            logger.info(f"Артефакт {artifact_id} успешно загружен.")
            return report
        except requests.RequestException as e:
            logger.error(f"Ошибка при запросе к сервису для загрузки артефакта: {e}", exc_info=True)
            return None

    def get_app_info(self, app_id):
        """
        Получение информации о приложении по его ID.
        """
        logger.info(f"Запрос информации о приложении с ID={app_id}.")
        try:
            report = requests.get(
                f'{self.url}/applications/{app_id}',
                allow_redirects=True,
                headers=self.headers,
                verify=False
            )
            if report.status_code != 200:
                logger.error(
                    f"Не удалось получить информацию о приложении. Код ответа: {report.status_code}, "
                    f"Текст ошибки: {report.text}"
                )
                return None
            logger.info(f"Информация о приложении {app_id} успешно получена.")
            return report
        except requests.RequestException as e:
            logger.error(f"Ошибка при запросе информации о приложении: {e}", exc_info=True)
            return None


def unzip_file(zip_path, extract_to):
    """
    Распаковывает zip-файл zip_path в директорию extract_to.
    """
    logger.info(f"Попытка распаковать архив {zip_path} в директорию {extract_to}.")
    try:
        if not os.path.exists(extract_to):
            os.makedirs(extract_to)
            logger.debug(f"Директория {extract_to} была создана.")

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)

        logger.info(f"Архив {zip_path} успешно распакован в {extract_to}.")
    except Exception as e:
        logger.error(f"Ошибка при распаковке архива {zip_path}: {e}", exc_info=True)
        raise


def load_json_data(file_path):
    """
    Загрузка данных из JSON файла.
    """
    logger.info(f"Загрузка данных из JSON файла: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        logger.debug(f"JSON данные из {file_path} успешно загружены.")
        return data
    except FileNotFoundError:
        logger.error(f"Файл {file_path} не найден.")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Ошибка декодирования JSON в файле {file_path}: {e}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"Неизвестная ошибка при чтении файла {file_path}: {e}", exc_info=True)
        raise



def generate_html_report(stingray, json_data, settings, output_path):
    """Генерирует HTML отчет на основе данных JSON"""

    new_app = get_new_app_info(stingray, settings['stingray_scan_id'])

    summary = json_data.get('summary', {})
    diff_nodes = json_data.get('diff_nodes', [])

    critical_areas = []

    conclusion = generate_conclusion(summary)

    current_date = datetime.now().strftime("%d.%m.%Y")

    html = f'''<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <title>Отчёт по контролю неизменности трасс вызовов ПМ БР (Android)</title>
  <style>
    :root {{
      --primary-color: #0a4d8c;
      --secondary-color: #f0f7ff;
      --accent-color: #0a75d1;
      --border-color: #e0e9f5;
      --text-color: #333;
      --light-text: #6e6e6e;
      --success-color: #28a745;
      --warning-color: #ffc107;
      --danger-color: #dc3545;
      --neutral-color: #6c757d;
      --shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
      --card-radius: 10px;
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
      font-size: 15px;
      line-height: 1.6;
      color: var(--text-color);
      background-color: #f9fbfd;
      padding: 0;
      margin: 0;
    }}

    .container {{
      max-width: 1200px;
      margin: 0 auto;
      padding: 40px 20px;
    }}

    /* Заголовки */
    h1, h2, h3, h4 {{
      margin: 0 0 20px 0;
      font-weight: 600;
      line-height: 1.3;
      color: var(--primary-color);
    }}

    h1 {{
      font-size: 28px;
      margin-bottom: 8px;
      font-weight: 700;
      position: relative;
    }}

    h1::after {{
      content: "";
      display: block;
      width: 80px;
      height: 4px;
      background: var(--accent-color);
      margin-top: 12px;
      border-radius: 2px;
    }}

    h2 {{
      font-size: 22px;
      margin-top: 40px;
      margin-bottom: 16px;
      padding-bottom: 8px;
      border-bottom: 1px solid var(--border-color);
    }}

    h3 {{
      font-size: 18px;
      margin-top: 24px;
      margin-bottom: 12px;
    }}

    p {{
      margin-bottom: 16px;
    }}

    /* Шапка отчета */
    .report-header {{
      display: flex;
      flex-direction: column;
      margin-bottom: 40px;
      position: relative;
    }}

    .report-header .logo {{
      position: absolute;
      top: 0;
      right: 0;
      opacity: 0.1;
      width: 120px;
      height: 120px;
      z-index: 0;
    }}

    .report-meta {{
      display: flex;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 12px;
      margin-bottom: 20px;
      position: relative;
      z-index: 1;
    }}

    .report-date {{
      padding: 8px 14px;
      background-color: var(--secondary-color);
      border-radius: 6px;
      color: var(--primary-color);
      font-weight: 500;
      font-size: 14px;
    }}

    .report-id {{
      padding: 8px 14px;
      background-color: var(--secondary-color);
      border-radius: 6px;
      color: var(--primary-color);
      font-weight: 500;
      font-size: 14px;
    }}

    /* Карточки сравнения */
    .comparison-cards {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 24px;
      margin-bottom: 40px;
    }}

    .app-card {{
      background: white;
      padding: 24px;
      border-radius: var(--card-radius);
      box-shadow: var(--shadow);
      transition: transform 0.2s ease, box-shadow 0.2s ease;
      position: relative;
      overflow: hidden;
    }}

    .app-card:hover {{
      transform: translateY(-4px);
      box-shadow: 0 6px 18px rgba(0, 0, 0, 0.12);
    }}

    .app-card.ethalon {{
      border-top: 4px solid var(--primary-color);
    }}

    .app-card.new {{
      border-top: 4px solid var(--accent-color);
    }}

    .app-card h3 {{
      font-size: 18px;
      margin-top: 0;
      margin-bottom: 20px;
      display: flex;
      align-items: center;
    }}

    .app-card h3 .version-badge {{
      margin-left: 10px;
      font-size: 12px;
      padding: 3px 8px;
      border-radius: 12px;
      background: var(--secondary-color);
      color: var(--primary-color);
      font-weight: 500;
    }}

    .app-details {{
      margin-top: 16px;
    }}

    .detail-row {{
      display: flex;
      margin-bottom: 12px;
      align-items: flex-start;
    }}

    .detail-label {{
      flex: 0 0 100px;
      color: var(--light-text);
      font-size: 14px;
    }}

    .detail-value {{
      flex: 1;
      font-weight: 500;
      word-break: break-all;
    }}

    .hash-value {{
      font-family: 'Courier New', monospace;
      font-size: 13px;
      background: var(--secondary-color);
      padding: 2px 4px;
      border-radius: 3px;
    }}

    /* Основные секции */
    .section {{
      background: white;
      padding: 30px;
      margin-bottom: 30px;
      border-radius: var(--card-radius);
      box-shadow: var(--shadow);
      position: relative;
    }}

    .section-icon {{
      position: absolute;
      top: 25px;
      right: 25px;
      width: 30px;
      height: 30px;
      opacity: 0.15;
    }}

    /* Результаты анализа */
    .result-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 16px;
      margin: 24px 0;
    }}

    .result-item {{
      background: var(--secondary-color);
      padding: 20px;
      border-radius: 8px;
      transition: transform 0.2s ease;
    }}

    .result-item:hover {{
      transform: translateY(-3px);
    }}

    .result-label {{
      font-size: 14px;
      margin-bottom: 8px;
      color: var(--light-text);
    }}

    .result-value {{
      font-size: 28px;
      font-weight: 700;
      color: var(--primary-color);
      display: flex;
      align-items: center;
    }}

    .conclusion {{
      margin-top: 24px;
      padding: 20px;
      border-radius: 8px;
      background-color: #fff8e1;
      border-left: 4px solid var(--warning-color);
    }}

    /* Глоссарий */
    .glossary {{
      margin-top: 20px;
    }}

    .glossary-item {{
      margin-bottom: 20px;
      position: relative;
      padding-left: 20px;
    }}

    .glossary-item::before {{
      content: "";
      position: absolute;
      left: 0;
      top: 8px;
      width: 8px;
      height: 8px;
      background: var(--accent-color);
      border-radius: 50%;
    }}

    .glossary-term {{
      font-weight: 600;
      font-family: 'Courier New', monospace;
      margin-bottom: 5px;
      color: var(--primary-color);
    }}

    .glossary-definition {{
      margin-left: 0;
    }}

    /* JSON блок */
    .json-container {{
      background: #282c34;
      border-radius: 8px;
      position: relative;
      margin: 24px 0;
      overflow: hidden;
    }}

    .json-header {{
      background: #21252b;
      padding: 10px 16px;
      color: #e6e6e6;
      font-size: 14px;
      font-weight: 500;
      cursor: pointer;
    }}

    .json-content {{
      padding: 16px;
      font-family: 'Fira Code', 'Courier New', monospace;
      white-space: pre;
      overflow-x: auto;
      color: #e6e6e6;
      font-size: 14px;
      line-height: 1.5;
      max-height: 250px;
      overflow: hidden;
      transition: max-height 0.3s ease-in-out;
    }}

    /* Boolean значения */
    .value-true {{
      color: var(--success-color);
    }}

    .value-false {{
      color: var(--danger-color);
    }}

    /* Подвал */
    .footer {{
      background: white;
      padding: 30px;
      border-radius: var(--card-radius);
      box-shadow: var(--shadow);
      margin-top: 40px;
      color: var(--light-text);
      font-size: 14px;
      position: relative;
    }}

    .footer::before {{
      content: "";
      position: absolute;
      bottom: 0;
      left: 0;
      right: 0;
      height: 4px;
      background: linear-gradient(90deg, var(--primary-color), var(--accent-color));
      border-bottom-left-radius: var(--card-radius);
      border-bottom-right-radius: var(--card-radius);
    }}

    .footer-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      gap: 24px;
    }}

    .footer-col h3 {{
      font-size: 16px;
      margin-top: 0;
      margin-bottom: 12px;
      color: var(--primary-color);
    }}

    .footer-field {{
      margin-bottom: 8px;
    }}

    .footer-label {{
      font-weight: 500;
      margin-bottom: 4px;
    }}

    .disclaimer {{
      margin-top: 24px;
      padding-top: 20px;
      border-top: 1px solid var(--border-color);
      font-size: 13px;
      text-align: center;
    }}

    /* Индикаторы статуса */
    .status-indicator {{
      display: inline-flex;
      align-items: center;
      margin-left: 10px;
    }}

    .status-indicator.success {{
      color: var(--success-color);
    }}

    .status-indicator.warning {{
      color: var(--warning-color);
    }}

    .status-indicator.error {{
      color: var(--danger-color);
    }}

    .status-indicator.neutral {{
      color: var(--neutral-color);
    }}

    /* Адаптивность */
    @media (max-width: 768px) {{
      .container {{
        padding: 20px 15px;
      }}

      h1 {{
        font-size: 24px;
      }}

      .section, .app-card {{
        padding: 20px;
      }}

      .result-grid {{
        grid-template-columns: 1fr;
      }}

      .footer-grid {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
  <script>
    // Простой скрипт для возможности разворачивания JSON блока
    document.addEventListener('DOMContentLoaded', function() {{
      const jsonHeader = document.querySelector('.json-header');
      if (jsonHeader) {{
        jsonHeader.addEventListener('click', function() {{
          const jsonContent = this.nextElementSibling;
          if (jsonContent.style.maxHeight) {{
            jsonContent.style.maxHeight = null;
          }} else {{
            jsonContent.style.maxHeight = jsonContent.scrollHeight + 'px';
          }}
        }});
      }}
    }});
  </script>
</head>
<body>
  <div class="container">
    <!-- Заголовок отчета -->
    <div class="report-header">
      <svg class="logo" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
        <path fill="#0a4d8c" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-1-13h2v6h-2zm0 8h2v2h-2z"/>
      </svg>
      <div class="report-meta">
        <div class="report-date">Дата формирования: {current_date}</div>
        <div class="report-id">ID отчета: КНТВ-{datetime.now().strftime("%Y-%m-A")}</div>
      </div>
      <h1>Отчёт по контролю неизменности трасс вызовов ПМ БР</h1>
      <p>Отчет о сравнительном анализе трасс вызовов Программного модуля Банка России в составе мобильного приложения.</p>
      <div style="margin-top: 16px; display: flex; gap: 12px;">
        <div style="background: #e7f3ff; padding: 6px 12px; border-radius: 4px; font-size: 13px; font-weight: 500; color: #0a4d8c;">
          <span style="display: inline-block; width: 14px; height: 14px; background: #0a4d8c; border-radius: 50%; margin-right: 5px;"></span> Организация-заказчик: {settings['organization_name']}
        </div>
      </div>
    </div>

    <!-- Карточки приложений -->
    <div class="comparison-cards">

      <div class="app-card new">
        <h3>Проверяемая версия <span class="version-badge">{new_app['version_name']}</span></h3>
        <div class="app-details">
          <div class="detail-row">
            <div class="detail-label">Название</div>
            <div class="detail-value">{new_app['name']}</div>
          </div>
          <div class="detail-row">
            <div class="detail-label">Пакет</div>
            <div class="detail-value">{new_app['package_name']}</div>
          </div>
          <div class="detail-row">
            <div class="detail-label">Размер</div>
            <div class="detail-value">{new_app['file_size']}</div>
          </div>
          <div class="detail-row">
            <div class="detail-label">Хэш</div>
            <div class="detail-value"><span class="hash-value">{new_app['md5']}</span></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Назначение и нормативная база -->
    <div class="section">
      <svg class="section-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
        <path fill="#0a4d8c" d="M12 2L4 5v6.09c0 5.05 3.41 9.76 8 10.91 4.59-1.15 8-5.86 8-10.91V5l-8-3zm6 9.09c0 4-2.55 7.7-6 8.83-3.45-1.13-6-4.82-6-8.83v-4.7l6-2.25 6 2.25v4.7z"/>
      </svg>
      <h2>Назначение и нормативная база</h2>
      <p>
        Настоящий отчёт составлен с целью сравнения двух версий мобильного приложения,
         чтобы убедиться в сохранении неизменности встроенного Программного модуля
        Банка России (ПМ БР). При выпуске обновлений критически важно проверить, не были ли внесены
        неконтролируемые изменения в порядок вызовов ПМ БР, поскольку это может привести
        к рискам в области криптографической защиты или иных аспектов безопасности.
      </p>

      <div style="margin-top: 20px; background: #f0f7ff; padding: 16px; border-radius: 8px; border-left: 4px solid #0a4d8c;">
        <h3 style="margin-top: 0; margin-bottom: 10px; color: #0a4d8c; font-size: 16px;">Нормативная основа проверки</h3>
        <p style="margin-bottom: 8px; font-size: 14px;">Проверка проведена на основании следующих документов:</p>
        <ul style="margin-top: 0; margin-bottom: 0; padding-left: 20px; font-size: 14px;">
          <li><strong>"Порядок проведения работ по оценке влияния аппаратных, программно-аппаратных и программных средств сети (системы) конфиденциальной связи"</strong>, утвержденный Заместителем руководителя Научно-технической службы – начальником 8 Центра ФСБ России от 20.11.2024</li>
          <li><strong>Приказ ФСБ России от 09.02.2005 № 66</strong> (ред. от 12.04.2010) «Об утверждении Положения о разработке, производстве, реализации и эксплуатации шифровальных (криптографических) средств защиты информации (Положение ПКЗ-2005)»</li>
        </ul>
      </div>
    </div>

    <!-- Методика проведения анализа -->
    <div class="section">
      <svg class="section-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
        <path fill="#0a4d8c" d="M18 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zM6 4h5v8l-2.5-1.5L6 12V4zm0 15l3-3.86 2.14 2.58 3-3.86L18 19H6z"/>
      </svg>
      <h2>1. Методика проведения анализа</h2>
      <p>
        Для проведения исследования использовалась специализированная методика статического анализа, 
        направленная на построение и сравнение трасс вызовов ПМ БР в составе мобильного приложения. 
        Данная методика разработана для выявления изменений в цепочках вызовов, которые могут 
        повлиять на безопасность криптографических операций.
      </p>

      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-top: 24px;">
        <div style="background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); padding: 16px;">
          <h3 style="color: #0a4d8c; font-size: 16px; margin-top: 0; margin-bottom: 12px;">Инструментальные средства</h3>
          <ul style="margin: 0; padding-left: 20px;">
            <li style="margin-bottom: 6px;">Анализатор трасс <strong>AppSec.Sting CR</strong></li>
            <li style="margin-bottom: 6px;">Утилита сравнения <strong>AppSec.Sting CR</strong></li>
            <li style="margin-bottom: 6px;">Верификатор контрольных сумм <strong>HashVerify</strong></li>
          </ul>
        </div>

        <div style="background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); padding: 16px;">
          <h3 style="color: #0a4d8c; font-size: 16px; margin-top: 0; margin-bottom: 12px;">Этапы проведения анализа</h3>
          <ol style="margin: 0; padding-left: 20px;">
            <li style="margin-bottom: 6px;">Расчет и сверка контрольных сумм исполняемых файлов</li>
            <li style="margin-bottom: 6px;">Декомпиляция/дизассемблирование и анализ структуры классов</li>
            <li style="margin-bottom: 6px;">Построение графов вызовов для выявленных точек входа в ПМ БР</li>
            <li style="margin-bottom: 6px;">Фильтрация промежуточных графов для выделения ключевых цепочек</li>
            <li style="margin-bottom: 6px;">Сравнение полученных графов с эталонными</li>
          </ol>
        </div>
      </div>

      <p style="margin-top: 24px;">
        Особое внимание в процессе анализа уделялось следующим аспектам:
      </p>
      <ul style="margin-top: 8px; margin-bottom: 0;">
        <li>Неизменность точек входа в ПМ БР (включая все публичные методы и интерфейсы)</li>
        <li>Сохранение структуры JNI-вызовов к нативным модулям криптографии</li>
      </ul>
    </div>

    <!-- Результаты сопоставления -->
    <div class="section">
      <svg class="section-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
        <path fill="#0a4d8c" d="M14 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6zm4 18H6V4h7v5h5v11zM9 13h6v2H9zm0-4h4v2H9zm0 8h6v2H9z"/>
      </svg>
      <h2>2. Результаты сопоставления</h2>
      <p>
        В таблице ниже отражены итоговые поля сравнения, полученные после
        сопоставления старой (эталонной) и новой версий.
        Они позволяют судить о том, есть ли различия в методах, вызывающих ПМ БР,
        и как это влияет на общее признание приложения «неизменным».
      </p>

      <div class="result-grid">
        <div class="result-item">
          <div class="result-label">Число методов с отличиями</div>
          <div class="result-value">{summary.get('methods_changed', 0)}</div>
        </div>

        <div class="result-item">
          <div class="result-label">Новые методы в цепочках</div>
          <div class="result-value">{summary.get('methods_added', 0)}</div>
        </div>

        <div class="result-item">
          <div class="result-label">Удалённые методы</div>
          <div class="result-value">{summary.get('methods_removed', 0)}</div>
        </div>

        <div class="result-item">
          <div class="result-label">Графы с расхождениями</div>
          <div class="result-value">{summary.get('graph_nodes_changed', 0)} 
            <span class="status-indicator warning">&#9888;</span>
          </div>
        </div>

        <div class="result-item">
          <div class="result-label">Совпадение названий методов</div>
          <div class="result-value {'value-true' if summary.get('methods_equal', False) else 'value-false'}">{str(summary.get('methods_equal', False)).lower()}</div>
        </div>

        <div class="result-item">
          <div class="result-label">Совпадение графов</div>
          <div class="result-value {'value-true' if summary.get('graph_nodes_equal', False) else 'value-false'}">{str(summary.get('graph_nodes_equal', False)).lower()}
            <span class="status-indicator {'success' if summary.get('graph_nodes_equal', False) else 'error'}">{'&#10004;' if summary.get('graph_nodes_equal', False) else '&#10060;'}</span>
          </div>
        </div>

        <div class="result-item">
          <div class="result-label">Приложение неизменно</div>
          <div class="result-value {'value-true' if summary.get('application_equal', False) else 'value-false'}">{str(summary.get('application_equal', False)).lower()}
            <span class="status-indicator {'success' if summary.get('application_equal', False) else 'error'}">{'&#10004;' if summary.get('application_equal', False) else '&#10060;'}</span>
          </div>
        </div>
      </div>

      <div class="conclusion">
        <h3>Интерпретация результатов</h3>
        <p>
          Методы по названию {'совпадают' if summary.get('methods_equal', False) else 'не совпадают'}, {'однако' if summary.get('methods_equal', False) else 'и'} <em>graph_nodes_changed</em> = {summary.get('graph_nodes_changed', 0)} и <em>graph_nodes_equal</em> = {str(summary.get('graph_nodes_equal', False)).lower()}
          {'свидетельствуют о фактических изменениях в структуре вызовов' if summary.get('graph_nodes_changed', 0) > 0 else 'указывают на отсутствие изменений в структуре вызовов'}.
          В итоге приложение {'не ' if not summary.get('application_equal', False) else ''}признано полностью идентичным:
          <strong>application_equal = {str(summary.get('application_equal', False)).lower()}</strong>.
        </p>
      </div>
    </div>

    <!-- Пояснения к полям отчёта -->
    <div class="section">
      <svg class="section-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
        <path fill="#0a4d8c" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-1-13h2v6h-2zm0 8h2v2h-2z"/>
      </svg>
      <h2>2. Пояснения к полям отчёта</h2>

      <div class="glossary">
        <div class="glossary-item">
          <div class="glossary-term">diff_nodes</div>
          <div class="glossary-definition">
            Перечень методов/файлов, которые присутствуют и в старой, и в новой версиях, но внутри обнаружены отличия по вызовам.
          </div>
        </div>

        <div class="glossary-item">
          <div class="glossary-term">diff_graphs</div>
          <div class="glossary-definition">
            Список трасс (графов), которые полностью отсутствовали в одной из версий;
            означает появление/исчезновение методов целиком.
          </div>
        </div>

        <div class="glossary-item">
          <div class="glossary-term">orig_size</div>
          <div class="glossary-definition">
            Общее число выявленных трасс (графов) в новой версии. Показывает масштаб анализа.
          </div>
        </div>

        <div class="glossary-item">
          <div class="glossary-term">base_size</div>
          <div class="glossary-definition">
            Общее число трасс (графов) в старой (эталонной) версии, с которой ведётся сравнение.
          </div>
        </div>

        <div class="glossary-item">
          <div class="glossary-term">methods_changed</div>
          <div class="glossary-definition">
            Сколько методов (одинаковых по названию) содержат изменения (новые/исключённые вызовы) внутри цепочки.
          </div>
        </div>

        <div class="glossary-item">
          <div class="glossary-term">methods_added</div>
          <div class="glossary-definition">
            Число новых методов в рамках тех же цепочек, которые не встречались в эталоне.
          </div>
        </div>

        <div class="glossary-item">
          <div class="glossary-term">methods_removed</div>
          <div class="glossary-definition">
            Число методов, которые встречались в эталоне, но не обнаружены в новом коде
            (в рамках совпадающих цепочек).
          </div>
        </div>

        <div class="glossary-item">
          <div class="glossary-term">graph_nodes_changed</div>
          <div class="glossary-definition">
            Количество графов (цепочек), где система зафиксировала отличия.
            Если число велико, вероятны серьёзные перестройки логики.
          </div>
        </div>

        <div class="glossary-item">
          <div class="glossary-term">methods_equal</div>
          <div class="glossary-definition">
            Результирующее значение, определяющее совпадают ли приложения по составу методов внутри графов.
          </div>
        </div>

        <div class="glossary-item">
          <div class="glossary-term">graph_nodes_equal</div>
          <div class="glossary-definition">
            Результирующее значение, определяющее совпадают ли приложения по графам.
          </div>
        </div>

        <div class="glossary-item">
          <div class="glossary-term">application_equal</div>
          <div class="glossary-definition">
            Итоговое решение: true, если приложение фактически не изменилось с точки зрения логики
            ПМ БР; false, если система зарегистрировала изменения.
          </div>
        </div>
      </div>
    </div>
    '''
    html += f'''
    <!-- Заключение -->
    <div class="section">
      <svg class="section-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
        <path fill="#0a4d8c" d="M20 2H4c-1.1 0-1.99.9-1.99 2L2 22l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H5.17l-.59.59-.58.58V4h16v12zm-9-4h2v2h-2zm0-6h2v4h-2z"/>
      </svg>
      <h2>3. Заключение</h2>
      <p>{conclusion['text']}</p>

      <div style="background: #e8f5e9; border-left: 4px solid #4caf50; padding: 16px; margin-top: 24px; border-radius: 4px;">
        <h3 style="margin-top: 0; color: #1b5e20; font-size: 16px;">Рекомендуемые действия</h3>
        <ol style="margin: 0; padding-left: 20px; font-size: 14px;">
    '''

    for recommendation in conclusion['recommendations']:
        html += f'''          <li style="margin-bottom: 8px;"><strong>{recommendation}</strong></li>\n'''

    html += '''        </ol>
      </div>
    </div>
'''

    html += f'''<!-- Исходная структура JSON -->
    <div class="section">
      <svg class="section-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
        <path fill="#0a4d8c" d="M9.4 16.6L4.8 12l4.6-4.6L8 6l-6 6 6 6 1.4-1.4zm5.2 0l4.6-4.6-4.6-4.6L16 6l6 6-6 6-1.4-1.4z"/>
      </svg>
      <h2>4. Исходная структура JSON (результат анализа)</h2>
      <p>
        Ниже приводится итоговый JSON, где <em>diff_nodes</em> и <em>diff_graphs</em>
        содержат детальные сведения о затронутых классах/файлах, а <em>summary</em>
        включает итоговые числовые и булевы (true/false) поля.
      </p>

      <div class="json-container">
        <div class="json-header">
          stack_trace_compare_result.json (нажмите для раскрытия полного содержимого)
        </div>
        <div class="json-content" style="max-height: 250px; overflow: hidden; transition: max-height 0.3s ease-in-out;">
{json.dumps(json_data, indent=2)}</div>
      </div>

      <p>
        Анализируя эти данные, можно реконструировать, какие вызовы были добавлены или
        исчезли, и сделать полноценный вывод о том, как именно изменилась логика в цепочках
        взаимодействия с ПМ БР.
      </p>

    </div>

    <div class="footer">
      <div class="footer-grid">
        <div class="footer-col">
          <h3>Исполнители</h3>
          <div class="footer-field">
            <div class="footer-label">Технический специалист:</div>
            <div>{settings['engineer_name']}</div>
          </div>
          <div class="footer-field">
            <div class="footer-label">Ответственный за контроль:</div>
            <div>{settings['controller_name']}</div>
          </div>
        </div>

        <div class="footer-col">
          <h3>Документация</h3>
          <div class="footer-field">
            <div class="footer-label">Номер отчета:</div>
            <div>КНТВ-''' + datetime.now().strftime("%Y-%m-A") + '''</div>
          </div>
          <div class="footer-field">
            <div class="footer-label">Дата проведения анализа:</div>
            <div>''' + datetime.now().strftime("%d.%m.%Y") + '''</div>
          </div>
          <div class="footer-field">
            <div class="footer-label">Приложения:</div>
            <div>Файлы графов вызовов, JSON-отчет</div>
          </div>
        </div>'''

    html += f'''<div class="footer-col">
          <h3>Подтверждение</h3>
          <div class="footer-field">
            <div class="footer-label">Статус отчета:</div>
            <div style="color: {conclusion['status_color']}; font-weight: 500;">{conclusion['status']}</div>
          </div>
        </div>
      </div>'''

    html += '''<div class="disclaimer">
        <p>
          Настоящий отчёт носит конфиденциальный характер и не подлежит распространению
          без согласования с владельцем. Данные приведены исключительно в целях оценки
          безопасности и соответствия приложения требованиям Банка России и регламентам регулятора.
        </p>
      </div>
    </div>
  </div>

  <script>
    // Инициализация интерактивности после загрузки DOM
    document.addEventListener('DOMContentLoaded', function() {
      const jsonHeader = document.querySelector('.json-header');
      if (jsonHeader) {
        jsonHeader.addEventListener('click', function() {
          const jsonContent = this.nextElementSibling;
          if (jsonContent.style.maxHeight && jsonContent.style.maxHeight !== '250px') {
            jsonContent.style.maxHeight = '250px';
          } else {
            jsonContent.style.maxHeight = jsonContent.scrollHeight + 'px';
          }
        });
      }
    });
  </script>
</body>
</html>
'''

    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(html)

    return output_path



def generate_conclusion(summary):
    """
    Генерирует соответствующее заключение на основе параметров анализа.
    """
    logger.debug("Генерация итогового заключения.")
    graph_nodes_equal = summary.get('graph_nodes_equal', False)
    methods_equal = summary.get('methods_equal', False)
    application_equal = summary.get('application_equal', False)
    graph_nodes_changed = summary.get('graph_nodes_changed', 0)

    calculated_app_equal = graph_nodes_equal and methods_equal
    if calculated_app_equal != application_equal:
        logger.warning(
            f"Предупреждение: Несогласованность данных. application_equal={application_equal}, "
            f"graph_nodes_equal={graph_nodes_equal}, methods_equal={methods_equal}"
        )

    conclusion = {
        'text': '',
        'recommendations': [],
        'status': '',
        'status_color': ''
    }

    if application_equal:
        conclusion['text'] = (
            "Приложение полностью соответствует эталону. Трассы вызовов ПМ БР остались неизменными. "
            "Рекомендуется выпуск приложения без дополнительных процедур согласования с регулятором."
        )
        conclusion['status'] = 'Соответствует требованиям'
        conclusion['status_color'] = '#1b5e20'
        conclusion['recommendations'] = [
            "Оформить документацию о соответствии требованиям",
            "Подготовить приложение к выпуску в магазины приложений",
            "Провести регулярный инструментальный контроль после выпуска"
        ]
        return conclusion

    conclusion['status'] = 'Не соответствует требованиям'
    conclusion['status_color'] = '#dc3545'

    reasons = []
    if not methods_equal:
        reasons.append("изменение методов взаимодействия с ПМ БР")
    if not graph_nodes_equal:
        reasons.append(f"обнаружены изменения в {graph_nodes_changed} графах вызовов")

    reasons_text = " и ".join(reasons)
    conclusion['text'] = (
        f"Приложение не соответствует эталону. Основные причины: {reasons_text}. "
        f"Требуется детальный анализ модифицированных функций и согласование "
        f"изменений с регулятором в соответствии с установленным порядком."
    )

    conclusion['recommendations'] = [
        "Предоставить дополнительную документацию о внесенных изменениях",
        "Согласовать изменения с регулятором",
        "Провести дополнительное тестирование затронутых функций",
        "Обновить эксплуатационную документацию с учетом внесенных изменений"
    ]
    return conclusion


def get_info_from_stingray(stingray, scan_id):
    """
    Получение информации об обнаруженных дефектах и загрузка результатов для анализа.
    """
    logger.info(f"Запрос информации о дефектах для сканирования scan_id={scan_id}.")
    try:
        defects = stingray.get_dast_issues(scan_id)
        if not defects or defects.status_code != 200:
            logger.error(
                f"Не удалось получить данные о дефектах. Код ответа: {defects.status_code if defects else 'N/A'}, "
                f"Текст: {defects.text if defects else 'Нет данных'}"
            )
            return None

        defects = defects.json()
        for defect in defects['results']:
            if defect['title'] in ('Изменения в трассах вызовов', 'Stack trace changed', 'Stack trace not changed', 'Нет изменений в трассах вызовов'):
                logger.debug(f"Найден интересующий нас дефект: {defect['title']}")
                defect_info = stingray.get_issue_info(defect['id'])
                if not defect_info or defect_info.status_code != 200:
                    logger.error(
                        f"Не удалось получить информацию о дефекте {defect['id']}. "
                        f"Код: {defect_info.status_code if defect_info else 'N/A'}, "
                        f"Текст: {defect_info.text if defect_info else 'N/A'}"
                    )
                    return None

                result_id = defect_info.json()['items'][0]['result']['id']
                download_result = stingray.download_artifact(scan_id, result_id)
                if not download_result:
                    logger.error("Скачивание результата сравнения не удалось.")
                    return None

                if download_result.status_code != 200:
                    logger.error(
                        f"Не удалось скачать результат сравнения. Код: {download_result.status_code}, "
                        f"Текст: {download_result.text}"
                    )
                    sys.exit(1)

                logger.info(f"Сохранение результата сравнения в файл {APPS_RESULT_COMPARE}.")
                with open(APPS_RESULT_COMPARE, 'wb') as f:
                    f.write(download_result.content)

                unzip_file(APPS_RESULT_COMPARE, '.')

                return load_json_data('./stack_trace_compare/stack_trace_compare_result.json')
        logger.warning("Не найдено дефектов, соответствующих ключевым заголовкам (трассам вызовов).")
        return None
    except Exception as e:
        logger.error(f"Произошла ошибка при получении информации из Stingray: {e}", exc_info=True)
        return None


def get_new_app_info(stingray, scan_id):
    """
    Получение информации о новом приложении (из ответа Stingray).
    """
    logger.info(f"Запрос информации о новом приложении по scan_id={scan_id}.")
    try:
        scan_info = stingray.get_scan_info(scan_id)
        if not scan_info or scan_info.status_code != 200:
            logger.error(
                f"Не удалось получить информацию о сканировании. Код: {scan_info.status_code if scan_info else 'N/A'}, "
                f"Текст: {scan_info.text if scan_info else 'N/A'}"
            )
            return None

        scan_info = scan_info.json()
        app_id = scan_info["application"]["id"]
        app_info_resp = stingray.get_app_info(app_id)
        if not app_info_resp:
            logger.error("Не удалось получить информацию о приложении.")
            return None

        if app_info_resp.status_code != 200:
            logger.error(
                f"Не удалось получить данные по приложению. Код: {app_info_resp.status_code}, "
                f"Текст: {app_info_resp.text}"
            )
            return None

        app_info = app_info_resp.json()

        app_info['file_size'] = f'{app_info["file_size"] * 0.000001} МБ'
        logger.debug(f"Информация о приложении: {app_info}")
        return app_info
    except Exception as e:
        logger.error(f"Ошибка при получении информации о новом приложении: {e}", exc_info=True)
        return None


def generate_cr(url, login, password, scan_id, org_name, engineer_name, controller_name, cr_report_path,
                use_ldap=False, authority_server_id=None):
    urllib3.disable_warnings()

    settings = {
        "stingray_url": url,
        "stingray_login": login,
        "stingray_password": password,
        "stingray_scan_id": scan_id,
        "organization_name": org_name,
        "engineer_name": engineer_name,
        "controller_name": controller_name,
        "use_ldap": use_ldap,
        "authority_server_id": authority_server_id
    }
    try:
        logger.info("Запуск процесса генерации отчета по анализу трасс вызовов.")

        stingray = stingrayAPI(
            settings['stingray_url'],
            settings['stingray_login'],
            settings['stingray_password'],
            settings['use_ldap'],
            settings['authority_server_id']
        )

        scan_details = get_info_from_stingray(
            stingray,
            settings['stingray_scan_id']
        )

        if not scan_details:
            logger.error("Не удалось получить детали сканирования. Завершение работы.")
            sys.exit(1)

        output_path = generate_html_report(stingray, scan_details, settings, cr_report_path)
        logger.info(f"Отчет успешно сгенерирован и сохранен в {output_path}")

    except Exception as e:
        logger.critical(f"Непредвиденная ошибка в процессе генерации отчета: {e}", exc_info=True)
        sys.exit(1)
