# locustfile.py
from locust import HttpUser, task, between, events
import random
import requests
import time
from datetime import datetime

# ========================================
# КОНФИГУРАЦИЯ
# ========================================
NOCODB_CONFIG = {
    "base_url": "https://app.nocodb.com",
    "workspace_id": "p2zp5kay2ja7qli",
    "table_id": "mpqzfhxx5kmz9tv",
    "api_token": "b4EJZcJpb4lP-_fbGm8Nlf-30qRoAZuVI3eRSlmk",
}

API_ENDPOINT = f"/api/v2/tables/{NOCODB_CONFIG['table_id']}/records"

# ========================================
# СТАТИСТИКА
# ========================================
stats = {
    "total_requests": 0,
    "successful": 0,
    "failed": 0,
    "errors": {}
}

# ========================================
# ТЕСТОВЫЕ ДАННЫЕ
# ========================================

УСТРОЙСТВА = [
    "Ноутбук-Dell-5420", "Ноутбук-HP-850", "Ноутбук-Lenovo-T480",
    "ПК-Бухгалтерия-01", "ПК-Отдел-Кадров-02", "ПК-Менеджер-03",
    "Принтер-HP-LaserJet", "Принтер-Canon-MF",
    "Монитор-Samsung-27", "Монитор-Dell-24",
    "iPhone-13-Pro", "Samsung-Galaxy-S22",
    "MacBook-Pro-16", "MacBook-Air-M2",
    "Сервер-Файловый-01", "Сервер-БД-02",
    "Роутер-Cisco-01", "Коммутатор-Netgear"
]

ОПИСАНИЯ_ПРОБЛЕМ = {
    "bug": [
        "Система зависает при открытии больших Excel файлов",
        "Синий экран после обновления Windows",
        "Приложение зависает при сохранении файла",
        "Сеть отключается каждые 30 минут",
        "Принтер печатает нечитаемые символы",
        "Мерцание экрана на внешнем мониторе",
        "USB порты не распознают устройства",
        "WiFi соединение часто обрывается",
        "Outlook не синхронизирует почту",
        "Нет доступа к сетевому диску"
    ],
    "feature": [
        "Требуется установка Adobe Photoshop для дизайна",
        "Нужен доступ к VPN для удаленной работы",
        "Запрос на установку второго монитора",
        "Требуется лицензия на AutoCAD",
        "Запрос на увеличение RAM до 16GB",
        "Нужен доступ к общему календарю",
        "Требуется установка Python и VS Code"
    ],
    "question": [
        "Как подключиться к корпоративному VPN из дома",
        "Какая процедура установки программного обеспечения",
        "Как настроить почту на мобильном устройстве",
        "Где найти драйверы для сетевого принтера",
        "Как запросить новое оборудование",
        "Какой график резервного копирования"
    ],
    "task": [
        "Установить Windows 11 на новый ноутбук",
        "Настроить учетную запись почты для нового сотрудника",
        "Заменить старый монитор на новый 27 дюймов",
        "Обновить антивирусные базы",
        "Очистить место на диске ПК",
        "Установить драйверы принтера"
    ]
}

ИСПОЛНИТЕЛИ = [
    "ivanov", "petrov", "sidorov", "kozlov",
    "tech_support_1", "tech_support_2", "admin", "helpdesk"
]

ПРИОРИТЕТЫ = ["critical", "high", "normal", "low"]
ВЕСА_ПРИОРИТЕТОВ = [0.05, 0.15, 0.60, 0.20]

ТИПЫ = ["bug", "feature", "question", "task"]
ВЕСА_ТИПОВ = [0.35, 0.15, 0.20, 0.30]

# Счетчик для уникальных ID в рамках сессии
ticket_counter = 0


def сгенерировать_заявку():
    """Генерация данных заявки с коротким уникальным ID"""
    global ticket_counter
    
    тип = random.choices(ТИПЫ, weights=ВЕСА_ТИПОВ, k=1)[0]
    приоритет = random.choices(ПРИОРИТЕТЫ, weights=ВЕСА_ПРИОРИТЕТОВ, k=1)[0]
    
    # Короткий уникальный ID: T + 5 цифр
    ticket_counter += 1
    ticket_id = f"T{10000 + ticket_counter}"
    
    описания = ОПИСАНИЯ_ПРОБЛЕМ[тип]
    описание = random.choice(описания)
    
    устройство = random.choice(УСТРОЙСТВА)
    исполнитель = random.choice(ИСПОЛНИТЕЛИ) if random.random() > 0.2 else ""
    заблокировано = random.random() < 0.1
    
    return {
        "ticketId": ticket_id,
        "title": описание[:80],
        "type": тип,
        "priority": приоритет,
        "assignee": исполнитель,
        "device": устройство,
        "description": описание,
        "blocked": заблокировано,
        "status": "backlog"
    }


