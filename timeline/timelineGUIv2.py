"""
timelineGUI.py

基于 PyQt5 构建明日方舟动作时间轴与覆盖率计算工具

【左侧时间轴区域】
- 背景网格每100帧一条竖线，刻度文字放在总覆盖轴上方
- 鼠标移动时更新红色指示线；异常时重新创建
- 根据各动作状态（含自动追加的延迟状态）周期性重复绘制至时间轴末尾
- 左上方提供“时间轴长度(帧)”设置（默认1800帧）和缩放滑块（仅缩放图形部分，文字固定）
- 总覆盖轴放在最上方，刻度文字位于其上，背景填充色取反（暗→白，亮→黑），高度为单行高度的一半，
  各动作名称文字与其对应的时间轴贴紧

【右侧参数设置面板】
- 面板最低宽度700px、最低高度200px（窗口最小高度300），滚动区域使用默认横向滚动条样式
- 每个动作条目包含动作名称、起始帧、删除按钮；每个动作下有多个状态条目，
  每个状态包含状态名称、持续帧、颜色选择、“有效”复选框、“等待帧”（若大于0自动追加延迟状态）、删除按钮
- 面板底部除已有按钮外，在最下面右侧新增三个按钮（切换模式、问号、说明），与覆盖率标签同行，行高固定40px

【计算覆盖率及优化】
- “计算覆盖率”按钮遍历所有有效状态联合区间，并在±50帧范围内调整各动作起始帧，
  给出建议调整量（以帧和秒显示），更新界面

【配置导入/导出】
- 导出配置为 JSON 文件（文件名形如“轴-YYYYMMDDhhmmss.json”）到程序目录；支持导入配置

-----------------------------------------------------------
通用工具函数：
"""


def seconds_to_frames(seconds):
    """将秒转换为帧（1秒 = 30帧）"""
    return int(seconds * 30)


def frames_to_seconds(frames):
    """将帧数转换为秒（1秒 = 30帧）"""
    return frames / 30.0


def merge_intervals(intervals):
    """
    合并重叠的时间区间。

    参数:
      intervals: 列表 [(start, end), ...]
    返回:
      合并后的区间列表
    """
    if not intervals:
        return []
    intervals = sorted(intervals, key=lambda x: x[0])
    merged = [intervals[0]]
    for current in intervals[1:]:
        prev = merged[-1]
        if current[0] <= prev[1]:
            merged[-1] = (prev[0], max(prev[1], current[1]))
        else:
            merged.append(current)
    return merged


# --------------------
# 主题定义（Dracula风格暗色与自定义淡紫色浅色）
# --------------------
DARK_THEME = {
    "background": "#1E1E2E",
    "panel": "#2E2E3E",
    "grid": "#3E3E4E",
    "text": "#D8DEE9",
    "highlight": "#BD93F9",
    "button": "#44475A",
    "button_hover": "#6272A4",
    "timeline_grid": "#5E5E6E",
}

LIGHT_THEME = {
    "background": "#DAD2FF",  # 最淡紫色背景
    "panel": "#DAD2FF",
    "grid": "#AAAAAA",
    "text": "#000000",  # 较深紫色文字
    "highlight": "#FFF2AF",  # 淡黄色高亮
    "button": "#B2A5FF",  # 淡紫色按钮
    "button_hover": "#493D9E",
    "timeline_grid": "#AAAAAA",
}

# --------------------
# 左侧时间轴显示区域
# --------------------
from PyQt5.QtWidgets import QGraphicsTextItem, QGraphicsItem
from PyQt5.QtGui import QPen, QBrush, QColor, QTransform, QIcon, QPixmap
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QGraphicsView,
    QGraphicsScene,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QSpinBox,
    QCheckBox,
    QScrollArea,
    QMessageBox,
    QComboBox,
    QSlider,
    QFileDialog,
    QSizePolicy,
)
import sys, json, os, datetime, random


