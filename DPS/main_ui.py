# main_ui.py
import sys
import json
import re
import os
from datetime import datetime
from urllib.parse import unquote
import requests
from bs4 import BeautifulSoup

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QScrollArea,
    QTextEdit,
    QSpinBox,
    QLineEdit,
    QCheckBox,
    QFileDialog,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
    QComboBox,
    QGridLayout,
    QSizePolicy,
    QGroupBox,
    QInputDialog,
    QMessageBox,
)
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QEvent, QTimer

from data_loader import DataLoader, DraggableTextEdit
from dps_calculator import DPSCalculator
from ui_styles import DARK_THEME, LIGHT_THEME, get_stylesheet
from ui_components import UIComponents
from PyQt5.QtGui import QIcon


def resource_path(relative_path):
    """ 获取资源的绝对路径，无论是开发环境还是PyInstaller打包后 """
    try:
        # PyInstaller 创建一个临时文件夹，并将路径存储在 _MEIPASS 中
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class PrtsInput(QLineEdit):
    enterPressed = pyqtSignal()
    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter) and event.modifiers() == Qt.ControlModifier:
            self.enterPressed.emit()
        else:
            super().keyPressEvent(event)

class OperatorTableWidget(QTableWidget):
    deletePressed = pyqtSignal(list)
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            selected_rows = sorted(list(set(index.row() for index in self.selectedIndexes())), reverse=True)
            if selected_rows:
                self.deletePressed.emit(selected_rows)
        else:
            super().keyPressEvent(event)