# ========================================
# ПОЛЬЗОВАТЕЛЬ LOCUST
# ========================================

class ApiPostUser(HttpUser):
    """Пользователь для тестирования POST запросов"""
    host = NOCODB_CONFIG["base_url"]
    
    # Увеличенное время ожидания для избежания 429
    wait_time = between(5, 15)
    
    @task
    def создать_заявку(self):
        """Создание заявки через POST запрос"""
        global stats
        
        данные = сгенерировать_заявку()
        stats["total_requests"] += 1
        
        try:
            start_time = time.time()
            
            response = requests.post(
                f"{NOCODB_CONFIG['base_url']}{API_ENDPOINT}",
                json=данные,
                headers={
                    "xc-token": NOCODB_CONFIG["api_token"],
                    "Content-Type": "application/json"
                },
                timeout=30
            )
            
            elapsed = (time.time() - start_time) * 1000
            
            if response.status_code in [200, 201]:
                stats["successful"] += 1
                print(f"[OK] {stats['successful']}/{stats['total_requests']} | "
                      f"{данные['ticketId']} | {elapsed:.0f}мс")
            else:
                stats["failed"] += 1
                error_key = f"HTTP {response.status_code}"
                stats["errors"][error_key] = stats["errors"].get(error_key, 0) + 1
                
                print(f"[FAIL] {stats['successful']}/{stats['total_requests']} | "
                      f"{error_key} | {elapsed:.0f}мс")
                print(f"       Заявка: {данные['ticketId']}")
                
                # Парсинг ошибки
                try:
                    error_json = response.json()
                    if "msg" in error_json:
                        print(f"       Ошибка: {error_json['msg']}")
                except:
                    print(f"       Ответ: {response.text[:300]}")
                
                # Обработка 429 - ждем дольше
                if response.status_code == 429:
                    wait_time = random.randint(10, 30)
                    print(f"       Ограничение скорости! Ожидание {wait_time}с...")
                    time.sleep(wait_time)
                    
        except requests.exceptions.Timeout:
            stats["failed"] += 1
            stats["errors"]["Timeout"] = stats["errors"].get("Timeout", 0) + 1
            print(f"[TIMEOUT] {данные['ticketId']}")
            
        except requests.exceptions.ConnectionError as e:
            stats["failed"] += 1
            stats["errors"]["ConnectionError"] = stats["errors"].get("ConnectionError", 0) + 1
            print(f"[CONNECTION ERROR] {str(e)[:150]}")
            
        except Exception as e:
            stats["failed"] += 1
            stats["errors"]["Exception"] = stats["errors"].get("Exception", 0) + 1
            print(f"[EXCEPTION] {str(e)[:150]}")


# ========================================
# ОБРАБОТЧИКИ СОБЫТИЙ
# ========================================

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    global stats
    stats = {"total_requests": 0, "successful": 0, "failed": 0, "errors": {}}
    
    print("=" * 70)
    print("ЗАПУСК НАГРУЗОЧНОГО ТЕСТИРОВАНИЯ")
    print("=" * 70)
    print(f"API: {NOCODB_CONFIG['base_url']}")
    print(f"Таблица: {NOCODB_CONFIG['table_id']}")
    print(f"Время ожидания: 5-15 секунд (для избежания 429)")
    print("=" * 70)


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    global stats
    
    print("=" * 70)
    print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("=" * 70)
    print(f"Всего запросов: {stats['total_requests']}")
    print(f"Успешно: {stats['successful']} ({stats['successful']/max(stats['total_requests'],1)*100:.1f}%)")
    print(f"Не успешно: {stats['failed']} ({stats['failed']/max(stats['total_requests'],1)*100:.1f}%)")
    if stats["errors"]:
        print("-" * 70)
        print("Ошибки:")
        for error, count in stats["errors"].items():
            print(f"  {error}: {count}")
    print("=" * 70)