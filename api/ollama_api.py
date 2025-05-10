#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API для взаимодействия с Ollama в приложении Qwen3-DevAgent-Core
"""

import json
import requests
import logging
from typing import Dict, List, Any, Iterator

from config import (OLLAMA_API_MODELS, OLLAMA_API_GENERATE, 
                   OLLAMA_API_CHAT, REQUEST_TIMEOUT, MAX_TOKENS)

logger = logging.getLogger("OllamaAPI")

class OllamaAPI:
    """Класс для взаимодействия с API Ollama"""
    
    def __init__(self, base_url=None):
        """
        Инициализация API Ollama
        
        Args:
            base_url: Базовый URL для API Ollama (если не указан, используется из config)
        """
        self.api_models = OLLAMA_API_MODELS
        self.api_generate = OLLAMA_API_GENERATE
        self.api_chat = OLLAMA_API_CHAT
        
        if base_url:
            # Переопределение базовых URL, если указан пользовательский
            self.api_models = f"{base_url}/api/tags"
            self.api_generate = f"{base_url}/api/generate"
            self.api_chat = f"{base_url}/api/chat"
            
    def list_models(self) -> List[Dict[str, Any]]:
        """
        Получение списка установленных моделей
        
        Returns:
            list: Список словарей с информацией о моделях
        """
        try:
            logger.debug(f"Запрос списка моделей: {self.api_models}")
            
            # Отправка запроса к API
            response = requests.get(self.api_models, timeout=REQUEST_TIMEOUT)
            
            # Проверка успешности запроса
            response.raise_for_status()
            
            # Разбор ответа
            data = response.json()
            models = data.get('models', [])
            
            logger.info(f"Получен список моделей: {len(models)} найдено")
            return models
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при получении списка моделей: {str(e)}")
            raise Exception(f"Не удалось получить список моделей: {str(e)}")
            
    def generate(self, model: str, prompt: str, params: Dict[str, Any] = None) -> str:
        """
        Генерация ответа на запрос без потоковой передачи
        
        Args:
            model: Идентификатор модели
            prompt: Текст запроса
            params: Дополнительные параметры для генерации
            
        Returns:
            str: Текст ответа модели
        """
        try:
            # Формирование запроса
            request_data = {
                'model': model,
                'prompt': prompt
            }
            
            # Добавление дополнительных параметров
            if params:
                request_data.update(params)
                
            # Установка максимального количества токенов, если не указано
            if 'max_tokens' not in request_data:
                request_data['max_tokens'] = MAX_TOKENS
                
            logger.debug(f"Запрос генерации к модели {model}")
            
            # Отправка запроса к API
            response = requests.post(
                self.api_generate, 
                json=request_data,
                timeout=REQUEST_TIMEOUT
            )
            
            # Проверка успешности запроса
            response.raise_for_status()
            
            # Разбор ответа
            data = response.json()
            generated_text = data.get('response', '')
            
            logger.debug(f"Получен ответ от модели: {len(generated_text)} символов")
            return generated_text
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при генерации ответа от модели {model}: {str(e)}")
            raise Exception(f"Не удалось получить ответ от модели: {str(e)}")
            
    def generate_stream(self, model: str, prompt: str, params: Dict[str, Any] = None) -> Iterator[str]:
        """
        Потоковая генерация ответа на запрос
        
        Args:
            model: Идентификатор модели
            prompt: Текст запроса
            params: Дополнительные параметры для генерации
            
        Returns:
            iterator: Итератор по токенам ответа
        """
        try:
            # Формирование запроса
            request_data = {
                'model': model,
                'prompt': prompt,
                'stream': True
            }
            
            # Добавление дополнительных параметров
            if params:
                request_data.update(params)
                
            # Установка максимального количества токенов, если не указано
            if 'max_tokens' not in request_data:
                request_data['max_tokens'] = MAX_TOKENS
                
            logger.debug(f"Запрос потоковой генерации к модели {model}")
            
            # Отправка запроса к API с потоковой передачей
            response = requests.post(
                self.api_generate, 
                json=request_data,
                stream=True,
                timeout=REQUEST_TIMEOUT
            )
            
            # Проверка успешности запроса
            response.raise_for_status()
            
            # Обработка потоковых данных
            for line in response.iter_lines():
                if line:
                    # Декодирование JSON
                    line_data = json.loads(line)
                    
                    # Извлечение токена ответа
                    token = line_data.get('response', '')
                    
                    # Проверка завершения генерации
                    if line_data.get('done', False):
                        break
                        
                    # Возврат токена
                    yield token
                    
            logger.debug(f"Завершена потоковая генерация от модели {model}")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при потоковой генерации от модели {model}: {str(e)}")
            raise Exception(f"Не удалось получить потоковый ответ от модели: {str(e)}")
            
    def chat(self, model: str, messages: List[Dict[str, str]], params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Отправка запроса в формате чата
        
        Args:
            model: Идентификатор модели
            messages: Список сообщений чата в формате [{'role': 'user', 'content': 'текст'}]
            params: Дополнительные параметры для генерации
            
        Returns:
            dict: Структура с ответом модели
        """
        try:
            # Формирование запроса
            request_data = {
                'model': model,
                'messages': messages
            }
            
            # Добавление дополнительных параметров
            if params:
                request_data.update(params)
                
            logger.debug(f"Запрос чата к модели {model}")
            
            # Отправка запроса к API
            response = requests.post(
                self.api_chat, 
                json=request_data,
                timeout=REQUEST_TIMEOUT
            )
            
            # Проверка успешности запроса
            response.raise_for_status()
            
            # Разбор ответа
            data = response.json()
            
            logger.debug(f"Получен ответ чата от модели {model}")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при запросе чата к модели {model}: {str(e)}")
            raise Exception(f"Не удалось получить ответ чата от модели: {str(e)}")
            
    def chat_stream(self, model: str, messages: List[Dict[str, str]], params: Dict[str, Any] = None) -> Iterator[Dict[str, Any]]:
        """
        Потоковая отправка запроса в формате чата
        
        Args:
            model: Идентификатор модели
            messages: Список сообщений чата в формате [{'role': 'user', 'content': 'текст'}]
            params: Дополнительные параметры для генерации
            
        Returns:
            iterator: Итератор по частям ответа
        """
        try:
            # Формирование запроса
            request_data = {
                'model': model,
                'messages': messages,
                'stream': True
            }
            
            # Добавление дополнительных параметров
            if params:
                request_data.update(params)
                
            logger.debug(f"Запрос потокового чата к модели {model}")
            
            # Отправка запроса к API с потоковой передачей
            response = requests.post(
                self.api_chat, 
                json=request_data,
                stream=True,
                timeout=REQUEST_TIMEOUT
            )
            
            # Проверка успешности запроса
            response.raise_for_status()
            
            # Обработка потоковых данных
            for line in response.iter_lines():
                if line:
                    # Декодирование JSON
                    line_data = json.loads(line)
                    
                    # Возврат данных
                    yield line_data
                    
                    # Проверка завершения генерации
                    if line_data.get('done', False):
                        break
                        
            logger.debug(f"Завершен потоковый чат с моделью {model}")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при потоковом чате с моделью {model}: {str(e)}")
            raise Exception(f"Не удалось получить потоковый ответ чата от модели: {str(e)}")
