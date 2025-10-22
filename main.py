import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.progressbar import ProgressBar
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.graphics import Color, Rectangle
import yt_dlp
import json
import os
from datetime import datetime
import threading

# Налаштування кольорів
PRIMARY_COLOR = get_color_from_hex("#6200ee")
SECONDARY_COLOR = get_color_from_hex("#03dac6")
BACKGROUND_COLOR = get_color_from_hex("#f5f5f5")
TEXT_COLOR = get_color_from_hex("#333333")

class ColoredBoxLayout(BoxLayout):
    """BoxLayout з кольоровим фоном"""
    def __init__(self, bg_color=None, **kwargs):
        super().__init__(**kwargs)
        if bg_color:
            with self.canvas.before:
                Color(bg_color[0], bg_color[1], bg_color[2], bg_color[3] if len(bg_color) > 3 else 1)
                self.rect = Rectangle(size=self.size, pos=self.pos)
            self.bind(size=self._update_rect, pos=self._update_rect)
    
    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

class DownloadApp(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 20
        self.spacing = 15
        self.history_file = 'download_history.json'
        self.download_folder = 'Downloads'
        
        # Створюємо папку для завантажень
        if not os.path.exists(self.download_folder):
            os.makedirs(self.download_folder)
        
        # Заголовок
        title = Label(
            text='Video Downloader',
            size_hint_y=None,
            height=60,
            font_size='24sp',
            bold=True,
            color=PRIMARY_COLOR
        )
        self.add_widget(title)
        
        # Поле для URL
        self.url_input = TextInput(
            hint_text='Вставте URL відео тут...',
            size_hint_y=None,
            height=50,
            multiline=False,
            background_color=get_color_from_hex("#ffffff"),
            foreground_color=TEXT_COLOR,
            padding=[15, 10]
        )
        self.add_widget(self.url_input)
        
        # Вибір якості
        quality_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        quality_layout.add_widget(Label(text='Якість:', size_hint_x=0.3, color=TEXT_COLOR))
        
        self.quality_spinner = Spinner(
            text='best',
            values=('best', 'worst', '720p', '480p', '360p', 'audio only'),
            size_hint_x=0.7,
            background_color=PRIMARY_COLOR,
            color=get_color_from_hex("#ffffff")
        )
        quality_layout.add_widget(self.quality_spinner)
        self.add_widget(quality_layout)
        
        # Кнопка завантаження
        self.download_btn = Button(
            text='Завантажити',
            size_hint_y=None,
            height=50,
            background_color=PRIMARY_COLOR,
            background_normal='',
            color=get_color_from_hex("#ffffff"),
            font_size='18sp'
        )
        self.download_btn.bind(on_press=self.start_download)
        self.add_widget(self.download_btn)
        
        # Прогрес бар
        self.progress_bar = ProgressBar(
            max=100,
            size_hint_y=None,
            height=20
        )
        self.add_widget(self.progress_bar)
        self.progress_bar.opacity = 0  # Спочатку прихований
        
        # Статус
        self.status_label = Label(
            text='',
            size_hint_y=None,
            height=30,
            color=TEXT_COLOR
        )
        self.add_widget(self.status_label)
        
        # Історія завантажень
        history_label = Label(
            text='Історія завантажень:',
            size_hint_y=None,
            height=40,
            font_size='16sp',
            bold=True,
            color=TEXT_COLOR
        )
        self.add_widget(history_label)
        
        # Прокручувана область для історії
        scroll = ScrollView(size_hint=(1, 1))
        self.history_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.history_layout.bind(minimum_height=self.history_layout.setter('height'))
        scroll.add_widget(self.history_layout)
        self.add_widget(scroll)
        
        # Завантажуємо історію
        self.load_history()

    def start_download(self, instance):
        url = self.url_input.text.strip()
        if not url:
            self.show_popup('Помилка', 'Будь ласка, введіть URL відео')
            return
        
        self.download_btn.disabled = True
        self.progress_bar.opacity = 1
        self.progress_bar.value = 0
        self.status_label.text = 'Підготовка до завантаження...'
        
        # Запускаємо завантаження в окремому потоці
        thread = threading.Thread(target=self.download_video, args=(url,))
        thread.daemon = True
        thread.start()

    def download_video(self, url):
        try:
            quality = self.quality_spinner.text
            
            ydl_opts = {
                'outtmpl': os.path.join(self.download_folder, '%(title)s.%(ext)s'),
                'progress_hooks': [self.progress_hook],
            }
            
            if quality == 'audio only':
                ydl_opts.update({
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                })
            elif quality != 'best' and quality != 'worst':
                ydl_opts['format'] = f'best[height<={quality[:-1]}]'
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                # Зберігаємо в історію
                self.save_to_history({
                    'title': info.get('title', 'Невідомо'),
                    'url': url,
                    'quality': quality,
                    'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'file': ydl.prepare_filename(info)
                })
                
                Clock.schedule_once(lambda dt: self.download_complete(True, info.get('title', 'Невідомо')))
                
        except Exception as e:
            # Фіксуємо помилку в окремій змінній для лямбда-функції
            error_message = str(e)
            Clock.schedule_once(lambda dt, msg=error_message: self.download_complete(False, msg))

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            if 'total_bytes' in d and d['total_bytes']:
                percent = (d['downloaded_bytes'] / d['total_bytes']) * 100
            elif 'total_bytes_estimate' in d and d['total_bytes_estimate']:
                percent = (d['downloaded_bytes'] / d['total_bytes_estimate']) * 100
            else:
                percent = 0
            
            percent_str = d.get('_percent_str', '0%')
            if hasattr(percent_str, 'strip'):
                percent_str = percent_str.strip()
            else:
                percent_str = str(percent_str)
            
            Clock.schedule_once(lambda dt, p=percent, s=percent_str: self.update_progress(p, s))
        
        elif d['status'] == 'finished':
            Clock.schedule_once(lambda dt: self.update_progress(100, 'Завершено'))

    def update_progress(self, value, status):
        self.progress_bar.value = value
        self.status_label.text = f'Статус: {status}'

    def download_complete(self, success, message):
        self.download_btn.disabled = False
        self.progress_bar.opacity = 0
        
        if success:
            self.status_label.text = f'Успішно завантажено: {message}'
            self.show_popup('Успіх', f'Відео "{message}" успішно завантажено!')
            self.url_input.text = ''
            self.load_history()  # Оновлюємо історію
        else:
            self.status_label.text = f'Помилка: {message}'
            self.show_popup('Помилка', f'Не вдалося завантажити відео: {message}')

    def save_to_history(self, item):
        history = self.load_history_data()
        history.insert(0, item)  # Додаємо на початок
        # Обмежуємо історію останніми 50 записами
        history = history[:50]
        
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

    def load_history_data(self):
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return []

    def load_history(self):
        self.history_layout.clear_widgets()
        history = self.load_history_data()
        
        if not history:
            empty_label = Label(
                text='Історія завантажень порожня',
                size_hint_y=None,
                height=40,
                color=get_color_from_hex("#666666"),
                italic=True
            )
            self.history_layout.add_widget(empty_label)
            return
        
        for item in history:
            # Створюємо контейнер для історії з білим фоном
            history_item = ColoredBoxLayout(
                orientation='vertical',
                size_hint_y=None,
                height=80,
                padding=10,
                spacing=5,
                bg_color=get_color_from_hex("#ffffff")
            )
            
            # Заголовок
            title_label = Label(
                text=item['title'][:50] + ('...' if len(item['title']) > 50 else ''),
                size_hint_y=None,
                height=25,
                text_size=(None, None),
                halign='left',
                color=TEXT_COLOR,
                bold=True
            )
            title_label.bind(texture_size=title_label.setter('size'))
            
            # Деталі
            details_label = Label(
                text=f"Якість: {item['quality']} | {item['date']}",
                size_hint_y=None,
                height=20,
                text_size=(None, None),
                halign='left',
                color=get_color_from_hex("#666666"),
                font_size='12sp'
            )
            details_label.bind(texture_size=details_label.setter('size'))
            
            history_item.add_widget(title_label)
            history_item.add_widget(details_label)
            
            self.history_layout.add_widget(history_item)

    def show_popup(self, title, message):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        message_label = Label(text=message)
        content.add_widget(message_label)
        
        btn = Button(
            text='OK',
            size_hint_y=None,
            height=40,
            background_color=PRIMARY_COLOR,
            background_normal='',
            color=get_color_from_hex("#ffffff")
        )
        
        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.8, 0.4)
        )
        
        btn.bind(on_press=popup.dismiss)
        content.add_widget(btn)
        popup.open()

class VideoDownloaderApp(App):
    def build(self):
        Window.clearcolor = BACKGROUND_COLOR
        self.title = 'Video Downloader'
        return DownloadApp()

if __name__ == '__main__':
    VideoDownloaderApp().run()