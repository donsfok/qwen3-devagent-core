#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Виджет списка моделей для приложения Qwen3-DevAgent-Core
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
                             QListWidgetItem, QPushButton, QLabel, QFrame, 
                             QProgressBar, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QIcon, QColor

from config import SUPPORTED_MODELS, UI_COLORS

class ModelListItem(QFrame):
    """Элемент списка моделей с информацией и кнопками управления"""
    
    def __init__(self, model_data, is_installed=False, parent=None):
        """
        Инициализация элемента списка моделей
        
        Args:
            model_data: Данные о модели (словарь)
            is_installed: Флаг, указывающий на то, установлена ли модель
            parent: Родительский виджет
        """
        super().__init__(parent)
        self.model_data = model_data
        self.is_installed = is_installed
        self.init_ui()
        
    def init_ui(self):
        """Настройка пользовательского интерфейса элемента"""
        # Настройка рамки и фона для элемента списка
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setStyleSheet(f"""
            ModelListItem {{
                background-color: {UI_COLORS['card_bg']};
                border-radius: 6px;
                margin: 2px;
                padding: 8px;
            }}
        """)
        
        # Основной слой для элемента списка
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Название модели
        name_label = QLabel(self.model_data['name'])
        name_font = QFont()
        name_font.setPointSize(12)
        name_font.setBold(True)
        name_label.setFont(name_font)
        name_label.setStyleSheet(f"color: {UI_COLORS['text_primary']};")
        layout.addWidget(name_label)
        
        # Источник модели
        source_label = QLabel(f"Источник: {self.model_data['source']}")
        source_label.setStyleSheet(f"color: {UI_COLORS['text_secondary']};")
        layout.addWidget(source_label)
        
        # Категория модели
        category_label = QLabel(f"Категория: {self.model_data['category']}")
        category_label.setStyleSheet(f"color: {UI_COLORS['text_secondary']};")
        layout.addWidget(category_label)
        
        # Статус установки
        status_layout = QHBoxLayout()
        self.status_label = QLabel()
        self.update_status_label()
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        layout.addLayout(status_layout)
        
        # Прогресс-бар для установки (скрытый по умолчанию)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Неопределенный прогресс
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
    def update_status_label(self):
        """Обновление метки статуса установки"""
        if self.is_installed:
            self.status_label.setText("Статус: Установлена")
            self.status_label.setStyleSheet(f"color: {UI_COLORS['success']};")
        else:
            self.status_label.setText("Статус: Не установлена")
            self.status_label.setStyleSheet(f"color: {UI_COLORS['warning']};")
            
    def set_installing(self, is_installing):
        """
        Установка состояния установки
        
        Args:
            is_installing: True если модель устанавливается, иначе False
        """
        if is_installing:
            self.status_label.setText("Статус: Установка...")
            self.status_label.setStyleSheet(f"color: {UI_COLORS['accent']};")
            self.progress_bar.setVisible(True)
        else:
            self.update_status_label()
            self.progress_bar.setVisible(False)
            
    def set_installed(self, is_installed):
        """
        Установка статуса установки
        
        Args:
            is_installed: True если модель установлена, иначе False
        """
        self.is_installed = is_installed
        self.update_status_label()
        self.progress_bar.setVisible(False)

