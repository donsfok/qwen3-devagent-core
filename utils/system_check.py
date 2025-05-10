#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Утилиты для проверки системных требований
"""

import os
import sys
import platform
import logging
import subprocess
from typing import Dict, Tuple, List, Optional

logger = logging.getLogger("SystemCheck")

def check_requirements() -> bool:
    """
    Проверка системных требований для работы приложения
    
    Returns:
        bool: True если все требования выполнены, иначе False
    """
    logger.info("Проверка системных требований...")
    
    # Проверка операционной системы
    if not check_os():
        logger.error("Операционная система не поддерживается")
        return False
        
    # Проверка версии Python
    if not check_python_version():
        logger.error("Версия Python не соответствует требованиям")
        return False
        
    # Проверка наличия Ollama
    if not check_ollama_installed():
        logger.error("Ollama не установлена или не доступна")
        return False
        
    # Проверка наличия необходимых системных утилит
    if not check_system_utilities():
        logger.error("Не все системные утилиты доступны")
        return False
        
    # Проверка соединения с сервисом Ollama
    if not check_ollama_connection():
        logger.error("Не удалось подключиться к сервису Ollama")
        return False
    
    logger.info("Все системные требования выполнены")
    return True
    
def check_os() -> bool:
    """
    Проверка операционной системы
    
    Returns:
        bool: True если ОС поддерживается, иначе False
    """
    system = platform.system()
    if system != "Linux":
        logger.warning(f"Операционная система {system} не поддерживается официально")
        return False
        
    # Проверка дистрибутива Linux
    try:
        # Чтение файла с информацией о дистрибутиве
        if os.path.exists("/etc/os-release"):
            with open("/etc/os-release", "r") as f:
                os_info = f.read()
                
            # Проверка поддерживаемых дистрибутивов
            supported_distros = ["ubuntu", "debian", "fedora", "arch", "centos"]
            if any(distro in os_info.lower() for distro in supported_distros):
                return True
                
            logger.warning("Дистрибутив Linux может быть не полностью совместим")
            return True
            
    except Exception as e:
        logger.warning(f"Не удалось определить дистрибутив Linux: {str(e)}")
        
    return True  # Разрешаем запуск на любой Linux
    
def check_python_version() -> bool:
    """
    Проверка версии Python
    
    Returns:
        bool: True если версия Python >= 3.8, иначе False
    """
    major, minor, _ = platform.python_version_tuple()
    if int(major) >= 3 and int(minor) >= 8:
        logger.info(f"Обнаружена совместимая версия Python: {platform.python_version()}")
        return True
    else:
        logger.warning(f"Несовместимая версия Python: {platform.python_version()}, требуется 3.8+")
        return False
        
def check_ollama_installed() -> bool:
    """
    Проверка наличия Ollama в системе
    
    Returns:
        bool: True если Ollama установлена, иначе False
    """
    try:
        # Проверка наличия исполняемого файла ollama
        result = subprocess.run(
            ["which", "ollama"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        if result.returncode == 0:
            ollama_path = result.stdout.strip()
            logger.info(f"Ollama найдена по пути: {ollama_path}")
            return True
        else:
            # Пробуем проверить напрямую по конкретным путям
            common_paths = [
                "/usr/bin/ollama",
                "/usr/local/bin/ollama",
                "/opt/ollama/ollama"
            ]
            
            for path in common_paths:
                if os.path.exists(path) and os.access(path, os.X_OK):
                    logger.info(f"Ollama найдена по пути: {path}")
                    return True
                    
            logger.warning("Ollama не найдена в системе")
            return False
            
    except Exception as e:
        logger.error(f"Ошибка при проверке наличия Ollama: {str(e)}")
        return False
        
def check_system_utilities() -> bool:
    """
    Проверка наличия необходимых системных утилит
    
    Returns:
        bool: True если все утилиты доступны, иначе False
    """
    required_utils = ["curl", "git"]
    missing_utils = []
    
    for util in required_utils:
        try:
            result = subprocess.run(
                ["which", util],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            if result.returncode != 0:
                missing_utils.append(util)
                
        except Exception as e:
            logger.error(f"Ошибка при проверке утилиты {util}: {str(e)}")
            missing_utils.append(util)
            
    if missing_utils:
        logger.warning(f"Отсутствуют необходимые утилиты: {', '.join(missing_utils)}")
        return False
        
    logger.info("Все необходимые системные утилиты доступны")
    return True
    
def check_ollama_connection() -> bool:
    """
    Проверка соединения с сервисом Ollama
    
    Returns:
        bool: True если соединение установлено, иначе False
    """
    try:
        # Проверка, запущен ли сервис Ollama
        result = subprocess.run(
            ["ps", "-ef"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        if "ollama serve" not in result.stdout:
            logger.warning("Сервис Ollama не запущен")
            
            # Попытка запустить сервис
            logger.info("Попытка запуска сервиса Ollama...")
            try:
                # Запуск сервиса в фоновом режиме
                subprocess.Popen(
                    ["ollama", "serve"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True
                )
                
                # Дожидаемся запуска сервиса
                import time
                import requests
                
                max_attempts = 5
                for attempt in range(max_attempts):
                    try:
                        response = requests.get("http://localhost:11434/api/tags", timeout=1)
                        if response.status_code == 200:
                            logger.info("Сервис Ollama успешно запущен")
                            return True
                    except:
                        pass
                        
                    time.sleep(2)
                    
                logger.error("Не удалось запустить сервис Ollama после нескольких попыток")
                return False
                
            except Exception as e:
                logger.error(f"Ошибка при запуске сервиса Ollama: {str(e)}")
                return False
                
        logger.info("Сервис Ollama запущен")
        return True
        
    except Exception as e:
        logger.error(f"Ошибка при проверке сервиса Ollama: {str(e)}")
        return False
        
def get_system_info() -> Dict[str, str]:
    """
    Получение информации о системе
    
    Returns:
        dict: Словарь с информацией о системе
    """
    info = {}
    
    # Общая информация о системе
    info['os'] = platform.system()
    info['os_release'] = platform.release()
    info['os_version'] = platform.version()
    
    # Информация о Python
    info['python_version'] = platform.python_version()
    
    # Информация о процессоре
    try:
        with open("/proc/cpuinfo", "r") as f:
            cpuinfo = f.read()
            
        for line in cpuinfo.split("\n"):
            if "model name" in line:
                info['cpu'] = line.split(":")[1].strip()
                break
                
        # Количество ядер
        info['cpu_cores'] = str(os.cpu_count())
    except:
        info['cpu'] = "Неизвестно"
        info['cpu_cores'] = "Неизвестно"
        
    # Информация о памяти
    try:
        with open("/proc/meminfo", "r") as f:
            meminfo = f.read()
            
        for line in meminfo.split("\n"):
            if "MemTotal" in line:
                mem_kb = int(line.split()[1])
                mem_gb = round(mem_kb / 1024 / 1024, 2)
                info['ram'] = f"{mem_gb} ГБ"
                break
    except:
        info['ram'] = "Неизвестно"
        
    # Информация о GPU
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        if result.returncode == 0 and result.stdout.strip():
            info['gpu'] = result.stdout.strip()
        else:
            info['gpu'] = "NVIDIA GPU не обнаружен"
    except:
        info['gpu'] = "Неизвестно"
        
    return info
