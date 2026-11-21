import sys
import os
import tempfile
import re
from datetime import datetime
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLabel, QTextEdit, QPushButton, 
                               QComboBox, QMessageBox, QFileDialog, QGroupBox,
                               QSpinBox, QSlider, QCheckBox, QDialog, QTextBrowser)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QPainter, QColor, QPen, QIcon, QAction
import mido
from mido import MidiFile, MidiTrack, Message, MetaMessage


class ProjectInfo:
    """项目信息元数据（集中管理所有项目相关信息）"""
    VERSION = "3.1.1"
    BUILD_DATE = datetime.now().strftime("%Y-%m-%d")  # 动态获取当前日期
    AUTHOR = "杜玛"
    LICENSE = "MIT"
    COPYRIGHT = "© 永久 杜玛"
    URL = "https://github.com/duma520"
    MAINTAINER_EMAIL = "不提供"
    NAME = "简谱转音乐工具"
    DESCRIPTION = """简谱转音乐工具
主要功能：
• 将简谱转换为MIDI音乐
• 支持多种调式和节拍
• 实时播放预览
• 钢琴卷帘可视化
• 支持和弦识别
• 多种乐器选择
"""

    VERSION_HISTORY = {
        "1.0.0": "初始版本",
        "2.0.0": "添加钢琴卷帘可视化",
        "2.5.0": "增强和弦识别功能",
        "2.9.0": "优化界面和性能"
    }
    
    HELP_TEXT = """
基本操作指南：

1. 输入简谱
   - 使用数字1-7代表音符
   - 括号内是时值（1=四分音符）
   - | 表示小节线
   - 加 ' 表示高音区
   - 加 . 表示低音区

2. 设置参数
   - 选择速度和调式
   - 调整音量和乐器
   - 启用/禁用和弦识别

3. 播放和保存
   - 点击播放按钮试听
   - 点击保存为MIDI文件

详细说明请参考示例输入。
"""

    @classmethod
    def get_metadata(cls) -> dict:
        """获取主要元数据字典"""
        return {
            'version': cls.VERSION,
            'author': cls.AUTHOR,
            'license': cls.LICENSE,
            'url': cls.URL
        }

    @classmethod
    def get_header(cls) -> str:
        """生成标准化的项目头信息"""
        return f"{cls.NAME} {cls.VERSION} | {cls.LICENSE} License | {cls.URL}"

    @classmethod
    def get_about_info(cls):
        """获取ABOUT信息字典"""
        return {
            "name": cls.NAME,
            "version": cls.VERSION,
            "build_date": cls.BUILD_DATE,
            "author": cls.AUTHOR,
            "license": cls.LICENSE,
            "copyright": cls.COPYRIGHT,
            "url": cls.URL,
            "description": cls.DESCRIPTION,
            "features": [
                "简谱到MIDI转换",
                "实时播放预览",
                "钢琴卷帘可视化",
                "多乐器支持",
                "和弦识别功能",
                "多种调式选择"
            ]
        }


class AboutDialog(QDialog):
    """关于对话框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("关于")
        self.setFixedSize(400, 500)
        
        layout = QVBoxLayout()
        
        # 标题
        title_label = QLabel(ProjectInfo.NAME)
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # 版本信息
        info = ProjectInfo.get_about_info()
        version_label = QLabel(f"版本: {info['version']} (Build: {info['build_date']})")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version_label)
        
        # 作者信息
        author_label = QLabel(f"作者: {info['author']}")
        author_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(author_label)
        
        # 版权信息
        copyright_label = QLabel(info['copyright'])
        copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(copyright_label)
        
        # 许可证
        license_label = QLabel(f"许可证: {info['license']}")
        license_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(license_label)
        
        # 网址
        url_label = QLabel(f"网址: {info['url']}")
        url_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        url_label.setOpenExternalLinks(True)
        url_label.setTextFormat(Qt.TextFormat.RichText)
        url_label.setText(f'<a href="{info["url"]}">{info["url"]}</a>')
        layout.addWidget(url_label)
        
        # 分割线
        line = QWidget()
        line.setFixedHeight(2)
        line.setStyleSheet("background-color: #c0c0c0;")
        layout.addWidget(line)
        
        # 描述
        desc_label = QLabel(info['description'])
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc_label)
        
        # 功能列表
        features_label = QLabel("主要功能:")
        features_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(features_label)
        
        for feature in info['features']:
            feature_label = QLabel(f"• {feature}")
            layout.addWidget(feature_label)
        
        # 版本历史
        history_label = QLabel("\n版本历史:")
        history_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(history_label)
        
        for version, desc in ProjectInfo.VERSION_HISTORY.items():
            history_item = QLabel(f"{version}: {desc}")
            layout.addWidget(history_item)
        
        # 关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        layout.addStretch()
        self.setLayout(layout)


class HelpDialog(QDialog):
    """帮助对话框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("帮助")
        self.setFixedSize(500, 400)
        
        layout = QVBoxLayout()
        
        # 帮助文本
        text_browser = QTextBrowser()
        text_browser.setPlainText(ProjectInfo.HELP_TEXT)
        layout.addWidget(text_browser)
        
        # 关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)


class PianoRollWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.notes = []
        self.current_pos = 0
        self.setMinimumHeight(150)
        self.setMaximumHeight(200)
        
    def set_notes(self, notes):
        self.notes = notes
        self.update()
    
    def set_current_pos(self, pos):
        self.current_pos = pos
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        width = self.width()
        height = self.height()
        
        if not self.notes:
            # 显示提示信息
            painter.setPen(QColor(100, 100, 100))
            painter.setFont(QFont("Arial", 12))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "暂无音符数据")
            return
        
        # 计算时间范围
        max_time = max([n[1] + n[2] for n in self.notes]) if self.notes else 1
        time_scale = (width - 60) / max_time if max_time > 0 else width - 60
        
        # 绘制背景网格
        painter.setPen(QPen(QColor(200, 200, 200), 1, Qt.PenStyle.DotLine))
        for i in range(0, int(max_time) + 1):
            x = 50 + i * time_scale
            painter.drawLine(x, 0, x, height)
        
        # 绘制音符
        note_colors = [QColor(70, 130, 180), QColor(100, 150, 200), QColor(130, 170, 220)]
        
        for i, note in enumerate(self.notes):
            pitch, start, duration, velocity = note
            
            # 计算Y位置（基于音高）
            y = height - 20 - ((pitch - 48) * 2)  # 简单映射
            
            # 确保在可见范围内
            if y < 0 or y > height - 10:
                continue
            
            x = 50 + start * time_scale
            w = max(3, duration * time_scale)  # 最小宽度3像素
            
            # 根据力度设置颜色亮度
            color = note_colors[i % len(note_colors)]
            painter.setPen(QPen(QColor(0, 0, 0), 1))  # 黑色边框
            painter.setBrush(color)
            painter.drawRoundedRect(x, y - 8, w, 16, 4, 4)
        
        # 绘制当前位置指示线
        if max_time > 0:
            x_pos = 50 + self.current_pos * time_scale
            painter.setPen(QPen(QColor(255, 0, 0), 2))
            painter.drawLine(x_pos, 0, x_pos, height)
        
        # 绘制时间刻度
        painter.setPen(QPen(QColor(0, 0, 0), 1))
        painter.setFont(QFont("Arial", 8))
        for i in range(0, int(max_time) + 1):
            x = 50 + i * time_scale
            painter.drawText(x - 10, height - 5, str(i))


