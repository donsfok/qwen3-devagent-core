#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Главное окно приложения Qwen3-DevAgent-Core
"""

import sys
import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QSplitter, QTabWidget, QPushButton, QLabel, 
                             QStatusBar, QMessageBox, QAction, QMenu, QToolBar)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont

from ui.model_list import ModelListWidget
from ui.chat_panel import ChatPanel
from ui.model_info import ModelInfoWidget
from models.model_manager import ModelManager
from config import UI_WINDOW_TITLE, UI_WINDOW_WIDTH, UI_WINDOW_HEIGHT, UI_MIN_WIDTH, UI_MIN_HEIGHT

class MainWindow(QMainWindow):
    """Главное окно приложения"""
    
    def __init__(self, model_manager):
        """
        Инициализация главного окна
        
        Args:
            model_manager: Экземпляр менеджера моделей
        """
        super().__init__()
        self.model_manager = model_manager
        self.current_model = None
        
        self.init_ui()
        
    def init_ui(self):
        """Настройка пользовательского интерфейса"""
        # Настройка основных параметров окна
        self.setWindowTitle(UI_WINDOW_TITLE)
        self.setGeometry(100, 100, UI_WINDOW_WIDTH, UI_WINDOW_HEIGHT)
        self.setMinimumSize(UI_MIN_WIDTH, UI_MIN_HEIGHT)
        
        # Создание меню и панели инструментов
        self.create_menu()
        self.create_toolbar()
        
        # Создание центрального виджета
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Основной слой для размещения элементов
        main_layout = QVBoxLayout(self.central_widget)
        
        # Создание разделителя для основных панелей
        self.splitter = QSplitter(Qt.Horizontal)
        
        # Левая часть (список моделей)
        self.model_list_widget = ModelListWidget(self.model_manager)
        self.model_list_widget.model_selected.connect(self.on_model_selected)
        self.model_list_widget.install_model.connect(self.on_install_model)
        self.model_list_widget.remove_model.connect(self.on_remove_model)
        self.model_list_widget.run_model.connect(self.on_run_model)
        self.splitter.addWidget(self.model_list_widget)
        
        # Правая часть (информация о модели + чат)
        self.right_panel = QWidget()
        right_layout = QVBoxLayout(self.right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Добавление информационной панели модели
        self.model_info_widget = ModelInfoWidget()
        right_layout.addWidget(self.model_info_widget)
        
        # Добавление чат-панели
        self.chat_panel = ChatPanel(self.model_manager)
        right_layout.addWidget(self.chat_panel)
        
        # Добавление правой панели в разделитель
        self.splitter.addWidget(self.right_panel)
        
        # Установка размеров разделителя
        self.splitter.setSizes([int(UI_WINDOW_WIDTH * 0.3), int(UI_WINDOW_WIDTH * 0.7)])
        
        # Добавление разделителя в основной слой
        main_layout.addWidget(self.splitter)
        
        # Создание и настройка строки состояния
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Готов к работе")
        
        # Первоначальное обновление списка моделей
        self.model_list_widget.refresh_model_list()
        
    def create_menu(self):
        """Создание главного меню приложения"""
        menu_bar = self.menuBar()
        
        # Меню "Файл"
        file_menu = menu_bar.addMenu("Файл")
        
        refresh_action = QAction("Обновить список моделей", self)
        refresh_action.triggered.connect(self.refresh_models)
        file_menu.addAction(refresh_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Выход", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Меню "Модели"
        models_menu = menu_bar.addMenu("Модели")
        
        install_action = QAction("Установить выбранную модель", self)
        install_action.triggered.connect(lambda: self.on_install_model(self.current_model))
        models_menu.addAction(install_action)
        
        run_action = QAction("Запустить выбранную модель", self)
        run_action.triggered.connect(lambda: self.on_run_model(self.current_model))
        models_menu.addAction(run_action)
        
        remove_action = QAction("Удалить выбранную модель", self)
        remove_action.triggered.connect(lambda: self.on_remove_model(self.current_model))
        models_menu.addAction(remove_action)
        
        models_menu.addSeparator()
        
        check_updates_action = QAction("Проверить обновления моделей", self)
        check_updates_action.triggered.connect(self.check_model_updates)
        models_menu.addAction(check_updates_action)
        
        # Меню "Справка"
        help_menu = menu_bar.addMenu("Справка")
        
        about_action = QAction("О программе", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)
        
    def create_toolbar(self):
        """Создание панели инструментов"""
        self.toolbar = QToolBar("Основная панель")
        self.toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(Qt.TopToolBarArea, self.toolbar)
        
        refresh_action = QAction("Обновить", self)
        refresh_action.setStatusTip("Обновить список моделей")
        refresh_action.triggered.connect(self.refresh_models)
        self.toolbar.addAction(refresh_action)
        
        self.toolbar.addSeparator()
        
    def refresh_models(self):
        """Обновление списка моделей"""
        self.status_bar.showMessage("Обновление списка моделей...")
        self.model_list_widget.refresh_model_list()
        self.status_bar.showMessage("Список моделей обновлен", 3000)
        
    def check_model_updates(self):
        """Проверка обновлений моделей"""
        self.status_bar.showMessage("Проверка обновлений моделей...")
        # Здесь будет логика проверки обновлений для моделей
        self.status_bar.showMessage("Проверка обновлений завершена", 3000)
        
    def show_about_dialog(self):
        """Отображение диалога 'О программе'"""
        QMessageBox.about(self, "О программе", 
                          "Qwen3-DevAgent-Core\n\n"
                          "Версия: 1.0.0\n\n"
                          "Приложение для работы с локальными ИИ-моделями\n"
                          "Позволяет устанавливать, запускать и взаимодействовать "
                          "с различными моделями искусственного интеллекта.")
        
    def on_model_selected(self, model_data):
        """
        Обработка выбора модели из списка
        
        Args:
            model_data: Данные о выбранной модели
        """
        self.current_model = model_data
        self.model_info_widget.update_model_info(model_data)
        self.status_bar.showMessage(f"Выбрана модель: {model_data['name']}")
        
    def on_install_model(self, model_data):
        """
        Обработка установки модели
        
        Args:
            model_data: Данные о модели для установки
        """
        if not model_data:
            self.status_bar.showMessage("Модель не выбрана", 3000)
            return
            
        reply = QMessageBox.question(self, 'Установка модели',
                                     f"Вы действительно хотите установить модель {model_data['name']}?\n"
                                     f"Требования: RAM: {model_data['requirements']['ram']}, "
                                     f"Диск: {model_data['requirements']['disk']}", 
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.status_bar.showMessage(f"Установка модели {model_data['name']}...")
            # Запускаем установку модели в отдельном потоке
            self.model_manager.install_model(model_data, 
                                             success_callback=lambda: self.on_install_success(model_data),
                                             error_callback=self.on_install_error,
                                             progress_callback=self.on_install_progress)
            
    def on_install_success(self, model_data):
        """
        Обработка успешной установки модели
        
        Args:
            model_data: Данные об установленной модели
        """
        self.status_bar.showMessage(f"Модель {model_data['name']} успешно установлена", 5000)
        self.model_list_widget.refresh_model_list()
        
    def on_install_error(self, error_message):
        """
        Обработка ошибки при установке модели
        
        Args:
            error_message: Текст сообщения об ошибке
        """
        self.status_bar.showMessage(f"Ошибка установки модели: {error_message}", 5000)
        QMessageBox.critical(self, "Ошибка установки модели", error_message)
        
    def on_install_progress(self, progress_message):
        """
        Обработка прогресса установки модели
        
        Args:
            progress_message: Текст сообщения о прогрессе
        """
        self.status_bar.showMessage(progress_message)
        
    def on_remove_model(self, model_data):
        """
        Обработка удаления модели
        
        Args:
            model_data: Данные о модели для удаления
        """
        if not model_data:
            self.status_bar.showMessage("Модель не выбрана", 3000)
            return
            
        reply = QMessageBox.question(self, 'Удаление модели',
                                     f"Вы действительно хотите удалить модель {model_data['name']}?", 
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.status_bar.showMessage(f"Удаление модели {model_data['name']}...")
            self.model_manager.remove_model(model_data, 
                                           success_callback=lambda: self.on_remove_success(model_data),
                                           error_callback=self.on_remove_error)
            
    def on_remove_success(self, model_data):
        """
        Обработка успешного удаления модели
        
        Args:
            model_data: Данные об удаленной модели
        """
        self.status_bar.showMessage(f"Модель {model_data['name']} успешно удалена", 5000)
        self.model_list_widget.refresh_model_list()
        
    def on_remove_error(self, error_message):
        """
        Обработка ошибки при удалении модели
        
        Args:
            error_message: Текст сообщения об ошибке
        """
        self.status_bar.showMessage(f"Ошибка удаления модели: {error_message}", 5000)
        QMessageBox.critical(self, "Ошибка удаления модели", error_message)
        
    def on_run_model(self, model_data):
        """
        Обработка запуска модели
        
        Args:
            model_data: Данные о модели для запуска
        """
        if not model_data:
            self.status_bar.showMessage("Модель не выбрана", 3000)
            return
            
        # Проверяем, установлена ли модель
        if not self.model_manager.is_model_installed(model_data['id']):
            reply = QMessageBox.question(self, 'Модель не установлена',
                                        f"Модель {model_data['name']} не установлена. Хотите установить?", 
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            
            if reply == QMessageBox.Yes:
                self.on_install_model(model_data)
            return
            
        self.status_bar.showMessage(f"Запуск модели {model_data['name']}...")
        
        # Активируем модель в чате
        self.chat_panel.set_active_model(model_data)
        self.status_bar.showMessage(f"Модель {model_data['name']} запущена и готова к использованию", 5000)
