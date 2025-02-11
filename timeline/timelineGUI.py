"""
timelineGUI.py

基于 PyQt5 构建明日方舟动作时间轴与覆盖率计算工具

【左侧时间轴区域】
- 显示背景网格（每100帧一条竖线及刻度），文本忽略缩放（ItemIgnoresTransformations）
- 鼠标移动时更新一条红色竖线指示当前位置；若更新过程中发现对象已被删除，则重新创建，避免因滚轮操作而崩溃
- 根据各动作设置的状态（含自动追加的延迟状态）周期性重复绘制至时间轴末尾
- 左上方提供“时间轴长度(帧)”设置（默认1800帧），以及缩放滑块（仅缩放图形部分，文字固定大小）
- 最上方显示所有动作中【有效】状态的并集区域

【右侧参数设置面板】
- 取消固定宽度，设置最低宽度（500像素），以保证内容全部显示而不出现横向滚动条
- 每个动作条目（OperatorActionWidget）包含动作名称、起始帧、删除按钮
- 每个动作下有多个状态条目（StateWidget），每个状态条目包含：
    - 状态名称、持续帧、颜色选择（下拉预置 red、transparent、blue、green、yellow、black，同时可自定义）
    - “有效”复选框（仅选中状态参与覆盖率计算）
    - “等待帧”（单位帧，默认0；若大于0，则在该状态后自动追加一个名称“延迟开启”、颜色透明、无效的延迟状态）
    - 删除状态按钮
- 面板底部提供“添加动作”、“更新显示”、“计算覆盖率”、“导出配置”、“导入配置”按钮

【计算覆盖率及优化】
- “计算覆盖率”按钮根据当前设置计算各有效状态（原状态，不包含自动生成的延迟状态）的联合区间，并在±50帧范围内对各动作起始帧进行简单优化（仅调整起始帧），给出建议调整量（同时以秒显示），并更新界面

【配置导入/导出】
- “导出配置”将当前参数保存为 JSON 文件（文件名形如“轴-YYYYMMDDhhmmss.json”）到程序目录
- “导入配置”可从 JSON 文件中加载设置到参数面板

注意：本版本在 update_timeline() 中清空场景后，会将保存的鼠标指示线置为 None，以避免后续 mouseMoveEvent 更新时访问已删除对象。
"""

import sys, json, os, datetime
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
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPen, QBrush, QColor, QTransform
from PyQt5.QtWidgets import QGraphicsTextItem, QGraphicsItem

import timeline  # 导入通用函数

# --- 左侧时间轴显示区域 ---


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
                pen = QPen(Qt.red, 2, Qt.SolidLine)
                self.mouse_line = self.scene.addLine(
                    x, 0, x, self.scene.sceneRect().height(), pen
                )
            else:
                self.mouse_line.setLine(x, 0, x, self.scene.sceneRect().height())
        except RuntimeError:
            # 出现异常则重新创建
            pen = QPen(Qt.red, 2, Qt.SolidLine)
            self.mouse_line = self.scene.addLine(
                x, 0, x, self.scene.sceneRect().height(), pen
            )
        super(TimelineView, self).mouseMoveEvent(event)


# --- 右侧“状态”条目控件 ---


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

        # 将“等待时间”改为“等待帧”
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


# --- 右侧“动作”控件，每个动作包含若干状态 ---


class OperatorActionWidget(QWidget):
    def __init__(self, parent_main, default_name="新动作", default_start=0):
        super().__init__()
        self.parent_main = parent_main  # 用于通知主窗口更新或删除动作
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
        """
        返回字典数据：
          {
             "name": 动作名称,
             "start": 起始帧,
             "states": [ { "name": 状态名称, "duration": 持续帧, "color": 颜色,
                           "valid": 是否有效, "delay": 等待帧 }, ... ],
             "cycle": 整个动作周期（扩展状态累计时长，包括每个状态后自动追加的延迟状态）
          }
        """
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


