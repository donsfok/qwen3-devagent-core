#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Панель чата для взаимодействия с ИИ-моделями
"""

import time
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
                             QPushButton, QLabel, QFrame, QScrollArea, 
                             QSplitter, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, pyqtSlot
from PyQt5.QtGui import QFont, QTextCursor

from config import UI_COLORS, MAX_TOKENS

class MessageWidget(QFrame):
    """Виджет для отображения одного сообщения в чате"""
    
    def __init__(self, is_user, message_text, parent=None):
        """
        Инициализация виджета сообщения
        
        Args:
            is_user: True если сообщение от пользователя, False если от ИИ
            message_text: Текст сообщения
            parent: Родительский виджет
        """
        super().__init__(parent)
        self.is_user = is_user
        self.message_text = message_text
        self.init_ui()
        
    def init_ui(self):
        """Настройка пользовательского интерфейса сообщения"""
        # Настройка внешнего вида в зависимости от типа сообщения
        if self.is_user:
            bg_color = UI_COLORS['primary']
            align = Qt.AlignRight
        else:
            bg_color = UI_COLORS['secondary']
            align = Qt.AlignLeft
            
        # Настройка стиля рамки
        self.setStyleSheet(f"""
            MessageWidget {{
                background-color: {bg_color};
                border-radius: 10px;
                padding: 8px;
                margin: 4px;
            }}
        """)
        
        # Создание слоя для сообщения
        layout = QVBoxLayout(self)
        
        # Метка с текстом сообщения
        message_label = QLabel(self.message_text)
        message_label.setWordWrap(True)
        message_label.setStyleSheet(f"color: {UI_COLORS['text_primary']};")
        layout.addWidget(message_label)
        
        # Настройка выравнивания
        layout.setAlignment(align)


class ModelResponseThread(QThread):
    """Поток для получения ответа от модели без блокировки интерфейса"""
    
    response_received = pyqtSignal(str)  # Сигнал с полученным ответом
    response_error = pyqtSignal(str)     # Сигнал с ошибкой
    token_received = pyqtSignal(str)     # Сигнал с текущим токеном (для потоковой генерации)
    
    def __init__(self, model_manager, model_id, prompt):
        """
        Инициализация потока ответа модели
        
        Args:
            model_manager: Экземпляр менеджера моделей
            model_id: Идентификатор модели
            prompt: Текст запроса к модели
        """
        super().__init__()
        self.model_manager = model_manager
        self.model_id = model_id
        self.prompt = prompt
        
    def run(self):
        """Основной метод потока - получение ответа от модели"""
        try:
            # Получение потокового ответа от модели
            full_response = ""
            
            for token in self.model_manager.generate_response(self.model_id, self.prompt):
                full_response += token
                self.token_received.emit(token)
                
            # Отправка сигнала с полным ответом
            self.response_received.emit(full_response)
            
        except Exception as e:
            # Отправка сигнала с ошибкой
            self.response_error.emit(str(e))


class ChatPanel(QWidget):
    """Панель чата для взаимодействия с ИИ-моделями"""
    
    def __init__(self, model_manager, parent=None):
        """
        Инициализация панели чата
        
        Args:
            model_manager: Экземпляр менеджера моделей
            parent: Родительский виджет
        """
        super().__init__(parent)
        self.model_manager = model_manager
        self.active_model = None
        self.messages = []  # История сообщений
        self.init_ui()
        
    def init_ui(self):
        """Настройка пользовательского интерфейса панели"""
        # Основной слой для панели
        layout = QVBoxLayout(self)
        
        # Заголовок чата
        self.chat_title = QLabel("Чат с ИИ")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        self.chat_title.setFont(title_font)
        self.chat_title.setStyleSheet(f"color: {UI_COLORS['text_primary']};")
        layout.addWidget(self.chat_title)
        
        # Статус активной модели
        self.model_status = QLabel("Выберите и запустите модель для начала общения")
        self.model_status.setStyleSheet(f"color: {UI_COLORS['text_secondary']};")
        layout.addWidget(self.model_status)
        
        # Область сообщений чата
        self.chat_area = QScrollArea()
        self.chat_area.setWidgetResizable(True)
        self.chat_area.setStyleSheet(f"""
            QScrollArea {{
                background-color: {UI_COLORS['background']};
                border: none;
            }}
        """)
        
        # Контейнер для сообщений
        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setAlignment(Qt.AlignTop)
        self.chat_layout.setContentsMargins(10, 10, 10, 10)
        self.chat_layout.setSpacing(10)
        
        # Добавление контейнера в область прокрутки
        self.chat_area.setWidget(self.chat_container)
        layout.addWidget(self.chat_area)
        
        # Поле ввода сообщения
        self.input_area = QTextEdit()
        self.input_area.setPlaceholderText("Введите сообщение...")
        self.input_area.setFixedHeight(80)
        self.input_area.setStyleSheet(f"""
            QTextEdit {{
                background-color: {UI_COLORS['card_bg']};
                color: {UI_COLORS['text_primary']};
                border-radius: 6px;
                padding: 8px;
            }}
        """)
        layout.addWidget(self.input_area)
        
        # Панель кнопок управления чатом
        buttons_layout = QHBoxLayout()
        
        # Кнопка отправки сообщения
        self.send_button = QPushButton("Отправить")
        self.send_button.setStyleSheet(f"""
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
        self.send_button.clicked.connect(self.on_send_clicked)
        self.send_button.setEnabled(False)  # Отключаем, пока не выбрана модель
        buttons_layout.addWidget(self.send_button)
        
        # Кнопка очистки чата
        self.clear_button = QPushButton("Очистить чат")
        self.clear_button.setStyleSheet(f"""
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
        """)
        self.clear_button.clicked.connect(self.clear_chat)
        buttons_layout.addWidget(self.clear_button)
        
        # Добавление панели кнопок
        layout.addLayout(buttons_layout)
        
        # Метка генерации ответа (скрыта по умолчанию)
        self.generation_label = QLabel("Генерация ответа...")
        self.generation_label.setStyleSheet(f"color: {UI_COLORS['accent']};")
        self.generation_label.setVisible(False)
        layout.addWidget(self.generation_label)
        
    def set_active_model(self, model_data):
        """
        Установка активной модели для чата
        
        Args:
            model_data: Данные о модели
        """
        self.active_model = model_data
        self.chat_title.setText(f"Чат с {model_data['name']}")
        self.model_status.setText(f"Активная модель: {model_data['name']} - {model_data['category']}")
        self.send_button.setEnabled(True)
        
        # Информационное сообщение в чате
        self.add_system_message(f"Модель {model_data['name']} активирована и готова к общению.\n"
                               f"Категория: {model_data['category']}")
        
    def add_message(self, is_user, text):
        """
        Добавление сообщения в чат
        
        Args:
            is_user: True если сообщение от пользователя, False если от ИИ
            text: Текст сообщения
        """
        # Создание виджета сообщения
        message_widget = MessageWidget(is_user, text)
        
        # Добавление сообщения в контейнер
        self.chat_layout.addWidget(message_widget)
        
        # Прокрутка до последнего сообщения
        self.chat_area.verticalScrollBar().setValue(
            self.chat_area.verticalScrollBar().maximum()
        )
        
        # Добавление в историю сообщений
        self.messages.append({
            "role": "user" if is_user else "assistant",
            "content": text
        })
        
    def add_system_message(self, text):
        """
        Добавление системного сообщения в чат
        
        Args:
            text: Текст системного сообщения
        """
        # Создание виджета сообщения без выделения (не от пользователя и не от ИИ)
        system_message = QLabel(text)
        system_message.setWordWrap(True)
        system_message.setStyleSheet(f"""
            QLabel {{
                color: {UI_COLORS['accent']};
                background-color: {UI_COLORS['background']};
                border: 1px solid {UI_COLORS['accent']};
                border-radius: 6px;
                padding: 8px;
            }}
        """)
        
        # Добавление сообщения в контейнер
        self.chat_layout.addWidget(system_message)
        
        # Прокрутка до последнего сообщения
        self.chat_area.verticalScrollBar().setValue(
            self.chat_area.verticalScrollBar().maximum()
        )
        
    def on_send_clicked(self):
        """Обработка нажатия на кнопку отправки сообщения"""
        if not self.active_model:
            QMessageBox.warning(self, "Модель не выбрана", 
                               "Пожалуйста, выберите и запустите модель для начала общения.")
            return
            
        # Получение текста из поля ввода
        message_text = self.input_area.toPlainText().strip()
        
        if not message_text:
            return
            
        # Добавление сообщения пользователя в чат
        self.add_message(True, message_text)
        
        # Очистка поля ввода
        self.input_area.clear()
        
        # Отключение кнопки отправки на время генерации ответа
        self.send_button.setEnabled(False)
        self.generation_label.setVisible(True)
        
        # Создание виджета для ответа ИИ (пустой изначально)
        ai_message = QLabel("")
        ai_message.setWordWrap(True)
        ai_message.setStyleSheet(f"""
            QLabel {{
                background-color: {UI_COLORS['secondary']};
                color: {UI_COLORS['text_primary']};
                border-radius: 10px;
                padding: 8px;
                margin: 4px;
            }}
        """)
        self.chat_layout.addWidget(ai_message)
        
        # Запуск потока для получения ответа от модели
        self.response_thread = ModelResponseThread(
            self.model_manager, 
            self.active_model['id'], 
            message_text
        )
        
        # Подключение сигналов
        self.response_thread.token_received.connect(
            lambda token: self.on_token_received(ai_message, token)
        )
        self.response_thread.response_received.connect(
            lambda response: self.on_response_received(response)
        )
        self.response_thread.response_error.connect(self.on_response_error)
        
        # Запуск потока
        self.response_thread.start()
        
    @pyqtSlot(QLabel, str)
    def on_token_received(self, label, token):
        """
        Обработка получения токена от модели (для потоковой генерации)
        
        Args:
            label: Метка для отображения текущего ответа
            token: Полученный токен
        """
        current_text = label.text()
        label.setText(current_text + token)
        
        # Прокрутка до последнего сообщения
        self.chat_area.verticalScrollBar().setValue(
            self.chat_area.verticalScrollBar().maximum()
        )
        
    @pyqtSlot(str)
    def on_response_received(self, response):
        """
        Обработка получения полного ответа от модели
        
        Args:
            response: Полный текст ответа
        """
        # Добавление ответа ИИ в историю сообщений
        self.messages.append({
            "role": "assistant",
            "content": response
        })
        
        # Возвращение интерфейса в нормальное состояние
        self.send_button.setEnabled(True)
        self.generation_label.setVisible(False)
        
    @pyqtSlot(str)
    def on_response_error(self, error_message):
        """
        Обработка ошибки при получении ответа от модели
        
        Args:
            error_message: Текст сообщения об ошибке
        """
        # Добавление сообщения об ошибке в чат
        self.add_system_message(f"Ошибка при генерации ответа: {error_message}")
        
        # Возвращение интерфейса в нормальное состояние
        self.send_button.setEnabled(True)
        self.generation_label.setVisible(False)
        
    def clear_chat(self):
        """Очистка чата и истории сообщений"""
        # Очистка виджетов
        for i in reversed(range(self.chat_layout.count())):
            item = self.chat_layout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()
                
        # Очистка истории сообщений
        self.messages = []
        
        # Добавление системного сообщения
        if self.active_model:
            self.add_system_message(f"Чат очищен. Модель {self.active_model['name']} готова к общению.")
        else:
            self.add_system_message("Чат очищен. Выберите и запустите модель для начала общения.")