class TimelineView(QGraphicsView):
    def __init__(self, scene, parent=None):
        super(TimelineView, self).__init__(scene, parent)
        self.scene = scene
        self.setMouseTracking(True)
        self.mouse_line = None

    def mouseMoveEvent(self, event):
        pos = self.mapToScene(event.pos())
        x = pos.x()
        try:
            if self.mouse_line is None or self.mouse_line.scene() is None:
                pen = QPen(QColor("#FF5555"), 2, Qt.SolidLine)
                self.mouse_line = self.scene.addLine(
                    x, 0, x, self.scene.sceneRect().height(), pen
                )
            else:
                self.mouse_line.setLine(x, 0, x, self.scene.sceneRect().height())
        except RuntimeError:
            pen = QPen(QColor("#FF5555"), 2, Qt.SolidLine)
            self.mouse_line = self.scene.addLine(
                x, 0, x, self.scene.sceneRect().height(), pen
            )
        super(TimelineView, self).mouseMoveEvent(event)


# --------------------
# 右侧状态条目控件
# --------------------
class StateWidget(QWidget):
    def __init__(
        self,
        parent_action,
        state_index,
        default_name="状态",
        default_duration=30,
        default_color="red",
    ):
        super().__init__()
        self.parent_action = parent_action
        self.state_index = state_index
        layout = QHBoxLayout()
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(5)

        self.name_edit = QLineEdit(f"{default_name}{state_index+1}")
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(1, 10000)
        self.duration_spin.setValue(default_duration)

        self.color_combo = QComboBox()
        self.color_combo.setEditable(True)
        self.color_combo.addItems(
            ["red", "transparent", "blue", "green", "yellow", "black"]
        )
        self.color_combo.setCurrentText(default_color)

        self.valid_checkbox = QCheckBox("有效")
        self.valid_checkbox.setChecked(True)

        # “等待帧”
        self.wait_spin = QSpinBox()
        self.wait_spin.setRange(0, 10000)
        self.wait_spin.setValue(0)

        self.delete_button = QPushButton("删除")
        self.delete_button.setFixedWidth(60)
        self.delete_button.clicked.connect(self.on_delete)

        layout.addWidget(QLabel("状态名:"))
        layout.addWidget(self.name_edit)
        layout.addWidget(QLabel("持续帧:"))
        layout.addWidget(self.duration_spin)
        layout.addWidget(QLabel("颜色:"))
        layout.addWidget(self.color_combo)
        layout.addWidget(self.valid_checkbox)
        layout.addWidget(QLabel("等待帧:"))
        layout.addWidget(self.wait_spin)
        layout.addWidget(self.delete_button)

        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

    def on_delete(self):
        self.parent_action.remove_state(self)