# --- 主窗口 ---


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("明日方舟动作时间轴与覆盖率计算工具")
        self.resize(1200, 600)
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
        # 取消固定宽度，设置最低宽度
        self.right_panel.setMinimumWidth(500)
        self.right_panel.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        right_layout = QVBoxLayout()
        right_layout.setSpacing(5)
        self.right_panel.setLayout(right_layout)
        main_layout.addWidget(self.right_panel, stretch=0)

        # 滚动区域（紧凑排列动作条目），禁用横向滚动条
        self.action_scroll = QScrollArea()
        self.action_scroll.setWidgetResizable(True)
        self.action_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.action_container = QWidget()
        self.action_layout = QVBoxLayout()
        self.action_layout.setContentsMargins(5, 5, 5, 5)
        self.action_layout.setSpacing(5)
        self.action_container.setLayout(self.action_layout)
        self.action_scroll.setWidget(self.action_container)
        right_layout.addWidget(self.action_scroll)

        # 底部控制按钮
        btn_layout = QHBoxLayout()
        self.add_action_button = QPushButton("添加动作")
        self.add_action_button.clicked.connect(self.add_operator_action)
        self.update_button = QPushButton("更新显示")
        self.update_button.clicked.connect(self.update_timeline)
        self.calc_button = QPushButton("计算覆盖率")
        self.calc_button.clicked.connect(self.calculate_coverage)
        btn_layout.addWidget(self.add_action_button)
        btn_layout.addWidget(self.update_button)
        btn_layout.addWidget(self.calc_button)
        right_layout.addLayout(btn_layout)

        # 导入/导出按钮
        io_layout = QHBoxLayout()
        self.export_button = QPushButton("导出配置")
        self.export_button.clicked.connect(self.export_config)
        self.import_button = QPushButton("导入配置")
        self.import_button.clicked.connect(self.import_config)
        io_layout.addWidget(self.export_button)
        io_layout.addWidget(self.import_button)
        right_layout.addLayout(io_layout)

        self.coverage_label = QLabel("覆盖率: N/A")
        right_layout.addWidget(self.coverage_label)

        self.operator_actions = []  # 存放所有动作条目
        self.add_operator_action()  # 默认添加一条动作
        self.update_timeline()

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
        对每个状态，如果 delay > 0，则在后追加一个延迟状态（名称"延迟开启", 颜色transparent, 无效）
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
        # 清空后置鼠标指示线置为 None，避免后续引用已删除对象
        self.timeline_view.mouse_line = None

        row_height = 30
        margin = 10
        union_area_height = 20  # 最上方显示有效区域
        num_actions = len(self.operator_actions)
        scene_height = union_area_height + 50 + num_actions * (row_height + margin)
        self.scene.setSceneRect(0, 0, self.timeline_length, scene_height)

        # 绘制背景网格（每100帧一条竖线及刻度），文本忽略缩放
        pen = QPen(Qt.gray)
        for x in range(0, self.timeline_length + 1, 100):
            self.scene.addLine(x, 0, x, scene_height, pen)
            txt = QGraphicsTextItem(f"{x}帧")
            txt.setDefaultTextColor(Qt.black)
            txt.setPos(x, 0)
            txt.setFlag(QGraphicsItem.ItemIgnoresTransformations, True)
            self.scene.addItem(txt)

        union_intervals = []
        for idx, op_widget in enumerate(self.operator_actions):
            data = op_widget.get_data()
            y = union_area_height + 50 + idx * (row_height + margin)
            txt = QGraphicsTextItem(data["name"])
            txt.setDefaultTextColor(Qt.black)
            txt.setPos(0, y - 20)
            txt.setFlag(QGraphicsItem.ItemIgnoresTransformations, True)
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
                    pen_rect = QPen(Qt.black)
                    self.scene.addRect(rect, pen_rect, brush)
                    if state["valid"]:
                        union_intervals.append((s_start, s_end))
                    cum += state["duration"]
        merged = timeline.merge_intervals(union_intervals)
        for u_start, u_end in merged:
            rect = QRectF(u_start, 0, u_end - u_start, union_area_height)
            brush = QBrush(QColor("red"))
            pen_rect = QPen(QColor("red"))
            self.scene.addRect(rect, pen_rect, brush)

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
        merged = timeline.merge_intervals(union_intervals)
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