class WheelEventFilter(QObject):
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Wheel:
            return True
        return super().eventFilter(obj, event)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.logic = DataLoader()
        self.calculator = DPSCalculator()
        self.operators_data = {}
        self.calculation_records = []
        self.current_record_index = -1
        self.current_operator_name = None
        self.dark_mode = True
        self.wheel_filter = WheelEventFilter(self)
        self.is_on_cooldown = False
        self.fetch_cooldown_timer = QTimer(self)
        self.fetch_cooldown_timer.setSingleShot(True)
        self._init_ui()
        self._connect_signals()
        self.apply_theme()
        self.setWindowIcon(QIcon(resource_path('icon.ico')))  # 设置窗口图标

    def _init_ui(self):
        self.setWindowTitle("Arknights 简易DPS计算器 (by Cyletix)")
        self.resize(1600, 900)
        self.setMinimumSize(1200, 700)
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        main_layout.addWidget(self._create_left_panel(), stretch=2)
        main_layout.addWidget(self._create_right_panel(), stretch=3)

    def _create_left_panel(self):
        left_panel = QWidget()
        left_panel.setObjectName("LeftPanel")
        layout = QVBoxLayout(left_panel)
        layout.setContentsMargins(10, 10, 10, 10)
        
        fetch_layout = QHBoxLayout()
        self.prts_input = PrtsInput()
        self.prts_input.setPlaceholderText("输入干员 (Ctrl+Enter 查询) 或 PRTS 链接")
        self.fetch_button = QPushButton("从PRTS获取")
        fetch_layout.addWidget(self.prts_input)
        fetch_layout.addWidget(self.fetch_button)
        layout.addLayout(fetch_layout)
        
        self.load_file_button = QPushButton("从本地HTML文件加载")
        layout.addWidget(self.load_file_button)
        
        self.drop_area = DraggableTextEdit()
        self.drop_area.setPlaceholderText("或将HTML文件拖拽至此。加载后将在下方列表创建默认快照。")
        # [修改] 调整高度
        self.drop_area.setMaximumHeight(80)
        layout.addWidget(self.drop_area)

        records_group = QGroupBox("计算快照管理")
        records_group_layout = QVBoxLayout(records_group)
        db_layout = QHBoxLayout()
        self.save_record_button = QPushButton("💾 保存当前计算快照")
        self.load_records_button = QPushButton("📂 加载快照文件")
        db_layout.addWidget(self.save_record_button)
        db_layout.addWidget(self.load_records_button)
        records_group_layout.addLayout(db_layout)

        # [修改] 扩展表格字段
        self.record_list_widget = OperatorTableWidget()
        self.record_list_widget.setColumnCount(9)
        self.record_list_widget.setHorizontalHeaderLabels(["快照名称", "干员", "职业", "稀有度", "精英阶段", "等级", "计算技能", "技能等级", "保存时间"])
        self.record_list_widget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.record_list_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.record_list_widget.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        for i in range(1, 9): # 其他列根据内容自适应
             self.record_list_widget.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeToContents)
        records_group_layout.addWidget(self.record_list_widget, stretch=1)
        layout.addWidget(records_group)
        
        return left_panel

    def _create_right_panel(self):
        right_panel = QWidget()
        right_panel.setObjectName("RightPanel")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(10, 10, 10, 10)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setObjectName("ScrollArea")
        scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignTop)
        self.inputs = {}
        self._create_right_panel_content()
        scroll_area.setWidget(scroll_content)
        right_layout.addWidget(scroll_area)
        right_layout.addWidget(self._create_footer_panel())
        return right_panel

    def _create_right_panel_content(self):
        top_section_layout = QHBoxLayout()
        top_section_layout.setSpacing(10)
        left_column_widget = QWidget()
        left_column_layout = QVBoxLayout(left_column_widget)
        left_column_layout.setContentsMargins(0, 0, 0, 0)
        left_column_layout.setAlignment(Qt.AlignTop)
        setup_group = QGroupBox("--- 计算设置 ---")
        setup_grid_layout = QGridLayout(setup_group)
        setup_grid_layout.setSpacing(15)
        skill_levels = ["1", "2", "3", "4", "5", "6", "7", "专精 I", "专精 II", "专精 III"]
        self.inputs["精英阶段"] = QComboBox()
        self.inputs["等级"] = QSpinBox(); self.inputs["等级"].setRange(1,1)
        self.inputs["计算技能"] = QComboBox(); self.inputs["计算技能"].addItems(["普攻", "技能 1", "技能 2", "技能 3"])
        self.inputs["技能等级"] = QComboBox(); self.inputs["技能等级"].addItems(skill_levels)
        self.inputs["信赖"] = QSpinBox(); self.inputs["信赖"].setRange(0, 100); self.inputs["信赖"].setValue(100)
        self.inputs["计算信赖"] = QCheckBox("计算信赖"); self.inputs["计算信赖"].setChecked(True)
        self.inputs["潜能"] = QComboBox(); self.inputs["潜能"].addItems([f"潜能 {i}" for i in range(1, 7)])
        self.inputs["计算潜能"] = QCheckBox("计算潜能"); self.inputs["计算潜能"].setChecked(True)
        setup_grid_layout.addWidget(QLabel("精英阶段:"), 0, 0, Qt.AlignRight); setup_grid_layout.addWidget(self.inputs["精英阶段"], 0, 1)
        setup_grid_layout.addWidget(QLabel("等级:"), 0, 2, Qt.AlignRight); setup_grid_layout.addWidget(self.inputs["等级"], 0, 3)
        setup_grid_layout.addWidget(QLabel("信赖(%):"), 0, 4, Qt.AlignRight); setup_grid_layout.addWidget(self.inputs["信赖"], 0, 5)
        setup_grid_layout.addWidget(self.inputs["计算信赖"], 0, 6)
        setup_grid_layout.addWidget(QLabel("计算技能:"), 1, 0, Qt.AlignRight); setup_grid_layout.addWidget(self.inputs["计算技能"], 1, 1)
        setup_grid_layout.addWidget(QLabel("技能等级:"), 1, 2, Qt.AlignRight); setup_grid_layout.addWidget(self.inputs["技能等级"], 1, 3)
        setup_grid_layout.addWidget(QLabel("潜能:"), 1, 4, Qt.AlignRight); setup_grid_layout.addWidget(self.inputs["潜能"], 1, 5)
        setup_grid_layout.addWidget(self.inputs["计算潜能"], 1, 6)
        setup_grid_layout.setColumnStretch(7, 1)
        left_column_layout.addWidget(setup_group)
        attr_group = QGroupBox("--- 基础属性 ---")
        attr_fields = [
            [("生命上限:", "生命上限", QLineEdit, "", None),("攻击:", "攻击", QLineEdit, "", None),("防御:", "防御", QLineEdit, "", None),("法术抗性:", "法术抗性", QLineEdit, "", None)],
            [("攻击间隔:", "攻击间隔", QLineEdit, "", None),("阻挡数:", "阻挡数", QLineEdit, "", None),("初始费用:", "初始费用", QLineEdit, "", None),("再部署时间:", "再部署时间", QLineEdit, "", None)],
        ]
        attr_layout = UIComponents.create_grid_layout(self, attr_fields, fixed_width=80)
        attr_group.setLayout(attr_layout)
        left_column_layout.addWidget(attr_group)
        left_column_layout.addStretch()
        potential_desc_group = QGroupBox("潜能描述")
        potential_desc_layout = QVBoxLayout(potential_desc_group)
        self.inputs["潜能描述"] = QTextEdit(); self.inputs["潜能描述"].setReadOnly(True)
        potential_desc_layout.addWidget(self.inputs["潜能描述"])
        top_section_layout.addWidget(left_column_widget, 3)
        top_section_layout.addWidget(potential_desc_group, 1)
        self.scroll_layout.addLayout(top_section_layout)
        self.scroll_layout.addWidget(QLabel("<b>--- 手动增益输入 ---</b>"))
        trait_desc_group = QGroupBox("特性描述")
        trait_desc_layout = QVBoxLayout(trait_desc_group)
        self.inputs["特性描述"] = QTextEdit(); self.inputs["特性描述"].setReadOnly(True)
        self.inputs["特性描述"].setFixedHeight(70)
        trait_desc_layout.addWidget(self.inputs["特性描述"])
        self.scroll_layout.addWidget(trait_desc_group)
        talent_layout = QHBoxLayout()
        talent_desc_group = QGroupBox("天赋描述")
        talent_desc_layout = QVBoxLayout(talent_desc_group)
        self.inputs["天赋描述"] = QTextEdit(); self.inputs["天赋描述"].setReadOnly(True)
        talent_desc_layout.addWidget(self.inputs["天赋描述"])
        talent_layout.addWidget(talent_desc_group, 2)
        talent_layout.addWidget(
            UIComponents.create_buff_panel(self, "talent", "天赋增益 (手动输入)", event_filter=self.wheel_filter), 3
        )
        self.scroll_layout.addLayout(talent_layout)
        self.scroll_layout.addWidget(
            UIComponents.create_buff_panel(self, "global", "全局增益 (来自队友、环境等)", event_filter=self.wheel_filter)
        )
        self.skill_widgets = []
        for i in range(1, 4):
            skill_prefix = f"技能 {i}"
            skill_group = QWidget()
            skill_layout = QVBoxLayout(skill_group)
            skill_layout.setContentsMargins(0, 10, 0, 0)
            desc_group = QGroupBox(f"技能 {i} 描述与参数")
            desc_layout = QGridLayout(desc_group)
            self.inputs[f"{skill_prefix}描述"] = QTextEdit(); self.inputs[f"{skill_prefix}描述"].setReadOnly(True); self.inputs[f"{skill_prefix}描述"].setFixedHeight(80)
            desc_layout.addWidget(self.inputs[f"{skill_prefix}描述"], 0, 0, 1, 10)
            headers = ["初始", "消耗", "持续", "回复", "触发"]
            for col, header in enumerate(headers):
                label = QLabel(f"<b>{header}:</b>")
                key = f"{skill_prefix}{header}"
                editor = QLineEdit(); editor.setReadOnly(True)
                self.inputs[key] = editor
                desc_layout.addWidget(label, 1, col * 2)
                desc_layout.addWidget(editor, 1, col * 2 + 1)
            skill_layout.addWidget(desc_group)
            skill_layout.addWidget(
                UIComponents.create_buff_panel(self, skill_prefix, f"技能 {i} 增益 (手动输入)", event_filter=self.wheel_filter)
            )
            skill_group.hide()
            self.skill_widgets.append(skill_group)
            self.scroll_layout.addWidget(skill_group)

    def _create_footer_panel(self):
        footer_panel = QWidget()
        footer_panel.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        main_footer_layout = QVBoxLayout(footer_panel)
        main_footer_layout.setContentsMargins(0, 10, 0, 0)
        top_footer_layout = QHBoxLayout()
        enemy_group = QGroupBox("--- 敌人参数 ---")
        enemy_layout = QGridLayout(enemy_group)
        enemy_layout.setSpacing(10)
        self.inputs["敌人数量"] = QSpinBox(); self.inputs["敌人数量"].setRange(1, 10); self.inputs["敌人数量"].setValue(1)
        self.inputs["敌人防御"] = QSpinBox(); self.inputs["敌人防御"].setRange(0, 5000)
        self.inputs["敌人法抗"] = QSpinBox(); self.inputs["敌人法抗"].setRange(0, 100)
        enemy_layout.addWidget(QLabel("敌人数量:"), 0, 0); enemy_layout.addWidget(self.inputs["敌人数量"], 0, 1)
        enemy_layout.addWidget(QLabel("敌人防御:"), 1, 0); enemy_layout.addWidget(self.inputs["敌人防御"], 1, 1)
        enemy_layout.addWidget(QLabel("敌人法抗:"), 2, 0); enemy_layout.addWidget(self.inputs["敌人法抗"], 2, 1)
        results_group = QGroupBox("--- 计算结果 ---")
        results_layout = QVBoxLayout(results_group)
        self.results_display = QTextEdit()
        self.results_display.setReadOnly(True)
        self.results_display.setPlaceholderText("点击“执行计算”后，结果将显示在此处。")
        self.results_display.setFixedHeight(130)
        results_layout.addWidget(self.results_display)
        top_footer_layout.addWidget(enemy_group, 1)
        top_footer_layout.addWidget(results_group, 3)
        main_footer_layout.addLayout(top_footer_layout)
        
        bottom_bar_layout = QHBoxLayout()
        # [修改] 调整按钮栏边距
        bottom_bar_layout.setContentsMargins(10, 10, 10, 10)
        self.calculate_button = QPushButton("执行计算")
        # [修改] 调整按钮宽度
        self.calculate_button.setMinimumWidth(160)
        bottom_bar_layout.addWidget(self.calculate_button)
        bottom_bar_layout.addStretch()
        self.theme_button = QPushButton("🌙")
        self.theme_button.setFixedSize(40, 40)
        self.theme_button.setObjectName("CircularButton")
        bottom_bar_layout.addWidget(self.theme_button)
        main_footer_layout.addLayout(bottom_bar_layout)
        return footer_panel

    def _connect_signals(self):
        self.fetch_button.clicked.connect(self.on_fetch_from_prts)
        self.prts_input.enterPressed.connect(self.on_fetch_from_prts)
        self.fetch_cooldown_timer.timeout.connect(self._reset_fetch_state)
        self.load_file_button.clicked.connect(self.on_load_html_file)
        self.drop_area.fileDropped.connect(self.on_file_dropped)
        self.save_record_button.clicked.connect(self.on_save_record)
        self.load_records_button.clicked.connect(self.on_load_records)
        self.record_list_widget.itemClicked.connect(self.on_record_selected)
        self.record_list_widget.deletePressed.connect(self.on_delete_record)
        self.inputs["精英阶段"].currentIndexChanged.connect(self.on_config_changed)
        self.inputs["等级"].valueChanged.connect(self.update_display_stats)
        self.inputs["信赖"].valueChanged.connect(self.update_display_stats)
        self.inputs["潜能"].currentIndexChanged.connect(self.on_config_changed)
        self.inputs["计算信赖"].stateChanged.connect(self.update_display_stats)
        self.inputs["计算潜能"].stateChanged.connect(self.update_display_stats)
        self.inputs["计算技能"].currentIndexChanged.connect(self._update_visible_skill_widgets)
        self.inputs["技能等级"].currentIndexChanged.connect(self.update_skill_description_display)
        self.calculate_button.clicked.connect(self.on_calculate)
        self.theme_button.clicked.connect(self.toggle_theme)

    def on_calculate(self):
        if not self.current_operator_name:
            self.results_display.setText("请先加载并选择一个干员。")
            return
        try:
            op_data = self.operators_data[self.current_operator_name]
            live_stats = {"atk": float(self.inputs["攻击"].text())}
            skill_choice = self.inputs["计算技能"].currentText()
            enemy_stats = {"def": self.inputs["敌人防御"].value(), "res": self.inputs["敌人法抗"].value()}
            skill_level_str = self.inputs["技能等级"].currentText().replace("专精 ", "Rank ")
            all_buffs = {}
            buff_prefixes = ["global", "talent"]
            if self.inputs["计算技能"].currentIndex() > 0:
                buff_prefixes.append(skill_choice)
            for prefix in buff_prefixes:
                if f"{prefix}_enable" in self.inputs and self.inputs[f"{prefix}_enable"].isChecked():
                    all_buffs[prefix] = self._collect_buffs_from_prefix(prefix)
            result_text = self.calculator.calculate_dps(
                op_data, live_stats, skill_choice, skill_level_str, enemy_stats, all_buffs
            )
            self.results_display.setText(result_text)
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.results_display.setText(f"计算出错: {e}\n请检查输入数据和干员数据。")

    def _collect_buffs_from_prefix(self, prefix):
        buffs = {}
        keys_map = {
            "direct_atk_flat": (QSpinBox, 0), "direct_atk_pct": (QSpinBox, 0), "final_atk_flat": (QSpinBox, 0),
            "direct_def_flat": (QSpinBox, 0), "direct_def_pct": (QSpinBox, 0), "final_def_flat": (QSpinBox, 0),
            "aspd": (QSpinBox, 0), "interval": (QLineEdit, 0.0),
            "phys_dmg_mult": (QSpinBox, 100), "arts_dmg_mult": (QSpinBox, 100),
        }
        for key_suffix, (widget_type, default_val) in keys_map.items():
            widget_key = f"{prefix}_{key_suffix}"
            if widget_key in self.inputs:
                widget = self.inputs[widget_key]
                if widget_type == QSpinBox:
                    buffs[key_suffix] = widget.value()
                elif widget_type == QLineEdit:
                    try:
                        buffs[key_suffix] = float(widget.text())
                    except ValueError:
                        buffs[key_suffix] = default_val
        return buffs
    
    def on_fetch_from_prts(self):
        if self.is_on_cooldown: return
        op_input = self.prts_input.text().strip()
        if not op_input:
            self.drop_area.setText("请输入干员名称或PRTS页面链接。")
            return
        operator_name = self.logic.extract_name_from_input(op_input)
        if not operator_name:
            self.drop_area.setText("无法从输入中识别干员名称或链接。")
            return
        self.is_on_cooldown = True
        self.fetch_button.setEnabled(False)
        self.fetch_button.setText("冷却中...")
        self.fetch_button.repaint(); QApplication.processEvents()
        self.fetch_cooldown_timer.start(1000)
        self.drop_area.setText(f"正在从PRTS获取“{operator_name}”的页面HTML...")
        QApplication.processEvents()
        parsed_data = self.logic.fetch_operator_data_from_html(operator_name)
        self.process_and_display_data(parsed_data, f"https://m.prts.wiki/w/{operator_name}")

    def _reset_fetch_state(self):
        self.is_on_cooldown = False
        self.fetch_button.setEnabled(True)
        self.fetch_button.setText("从PRTS获取")

    def on_file_dropped(self, file_path):
        self.drop_area.setText(f"已加载文件: {file_path}")
        try:
            with open(file_path, "r", encoding="utf-8") as f: content = f.read()
            parsed_data = self.logic.parse_html(content)
            self.process_and_display_data(parsed_data, f"file:///{file_path}")
        except Exception as e:
            self.drop_area.setText(f"读取或解析文件失败: {e}")

    def on_load_html_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择PRTS HTML文件", "", "HTML Files (*.html)")
        if file_path: self.on_file_dropped(file_path)

    def process_and_display_data(self, parsed_data, source_url):
        if parsed_data and "error" not in parsed_data and "干员名称" in parsed_data:
            name = parsed_data["干员名称"]
            parsed_data["PRTS地址"] = source_url
            self.operators_data[name] = parsed_data
            
            existing_indices = [i for i, r in enumerate(self.calculation_records) if r['recordName'] == name]
            
            if existing_indices:
                self.record_list_widget.setCurrentCell(existing_indices[0], 0)
                self.on_record_selected(self.record_list_widget.item(existing_indices[0], 0))
                self.drop_area.setText(f"已选择已存在的默认快照: {name}")
            else:
                self.display_operator_data(parsed_data)
                
                default_record = {
                    "recordName": name,
                    "operatorName": name,
                    "timestamp": datetime.now().astimezone().isoformat(),
                    "rawData": parsed_data,
                    "calculationSetup": self._gather_current_setup(),
                    "calculationResult": {"fullText": "默认快照已生成。请点击“执行计算”。"}
                }
                self.calculation_records.append(default_record)
                self.update_record_list()
                new_row_index = len(self.calculation_records) - 1
                self.record_list_widget.setCurrentCell(new_row_index, 0)
                self.on_record_selected(self.record_list_widget.item(new_row_index, 0))
                self.drop_area.setText(f"已为干员“{name}”创建默认快照。")
        else:
            error_msg = parsed_data.get("error", "未知解析错误")
            self.drop_area.setText(f"错误: {error_msg}")

    def _gather_current_setup(self):
        setup = {"config": {}, "buffs": {}, "enemy": {}}
        for key in ["精英阶段", "等级", "计算技能", "技能等级", "潜能", "信赖"]:
            if isinstance(self.inputs[key], QComboBox):
                setup["config"][key] = self.inputs[key].currentText()
            else: # QSpinBox
                setup["config"][key] = self.inputs[key].value()
        for key in ["计算信赖", "计算潜能"]:
            setup["config"][key] = self.inputs[key].isChecked()
        all_buff_keys = ["enable", "direct_atk_flat", "direct_atk_pct", "final_atk_flat", 
                         "direct_def_flat", "direct_def_pct", "final_def_flat", 
                         "aspd", "interval", "phys_dmg_mult", "arts_dmg_mult"]
        for prefix in ["global", "talent", "技能 1", "技能 2", "技能 3"]:
            for key_suffix in all_buff_keys:
                widget_key = f"{prefix}_{key_suffix}"
                if widget_key in self.inputs:
                    widget = self.inputs[widget_key]
                    if isinstance(widget, QSpinBox): setup["buffs"][widget_key] = widget.value()
                    elif isinstance(widget, QLineEdit): setup["buffs"][widget_key] = widget.text()
                    elif isinstance(widget, (QCheckBox, QGroupBox)): setup["buffs"][widget_key] = widget.isChecked()
        for key in ["敌人数量", "敌人防御", "敌人法抗"]:
            setup["enemy"][key] = self.inputs[key].value()
        return setup

    def _restore_ui_from_record(self, record):
        setup = record.get("calculationSetup", {})
        config = setup.get("config", {})
        for key, value in config.items():
             if key in self.inputs:
                widget = self.inputs[key]
                if isinstance(widget, QComboBox): widget.setCurrentText(value)
                elif isinstance(widget, QSpinBox): widget.setValue(value)
                elif isinstance(widget, QCheckBox): widget.setChecked(value)
        buffs = setup.get("buffs", {})
        for widget_key, value in buffs.items():
            if widget_key in self.inputs:
                widget = self.inputs[widget_key]
                if isinstance(widget, QSpinBox): widget.setValue(value)
                elif isinstance(widget, QLineEdit): widget.setText(value)
                elif isinstance(widget, (QCheckBox, QGroupBox)): widget.setChecked(value)
        enemy = setup.get("enemy", {})
        for key in ["敌人数量", "敌人防御", "敌人法抗"]:
            if key in enemy: self.inputs[key].setValue(enemy[key])
        result = record.get("calculationResult", {})
        self.results_display.setText(result.get("fullText", ""))

    def on_save_record(self):
        if not self.current_operator_name:
            QMessageBox.warning(self, "操作失败", "请先加载一个干员并进行计算，才能保存快照。")
            return
        record_name, ok = QInputDialog.getText(self, "保存计算快照", "请输入快照文件名:")
        if not ok or not record_name.strip():
            return
        record_name = record_name.strip()
        new_record = {
            "recordName": record_name,
            "operatorName": self.current_operator_name,
            "timestamp": datetime.now().astimezone().isoformat(),
            "rawData": self.operators_data[self.current_operator_name],
            "calculationSetup": self._gather_current_setup(),
            "calculationResult": {"fullText": self.results_display.toPlainText()}
        }
        file_path, _ = QFileDialog.getSaveFileName(self, "选择快照文件保存位置", f"{record_name}.json", "JSON Files (*.json)")
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(new_record, f, ensure_ascii=False, indent=2)
                if not any(r['recordName'] == record_name for r in self.calculation_records):
                    self.calculation_records.append(new_record)
                    self.update_record_list()
                    self.record_list_widget.setCurrentCell(len(self.calculation_records) - 1, 0)
                self.drop_area.setText(f"快照 '{record_name}' 已保存至: {os.path.basename(file_path)}")
            except Exception as e:
                QMessageBox.critical(self, "保存失败", f"保存快照文件失败: {e}")

    def on_load_records(self):
        file_paths, _ = QFileDialog.getOpenFileNames(self, "加载快照文件 (可多选)", "", "JSON Files (*.json)")
        if file_paths:
            loaded_count = 0; skipped_count = 0
            existing_names = {r['recordName'] for r in self.calculation_records}
            for file_path in file_paths:
                try:
                    with open(file_path, "r", encoding="utf-8") as f: loaded_record = json.load(f)
                    if not isinstance(loaded_record, dict) or "recordName" not in loaded_record:
                        print(f"Skipping invalid file: {file_path}"); continue
                    if loaded_record['recordName'] not in existing_names:
                        self.calculation_records.append(loaded_record)
                        op_name = loaded_record.get("operatorName"); raw_data = loaded_record.get("rawData")
                        if op_name and raw_data: self.operators_data[op_name] = raw_data
                        existing_names.add(loaded_record['recordName'])
                        loaded_count += 1
                    else: skipped_count += 1
                except Exception as e:
                    QMessageBox.critical(self, "加载失败", f"加载文件 {os.path.basename(file_path)} 失败: {e}")
            if loaded_count > 0: self.update_record_list()
            self.drop_area.setText(f"加载完成。新增 {loaded_count} 个快照，跳过 {skipped_count} 个重复快照。")

    def on_delete_record(self, rows_to_delete):
        for row in rows_to_delete:
            if 0 <= row < len(self.calculation_records): self.calculation_records[row] = None
        self.calculation_records = [r for r in self.calculation_records if r is not None]
        self.update_record_list()
        self.drop_area.setText(f"已从当前会话中移除 {len(rows_to_delete)} 个快照。")

    def display_operator_data(self, data):
        self.current_operator_name = data.get("干员名称", "")
        for name, widget in self.inputs.items():
            if isinstance(widget, QLineEdit):
                if "interval" not in name: widget.clear()
            elif isinstance(widget, QTextEdit): widget.clear()
            elif isinstance(widget, QSpinBox): widget.setValue(100 if "mult" in name else 0)
            elif isinstance(widget, QComboBox): widget.setCurrentIndex(0)
            elif isinstance(widget, QCheckBox): widget.setChecked(True)
            elif isinstance(widget, QGroupBox): widget.setChecked(True)
        self.inputs["计算信赖"].setChecked(True)
        self.inputs["计算潜能"].setChecked(True)
        self.inputs["信赖"].setValue(100)
        self.inputs["特性描述"].setPlainText(data.get("特性-描述", "未能获取特性信息。"))
        self.inputs["精英阶段"].blockSignals(True)
        self.inputs["精英阶段"].clear()
        hp_values = [v for v in data.get("attributes", {}).get("hp", []) if v]
        max_elite_level = len(hp_values) - 1 if len(hp_values) > 1 else 0
        self.inputs["精英阶段"].addItems([f"精英 {i}" for i in range(max_elite_level)])
        default_elite_index = len(self.inputs["精英阶段"])-1
        if default_elite_index >= 0 : self.inputs["精英阶段"].setCurrentIndex(max(default_elite_index-1, 0))
        self.inputs["精英阶段"].blockSignals(False)
        default_skill_index = 2 if "技能 2" in data else 0
        self.inputs["计算技能"].setCurrentIndex(default_skill_index)
        level_7_index = self.inputs["技能等级"].findText("7")
        if level_7_index != -1: self.inputs["技能等级"].setCurrentIndex(level_7_index)
        self.inputs["攻击间隔"].setText(data.get("攻击间隔", "N/A"))
        self.inputs["阻挡数"].setText(data.get("阻挡数", "N/A"))
        self.on_config_changed()

    def on_config_changed(self):
        if not self.current_operator_name: return
        self.update_level_range()
        self.update_talent_display()
        self.update_potential_display()
        self.update_deployment_cost()
        self.update_redeploy_time()
        self.update_display_stats()

    def on_record_selected(self, item):
        row = item.row()
        if 0 <= row < len(self.calculation_records):
            self.current_record_index = row
            record = self.calculation_records[row]
            self.display_operator_data(record["rawData"])
            self._restore_ui_from_record(record)

    def update_record_list(self):
        self.record_list_widget.setRowCount(0)
        for record in self.calculation_records:
            row_pos = self.record_list_widget.rowCount()
            self.record_list_widget.insertRow(row_pos)
            
            op_name = record.get("operatorName", "N/A")
            raw_data = self.operators_data.get(op_name, {})
            config = record.get("calculationSetup", {}).get("config", {})
            
            self.record_list_widget.setItem(row_pos, 0, QTableWidgetItem(record.get("recordName", "无标题")))
            self.record_list_widget.setItem(row_pos, 1, QTableWidgetItem(op_name))
            self.record_list_widget.setItem(row_pos, 2, QTableWidgetItem(raw_data.get("职业", "?")))
            self.record_list_widget.setItem(row_pos, 3, QTableWidgetItem(str(raw_data.get("稀有度", "?"))))
            self.record_list_widget.setItem(row_pos, 4, QTableWidgetItem(config.get("精英阶段", "?")))
            self.record_list_widget.setItem(row_pos, 5, QTableWidgetItem(str(config.get("等级", "?"))))
            self.record_list_widget.setItem(row_pos, 6, QTableWidgetItem(config.get("计算技能", "?")))
            self.record_list_widget.setItem(row_pos, 7, QTableWidgetItem(config.get("技能等级", "?")))
            
            timestamp_str = "N/A"
            try:
                ts = datetime.fromisoformat(record.get("timestamp", ""))
                timestamp_str = ts.strftime('%y-%m-%d %H:%M')
            except (ValueError, TypeError): pass
            self.record_list_widget.setItem(row_pos, 8, QTableWidgetItem(timestamp_str))

    def update_level_range(self):
        if not self.current_operator_name: return
        op_data = self.operators_data[self.current_operator_name]
        rarity = op_data.get("稀有度", 1)
        elite_level = self.inputs["精英阶段"].currentIndex()
        level_caps = {6: [50, 80, 90], 5: [50, 70, 80], 4: [45, 60, 70], 3: [40, 55, 70], 2: [30, 55], 1: [30]}
        caps = level_caps.get(rarity, [30])
        if elite_level >= len(caps): return
        max_level = caps[elite_level]
        self.inputs["等级"].blockSignals(True)
        self.inputs["等级"].setRange(1, max_level)
        self.inputs["等级"].setValue(max_level)
        self.inputs["等级"].blockSignals(False)

    def update_display_stats(self):
        if not self.current_operator_name: return
        op_data = self.operators_data[self.current_operator_name]
        stats = self.calculator.calculate_live_stats(
            op_data, self.inputs["精英阶段"].currentIndex(), self.inputs["等级"].value(),
            self.inputs["信赖"].value(), self.inputs["潜能"].currentIndex() + 1,
            {"calc_trust": self.inputs["计算信赖"].isChecked(), "calc_potential": self.inputs["计算潜能"].isChecked()},
        )
        key_map = {"hp": "生命上限", "atk": "攻击", "def": "防御", "res": "法术抗性"}
        for key, value in stats.items():
            if key_map.get(key) in self.inputs:
                self.inputs[key_map[key]].setText(str(value))

    def update_talent_display(self):
        if not self.current_operator_name: return
        op_data = self.operators_data[self.current_operator_name]
        theme_dict = DARK_THEME if self.dark_mode else LIGHT_THEME
        unlocked_color, locked_color = theme_dict['text'], theme_dict['button']
        elite_level = self.inputs["精英阶段"].currentIndex()
        html_lines = []
        for talent in op_data.get("天赋", []):
            condition = talent.get("条件", "").strip()
            unlocked = ("精英2" in condition and elite_level >= 2) or \
                       ("精英1" in condition and elite_level >= 1) or \
                       ("精英" not in condition)
            color = unlocked_color if unlocked else locked_color
            html_lines.append(f'<div style="color:{color}; margin-bottom: 5px;">'
                              f'<b>{talent.get("名称", "")}</b> (解锁: {condition})<br>'
                              f'{talent.get("描述", "")}</div>')
        self.inputs["天赋描述"].setHtml("".join(html_lines))

    def update_potential_display(self):
        if not self.current_operator_name: return
        op_data = self.operators_data[self.current_operator_name]
        theme_dict = DARK_THEME if self.dark_mode else LIGHT_THEME
        unlocked_color, locked_color = theme_dict['text'], theme_dict['button']
        selected_potential_level = self.inputs["潜能"].currentIndex() + 1
        html_lines = []
        for item in op_data.get("潜能", []):
            item_level = int(re.search(r'\d+', item.get('等级', '1')).group())
            color = unlocked_color if item_level <= selected_potential_level else locked_color
            html_lines.append(f'<b style="color:{color};">{item["等级"]}:</b> <span style="color:{color};">{item["描述"]}</span>')
        self.inputs["潜能描述"].setHtml("<br>".join(html_lines))

    def update_deployment_cost(self):
        if not self.current_operator_name: return
        op_data = self.operators_data[self.current_operator_name]
        costs = [int(c) for c in re.findall(r"\d+", op_data.get("cost_progression", ""))]
        if not costs: return
        elite = self.inputs["精英阶段"].currentIndex()
        pot = self.inputs["潜能"].currentIndex()
        base_cost = costs[min(elite, len(costs) - 1)]
        cost_reduction = sum(1 for i in range(pot) if i < len(op_data.get("潜能", [])) and "部署费用" in op_data["潜能"][i].get("描述", ""))
        self.inputs["初始费用"].setText(str(base_cost - cost_reduction))

    def update_redeploy_time(self):
        if not self.current_operator_name: return
        op_data = self.operators_data[self.current_operator_name]
        base_redeploy_str = op_data.get("再部署时间", "0s")
        match = re.search(r'[\d\.]+', base_redeploy_str)
        base_redeploy_time = float(match.group()) if match else 0
        redeploy_reduction = 0
        potential_data = op_data.get("潜能", [])
        pot_index = self.inputs["潜能"].currentIndex()
        for i in range(pot_index):
            if i < len(potential_data) and "再部署时间" in potential_data[i].get("描述", ""):
                reduction_match = re.search(r'-(\d+)', potential_data[i].get("描述", ""))
                if reduction_match: redeploy_reduction += int(reduction_match.group(1))
        self.inputs["再部署时间"].setText(f"{base_redeploy_time - redeploy_reduction:.0f}s")

    def _update_visible_skill_widgets(self):
        selected_skill_index = self.inputs["计算技能"].currentIndex()
        for i, widget_group in enumerate(self.skill_widgets, 1):
            widget_group.setVisible(i == selected_skill_index)
        self.update_skill_description_display()

    def update_skill_description_display(self):
        if not self.current_operator_name: return
        skill_num = self.inputs["计算技能"].currentIndex()
        if skill_num == 0: return
        op_data = self.operators_data[self.current_operator_name]
        skill_data = op_data.get(f"技能 {skill_num}")
        if not skill_data or "levels" not in skill_data: return
        level_text = self.inputs["技能等级"].currentText().replace("专精 ", "Rank ")
        level_info = skill_data["levels"].get(level_text, {})
        self.inputs[f"技能 {skill_num}描述"].setPlainText(level_info.get("description", "无此等级数据"))
        for key in ["initial_sp", "sp_cost", "duration"]:
            sp_key = "初始" if key == "initial_sp" else "消耗" if key == "sp_cost" else "持续"
            self.inputs[f"技能 {skill_num}{sp_key}"].setText(str(level_info.get(key, "")))
        self.inputs[f"技能 {skill_num}回复"].setText(skill_data.get("回复类型", ""))
        self.inputs[f"技能 {skill_num}触发"].setText(skill_data.get("触发类型", ""))

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.theme_button.setText("🌙" if self.dark_mode else "☀️")
        self.apply_theme()

    def apply_theme(self):
        theme_dict = DARK_THEME if self.dark_mode else LIGHT_THEME
        stylesheet = get_stylesheet(theme_dict)
        self.setStyleSheet(stylesheet)
        self.update_potential_display()
        self.update_talent_display()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())