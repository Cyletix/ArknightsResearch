# main_ui.py
import sys
import json
import re
import os
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
)
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QEvent

from data_loader import DataLoader, DraggableTextEdit
from dps_calculator import DPSCalculator
from ui_styles import DARK_THEME, LIGHT_THEME, get_stylesheet
from ui_components import UIComponents

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
        self.current_operator_name = None
        self.dark_mode = True
        self.wheel_filter = WheelEventFilter(self)
        self._init_ui()
        self._connect_signals()
        self.apply_theme()

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
        self.prts_input = QLineEdit()
        self.prts_input.setPlaceholderText("输入干员名称 (如: 新约能天使) 或 PRTS 链接")
        self.fetch_button = QPushButton("从PRTS获取")
        fetch_layout.addWidget(self.prts_input)
        fetch_layout.addWidget(self.fetch_button)
        layout.addLayout(fetch_layout)
        self.load_file_button = QPushButton("从本地HTML文件加载")
        layout.addWidget(self.load_file_button)
        self.drop_area = DraggableTextEdit()
        self.drop_area.setPlaceholderText("或将HTML文件拖拽至此")
        self.drop_area.setMaximumHeight(100)
        layout.addWidget(self.drop_area)
        db_layout = QHBoxLayout()
        self.save_db_button = QPushButton("保存数据库")
        self.load_db_button = QPushButton("加载数据库")
        db_layout.addWidget(self.save_db_button)
        db_layout.addWidget(self.load_db_button)
        layout.addLayout(db_layout)
        layout.addWidget(QLabel("已加载干员:"))
        self.operator_list_widget = QTableWidget()
        self.operator_list_widget.setColumnCount(3)
        self.operator_list_widget.setHorizontalHeaderLabels(["名称", "职业", "稀有度"])
        self.operator_list_widget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.operator_list_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.operator_list_widget.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )
        layout.addWidget(self.operator_list_widget, stretch=1)
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

        # 【修改】移除标题的 bold 标签
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

        # 【修改】将基础属性也放入GroupBox中，并移除label的bold标签和括号
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
            skill_prefix = f"技能{i}"
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
        # 【布局重构】完全重写页脚布局
        footer_panel = QWidget()
        footer_panel.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        main_footer_layout = QVBoxLayout(footer_panel)
        main_footer_layout.setContentsMargins(0, 10, 0, 0)

        # 上半部分：左右布局
        top_footer_layout = QHBoxLayout()
        
        # 左侧：敌人参数（垂直布局）
        enemy_group = QGroupBox("--- 敌人参数 ---")
        enemy_layout = QGridLayout(enemy_group)
        enemy_layout.setSpacing(10)
        
        self.inputs["敌人数量"] = QSpinBox(); self.inputs["敌人数量"].setRange(1, 10); self.inputs["敌人数量"].setValue(1)
        self.inputs["敌人防御"] = QSpinBox(); self.inputs["敌人防御"].setRange(0, 5000)
        self.inputs["敌人法抗"] = QSpinBox(); self.inputs["敌人法抗"].setRange(0, 100)
        
        enemy_layout.addWidget(QLabel("敌人数量:"), 0, 0); enemy_layout.addWidget(self.inputs["敌人数量"], 0, 1)
        enemy_layout.addWidget(QLabel("敌人防御:"), 1, 0); enemy_layout.addWidget(self.inputs["敌人防御"], 1, 1)
        enemy_layout.addWidget(QLabel("敌人法抗:"), 2, 0); enemy_layout.addWidget(self.inputs["敌人法抗"], 2, 1)

        # 右侧：计算结果
        results_group = QGroupBox("--- 计算结果 ---")
        results_layout = QVBoxLayout(results_group)
        self.results_display = QTextEdit()
        self.results_display.setReadOnly(True)
        self.results_display.setPlaceholderText("点击“执行计算”后，结果将显示在此处。")
        self.results_display.setFixedHeight(130) # 降低高度
        results_layout.addWidget(self.results_display)
        
        top_footer_layout.addWidget(enemy_group, 1) # 左侧占1份
        top_footer_layout.addWidget(results_group, 3) # 右侧占3份
        main_footer_layout.addLayout(top_footer_layout)

        # 下半部分：按钮栏
        bottom_bar_layout = QHBoxLayout()
        bottom_bar_layout.setContentsMargins(0, 10, 0, 0)
        self.calculate_button = QPushButton("执行计算")
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
        self.load_file_button.clicked.connect(self.on_load_html_file)
        self.drop_area.fileDropped.connect(self.on_file_dropped)
        self.save_db_button.clicked.connect(self.on_save_database)
        self.load_db_button.clicked.connect(self.on_load_database)
        self.operator_list_widget.itemClicked.connect(self.on_operator_selected)
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
            all_buffs = {}
            buff_prefixes = ["global", "talent"]
            if self.inputs["计算技能"].currentIndex() > 0:
                buff_prefixes.append(f"技能{self.inputs['计算技能'].currentIndex()}")
            for prefix in buff_prefixes:
                if f"{prefix}_enable" in self.inputs and self.inputs[f"{prefix}_enable"].isChecked():
                    all_buffs[prefix] = self._collect_buffs_from_prefix(prefix)
            result_text = self.calculator.calculate_dps(op_data, live_stats, skill_choice, enemy_stats, all_buffs)
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
        op_input = self.prts_input.text().strip()
        if not op_input:
            self.drop_area.setText("请输入干员名称或PRTS页面链接。")
            return
        operator_name = self.logic.extract_name_from_input(op_input)
        if not operator_name:
            self.drop_area.setText("无法从输入中识别干员名称或链接。")
            return
        self.drop_area.setText(f"正在从PRTS获取“{operator_name}”的数据...")
        QApplication.processEvents()
        parsed_data = self.logic.fetch_operator_data(operator_name)
        self.process_and_display_data(parsed_data, f"https://m.prts.wiki/w/{operator_name}")

    def on_file_dropped(self, file_path):
        self.drop_area.setText(f"已加载文件: {file_path}")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            parsed_data = self.logic.parse_html(content)
            self.process_and_display_data(parsed_data, f"file:///{file_path}")
        except Exception as e:
            self.drop_area.setText(f"读取或解析文件失败: {e}")

    def process_and_display_data(self, parsed_data, source_url):
        if parsed_data and "error" not in parsed_data and "干员名称" in parsed_data:
            name = parsed_data["干员名称"]
            parsed_data["PRTS地址"] = source_url
            self.operators_data[name] = parsed_data
            self.update_operator_list()
            self.select_operator_in_list(name)
            self.drop_area.append(f"\n成功获取/解析干员: {name}")
        else:
            error_msg = parsed_data.get("error", "未知解析错误")
            self.drop_area.setText(f"错误: {error_msg}")

    def on_load_html_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择PRTS HTML文件", "", "HTML Files (*.html)")
        if file_path:
            self.on_file_dropped(file_path)

    def on_save_database(self):
        if not self.operators_data:
            self.drop_area.setText("数据库为空，无需保存。")
            return
        file_path, _ = QFileDialog.getSaveFileName(self, "保存干员数据库", "arknights_operators.json", "JSON Files (*.json)")
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(self.operators_data, f, ensure_ascii=False, indent=4)
                self.drop_area.setText(f"数据库已成功保存至: {file_path}")
            except Exception as e:
                self.drop_area.setText(f"保存数据库失败: {e}")

    def on_load_database(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "加载干员数据库", "", "JSON Files (*.json)")
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    loaded_data = json.load(f)
                self.operators_data.update(loaded_data)
                self.update_operator_list()
                self.drop_area.setText(f"数据库已从 {file_path} 加载并合并。")
            except Exception as e:
                self.drop_area.setText(f"加载数据库失败: {e}")

    def on_operator_selected(self, item):
        name = self.operator_list_widget.item(item.row(), 0).text()
        if name in self.operators_data:
            self.display_operator_data(self.operators_data[name])

    def display_operator_data(self, data):
        self.current_operator_name = data.get("干员名称", "")
        for name, widget in self.inputs.items():
            if isinstance(widget, QLineEdit):
                if "interval" not in name: widget.clear()
            elif isinstance(widget, QTextEdit): widget.clear()
            elif isinstance(widget, QSpinBox):
                default_value = 100 if "mult" in name else 0
                widget.setValue(default_value)
            elif isinstance(widget, QComboBox): widget.setCurrentIndex(0)
            elif isinstance(widget, QCheckBox): widget.setChecked(True)
            elif isinstance(widget, QGroupBox): widget.setChecked(True)
        self.inputs["计算信赖"].setChecked(True)
        self.inputs["计算潜能"].setChecked(True)
        self.inputs["信赖"].setValue(100)
        self.inputs["特性描述"].setPlainText(data.get("特性-描述", "未能获取特性信息。"))
        self.inputs["精英阶段"].blockSignals(True)
        self.inputs["精英阶段"].clear()
        hp_values = data.get("attributes", {}).get("hp", [])
        max_elite_level = len(hp_values) - 2 if len(hp_values) > 1 else 0
        self.inputs["精英阶段"].addItems([f"精英 {i}" for i in range(max_elite_level + 1)])
        default_elite_index = min(max_elite_level, 1)
        self.inputs["精英阶段"].setCurrentIndex(default_elite_index)
        self.inputs["精英阶段"].blockSignals(False)
        default_skill_index = 0
        if "技能2" in data:
            default_skill_index = 2
        self.inputs["计算技能"].setCurrentIndex(default_skill_index)
        level_7_index = self.inputs["技能等级"].findText("7")
        if level_7_index != -1:
            self.inputs["技能等级"].setCurrentIndex(level_7_index)
        self.inputs["攻击间隔"].setText(data.get("攻击间隔", "N/A"))
        self.inputs["阻挡数"].setText(data.get("阻挡数", "N/A"))
        self.inputs["再部署时间"].setText(data.get("再部署时间", "N/A"))
        self.on_config_changed()

    def on_config_changed(self):
        self.update_level_range()
        self.update_talent_display()
        self.update_potential_display()
        self.update_deployment_cost()
        self.update_display_stats()

    def update_operator_list(self):
        self.operator_list_widget.setRowCount(0)
        for name, data in sorted(self.operators_data.items()):
            row_pos = self.operator_list_widget.rowCount()
            self.operator_list_widget.insertRow(row_pos)
            self.operator_list_widget.setItem(row_pos, 0, QTableWidgetItem(name))
            self.operator_list_widget.setItem(row_pos, 1, QTableWidgetItem(data.get("职业", "")))
            self.operator_list_widget.setItem(row_pos, 2, QTableWidgetItem(str(data.get("稀有度", ""))))

    def select_operator_in_list(self, name):
        for row in range(self.operator_list_widget.rowCount()):
            if self.operator_list_widget.item(row, 0).text() == name:
                self.operator_list_widget.setCurrentCell(row, 0)
                self.display_operator_data(self.operators_data[name])
                break

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
        unlocked_color = theme_dict['text']
        locked_color = theme_dict['button']
        elite_level = self.inputs["精英阶段"].currentIndex()
        full_talents = op_data.get("天赋", [])
        html_lines = []
        for talent in full_talents:
            condition = talent.get("条件", "").strip()
            unlocked = False
            if "精英2" in condition:
                if elite_level >= 2: unlocked = True
            elif "精英1" in condition:
                if elite_level >= 1: unlocked = True
            else: unlocked = True
            color = unlocked_color if unlocked else locked_color
            line = (f'<div style="color:{color}; margin-bottom: 5px;">'
                    f'<b>{talent.get("名称", "")}</b> (解锁: {condition})<br>'
                    f'{talent.get("描述", "")}'
                    f'</div>')
            html_lines.append(line)
        self.inputs["天赋描述"].setHtml("".join(html_lines))

    def update_potential_display(self):
        if not self.current_operator_name: return
        op_data = self.operators_data[self.current_operator_name]
        theme_dict = DARK_THEME if self.dark_mode else LIGHT_THEME
        unlocked_color = theme_dict['text']
        locked_color = theme_dict['button']
        selected_potential_level = self.inputs["潜能"].currentIndex() + 1
        html_lines = []
        all_potentials = op_data.get("潜能", [])
        for item in all_potentials:
            item_level = 1
            try:
                level_match = re.search(r'\d+', item.get('等级', ''))
                if level_match: item_level = int(level_match.group())
            except (AttributeError, ValueError): pass
            color = unlocked_color if item_level <= selected_potential_level else locked_color
            line = f'<b style="color:{color};">{item["等级"]}:</b> <span style="color:{color};">{item["描述"]}</span>'
            html_lines.append(line)
        self.inputs["潜能描述"].setHtml("<br>".join(html_lines))

    def update_deployment_cost(self):
        if not self.current_operator_name: return
        op_data = self.operators_data[self.current_operator_name]
        costs_str = op_data.get("cost_progression", "")
        costs = [int(c) for c in re.findall(r"\d+", costs_str)]
        elite = self.inputs["精英阶段"].currentIndex()
        pot = self.inputs["潜能"].currentIndex()
        if not costs: return
        base_cost = costs[min(elite, len(costs) - 1)]
        cost_reduction = 0
        potential_data = op_data.get("潜能", [])
        for i in range(pot):
            if i < len(potential_data):
                p_desc = potential_data[i].get("描述", "")
                if "部署费用" in p_desc: cost_reduction += 1
        self.inputs["初始费用"].setText(str(base_cost - cost_reduction))

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
        skill_data = op_data.get(f"技能{skill_num}")
        if not skill_data or "levels" not in skill_data: return
        level_text = self.inputs["技能等级"].currentText().replace("专精 ", "Rank ")
        level_info = skill_data["levels"].get(level_text, {})
        self.inputs[f"技能{skill_num}描述"].setPlainText(level_info.get("description", "无此等级数据"))
        self.inputs[f"技能{skill_num}初始"].setText(str(level_info.get("initial_sp", "")))
        self.inputs[f"技能{skill_num}消耗"].setText(str(level_info.get("sp_cost", "")))
        self.inputs[f"技能{skill_num}持续"].setText(str(level_info.get("duration", "")))
        self.inputs[f"技能{skill_num}回复"].setText(skill_data.get("回复类型", ""))
        self.inputs[f"技能{skill_num}触发"].setText(skill_data.get("触发类型", ""))

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