class MusicConverter(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 立即显示窗口并处理事件
        self.show()
        QApplication.processEvents()
        
        # 初始化 UI
        self.init_ui()
        QApplication.processEvents()
        
        # 初始化变量
        self.current_midi_file = None
        self.playback_active = False
        self.notes_data = []
        self.current_pos = 0
        self.pygame_initialized = False
        self.pygame = None  # 用于存储pygame模块引用
        
        # 延迟初始化音频（200ms后）
        QTimer.singleShot(200, self.init_audio)
        
    def init_ui(self):
        # 设置窗口标题（使用ProjectInfo）
        self.setWindowTitle(f"{ProjectInfo.NAME} {ProjectInfo.VERSION} (Build: {ProjectInfo.BUILD_DATE})")
        
        # 尝试设置图标
        if os.path.exists("icon.ico"):
            self.setWindowIcon(QIcon("icon.ico"))
        
        self.setGeometry(100, 100, 900, 700)
        
        # 创建菜单栏
        menubar = self.menuBar()
        
        # 帮助菜单
        help_menu = menubar.addMenu("帮助")
        
        # 关于动作
        about_action = QAction("关于", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        # 帮助动作
        help_action = QAction("使用帮助", self)
        help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)
        
        # 主窗口部件
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        
        # 控制面板
        control_group = QGroupBox("设置")
        control_layout = QHBoxLayout()
        
        # 速度设置
        control_layout.addWidget(QLabel('速度(BPM):'))
        self.tempo_spin = QSpinBox()
        self.tempo_spin.setRange(40, 240)
        self.tempo_spin.setValue(120)
        control_layout.addWidget(self.tempo_spin)
        
        # 音量控制
        control_layout.addWidget(QLabel('音量:'))
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 127)
        self.volume_slider.setValue(100)
        self.volume_slider.setFixedWidth(150)
        control_layout.addWidget(self.volume_slider)
        
        # 调式选择
        control_layout.addWidget(QLabel('调式:'))
        self.key_combo = QComboBox()
        self.key_combo.addItems(['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'])
        control_layout.addWidget(self.key_combo)
        
        # 节拍选择
        control_layout.addWidget(QLabel('节拍:'))
        self.beat_combo = QComboBox()
        self.beat_combo.addItems(['4/4', '3/4', '2/4', '6/8'])
        control_layout.addWidget(self.beat_combo)
        
        control_group.setLayout(control_layout)
        main_layout.addWidget(control_group)
        
        # 乐器选择面板
        instrument_group = QGroupBox("乐器设置")
        instrument_layout = QHBoxLayout()
        
        # 主乐器选择
        instrument_layout.addWidget(QLabel('乐器:'))
        self.instrument_combo = QComboBox()
        self.populate_instruments()
        instrument_layout.addWidget(self.instrument_combo)
        
        # 和弦支持
        self.chord_check = QCheckBox('启用和弦识别')
        self.chord_check.setChecked(True)
        instrument_layout.addWidget(self.chord_check)
        
        instrument_layout.addStretch()
        instrument_group.setLayout(instrument_layout)
        main_layout.addWidget(instrument_group)
        
        # 输入区域
        input_group = QGroupBox("简谱输入")
        input_layout = QVBoxLayout()
        
        # 示例按钮
        example_btn = QPushButton('显示示例')
        example_btn.clicked.connect(self.show_example)
        example_btn.setFixedWidth(100)
        input_layout.addWidget(example_btn, alignment=Qt.AlignmentFlag.AlignRight)
        
        # 输入框
        self.input_area = QTextEdit()
        self.input_area.setPlaceholderText(
            '请输入简谱...\n\n'
            '格式说明：\n'
            '• 数字1-7代表音符\n'
            '• 括号内是时值（1=四分音符，2=二分音符，0.5=八分音符）\n'
            '• | 表示小节线\n'
            '• 加 \' 表示高音区（如 1\'）\n'
            '• 加 . 表示低音区（如 1.）\n'
            '• 和弦可以用空格分隔多个音符\n'
            '• #开头的行为注释\n\n'
            '示例：1 2 3 4 5 6 7  |  1(2) 2(1) 3(1)  |  1\' 2\' 3\'  |  1. 2. 3.'
        )
        self.input_area.setFont(QFont("Consolas", 11))
        input_layout.addWidget(self.input_area)
        
        input_group.setLayout(input_layout)
        main_layout.addWidget(input_group)
        
        # 钢琴卷帘窗
        self.piano_roll = PianoRollWidget()
        main_layout.addWidget(self.piano_roll)
        
        # 按钮面板
        button_layout = QHBoxLayout()
        
        self.play_btn = QPushButton('播放')
        self.play_btn.clicked.connect(self.toggle_playback)
        self.play_btn.setFixedWidth(80)
        button_layout.addWidget(self.play_btn)
        
        self.stop_btn = QPushButton('停止')
        self.stop_btn.clicked.connect(self.stop_music)
        self.stop_btn.setFixedWidth(80)
        button_layout.addWidget(self.stop_btn)
        
        save_btn = QPushButton('保存为MIDI')
        save_btn.clicked.connect(self.save_midi)
        save_btn.setFixedWidth(100)
        button_layout.addWidget(save_btn)
        
        clear_btn = QPushButton('清除')
        clear_btn.clicked.connect(self.clear_input)
        clear_btn.setFixedWidth(80)
        button_layout.addWidget(clear_btn)
        
        button_layout.addStretch()
        main_layout.addLayout(button_layout)
        
        # 状态栏
        self.status_bar = self.statusBar()
        self.status_bar.showMessage(f'{ProjectInfo.get_header()} | 正在初始化...')
        
        # 播放定时器
        self.playback_timer = QTimer()
        self.playback_timer.timeout.connect(self.update_playback_position)
        self.playback_timer.setInterval(50)
    
    def show_about(self):
        """显示关于对话框"""
        about_dialog = AboutDialog(self)
        about_dialog.exec()
    
    def show_help(self):
        """显示帮助对话框"""
        help_dialog = HelpDialog(self)
        help_dialog.exec()
    
    def populate_instruments(self):
        """填充乐器列表"""
        instruments = [
            "钢琴", "电钢琴", "风琴", "吉他", "贝斯", "小提琴", 
            "大提琴", "竖琴", "小号", "萨克斯", "长笛", "口琴"
        ]
        self.instrument_combo.addItems(instruments)
    
    def init_audio(self):
        """初始化音频系统（延迟初始化）"""
        try:
            import pygame
            import pygame.midi
            self.pygame = pygame
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            self.pygame_initialized = True
            self.status_bar.showMessage(f'{ProjectInfo.get_header()} | 音频系统初始化完成')
        except ImportError:
            self.status_bar.showMessage(f'{ProjectInfo.get_header()} | 警告: pygame未安装，播放功能不可用')
        except Exception as e:
            self.status_bar.showMessage(f'{ProjectInfo.get_header()} | 音频初始化失败: {str(e)}')
    
    def show_example(self):
        example = """# C大调音阶示例
1 2 3 4 5 6 7

# 带时值的音阶（括号内是时值）
1(1) 2(0.5) 3(0.5) | 4(2) 5(1) 6(0.5) 7(0.5) | 1'(2)

# 和弦示例（多个音符同时演奏）
1 3 5 | 4 6 1' | 5 7 2' | 1' 3' 5'

# 高低音示例
1. 2. 3. 4. | 1 2 3 4 | 1' 2' 3' 4'

# 小星星
1 1 5 5 | 6 6 5(2) | 4 4 3 3 | 2 2 1(2)
"""
        self.input_area.setPlainText(example)
    
    def parse_jianpu(self, text, key='C'):
        """解析简谱，生成MIDI消息列表和钢琴卷帘数据"""
        midi_messages = []
        self.notes_data = []
        current_time = 0.0  # 当前时间（以四分音符为单位）
        ticks_per_beat = 480  # MIDI ticks per quarter note
        
        # 音名到MIDI音符号的映射（C4 = 60）
        note_to_midi = {
            'C': 60, 'C#': 61, 'D': 62, 'D#': 63, 'E': 64, 'F': 65,
            'F#': 66, 'G': 67, 'G#': 68, 'A': 69, 'A#': 70, 'B': 71
        }
        
        # 根据调式调整基准音
        key_shift = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'].index(key)
        
        # 简谱数字到音名的映射（在C大调中）
        jianpu_to_note = {
            '1': 'C', '2': 'D', '3': 'E', '4': 'F', '5': 'G', '6': 'A', '7': 'B'
        }
        
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # 按小节分割
            bars = line.split('|')
            for bar in bars:
                bar = bar.strip()
                if not bar:
                    continue
                
                # 解析小节内的音符
                notes = bar.split()
                for note_str in notes:
                    note_str = note_str.strip()
                    if not note_str or note_str.startswith('#'):
                        continue
                    
                    # 解析时值
                    duration = 1.0  # 默认四分音符
                    if '(' in note_str and ')' in note_str:
                        match = re.search(r'\((.*?)\)', note_str)
                        if match:
                            try:
                                duration = float(match.group(1))
                            except:
                                duration = 1.0
                            note_str = re.sub(r'\(.*?\)', '', note_str)
                    
                    # 处理每个音符
                    notes_to_play = []
                    
                    # 检查是否是多个音符（空格分隔的和弦）
                    if ' ' in note_str and self.chord_check.isChecked():
                        notes_to_play = note_str.split()
                    else:
                        notes_to_play = [note_str]
                    
                    chord_notes = []
                    for single_note in notes_to_play:
                        # 确定八度
                        octave_shift = 0
                        base_note = single_note
                        
                        # 处理高音点
                        high_octave_count = single_note.count("'")
                        if high_octave_count > 0:
                            octave_shift = 12 * high_octave_count
                            base_note = base_note.replace("'", "")
                        
                        # 处理低音点
                        low_octave_count = single_note.count(".")
                        if low_octave_count > 0:
                            octave_shift = -12 * low_octave_count
                            base_note = base_note.replace(".", "")
                        
                        # 获取音名
                        if base_note in jianpu_to_note:
                            base_note_name = jianpu_to_note[base_note]
                            # 计算MIDI音符号
                            base_midi = note_to_midi.get(base_note_name, 60)
                            midi_note = base_midi + key_shift + octave_shift
                            
                            # 确保音符在有效范围内
                            midi_note = max(0, min(127, midi_note))
                            chord_notes.append(midi_note)
                    
                    if chord_notes:
                        # 计算时间（ticks）
                        start_tick = int(current_time * ticks_per_beat)
                        duration_ticks = int(duration * ticks_per_beat)
                        
                        # 为和弦中的每个音符添加消息
                        for midi_note in chord_notes:
                            # 添加音符开消息
                            midi_messages.append({
                                'type': 'note_on',
                                'note': midi_note,
                                'velocity': self.volume_slider.value(),
                                'time': start_tick
                            })
                            
                            # 添加音符关消息
                            midi_messages.append({
                                'type': 'note_off',
                                'note': midi_note,
                                'velocity': 0,
                                'time': start_tick + duration_ticks
                            })
                            
                            # 添加到钢琴卷帘数据
                            self.notes_data.append((
                                midi_note,
                                current_time,
                                duration,
                                self.volume_slider.value()
                            ))
                    
                    # 更新当前时间
                    current_time += duration
        
        # 按时间排序
        midi_messages.sort(key=lambda x: x['time'])
        
        # 更新钢琴卷帘
        self.piano_roll.set_notes(self.notes_data)
        
        return midi_messages
    
    def create_midi_file(self, messages, tempo=120):
        """创建MIDI文件"""
        mid = MidiFile(ticks_per_beat=480)
        track = MidiTrack()
        mid.tracks.append(track)
        
        # 设置速度（微秒每四分音符）
        tempo_value = mido.bpm2tempo(tempo)
        track.append(MetaMessage('set_tempo', tempo=tempo_value, time=0))
        
        # 设置音轨名称
        track.append(MetaMessage('track_name', name='Piano', time=0))
        
        # 设置乐器（根据选择）
        instrument_map = {
            "钢琴": 0, "电钢琴": 4, "风琴": 16, "吉他": 24, "贝斯": 32,
            "小提琴": 40, "大提琴": 42, "竖琴": 46, "小号": 56,
            "萨克斯": 65, "长笛": 73, "口琴": 22
        }
        program = instrument_map.get(self.instrument_combo.currentText(), 0)
        track.append(Message('program_change', program=program, time=0))
        
        # 添加音符消息
        prev_time = 0
        for msg in messages:
            delta = msg['time'] - prev_time
            if delta < 0:
                delta = 0
            
            if msg['type'] == 'note_on':
                track.append(Message('note_on', 
                                   note=msg['note'], 
                                   velocity=msg['velocity'], 
                                   time=delta))
            else:  # note_off
                track.append(Message('note_off', 
                                   note=msg['note'], 
                                   velocity=msg['velocity'], 
                                   time=delta))
            prev_time = msg['time']
        
        return mid
    
    def play_music(self):
        """播放音乐"""
        if not self.pygame_initialized:
            QMessageBox.warning(self, '警告', '音频系统未初始化，无法播放！')
            return
            
        text = self.input_area.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, '警告', '请输入简谱内容！')
            return
        
        try:
            # 解析简谱
            messages = self.parse_jianpu(text, self.key_combo.currentText())
            
            if not messages:
                QMessageBox.warning(self, '警告', '没有可播放的音符！')
                return
            
            # 创建MIDI文件
            mid = self.create_midi_file(messages, self.tempo_spin.value())
            
            # 保存到临时文件
            if self.current_midi_file and os.path.exists(self.current_midi_file):
                try:
                    os.unlink(self.current_midi_file)
                except:
                    pass
            
            temp_file = tempfile.NamedTemporaryFile(suffix='.mid', delete=False)
            temp_file.close()
            self.current_midi_file = temp_file.name
            mid.save(self.current_midi_file)
            
            # 播放MIDI文件
            self.pygame.mixer.music.load(self.current_midi_file)
            self.pygame.mixer.music.play()
            
            self.playback_active = True
            self.play_btn.setText('暂停')
            self.current_pos = 0
            self.playback_timer.start()
            self.status_bar.showMessage(f'{ProjectInfo.get_header()} | 正在播放...')
            
        except Exception as e:
            QMessageBox.critical(self, '错误', f'播放失败: {str(e)}')
            import traceback
            traceback.print_exc()
    
    def pause_music(self):
        """暂停音乐"""
        if self.pygame_initialized:
            self.pygame.mixer.music.pause()
            self.playback_active = False
            self.play_btn.setText('继续')
            self.playback_timer.stop()
            self.status_bar.showMessage(f'{ProjectInfo.get_header()} | 已暂停')
    
    def resume_music(self):
        """继续播放"""
        if self.pygame_initialized:
            self.pygame.mixer.music.unpause()
            self.playback_active = True
            self.play_btn.setText('暂停')
            self.playback_timer.start()
            self.status_bar.showMessage(f'{ProjectInfo.get_header()} | 继续播放...')
    
    def toggle_playback(self):
        """切换播放/暂停"""
        if not self.pygame_initialized:
            QMessageBox.warning(self, '警告', '音频系统未初始化，无法播放！')
            return
            
        if not self.current_midi_file:
            self.play_music()
        elif self.playback_active:
            self.pause_music()
        else:
            self.resume_music()
    
    def stop_music(self):
        """停止播放"""
        if self.pygame_initialized:
            self.pygame.mixer.music.stop()
        self.playback_active = False
        self.play_btn.setText('播放')
        self.playback_timer.stop()
        self.current_pos = 0
        self.piano_roll.set_current_pos(0)
        self.status_bar.showMessage(f'{ProjectInfo.get_header()} | 播放已停止')
        
        # 清理临时文件
        if self.current_midi_file and os.path.exists(self.current_midi_file):
            try:
                os.unlink(self.current_midi_file)
            except:
                pass
            self.current_midi_file = None
    
    def update_playback_position(self):
        """更新播放位置"""
        if self.pygame_initialized and self.pygame.mixer.music.get_busy():
            # 计算当前播放位置（秒）
            pos = self.pygame.mixer.music.get_pos() / 1000.0
            # 转换为节拍位置
            beats_per_second = self.tempo_spin.value() / 60.0
            self.current_pos = pos * beats_per_second
            self.piano_roll.set_current_pos(self.current_pos)
        else:
            # 播放结束
            if self.playback_active:
                self.stop_music()
    
    def save_midi(self):
        """保存MIDI文件"""
        text = self.input_area.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, '警告', '请输入简谱内容！')
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, '保存MIDI文件', '', 'MIDI文件 (*.mid)')
        
        if file_path:
            if not file_path.endswith('.mid'):
                file_path += '.mid'
            
            try:
                messages = self.parse_jianpu(text, self.key_combo.currentText())
                if not messages:
                    QMessageBox.warning(self, '警告', '没有可保存的音符！')
                    return
                    
                mid = self.create_midi_file(messages, self.tempo_spin.value())
                mid.save(file_path)
                self.status_bar.showMessage(f'{ProjectInfo.get_header()} | 已保存到: {file_path}')
                QMessageBox.information(self, '成功', 'MIDI文件保存成功！')
            except Exception as e:
                QMessageBox.critical(self, '错误', f'保存失败: {str(e)}')
    
    def clear_input(self):
        """清空输入"""
        self.input_area.clear()
        self.stop_music()
        self.notes_data = []
        self.piano_roll.set_notes([])
        self.piano_roll.set_current_pos(0)
        self.status_bar.showMessage(f'{ProjectInfo.get_header()} | 输入已清除')
    
    def closeEvent(self, event):
        """关闭窗口"""
        self.stop_music()
        if self.pygame_initialized:
            self.pygame.mixer.quit()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # 创建主窗口（不立即显示）
    converter = MusicConverter()
    
    sys.exit(app.exec())