class ModelListWidget(QWidget):
    """Виджет для отображения списка моделей с возможностью управления"""
    
    # Сигналы
    model_selected = pyqtSignal(dict)  # Сигнал о выборе модели
    install_model = pyqtSignal(dict)   # Сигнал для установки модели
    remove_model = pyqtSignal(dict)    # Сигнал для удаления модели
    run_model = pyqtSignal(dict)       # Сигнал для запуска модели
    
    def __init__(self, model_manager, parent=None):
        """
        Инициализация виджета списка моделей
        
        Args:
            model_manager: Экземпляр менеджера моделей
            parent: Родительский виджет
        """
        super().__init__(parent)
        self.model_manager = model_manager
        self.model_items = {}  # Хранение элементов списка по ID модели
        self.init_ui()
        
    def init_ui(self):
        """Настройка пользовательского интерфейса виджета"""
        # Основной слой для виджета
        layout = QVBoxLayout(self)
        
        # Заголовок списка
        title_label = QLabel("Доступные модели")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {UI_COLORS['text_primary']};")
        layout.addWidget(title_label)
        
        # Список моделей
        self.model_list = QListWidget()
        self.model_list.setSpacing(4)
        self.model_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {UI_COLORS['background']};
                border: none;
            }}
            QListWidget::item {{
                border: none;
                padding: 2px;
            }}
            QListWidget::item:selected {{
                background-color: {UI_COLORS['primary']};
                border-radius: 4px;
            }}
        """)
        self.model_list.itemClicked.connect(self.on_item_clicked)
        layout.addWidget(self.model_list)
        
        # Панель кнопок
        buttons_layout = QHBoxLayout()
        
        # Кнопка установки
        self.install_button = QPushButton("Установить")
        self.install_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {UI_COLORS['primary']};
                color: {UI_COLORS['text_primary']};
                padding: 8px 16px;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {UI_COLORS['secondary']};
            }}
            QPushButton:pressed {{
                background-color: {UI_COLORS['accent']};
            }}
            QPushButton:disabled {{
                background-color: #555;
                color: #999;
            }}
        """)
        self.install_button.clicked.connect(self.on_install_clicked)
        buttons_layout.addWidget(self.install_button)
        
        # Кнопка запуска
        self.run_button = QPushButton("Запустить")
        self.run_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {UI_COLORS['success']};
                color: {UI_COLORS['text_primary']};
                padding: 8px 16px;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: #8aab7b;
            }}
            QPushButton:pressed {{
                background-color: #7a9b6b;
            }}
            QPushButton:disabled {{
                background-color: #555;
                color: #999;
            }}
        """)
        self.run_button.clicked.connect(self.on_run_clicked)
        buttons_layout.addWidget(self.run_button)
        
        # Кнопка удаления
        self.remove_button = QPushButton("Удалить")
        self.remove_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {UI_COLORS['error']};
                color: {UI_COLORS['text_primary']};
                padding: 8px 16px;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: #aa555e;
            }}
            QPushButton:pressed {{
                background-color: #9a4a53;
            }}
            QPushButton:disabled {{
                background-color: #555;
                color: #999;
            }}
        """)
        self.remove_button.clicked.connect(self.on_remove_clicked)
        buttons_layout.addWidget(self.remove_button)
        
        # Добавление панели кнопок
        layout.addLayout(buttons_layout)
        
        # Кнопка обновления списка
        self.refresh_button = QPushButton("Обновить список")
        self.refresh_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {UI_COLORS['secondary']};
                color: {UI_COLORS['text_primary']};
                padding: 8px 16px;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {UI_COLORS['accent']};
            }}
            QPushButton:pressed {{
                background-color: {UI_COLORS['primary']};
            }}
        """)
        self.refresh_button.clicked.connect(self.refresh_model_list)
        layout.addWidget(self.refresh_button)
        
        # Изначально отключаем кнопки, пока модель не выбрана
        self.install_button.setEnabled(False)
        self.run_button.setEnabled(False)
        self.remove_button.setEnabled(False)
        
    def refresh_model_list(self):
        """Обновление списка моделей"""
        self.model_list.clear()
        self.model_items.clear()
        
        # Получение списка установленных моделей
        installed_models = self.model_manager.get_installed_models()
        
        # Добавление моделей из списка поддерживаемых
        for model_data in SUPPORTED_MODELS:
            is_installed = model_data['id'] in installed_models
            
            # Создание элемента списка
            item = QListWidgetItem()
            item.setData(Qt.UserRole, model_data)
            
            # Создание виджета элемента
            model_item = ModelListItem(model_data, is_installed)
            
            # Установка размера элемента
            item.setSizeHint(model_item.sizeHint())
            
            # Добавление элемента в список
            self.model_list.addItem(item)
            self.model_list.setItemWidget(item, model_item)
            
            # Сохранение ссылки на элемент
            self.model_items[model_data['id']] = {
                'item': item,
                'widget': model_item
            }
            
    def on_item_clicked(self, item):
        """
        Обработка выбора элемента списка
        
        Args:
            item: Выбранный элемент списка
        """
        model_data = item.data(Qt.UserRole)
        
        # Отправка сигнала о выборе модели
        self.model_selected.emit(model_data)
        
        # Активация кнопок управления
        is_installed = self.model_manager.is_model_installed(model_data['id'])
        self.install_button.setEnabled(not is_installed)
        self.run_button.setEnabled(is_installed)
        self.remove_button.setEnabled(is_installed)
        
    def on_install_clicked(self):
        """Обработка нажатия на кнопку установки"""
        selected_items = self.model_list.selectedItems()
        if not selected_items:
            return
            
        item = selected_items[0]
        model_data = item.data(Qt.UserRole)
        
        # Отображение состояния установки
        if model_data['id'] in self.model_items:
            widget = self.model_items[model_data['id']]['widget']
            widget.set_installing(True)
        
        # Отправка сигнала для установки модели
        self.install_model.emit(model_data)
        
    def on_run_clicked(self):
        """Обработка нажатия на кнопку запуска"""
        selected_items = self.model_list.selectedItems()
        if not selected_items:
            return
            
        item = selected_items[0]
        model_data = item.data(Qt.UserRole)
        
        # Отправка сигнала для запуска модели
        self.run_model.emit(model_data)
        
    def on_remove_clicked(self):
        """Обработка нажатия на кнопку удаления"""
        selected_items = self.model_list.selectedItems()
        if not selected_items:
            return
            
        item = selected_items[0]
        model_data = item.data(Qt.UserRole)
        
        # Отправка сигнала для удаления модели
        self.remove_model.emit(model_data)
        
    def update_model_status(self, model_id, is_installed):
        """
        Обновление статуса установки модели
        
        Args:
            model_id: Идентификатор модели
            is_installed: True если модель установлена, иначе False
        """
        if model_id in self.model_items:
            widget = self.model_items[model_id]['widget']
            widget.set_installed(is_installed)
            
            # Обновление доступности кнопок, если эта модель выбрана
            selected_items = self.model_list.selectedItems()
            if selected_items and selected_items[0] == self.model_items[model_id]['item']:
                self.install_button.setEnabled(not is_installed)
                self.run_button.setEnabled(is_installed)
                self.remove_button.setEnabled(is_installed)
