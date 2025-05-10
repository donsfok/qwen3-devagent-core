#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Виджет информации о модели для приложения Qwen3-DevAgent-Core
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QSizePolicy)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from config import UI_COLORS

class ModelInfoWidget(QFrame):
    """Виджет для отображения информации о выбранной модели"""
    
    def __init__(self, parent=None):
        """
        Инициализация виджета информации о модели
        
        Args:
            parent: Родительский виджет
        """
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """Настройка пользовательского интерфейса виджета"""
        # Настройка внешнего вида виджета
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setStyleSheet(f"""
            ModelInfoWidget {{
                background-color: {UI_COLORS['card_bg']};
                border-radius: 8px;
                padding: 10px;
                margin: 5px;
            }}
        """)
        
        # Ограничение максимальной высоты
        self.setMaximumHeight(200)
        
        # Основной слой для виджета
        layout = QVBoxLayout(self)
        
        # Заголовок информационной панели
        title_label = QLabel("Информация о модели")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {UI_COLORS['text_primary']};")
        layout.addWidget(title_label)
        
        # Контейнер для информации о модели
        info_container = QWidget()
        info_layout = QVBoxLayout(info_container)
        info_layout.setContentsMargins(0, 0, 0, 0)
        
        # Название модели
        self.name_label = QLabel("Выберите модель из списка")
        self.name_label.setStyleSheet(f"color: {UI_COLORS['text_primary']}; font-weight: bold;")
        info_layout.addWidget(self.name_label)
        
        # Описание модели
        self.description_label = QLabel("")
        self.description_label.setWordWrap(True)
        self.description_label.setStyleSheet(f"color: {UI_COLORS['text_secondary']};")
        info_layout.addWidget(self.description_label)
        
        # Контейнер для требований и метаданных
        details_widget = QWidget()
        details_layout = QHBoxLayout(details_widget)
        details_layout.setContentsMargins(0, 0, 0, 0)
        
        # Требования к системе
        requirements_widget = QWidget()
        requirements_layout = QVBoxLayout(requirements_widget)
        requirements_layout.setContentsMargins(0, 0, 0, 0)
        
        requirements_title = QLabel("Требования:")
        requirements_title.setStyleSheet(f"color: {UI_COLORS['text_primary']}; font-weight: bold;")
        requirements_layout.addWidget(requirements_title)
        
        self.ram_label = QLabel("")
        self.ram_label.setStyleSheet(f"color: {UI_COLORS['text_secondary']};")
        requirements_layout.addWidget(self.ram_label)
        
        self.disk_label = QLabel("")
        self.disk_label.setStyleSheet(f"color: {UI_COLORS['text_secondary']};")
        requirements_layout.addWidget(self.disk_label)
        
        self.gpu_label = QLabel("")
        self.gpu_label.setStyleSheet(f"color: {UI_COLORS['text_secondary']};")
        requirements_layout.addWidget(self.gpu_label)
        
        details_layout.addWidget(requirements_widget)
        
        # Метаданные модели
        metadata_widget = QWidget()
        metadata_layout = QVBoxLayout(metadata_widget)
        metadata_layout.setContentsMargins(0, 0, 0, 0)
        
        metadata_title = QLabel("Метаданные:")
        metadata_title.setStyleSheet(f"color: {UI_COLORS['text_primary']}; font-weight: bold;")
        metadata_layout.addWidget(metadata_title)
        
        self.source_label = QLabel("")
        self.source_label.setStyleSheet(f"color: {UI_COLORS['text_secondary']};")
        metadata_layout.addWidget(self.source_label)
        
        self.category_label = QLabel("")
        self.category_label.setStyleSheet(f"color: {UI_COLORS['text_secondary']};")
        metadata_layout.addWidget(self.category_label)
        
        details_layout.addWidget(metadata_widget)
        
        # Добавление контейнеров в основной слой
        info_layout.addWidget(details_widget)
        layout.addWidget(info_container)
        
    def update_model_info(self, model_data):
        """
        Обновление информации о модели
        
        Args:
            model_data: Данные о модели (словарь)
        """
        if not model_data:
            self.clear_info()
            return
            
        # Обновление названия и описания
        self.name_label.setText(model_data['name'])
        self.description_label.setText(model_data['description'])
        
        # Обновление требований
        if 'requirements' in model_data:
            self.ram_label.setText(f"RAM: {model_data['requirements']['ram']}")
            self.disk_label.setText(f"Диск: {model_data['requirements']['disk']}")
            self.gpu_label.setText(f"GPU: {model_data['requirements']['gpu']}")
        
        # Обновление метаданных
        self.source_label.setText(f"Источник: {model_data['source']}")
        self.category_label.setText(f"Категория: {model_data['category']}")
        
    def clear_info(self):
        """Очистка информации о модели"""
        self.name_label.setText("Выберите модель из списка")
        self.description_label.setText("")
        self.ram_label.setText("")
        self.disk_label.setText("")
        self.gpu_label.setText("")
        self.source_label.setText("")
        self.category_label.setText("")
