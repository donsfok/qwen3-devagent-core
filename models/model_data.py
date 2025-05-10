#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Структуры данных для работы с моделями в приложении Qwen3-DevAgent-Core
"""

import json
import os
import logging
from typing import Dict, List, Optional, Any

from config import MODELS_DIR

logger = logging.getLogger("ModelData")

class ModelMetadata:
    """Класс для хранения метаданных о модели"""
    
    def __init__(self, model_id: str, data: Dict[str, Any] = None):
        """
        Инициализация метаданных модели
        
        Args:
            model_id: Идентификатор модели
            data: Словарь с метаданными модели
        """
        self.model_id = model_id
        
        # Базовые метаданные
        self.name = None
        self.description = None
        self.source = None
        self.category = None
        self.requirements = {}
        self.install_command = None
        
        # Дополнительные метаданные
        self.tags = []
        self.parameters = {}
        self.version = None
        self.installed_date = None
        self.last_used = None
        
        # Заполнение данными
        if data:
            self.update_from_dict(data)
            
    def update_from_dict(self, data: Dict[str, Any]):
        """
        Обновление метаданных из словаря
        
        Args:
            data: Словарь с метаданными
        """
        # Обновление базовых полей
        self.name = data.get('name', self.name)
        self.description = data.get('description', self.description)
        self.source = data.get('source', self.source)
        self.category = data.get('category', self.category)
        self.requirements = data.get('requirements', self.requirements)
        self.install_command = data.get('install_command', self.install_command)
        
        # Обновление дополнительных полей
        self.tags = data.get('tags', self.tags)
        self.parameters = data.get('parameters', self.parameters)
        self.version = data.get('version', self.version)
        self.installed_date = data.get('installed_date', self.installed_date)
        self.last_used = data.get('last_used', self.last_used)
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Преобразование метаданных в словарь
        
        Returns:
            dict: Словарь с метаданными модели
        """
        return {
            'model_id': self.model_id,
            'name': self.name,
            'description': self.description,
            'source': self.source,
            'category': self.category,
            'requirements': self.requirements,
            'install_command': self.install_command,
            'tags': self.tags,
            'parameters': self.parameters,
            'version': self.version,
            'installed_date': self.installed_date,
            'last_used': self.last_used
        }
        
    def save(self):
        """Сохранение метаданных модели в файл"""
        try:
            # Создание директории для моделей, если она не существует
            os.makedirs(MODELS_DIR, exist_ok=True)
            
            # Путь к файлу метаданных
            metadata_path = os.path.join(MODELS_DIR, f"{self.model_id}_metadata.json")
            
            # Сохранение метаданных в файл
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
                
            logger.info(f"Метаданные модели {self.model_id} сохранены")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при сохранении метаданных модели {self.model_id}: {str(e)}")
            return False
            
    @classmethod
    def load(cls, model_id: str) -> Optional['ModelMetadata']:
        """
        Загрузка метаданных модели из файла
        
        Args:
            model_id: Идентификатор модели
            
        Returns:
            ModelMetadata: Экземпляр метаданных модели или None, если файл не найден
        """
        try:
            # Путь к файлу метаданных
            metadata_path = os.path.join(MODELS_DIR, f"{model_id}_metadata.json")
            
            # Проверка существования файла
            if not os.path.exists(metadata_path):
                logger.warning(f"Файл метаданных для модели {model_id} не найден")
                return None
                
            # Загрузка метаданных из файла
            with open(metadata_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Создание экземпляра метаданных
            metadata = cls(model_id)
            metadata.update_from_dict(data)
            
            logger.info(f"Метаданные модели {model_id} загружены")
            return metadata
            
        except Exception as e:
            logger.error(f"Ошибка при загрузке метаданных модели {model_id}: {str(e)}")
            return None

class ModelsList:
    """Класс для управления списком моделей"""
    
    def __init__(self):
        """Инициализация списка моделей"""
        self.models = {}  # Словарь моделей (ID -> метаданные)
        self.load_all_models()
        
    def load_all_models(self):
        """Загрузка всех моделей из директории с метаданными"""
        try:
            # Проверка существования директории
            if not os.path.exists(MODELS_DIR):
                os.makedirs(MODELS_DIR, exist_ok=True)
                return
                
            # Поиск файлов метаданных
            for filename in os.listdir(MODELS_DIR):
                if filename.endswith('_metadata.json'):
                    # Извлечение ID модели из имени файла
                    model_id = filename.replace('_metadata.json', '')
                    
                    # Загрузка метаданных
                    metadata = ModelMetadata.load(model_id)
                    if metadata:
                        self.models[model_id] = metadata
                        
            logger.info(f"Загружено {len(self.models)} моделей из директории метаданных")
            
        except Exception as e:
            logger.error(f"Ошибка при загрузке моделей: {str(e)}")
            
    def add_model(self, metadata: ModelMetadata):
        """
        Добавление модели в список
        
        Args:
            metadata: Метаданные модели
        """
        self.models[metadata.model_id] = metadata
        metadata.save()
        
    def remove_model(self, model_id: str) -> bool:
        """
        Удаление модели из списка
        
        Args:
            model_id: Идентификатор модели
            
        Returns:
            bool: True если модель удалена, иначе False
        """
        if model_id in self.models:
            # Удаление из словаря
            del self.models[model_id]
            
            # Удаление файла метаданных
            metadata_path = os.path.join(MODELS_DIR, f"{model_id}_metadata.json")
            if os.path.exists(metadata_path):
                os.remove(metadata_path)
                
            logger.info(f"Модель {model_id} удалена из списка")
            return True
        else:
            logger.warning(f"Модель {model_id} не найдена в списке для удаления")
            return False
            
    def get_model(self, model_id: str) -> Optional[ModelMetadata]:
        """
        Получение метаданных модели по ID
        
        Args:
            model_id: Идентификатор модели
            
        Returns:
            ModelMetadata: Метаданные модели или None, если модель не найдена
        """
        return self.models.get(model_id)
        
    def get_all_models(self) -> List[ModelMetadata]:
        """
        Получение списка всех моделей
        
        Returns:
            list: Список метаданных всех моделей
        """
        return list(self.models.values())
