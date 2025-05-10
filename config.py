#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Конфигурационный файл приложения Qwen3-DevAgent-Core
"""

import os
import platform
import json

# Базовые пути
HOME_DIR = os.path.expanduser("~")
CONFIG_DIR = os.path.join(HOME_DIR, ".qwen3-devagent")
MODELS_DIR = os.path.join(CONFIG_DIR, "models")
CACHE_DIR = os.path.join(CONFIG_DIR, "cache")

# Конфигурация Ollama
OLLAMA_HOST = "localhost"
OLLAMA_PORT = 11434
OLLAMA_BASE_URL = f"http://{OLLAMA_HOST}:{OLLAMA_PORT}"
OLLAMA_API_MODELS = f"{OLLAMA_BASE_URL}/api/tags"
OLLAMA_API_GENERATE = f"{OLLAMA_BASE_URL}/api/generate"
OLLAMA_API_CHAT = f"{OLLAMA_BASE_URL}/api/chat"

# Конфигурация запросов
REQUEST_TIMEOUT = 30  # секунды
MAX_TOKENS = 2048  # максимальное количество токенов в ответе

# Параметры интерфейса
UI_WINDOW_TITLE = "Qwen3-DevAgent - Интерфейс для ИИ-моделей"
UI_WINDOW_WIDTH = 1200
UI_WINDOW_HEIGHT = 800
UI_MIN_WIDTH = 800
UI_MIN_HEIGHT = 600

# Цветовая схема
UI_COLORS = {
    "primary": "#4a6fa5",      # Основной цвет
    "secondary": "#5e81ac",    # Вторичный цвет
    "accent": "#88c0d0",       # Акцентный цвет
    "background": "#2e3440",   # Фон приложения
    "card_bg": "#3b4252",      # Фон карточек
    "text_primary": "#eceff4", # Основной текст
    "text_secondary": "#d8dee9", # Вторичный текст
    "success": "#a3be8c",      # Успешные операции
    "warning": "#ebcb8b",      # Предупреждения
    "error": "#bf616a",        # Ошибки
}

# Список поддерживаемых моделей с описанием
SUPPORTED_MODELS = [
    {
        "id": "qwen3",
        "name": "Qwen3",
        "description": "Универсальный агент для различных задач",
        "source": "ModelScope",
        "category": "Универсальная модель",
        "requirements": {
            "ram": "8 ГБ",
            "disk": "4 ГБ",
            "gpu": "Опционально (>4GB VRAM)"
        },
        "install_command": "ollama pull qwen3"
    },
    {
        "id": "llama3.1",
        "name": "Llama 3.1",
        "description": "Универсальная модель для общих задач",
        "source": "Meta",
        "category": "Универсальная модель",
        "requirements": {
            "ram": "8 ГБ",
            "disk": "4 ГБ",
            "gpu": "Опционально (>4GB VRAM)"
        },
        "install_command": "ollama pull llama3.1"
    },
    {
        "id": "codellama",
        "name": "Code Llama",
        "description": "Специализированная модель для программирования",
        "source": "Meta",
        "category": "Программирование",
        "requirements": {
            "ram": "8 ГБ",
            "disk": "4 ГБ",
            "gpu": "Опционально (>4GB VRAM)"
        },
        "install_command": "ollama pull codellama"
    },
    {
        "id": "starcoder2",
        "name": "StarCoder 2",
        "description": "Модель для кодирования и генерации скриптов",
        "source": "HuggingFace",
        "category": "Программирование",
        "requirements": {
            "ram": "8 ГБ",
            "disk": "4 ГБ",
            "gpu": "Опционально (>4GB VRAM)"
        },
        "install_command": "ollama pull starcoder2"
    },
    {
        "id": "phi3-mini",
        "name": "Phi-3 Mini",
        "description": "Легкая модель для быстрого ответа",
        "source": "Microsoft",
        "category": "Легкая модель",
        "requirements": {
            "ram": "4 ГБ",
            "disk": "2 ГБ",
            "gpu": "Опционально"
        },
        "install_command": "ollama pull phi3-mini"
    },
    {
        "id": "deepseek-coder-v2",
        "name": "DeepSeek Coder V2",
        "description": "Специализированная модель для разработки кода",
        "source": "DeepSeek",
        "category": "Программирование",
        "requirements": {
            "ram": "8 ГБ",
            "disk": "4 ГБ",
            "gpu": "Опционально (>4GB VRAM)"
        },
        "install_command": "ollama pull deepseek-coder:v2"
    },
    {
        "id": "mistral-large",
        "name": "Mistral Large",
        "description": "Модель для логики и рассуждений",
        "source": "Mistral AI",
        "category": "Универсальная модель",
        "requirements": {
            "ram": "8 ГБ",
            "disk": "5 ГБ",
            "gpu": "Рекомендуется (>6GB VRAM)"
        },
        "install_command": "ollama pull mistral-large"
    },
    {
        "id": "mixtral",
        "name": "Mixtral",
        "description": "MoE модель для сложных задач",
        "source": "Mistral AI",
        "category": "Универсальная модель",
        "requirements": {
            "ram": "16 ГБ",
            "disk": "8 ГБ",
            "gpu": "Рекомендуется (>8GB VRAM)"
        },
        "install_command": "ollama pull mixtral"
    },
    {
        "id": "openchat",
        "name": "OpenChat",
        "description": "Быстрая и точная модель для диалогов",
        "source": "Open Source",
        "category": "Диалоговая модель",
        "requirements": {
            "ram": "8 ГБ",
            "disk": "4 ГБ",
            "gpu": "Опционально (>4GB VRAM)"
        },
        "install_command": "ollama pull openchat"
    }
]

# Создание необходимых директорий при импорте модуля
os.makedirs(CONFIG_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)