# --------------------
# 右侧动作条目控件（每个动作包含多个状态）
# --------------------
class OperatorActionWidget(QWidget):
    def __init__(self, parent_main, default_name="动作", default_start=0):
        super().__init__()
        self.parent_main = parent_main
        self.state_widgets = []

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        # 动作头部信息
        header_layout = QHBoxLayout()
        self.name_edit = QLineEdit(default_name)
        self.start_spin = QSpinBox()
        self.start_spin.setRange(0, 10000)
        self.start_spin.setValue(default_start)
        self.delete_button = QPushButton("删除动作")
        self.delete_button.setFixedWidth(80)
        self.delete_button.clicked.connect(self.on_delete)

        header_layout.addWidget(QLabel("动作名:"))
        header_layout.addWidget(self.name_edit)
        header_layout.addWidget(QLabel("起始帧:"))
        header_layout.addWidget(self.start_spin)
        header_layout.addWidget(self.delete_button)
        main_layout.addLayout(header_layout)

        # 状态列表（紧凑排列）
        self.states_layout = QVBoxLayout()
        self.states_layout.setContentsMargins(0, 0, 0, 0)
        self.states_layout.setSpacing(2)
        main_layout.addLayout(self.states_layout)

        # “添加状态”按钮
        self.add_state_button = QPushButton("添加状态")
        self.add_state_button.clicked.connect(self.add_state)
        main_layout.addWidget(self.add_state_button)

        self.setLayout(main_layout)
        # 默认添加两个状态：第1个有效 red；第2个无效 transparent
        self.add_state(default_duration=30, default_color="red")
        self.add_state(
            default_duration=20, default_color="transparent", default_valid=False
        )

        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

    def add_state(self, default_duration=30, default_color="red", default_valid=True):
        state_index = len(self.state_widgets)
        state_widget = StateWidget(
            self,
            state_index,
            default_name="状态",
            default_duration=default_duration,
            default_color=default_color,
        )
        state_widget.valid_checkbox.setChecked(default_valid)
        self.state_widgets.append(state_widget)
        self.states_layout.addWidget(state_widget)
        self.parent_main.update_timeline()

    def remove_state(self, state_widget):
        if len(self.state_widgets) <= 1:
            QMessageBox.warning(self, "提示", "至少需要一个状态")
            return
        self.state_widgets.remove(state_widget)
        self.states_layout.removeWidget(state_widget)
        state_widget.deleteLater()
        for idx, sw in enumerate(self.state_widgets):
            sw.state_index = idx
        self.parent_main.update_timeline()

    def on_delete(self):
        self.parent_main.remove_operator_action(self)

    def get_data(self):
        data = {}
        data["name"] = self.name_edit.text()
        data["start"] = self.start_spin.value()
        data["states"] = []
        total_duration = 0
        for sw in self.state_widgets:
            state_data = {
                "name": sw.name_edit.text(),
                "duration": sw.duration_spin.value(),
                "color": sw.color_combo.currentText().strip().lower(),
                "valid": sw.valid_checkbox.isChecked(),
                "delay": sw.wait_spin.value(),
            }
            total_duration += state_data["duration"]
            if state_data["delay"] > 0:
                total_duration += state_data["delay"]
            data["states"].append(state_data)
        data["cycle"] = total_duration
        return data


