#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Менеджер моделей для приложения Qwen3-DevAgent-Core
"""

import os
import json
import logging
import subprocess
import threading
import time

from PyQt5.QtCore import QObject, pyqtSignal

from api.ollama_api import OllamaAPI
from config import SUPPORTED_MODELS

logger = logging.getLogger("ModelManager")

class ModelManager(QObject):
    """Класс для управления моделями ИИ"""
    
    # Сигналы для асинхронных операций
    model_installed = pyqtSignal(str)     # Сигнал об успешной установке модели
    model_removed = pyqtSignal(str)       # Сигнал об успешном удалении модели
    install_progress = pyqtSignal(str)    # Сигнал о прогрессе установки
    install_error = pyqtSignal(str)       # Сигнал об ошибке установки
    
    def __init__(self, ollama_api):
        """
        Инициализация менеджера моделей
        
        Args:
            ollama_api: Экземпляр API для взаимодействия с Ollama
        """
        super().__init__()
        self.ollama_api = ollama_api
        self.installed_models = {}
        self.refresh_installed_models()
        
    def refresh_installed_models(self):
        """Обновление списка установленных моделей"""
        try:
            # Получение списка моделей через Ollama API
            models = self.ollama_api.list_models()
            
            # Обновление словаря установленных моделей
            self.installed_models = {}
            
            for model in models:
                model_id = model['name'].split(':')[0]  # Получение ID без тега
                self.installed_models[model_id] = model
                
            logger.info(f"Обновлен список установленных моделей: {len(self.installed_models)} моделей найдено")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при обновлении списка моделей: {str(e)}")
            return False
            
    def get_installed_models(self):
        """
        Получение списка установленных моделей
        
        Returns:
            list: Список идентификаторов установленных моделей
        """
        # Обновление списка моделей
        self.refresh_installed_models()
        return list(self.installed_models.keys())
        
    def is_model_installed(self, model_id):
        """
        Проверка, установлена ли модель
        
        Args:
            model_id: Идентификатор модели
            
        Returns:
            bool: True если модель установлена, иначе False
        """
        # Обновление списка моделей
        self.refresh_installed_models()
        return model_id in self.installed_models
        
    def get_model_info(self, model_id):
        """
        Получение информации о модели из списка поддерживаемых
        
        Args:
            model_id: Идентификатор модели
            
        Returns:
            dict: Данные о модели или None, если модель не найдена
        """
        for model in SUPPORTED_MODELS:
            if model['id'] == model_id:
                return model
        return None
        
    def install_model(self, model_data, success_callback=None, error_callback=None, progress_callback=None):
        """
        Установка модели через Ollama
        
        Args:
            model_data: Данные о модели для установки
            success_callback: Функция обратного вызова при успешной установке
            error_callback: Функция обратного вызова при ошибке установки
            progress_callback: Функция обратного вызова для обновления прогресса
        """
        def installation_thread():
            try:
                # Получение команды установки
                install_command = model_data.get('install_command', f"ollama pull {model_data['id']}")
                
                # Запуск установки с выводом прогресса
                logger.info(f"Начало установки модели {model_data['name']} (ID: {model_data['id']})")
                
                # Создание процесса
                process = subprocess.Popen(
                    install_command.split(),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True
                )
                
                # Чтение и обработка вывода
                while True:
                    output = process.stdout.readline()
                    if output == '' and process.poll() is not None:
                        break
                    if output:
                        logger.debug(output.strip())
                        if progress_callback:
                            progress_callback(f"Установка {model_data['name']}: {output.strip()}")
                
                # Проверка успешного завершения
                return_code = process.poll()
                if return_code == 0:
                    logger.info(f"Модель {model_data['name']} успешно установлена")
                    
                    # Обновление списка установленных моделей
                    self.refresh_installed_models()
                    
                    # Отправка сигнала об установке
                    self.model_installed.emit(model_data['id'])
                    
                    # Вызов функции обратного вызова
                    if success_callback:
                        success_callback()
                else:
                    error_output = process.stderr.read()
                    error_message = f"Ошибка установки модели (код {return_code}): {error_output}"
                    logger.error(error_message)
                    
                    # Отправка сигнала об ошибке
                    self.install_error.emit(error_message)
                    
                    # Вызов функции обратного вызова
                    if error_callback:
                        error_callback(error_message)
                        
            except Exception as e:
                error_message = f"Ошибка при установке модели: {str(e)}"
                logger.error(error_message)
                
                # Отправка сигнала об ошибке
                self.install_error.emit(error_message)
                
                # Вызов функции обратного вызова
                if error_callback:
                    error_callback(error_message)
        
        # Запуск установки в отдельном потоке
        install_thread = threading.Thread(target=installation_thread)
        install_thread.daemon = True
        install_thread.start()
        
    def remove_model(self, model_data, success_callback=None, error_callback=None):
        """
        Удаление модели
        
        Args:
            model_data: Данные о модели для удаления
            success_callback: Функция обратного вызова при успешном удалении
            error_callback: Функция обратного вызова при ошибке удаления
        """
        def removal_thread():
            try:
                # Формирование команды удаления
                model_id = model_data['id']
                remove_command = f"ollama rm {model_id}"
                
                # Запуск удаления
                logger.info(f"Начало удаления модели {model_data['name']} (ID: {model_id})")
                
                # Выполнение команды
                result = subprocess.run(
                    remove_command.split(),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True
                )
                
                # Проверка успешного завершения
                if result.returncode == 0:
                    logger.info(f"Модель {model_data['name']} успешно удалена")
                    
                    # Обновление списка установленных моделей
                    self.refresh_installed_models()
                    
                    # Отправка сигнала об удалении
                    self.model_removed.emit(model_id)
                    
                    # Вызов функции обратного вызова
                    if success_callback:
                        success_callback()
                else:
                    error_message = f"Ошибка удаления модели (код {result.returncode}): {result.stderr}"
                    logger.error(error_message)
                    
                    # Вызов функции обратного вызова
                    if error_callback:
                        error_callback(error_message)
                        
            except Exception as e:
                error_message = f"Ошибка при удалении модели: {str(e)}"
                logger.error(error_message)
                
                # Вызов функции обратного вызова
                if error_callback:
                    error_callback(error_message)
        
        # Запуск удаления в отдельном потоке
        remove_thread = threading.Thread(target=removal_thread)
        remove_thread.daemon = True
        remove_thread.start()
        
    def generate_response(self, model_id, prompt, max_tokens=None):
        """
        Генерация ответа модели на запрос
        
        Args:
            model_id: Идентификатор модели
            prompt: Текст запроса
            max_tokens: Максимальное количество токенов в ответе
            
        Returns:
            iterator: Итератор по токенам ответа
        """
        try:
            # Установка параметров генерации
            params = {}
            
            if max_tokens:
                params['max_tokens'] = max_tokens
                
            # Получение ответа от API
            for token in self.ollama_api.generate_stream(model_id, prompt, params):
                yield token
                
        except Exception as e:
            logger.error(f"Ошибка при генерации ответа от модели {model_id}: {str(e)}")
            raise e