# --------------------
# 主窗口
# --------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.dark_mode = True  # 默认暗色模式
        self.set_theme()
        self.setWindowIcon(QIcon("icon.svg"))
        self.setWindowTitle(
            "ActionTimeLine - 明日方舟动作时间轴与覆盖率计算工具 --by Cyletix"
        )
        self.resize(1200, 300)
        self.setMinimumHeight(300)
        self.timeline_length = 1800  # 默认1800帧
        self.zoom_factor = 1.0

        main_widget = QWidget()
        main_layout = QHBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # 左侧：上部控制（缩放、时间轴长度）+ 时间轴显示区域
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)
        main_layout.addWidget(left_panel, stretch=3)

        top_control_layout = QHBoxLayout()
        zoom_label = QLabel("缩放:")
        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setMinimum(50)
        self.zoom_slider.setMaximum(200)
        self.zoom_slider.setValue(100)
        self.zoom_slider.valueChanged.connect(self.on_zoom_change)
        top_control_layout.addWidget(zoom_label)
        top_control_layout.addWidget(self.zoom_slider)

        length_label = QLabel("时间轴长度(帧):")
        self.length_spin = QSpinBox()
        self.length_spin.setRange(100, 10000)
        self.length_spin.setValue(self.timeline_length)
        self.length_spin.valueChanged.connect(self.on_length_change)
        top_control_layout.addWidget(length_label)
        top_control_layout.addWidget(self.length_spin)

        left_layout.addLayout(top_control_layout)

        self.scene = QGraphicsScene()
        self.timeline_view = TimelineView(self.scene)
        left_layout.addWidget(self.timeline_view)

        # 右侧：参数设置面板
        self.right_panel = QWidget()
        self.right_panel.setMinimumWidth(700)
        self.right_panel.setMinimumHeight(200)
        self.right_panel.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        right_layout = QVBoxLayout()
        right_layout.setSpacing(5)
        self.right_panel.setLayout(right_layout)
        main_layout.addWidget(self.right_panel, stretch=0)

        # 滚动区域（紧凑排列动作条目），恢复默认滚动条样式（允许横向滚动）
        self.action_scroll = QScrollArea()
        self.action_scroll.setWidgetResizable(True)
        self.action_container = QWidget()
        self.action_layout = QVBoxLayout()
        self.action_layout.setContentsMargins(5, 5, 5, 5)
        self.action_layout.setSpacing(5)
        self.action_container.setLayout(self.action_layout)
        self.action_scroll.setWidget(self.action_container)
        right_layout.addWidget(self.action_scroll)

        # 底部控制按钮（上排：添加、更新、计算、导入、导出）
        btn_layout = QHBoxLayout()
        self.add_action_button = QPushButton("添加动作")
        self.add_action_button.clicked.connect(self.add_operator_action)
        self.update_button = QPushButton("更新显示")
        self.update_button.clicked.connect(self.update_timeline)
        self.calc_button = QPushButton("计算覆盖率")
        self.calc_button.clicked.connect(self.calculate_coverage)
        self.export_button = QPushButton("导出配置")
        self.export_button.clicked.connect(self.export_config)
        self.import_button = QPushButton("导入配置")
        self.import_button.clicked.connect(self.import_config)
        btn_layout.addWidget(self.add_action_button)
        btn_layout.addWidget(self.update_button)
        btn_layout.addWidget(self.calc_button)
        btn_layout.addWidget(self.export_button)
        btn_layout.addWidget(self.import_button)
        right_layout.addLayout(btn_layout)

        # 最下面右侧一行：覆盖率标签与三个新按钮（右对齐），固定高度40
        bottom_layout = QHBoxLayout()
        self.coverage_label = QLabel("覆盖率: N/A")
        bottom_layout.addWidget(self.coverage_label)
        bottom_layout.addStretch()
        # 在覆盖率标签右侧新增提示标签，用于显示“未抽到”
        self.surprise_msg_label = QLabel("")
        self.surprise_msg_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        bottom_layout.addWidget(self.surprise_msg_label)
        # 切换模式按钮（使用 emoji 图标）
        self.toggle_button = QPushButton("🌙")  # 暗色模式下显示月亮
        self.toggle_button.clicked.connect(self.toggle_theme)
        self.toggle_button.setFixedSize(40, 40)
        self.toggle_button.setStyleSheet(
            """
            QPushButton {
                border-radius: 20px;
                font-size: 18px;
            }
        """
        )
        bottom_layout.addWidget(self.toggle_button)
        # 问号按钮：点击后2%随机弹出图库中一张图片，并在弹窗中显示图片；否则更新提示标签
        self.surprise_button = QPushButton("?")
        self.surprise_button.setToolTip("点我抽卡")
        self.surprise_button.setFixedSize(40, 40)
        self.surprise_button.setStyleSheet(
            """
            QPushButton {
                border-radius: 20px;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #FFF2AF;
            }
        """
        )
        self.surprise_button.clicked.connect(self.handle_surprise)
        bottom_layout.addWidget(self.surprise_button)
        # 说明按钮
        self.info_button = QPushButton("说明")
        self.info_button.setFixedSize(60, 40)
        self.info_button.setStyleSheet(
            """
            QPushButton {
                border-radius: 8px;
                font-size: 14px;
            }
        """
        )
        self.info_button.clicked.connect(self.show_info)
        bottom_layout.addWidget(self.info_button)
        right_layout.addLayout(bottom_layout)

        self.operator_actions = []
        self.add_operator_action()  # 默认添加一条动作
        self.update_timeline()

    def set_theme(self):
        """应用当前模式的主题"""
        self.theme = DARK_THEME if self.dark_mode else LIGHT_THEME
        self.setStyleSheet(
            f"""
            QMainWindow {{
                background-color: {self.theme['background']};
                color: {self.theme['text']};
            }}
            QWidget {{
                background-color: {self.theme['panel']};
                color: {self.theme['text']};
            }}
            QLabel {{
                color: {self.theme['text']};
                font-size: 14px;
            }}
            QPushButton {{
                background-color: {self.theme['button']};
                color: {self.theme['text']};
                border-radius: 8px;
                padding: 5px;
            }}
            QPushButton:hover {{
                background-color: {self.theme['button_hover']};
            }}
            QSpinBox, QLineEdit, QComboBox, QCheckBox {{
                background-color: {self.theme['background']};
                color: {self.theme['text']};
            }}
        """
        )

    def toggle_theme(self):
        """切换深/浅色模式"""
        self.dark_mode = not self.dark_mode
        self.toggle_button.setText("🌙" if self.dark_mode else "☀️")
        self.set_theme()
        self.update_timeline()

    def show_info(self):
        """显示说明弹窗"""
        info_text = (
            "这是明日方舟动作时间轴与覆盖率计算工具。\n\n"
            "左侧查看状态循环时间轴覆盖情况；\n"
            "右侧添加和设置动作及状态。\n"
            "动作名:干员平a, 干员1技能, 快活/召唤物阻挡等等\n"
            "状态:技能开启/持续/结束状态，也可以填写攻击间隔,等待状态, 快活死亡状态等\n"
            "颜色支持色号, 格式: #123456\n"
            '点击"计算覆盖率"，程序会自动优化各动作起始帧以提高整体覆盖率。\n\n'
            "作者：Cyletix"
        )
        QMessageBox.information(self, "工具说明", info_text)

    def handle_surprise(self):
        """问号按钮：2%概率随机弹出图库中一张图片，并在弹窗中显示图片；否则在底部提示“未抽到惊喜”"""
        import random

        if random.random() < 0.05:
            img_dir = os.path.join(os.getcwd(), "img")
            if os.path.exists(img_dir):
                imgs = [
                    f
                    for f in os.listdir(img_dir)
                    if f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif"))
                ]
                if imgs:
                    img_file = random.choice(imgs)
                    img_path = os.path.join(img_dir, img_file)
                    pixmap = QPixmap(img_path)
                    if not pixmap.isNull():
                        # 解析文件名格式，例如 "4_豆苗.jpg"
                        base = os.path.splitext(img_file)[0]
                        parts = base.split("_")
                        if len(parts) >= 2:
                            star = parts[0]
                            name = parts[1]
                        else:
                            star = ""
                            name = base
                        self.surprise_msg_label.setText(f"你抽到了{star}星干员{name}!")
                        msg_box = QMessageBox(self)
                        msg_box.setWindowTitle(f"你抽到了{star}星干员{name}!")
                        msg_box.setIconPixmap(
                            pixmap.scaled(
                                400, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation
                            )
                        )
                        msg_box.setStandardButtons(QMessageBox.Ok)
                        msg_box.exec_()
                        self.surprise_msg_label.setText("")
                    else:
                        self.surprise_msg_label.setText("图片加载失败")
                        QTimer.singleShot(
                            3000, lambda: self.surprise_msg_label.setText("")
                        )
                else:
                    self.surprise_msg_label.setText("图库中无图片")
                    QTimer.singleShot(3000, lambda: self.surprise_msg_label.setText(""))
            else:
                self.surprise_msg_label.setText("未找到图库文件夹")
                QTimer.singleShot(3000, lambda: self.surprise_msg_label.setText(""))
        else:
            self.surprise_msg_label.setText("什么也没抽到, 请再试一次")
            from PyQt5.QtCore import QTimer

            QTimer.singleShot(3000, lambda: self.surprise_msg_label.setText(""))

    def on_zoom_change(self, value):
        self.zoom_factor = value / 100.0
        t = QTransform()
        t.scale(self.zoom_factor, 1)
        self.timeline_view.setTransform(t)
        self.update_timeline()

    def on_length_change(self, value):
        self.timeline_length = value
        self.update_timeline()

    def add_operator_action(self):
        action_widget = OperatorActionWidget(self)
        self.operator_actions.append(action_widget)
        self.action_layout.addWidget(action_widget)
        self.update_timeline()

    def remove_operator_action(self, action_widget):
        if action_widget in self.operator_actions:
            self.operator_actions.remove(action_widget)
            self.action_layout.removeWidget(action_widget)
            action_widget.deleteLater()
            self.update_timeline()

    def build_extended_states(self, data):
        """
        对于每个动作，构建扩展状态列表：
        对每个状态，如果 delay > 0，则在后追加一个延迟状态（名称"延迟开启", 颜色 transparent, 无效）
        返回扩展列表及总周期
        """
        ext_states = []
        for state in data["states"]:
            ext_states.append(
                {
                    "name": state["name"],
                    "duration": state["duration"],
                    "color": state["color"],
                    "valid": state["valid"],
                }
            )
            if state["delay"] > 0:
                ext_states.append(
                    {
                        "name": "延迟开启",
                        "duration": state["delay"],
                        "color": "transparent",
                        "valid": False,
                    }
                )
        total = sum(s["duration"] for s in ext_states)
        return ext_states, total

    def update_timeline(self):
        self.scene.clear()
        self.timeline_view.mouse_line = None

        # 布局参数（保持用户设定）
        row_height = 30
        margin = 20
        top_margin = 25
        union_area_height = row_height // 2
        num_actions = len(self.operator_actions)
        scene_height = (
            top_margin + union_area_height + num_actions * (row_height + margin)
        )
        self.scene.setSceneRect(0, 0, self.timeline_length, scene_height)

        # 绘制背景网格和刻度：刻度文字放在总覆盖轴上方（y = top_margin - 20）
        pen = QPen(QColor(self.theme["timeline_grid"]))
        for x in range(0, self.timeline_length + 1, 100):
            self.scene.addLine(x, top_margin + union_area_height, x, scene_height, pen)
            txt = QGraphicsTextItem(f"{x}帧")
            txt.setDefaultTextColor(QColor(self.theme["text"]))
            txt.setPos(x, top_margin - 20)
            txt.setFlag(QGraphicsItem.ItemIgnoresTransformations, True)
            txt.setZValue(10)
            self.scene.addItem(txt)

        union_intervals = []
        # 绘制各动作时间轴（从总覆盖轴下方开始）
        for idx, op_widget in enumerate(self.operator_actions):
            data = op_widget.get_data()
            y = top_margin + union_area_height + margin + idx * (row_height + margin)
            # 将动作名称放置于时间轴内，紧贴顶部
            txt = QGraphicsTextItem(data["name"])
            txt.setDefaultTextColor(QColor(self.theme["text"]))
            txt.setPos(0, y)
            txt.setFlag(QGraphicsItem.ItemIgnoresTransformations, True)
            txt.setZValue(10)
            self.scene.addItem(txt)
            start = data["start"]
            ext_states, cycle = self.build_extended_states(data)
            if cycle <= 0:
                continue
            max_cycle_index = int((self.timeline_length - start) / cycle) + 1
            for i in range(max_cycle_index):
                base = start + i * cycle
                cum = 0
                for state in ext_states:
                    s_start = base + cum
                    s_end = s_start + state["duration"]
                    if s_start >= self.timeline_length:
                        break
                    if s_end > self.timeline_length:
                        s_end = self.timeline_length
                    rect = QRectF(s_start, y, s_end - s_start, row_height)
                    try:
                        color = QColor(state["color"])
                        if not color.isValid():
                            color = QColor("transparent")
                    except Exception:
                        color = QColor("transparent")
                    if not state["valid"]:
                        color.setAlpha(100)
                    brush = QBrush(color)
                    pen_rect = QPen(QColor(self.theme["grid"]))
                    self.scene.addRect(rect, pen_rect, brush)
                    if state["valid"]:
                        union_intervals.append((s_start, s_end))
                    cum += state["duration"]

        # 绘制总覆盖轴：放在 top_margin 处，高度为 union_area_height，
        # 不绘制边框，只填充背景色：暗模式下用白色，亮模式下用黑色
        cover_color = QColor(255, 255, 255) if self.dark_mode else QColor(0, 0, 0)
        merged = merge_intervals(union_intervals)
        for u_start, u_end in merged:
            rect = QRectF(u_start, top_margin, u_end - u_start, union_area_height)
            self.scene.addRect(rect, QPen(Qt.NoPen), QBrush(cover_color))

    def compute_union_coverage(self):
        union_intervals = []
        for op_widget in self.operator_actions:
            data = op_widget.get_data()
            start = data["start"]
            ext_states, cycle = self.build_extended_states(data)
            if cycle <= 0:
                continue
            max_cycle_index = int((self.timeline_length - start) / cycle) + 1
            for i in range(max_cycle_index):
                base = start + i * cycle
                cum = 0
                for state in ext_states:
                    s_start = base + cum
                    s_end = s_start + state["duration"]
                    if s_start >= self.timeline_length:
                        break
                    if s_end > self.timeline_length:
                        s_end = self.timeline_length
                    if state["valid"]:
                        union_intervals.append((s_start, s_end))
                    cum += state["duration"]
        merged = merge_intervals(union_intervals)
        total = sum(e - s for s, e in merged)
        return total

    def optimize_timeline(self):
        shifts = [0] * len(self.operator_actions)
        best_total = self.compute_union_coverage()
        for i, action in enumerate(self.operator_actions):
            orig = action.start_spin.value()
            best_for_action = orig
            for shift in range(-50, 51):
                candidate = max(0, orig + shift)
                action.start_spin.setValue(candidate)
                self.update_timeline()
                cand_total = self.compute_union_coverage()
                if cand_total > best_total:
                    best_total = cand_total
                    best_for_action = candidate
            action.start_spin.setValue(best_for_action)
            shifts[i] = best_for_action - orig
        self.update_timeline()
        return shifts, best_total

    def calculate_coverage(self):
        try:
            shifts, total_cov = self.optimize_timeline()
            coverage_ratio = (
                total_cov / self.timeline_length if self.timeline_length > 0 else 0
            )
            shift_info = "\n".join(
                f"动作 {i+1}: 调整 {s} 帧 ({s/30:.2f} 秒)"
                for i, s in enumerate(shifts)
                if s != 0
            )
            msg = f"优化后覆盖率: {coverage_ratio:.2f}\n{shift_info if shift_info else '无调整'}"
            self.coverage_label.setText(f"覆盖率: {coverage_ratio:.2f}")
            QMessageBox.information(self, "覆盖率计算结果", msg)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"计算覆盖率时出错: {e}")

    def export_config(self):
        config = {"timeline_length": self.timeline_length, "actions": []}
        for op_widget in self.operator_actions:
            config["actions"].append(op_widget.get_data())
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"轴-{timestamp}.json"
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
            QMessageBox.information(
                self, "导出配置", f"配置已导出到 {os.path.abspath(filename)}"
            )
        except Exception as e:
            QMessageBox.critical(self, "导出错误", str(e))

    def import_config(self):
        fname, _ = QFileDialog.getOpenFileName(
            self, "选择配置文件", os.getcwd(), "JSON Files (*.json)"
        )
        if not fname:
            return
        try:
            with open(fname, "r", encoding="utf-8") as f:
                config = json.load(f)
            if "timeline_length" in config:
                self.timeline_length = config["timeline_length"]
                self.length_spin.setValue(self.timeline_length)
            for op in self.operator_actions:
                op.deleteLater()
            self.operator_actions = []
            while self.action_layout.count():
                item = self.action_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            for action_data in config.get("actions", []):
                op_widget = OperatorActionWidget(self)
                op_widget.name_edit.setText(action_data.get("name", "新动作"))
                op_widget.start_spin.setValue(action_data.get("start", 0))
                for sw in op_widget.state_widgets:
                    sw.deleteLater()
                op_widget.state_widgets = []
                while op_widget.states_layout.count():
                    item = op_widget.states_layout.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
                for state in action_data.get("states", []):
                    op_widget.add_state(
                        default_duration=state.get("duration", 30),
                        default_color=state.get("color", "red"),
                        default_valid=state.get("valid", True),
                    )
                    op_widget.state_widgets[-1].wait_spin.setValue(
                        state.get("delay", 0)
                    )
                self.operator_actions.append(op_widget)
                self.action_layout.addWidget(op_widget)
            self.update_timeline()
            QMessageBox.information(self, "导入配置", "配置导入成功！")
        except Exception as e:
            QMessageBox.critical(self, "导入错误", str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
