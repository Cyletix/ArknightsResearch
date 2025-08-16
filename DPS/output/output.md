### ui_styles.py
```
# ui_styles.py

DARK_THEME = {
    "background": "#1E1E2E",
    "panel": "#2E2E3E",
    "text": "#D8DEE9",
    "highlight": "#BD93F9",
    "button": "#44475A",
    "button_hover": "#6272A4",
    "input_bg": "#3E3E4E",
    "table_header": "#3E3E4E",
    "table_grid": "#4A4A5A",
}

LIGHT_THEME = {
    "background": "#F0F0FF",
    "panel": "#FFFFFF",
    "text": "#2E2E3E",
    "highlight": "#493D9E",
    "button": "#B2A5FF",
    "button_hover": "#8A78FF",
    "input_bg": "#EAEAF5",
    "table_header": "#EAEAF5",
    "table_grid": "#D0D0E0",
}


def get_stylesheet(theme):
    """根据主题字典生成QSS样式表字符串"""
    return f"""
        QMainWindow, QWidget {{ 
            background-color: {theme['background']}; 
            color: {theme['text']}; 
            font-family: 'Segoe UI', 'Microsoft YaHei', 'Arial'; 
            font-size: 15px; 
        }}
        #LeftPanel, #RightPanel {{ 
            background-color: {theme['panel']}; 
            border-radius: 8px; 
        }}
        QLabel {{ 
            background-color: transparent; 
        }}
        QPushButton {{ 
            background-color: {theme['button']}; 
            color: {theme['text']}; 
            border: none; 
            padding: 8px 16px; 
            border-radius: 8px; 
            font-size: 14px; 
        }}
        QPushButton:hover {{ 
            background-color: {theme['button_hover']}; 
        }}
        QPushButton:pressed {{ 
            background-color: {theme['highlight']}; 
        }}
        #CircularButton {{ 
            border-radius: 20px; 
            font-size: 18px; 
            padding: 0px; 
        }}
        QLineEdit, QSpinBox, QTextEdit, QComboBox {{ 
            background-color: {theme['input_bg']}; 
            color: {theme['text']}; 
            border: 1px solid {theme['button']}; 
            border-radius: 5px; 
            padding: 5px; 
        }}
        QLineEdit:focus, QSpinBox:focus, QTextEdit:focus, QComboBox:focus {{ 
            border-color: {theme['highlight']}; 
        }}
        QComboBox::drop-down {{ 
            border: none; 
        }} 
        QComboBox::down-arrow {{ 
            image: url(none); 
        }}
        QTableWidget {{ 
            background-color: {theme['input_bg']}; 
            border: 1px solid {theme['button']}; 
            gridline-color: {theme['table_grid']}; 
        }}
        QHeaderView::section {{ 
            background-color: {theme['table_header']}; 
            padding: 4px; 
            border: 1px solid {theme['table_grid']}; 
        }}
        #ScrollArea {{ 
            border: none; 
        }}
        QScrollBar:vertical {{ 
            border: none; 
            background: {theme['panel']}; 
            width: 10px; 
            margin: 0px; 
        }}
        QScrollBar::handle:vertical {{ 
            background: {theme['button']}; 
            min-height: 20px; 
            border-radius: 5px; 
        }}
        QScrollBar::handle:vertical:hover {{ 
            background: {theme['button_hover']}; 
        }}
    """

```

### main_ui.py
```
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
            
            # [新增] 获取当前选择的技能等级文本，并转换为接口格式
            skill_level_str = self.inputs["技能等级"].currentText().replace("专精 ", "Rank ")

            all_buffs = {}
            buff_prefixes = ["global", "talent"]
            if self.inputs["计算技能"].currentIndex() > 0:
                buff_prefixes.append(skill_choice)
            for prefix in buff_prefixes:
                if f"{prefix}_enable" in self.inputs and self.inputs[f"{prefix}_enable"].isChecked():
                    all_buffs[prefix] = self._collect_buffs_from_prefix(prefix)
            
            # [修改] 在调用计算器时，传入 skill_level_str
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
            widget = self.inputs[widget_key]
            if widget_type == QSpinBox:
                buffs[key_suffix] = widget.value()
            elif widget_type == QLineEdit:
                try:
                    buffs[key_suffix] = float(widget.text())
                except ValueError:
                    buffs[key_suffix] = default_val
        return buffs
    
    # def on_fetch_from_prts(self):
    #     op_input = self.prts_input.text().strip()
    #     if not op_input:
    #         self.drop_area.setText("请输入干员名称或PRTS页面链接。")
    #         return
    #     operator_name = self.logic.extract_name_from_input(op_input)
    #     if not operator_name:
    #         self.drop_area.setText("无法从输入中识别干员名称或链接。")
    #         return
    #     self.drop_area.setText(f"正在从PRTS获取“{operator_name}”的数据...")
    #     QApplication.processEvents()
    #     parsed_data = self.logic.fetch_operator_data(operator_name)
    #     self.process_and_display_data(parsed_data, f"https://m.prts.wiki/w/{operator_name}")
    # main_ui.py -> 找到并替换这个函数
    def on_fetch_from_prts(self):
        op_input = self.prts_input.text().strip()
        if not op_input:
            self.drop_area.setText("请输入干员名称或PRTS页面链接。")
            return

        # 1. [保持不变] 从输入框提取规范的干员名称
        operator_name = self.logic.extract_name_from_input(op_input)
        if not operator_name:
            self.drop_area.setText("无法从输入中识别干员名称或链接。")
            return
        
        self.drop_area.setText(f"正在从PRTS获取“{operator_name}”的页面HTML...")
        QApplication.processEvents() # 刷新UI显示

        # 2. [核心修改] 调用新的在线数据获取流程
        #    注意：这里我们直接调用 data_loader.py 中修改后的新逻辑
        #    这个新逻辑会获取HTML并使用 parse_html_prts 进行解析
        parsed_data = self.logic.fetch_operator_data_from_html(operator_name)
        
        # 3. [保持不变] 处理并显示返回的数据
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
        # self.inputs["再部署时间"].setText(data.get("再部署时间", "N/A")) # 不再直接设置原始文本，让 on_config_changed 去调用计算函数
        self.on_config_changed()

    def on_config_changed(self):
        self.update_level_range()
        self.update_talent_display()
        self.update_potential_display()
        self.update_deployment_cost()
        self.update_redeploy_time() # <--- 在此处调用
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

    # 根据潜能更新再部署时间
    def update_redeploy_time(self):
        if not self.current_operator_name:
            return
        op_data = self.operators_data[self.current_operator_name]

        # 1. 获取基础再部署时间并转换为数字
        base_redeploy_str = op_data.get("再部署时间", "0s")
        try:
            match = re.search(r'[\d\.]+', base_redeploy_str)
            base_redeploy_time = float(match.group()) if match else 0
        except (ValueError, AttributeError):
            base_redeploy_time = 0

        # 2. 计算潜能带来的再部署时间减少量
        redeploy_reduction = 0
        potential_data = op_data.get("潜能", [])
        # self.inputs["潜能"].currentIndex() -> 潜能1为0, 潜能2为1...
        # potential_data 列表 -> 索引0为潜能2效果, 索引1为潜能3效果...
        # 所以, 当选择潜能3(index 2)时, 循环需要检查 index 0 和 1
        pot_index = self.inputs["潜能"].currentIndex()
        for i in range(pot_index):
            if i < len(potential_data):
                desc = potential_data[i].get("描述", "")
                if "再部署时间" in desc:
                    reduction_match = re.search(r'-(\d+)', desc)
                    if reduction_match:
                        redeploy_reduction += int(reduction_match.group(1))

        # 3. 计算最终值并更新UI
        final_redeploy_time = base_redeploy_time - redeploy_reduction
        self.inputs["再部署时间"].setText(f"{final_redeploy_time:.0f}s")

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
        self.inputs[f"技能 {skill_num}初始"].setText(str(level_info.get("initial_sp", "")))
        self.inputs[f"技能 {skill_num}消耗"].setText(str(level_info.get("sp_cost", "")))
        self.inputs[f"技能 {skill_num}持续"].setText(str(level_info.get("duration", "")))
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
```

### ui_components.py
```
# ui_components.py
from PyQt5.QtWidgets import (
    QWidget,
    QGridLayout,
    QLabel,
    QLineEdit,
    QSpinBox,
    QComboBox,
    QCheckBox,
    QGroupBox,
)
from PyQt5.QtCore import Qt


class UIComponents:
    @staticmethod
    def create_grid_layout(parent, fields, fixed_width=None):
        grid = QGridLayout()
        grid.setHorizontalSpacing(15) 
        grid.setVerticalSpacing(10)
        parent.inputs = getattr(parent, "inputs", {})
        max_cols = max(len(row_fields) for row_fields in fields) if fields else 0
        for row, row_fields in enumerate(fields):
            for col, field_info in enumerate(row_fields):
                if not field_info:
                    continue
                label_text, key, widget_type, default_val, val_range = field_info
                label = QLabel(label_text)
                label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
                editor = widget_type()
                if widget_type == QLineEdit:
                    editor.setText(str(default_val))
                    if fixed_width:
                        editor.setFixedWidth(fixed_width)
                elif widget_type == QSpinBox:
                    if val_range:
                        editor.setRange(*val_range)
                    editor.setValue(default_val)
                    if fixed_width:
                        editor.setFixedWidth(fixed_width)
                elif widget_type == QComboBox:
                    if isinstance(default_val, list):
                        editor.addItems(default_val)
                elif widget_type == QCheckBox:
                    editor.setChecked(default_val)
                parent.inputs[key] = editor
                grid.addWidget(label, row, col * 2)
                grid.addWidget(editor, row, col * 2 + 1)
        grid.setColumnStretch(max_cols * 2, 1)
        return grid

    @staticmethod
    # 【关键修改】函数定义中增加了 event_filter 参数，以接收它
    def create_buff_panel(parent, prefix, title, event_filter=None):
        group_box = QGroupBox(title)
        group_box.setCheckable(True)
        parent.inputs[f"{prefix}_enable"] = group_box

        layout = QGridLayout(group_box)
        layout.setContentsMargins(10, 5, 10, 10)
        layout.setHorizontalSpacing(15)
        layout.setVerticalSpacing(8)

        fields = [
            (0, 0, "攻击力(+):", "direct_atk_flat", 0, (-2000, 5000)),
            (0, 2, "攻击力(%):", "direct_atk_pct", 0, (-100, 1000)),
            (1, 0, "防御力(+):", "direct_def_flat", 0, (-2000, 5000)),
            (1, 2, "防御力(%):", "direct_def_pct", 0, (-100, 1000)),
            (2, 0, "最终攻击(+):", "final_atk_flat", 0, (-2000, 5000)),
            (2, 2, "最终防御(+):", "final_def_flat", 0, (-2000, 5000)),
            (3, 0, "攻击速度(+):", "aspd", 0, (-100, 500)),
            (3, 2, "攻击间隔(-):", "interval", "0.0", None),
            (4, 0, "物理伤害倍率(%):", "phys_dmg_mult", 100, (0, 500)),
            (4, 2, "法术伤害倍率(%):", "arts_dmg_mult", 100, (0, 500)),
        ]

        for row, col, label_text, key_suffix, default, val_range in fields:
            label = QLabel(label_text)

            key = f"{prefix}_{key_suffix}"
            if isinstance(default, str):
                editor = QLineEdit(default)
                editor.setFixedWidth(80) 
            else:
                editor = QSpinBox()
                if val_range:
                    editor.setRange(*val_range)
                editor.setValue(default)
                editor.setFixedWidth(80)
                if event_filter:
                    editor.installEventFilter(event_filter)

            parent.inputs[key] = editor
            layout.addWidget(label, row, col)
            layout.addWidget(editor, row, col + 1)

        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(3, 1)
        return group_box
```

### tempCodeRunnerFile.py
```
技能 
```

### data_loader.py
```
# data_loader.py (恢复了本地解析功能的最终完整版)
import requests
import json
import re
from urllib.parse import unquote
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtCore import pyqtSignal
import os


def log_to_file(filename, content):
    """一个简单的日志记录函数，现在会记录所有关键步骤"""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    try:
        with open(os.path.join(log_dir, filename), "w", encoding="utf-8") as f:
            f.write(content)
        print(f"日志已保存到: {os.path.join(log_dir, filename)}")
    except Exception as e:
        print(f"写入日志失败: {e}")


class DraggableTextEdit(QTextEdit):
    fileDropped = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            e.acceptProposedAction()
        else:
            e.ignore()

    def dragMoveEvent(self, e):
        if e.mimeData().hasUrls():
            e.acceptProposedAction()
        else:
            e.ignore()

    def dropEvent(self, e):
        if e.mimeData().hasUrls():
            url = e.mimeData().urls()[0]
            if url.isLocalFile() and url.toLocalFile().endswith(".html"):
                self.fileDropped.emit(url.toLocalFile())
        else:
            e.ignore()


class DataLoader:
    def __init__(self):
        self.API_URL = "https://m.prts.wiki/api.php"

    def _cargo_query(self, params):
        base_params = {"action": "cargoquery", "format": "json", "limit": 500}
        # 增加一个模拟浏览器的headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        try:
            response = requests.get(
                self.API_URL, params={**base_params, **params}, timeout=10, headers=headers # 把headers加上
            )
            response.raise_for_status()
            return response.json().get("cargoquery", [])
        except requests.exceptions.RequestException as e:
            print(f"Cargo query failed: {e}")
            return None

    def _fetch_page_html(self, page_name):
        params = {
            "action": "parse",
            "page": page_name,
            "prop": "text",
            "format": "json",
        }
        try:
            response = requests.get(self.API_URL, params=params, timeout=10)
            response.raise_for_status()
            return response.json()["parse"]["text"]["*"]
        except (requests.exceptions.RequestException, KeyError) as e:
            print(f"从API获取HTML失败: {e}")
            return None

    def fetch_operator_data(self, operator_name):
        """[在线获取功能] 采用先获取charId再查询Cargo的稳健策略"""
        try:
            # 第1步：获取页面HTML
            html_content = self._fetch_page_html(operator_name)
            if not html_content:
                return {"error": "网络请求失败：无法获取页面HTML内容"}
            log_to_file(f"log_{operator_name}_1_page.html", html_content)

            # 第2步：从HTML中解析出charId
            soup = BeautifulSoup(html_content, "html.parser")
            spine_div = soup.find("div", id="spine-root")
            if not spine_div or "data-id" not in spine_div.attrs:
                return {"error": "解析失败：无法在页面中找到干员内部ID(charId)"}
            char_id = spine_div["data-id"]
            print(f"成功找到 {operator_name} 的 charId: {char_id}")

            # 第3步：使用charId进行精确的cargo查询
            op_data_list = self._cargo_query(
                {
                    "tables": "Operators",
                    "fields": "name, rarity, class, subClass, position, block, attackInterval, cost, cost_e1, cost_e2, redeploy, hp_i0_1, hp_i0_max, hp_i1_max, hp_i2_max, atk_i0_1, atk_i0_max, atk_i1_max, atk_i2_max, def_i0_1, def_i0_max, def_i1_max, def_i2_max, res_i0_1, res_i0_max, res_i1_max, res_i2_max, trustHp, trustAtk, trustDef",
                    "where": f"charId='{char_id}'",
                }
            )

            if not op_data_list:
                return {
                    "error": f"通过ID '{char_id}' 查询Cargo失败，请检查干员名称或网络"
                }

            log_to_file(
                f"log_{operator_name}_2_cargo_base.json",
                json.dumps(op_data_list, indent=2, ensure_ascii=False),
            )
            op_base = op_data_list[0]["title"]

            data = {
                "干员名称": op_base["name"],
                "稀有度": int(op_base["rarity"]) + 1,
                "职业": op_base["class"],
                "子职业": op_base["subClass"],
                "攻击间隔": f"{op_base['attackInterval']}s",
                "阻挡数": op_base["block"],
                "cost_progression": f"{op_base['cost']}→{op_base['cost_e1']}→{op_base.get('cost_e2', op_base['cost_e1'])}",
                "再部署时间": f"{op_base['redeploy']}s",
                "attributes": {
                    "hp": [
                        op_base["hp_i0_1"],
                        op_base["hp_i0_max"],
                        op_base["hp_i1_max"],
                        op_base["hp_i2_max"],
                    ],
                    "atk": [
                        op_base["atk_i0_1"],
                        op_base["atk_i0_max"],
                        op_base["atk_i1_max"],
                        op_base["atk_i2_max"],
                    ],
                    "def": [
                        op_base["def_i0_1"],
                        op_base["def_i0_max"],
                        op_base["def_i1_max"],
                        op_base["def_i2_max"],
                    ],
                    "res": [
                        op_base["res_i0_1"],
                        op_base["res_i0_max"],
                        op_base["res_i1_max"],
                        op_base["res_i2_max"],
                    ],
                },
                "trust_bonus": {
                    "hp": op_base.get("trustHp", "0"),
                    "atk": op_base.get("trustAtk", "0"),
                    "def": op_base.get("trustDef", "0"),
                },
            }

            potential_data = self._cargo_query(
                {
                    "tables": "Potentials",
                    "fields": "level, description",
                    "where": f"charId='{char_id}'",
                    "order_by": "level",
                }
            )
            data["潜能"] = [
                {
                    "等级": f"潜能{p['title']['level']}",
                    "描述": p["title"]["description"],
                }
                for p in potential_data
            ]

            talent_data = self._cargo_query(
                {
                    "tables": "Talents",
                    "fields": "talentName, unlock, description",
                    "where": f"charId='{char_id}'",
                }
            )
            data["天赋"] = [
                {
                    "名称": t["title"]["talentName"],
                    "条件": t["title"]["unlock"],
                    "描述": t["title"]["description"],
                }
                for t in talent_data
            ]

            skill_data_raw = self._cargo_query(
                {
                    "tables": "Skills",
                    "fields": "skillName, skillIndex, spType, trigger, levels",
                    "where": f"charId='{char_id}'",
                    "order_by": "skillIndex",
                }
            )
            log_to_file(
                f"log_{operator_name}_3_cargo_skills.json",
                json.dumps(skill_data_raw, indent=2, ensure_ascii=False),
            )

            for i, skill in enumerate(skill_data_raw):
                skill_info = skill["title"]
                levels_str = skill_info.get("levels", "[]")
                if not levels_str:
                    continue
                levels_data = json.loads(levels_str)
                level_map = {}
                for item in levels_data:
                    key = item["level"].replace("专精 ", "Rank ")
                    # [修改] 清理 duration 字段，只保留数字
                    duration_text = str(item.get("duration", ""))
                    duration_match = re.search(r'[\d\.]+', duration_text)
                    duration_val = duration_match.group() if duration_match else "0"

                    level_map[key] = {
                        "description": item.get("description", ""),
                        "sp_cost": item.get("spCost", ""),
                        "initial_sp": item.get("initialSp", ""),
                        "duration": duration_val,
                        **item.get("variables", {}),
                    }
                data[f"技能 {i+1}"] = {
                    "名称": skill_info["skillName"],
                    "回复类型": skill_info["spType"],
                    "触发类型": skill_info["trigger"],
                    "levels": level_map,
                }

            self._parse_html_for_fallback(html_content, data)
            log_to_file(
                f"log_{operator_name}_4_final_data.json",
                json.dumps(data, indent=2, ensure_ascii=False),
            )
            return data

        except Exception as e:
            import traceback

            traceback.print_exc()
            return {"error": f"处理在线数据时发生未知错误: {e}"}

# data_loader.py -> 找到 fetch_operator_data 函数，并用下面这两个函数替换它

    def fetch_operator_data_from_html(self, operator_name):
        """[新的在线获取功能] 采用稳定的HTML获取和解析策略"""
        try:
            # 第1步：使用稳定的 _fetch_page_html 获取页面内容
            html_content = self._fetch_page_html(operator_name)
            if not html_content:
                return {"error": "网络请求失败：无法获取页面HTML内容"}
            log_to_file(f"log_{operator_name}_1_page.html", html_content)

            # 第2步：直接调用我们修改好的 parse_html_prts 解析函数
            print("HTML获取成功，正在调用在线HTML解析器(parse_html_prts)...")
            parsed_data = self.parse_html_prts(html_content)
            
            # 第3步：返回解析结果
            return parsed_data

        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"error": f"处理在线数据时发生未知错误: {e}"}

    def fetch_operator_data_from_cargo(self, operator_name):
        """[原在线获取功能-备用] 采用先获取charId再查询Cargo的策略"""
        try:
            # 第1步：获取页面HTML
            html_content = self._fetch_page_html(operator_name)
            if not html_content:
                return {"error": "网络请求失败：无法获取页面HTML内容"}
            log_to_file(f"log_{operator_name}_1_page.html", html_content)

            # 第2步：从HTML中解析出charId
            soup = BeautifulSoup(html_content, "html.parser")
            spine_div = soup.find("div", id="spine-root")
            if not spine_div or "data-id" not in spine_div.attrs:
                return {"error": "解析失败：无法在页面中找到干员内部ID(charId)"}
            char_id = spine_div["data-id"]
            print(f"成功找到 {operator_name} 的 charId: {char_id}")

            # 第3步：使用charId进行精确的cargo查询 (此部分当前不稳定)
            op_data_list = self._cargo_query(
                {
                    "tables": "Operators",
                    "fields": "name, rarity, class, subClass, position, block, attackInterval, cost, cost_e1, cost_e2, redeploy, hp_i0_1, hp_i0_max, hp_i1_max, hp_i2_max, atk_i0_1, atk_i0_max, atk_i1_max, atk_i2_max, def_i0_1, def_i0_max, def_i1_max, def_i2_max, res_i0_1, res_i0_max, res_i1_max, res_i2_max, trustHp, trustAtk, trustDef",
                    "where": f"charId='{char_id}'",
                }
            )

            if not op_data_list:
                return {
                    "error": f"通过ID '{char_id}' 查询Cargo失败，请检查干员名称或网络"
                }

            # ... 此处省略原函数剩余的Cargo数据拼接逻辑 ...
            # 为了简洁，此处不再重复粘贴，原有的数据处理逻辑都应保留在此函数内

            op_base = op_data_list[0]["title"]
            data = {
                "干员名称": op_base["name"], "稀有度": int(op_base["rarity"]) + 1, "职业": op_base["class"],
                "子职业": op_base["subClass"], "攻击间隔": f"{op_base['attackInterval']}s", "阻挡数": op_base["block"],
                "cost_progression": f"{op_base['cost']}→{op_base['cost_e1']}→{op_base.get('cost_e2', op_base['cost_e1'])}",
                "再部署时间": f"{op_base['redeploy']}s",
                "attributes": {
                    "hp": [op_base["hp_i0_1"], op_base["hp_i0_max"], op_base["hp_i1_max"], op_base["hp_i2_max"]],
                    "atk": [op_base["atk_i0_1"], op_base["atk_i0_max"], op_base["atk_i1_max"], op_base["atk_i2_max"]],
                    "def": [op_base["def_i0_1"], op_base["def_i0_max"], op_base["def_i1_max"], op_base["def_i2_max"]],
                    "res": [op_base["res_i0_1"], op_base["res_i0_max"], op_base["res_i1_max"], op_base["res_i2_max"]],
                },
                "trust_bonus": {"hp": op_base.get("trustHp", "0"), "atk": op_base.get("trustAtk", "0"), "def": op_base.get("trustDef", "0"),},
            }
            # ... 其他潜能、天赋、技能的cargo查询和数据组装逻辑也应在此处 ...
            return data

        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"error": f"处理在线数据时发生未知错误: {e}"}

    def _parse_html_for_fallback(self, html_content, data):
        soup = BeautifulSoup(html_content, "html.parser")
        trait_header = soup.find("span", id="特性")
        if trait_header:
            trait_table = (
                trait_header.find_parent("h2")
                .find_next_sibling("section")
                .find("table")
            )
            if trait_table and len(trait_table.select("td")) > 1:
                data["特性-描述"] = trait_table.select("td")[1].text.strip()

    def extract_name_from_input(self, user_input):
        if "prts.wiki" in user_input:
            try:
                return unquote(user_input.split("/")[-1])
            except:
                return user_input.strip()
        return user_input.strip()

# data_loader.py -> 请用此函数完整替换旧的 parse_html 函数

    def parse_html(self, html_content):
        """[本地文件功能-最终修正版]
        此函数专门用于解析您手动保存的、结构完整的HTML文件。
        """
        soup = BeautifulSoup(html_content, "html.parser")
        data = {"attributes": {}, "trust_bonus": {}}
        try:
            # [兼容修改] 兼容移动版和桌面版的干员名称获取
            name_tag = soup.find("div", class_="charname") or soup.find("h1", id="firstHeading")
            if name_tag:
                data["干员名称"] = name_tag.text.strip()
            else:
                raise ValueError("未能找到干员名称")

            # [新增] 兼容移动版和桌面版的职业获取
            class_tag = soup.select_one(".charclass-img img")
            if class_tag and class_tag.get("src"):
                src = class_tag.get("src")
                if "近卫" in src: data["职业"] = "近卫"
                elif "狙击" in src: data["职业"] = "狙击"
                elif "重装" in src: data["职业"] = "重装"
                elif "医疗" in src: data["职业"] = "医疗"
                elif "辅助" in src: data["职业"] = "辅助"
                elif "术师" in src: data["职业"] = "术师"
                elif "先锋" in src: data["职业"] = "先锋"
                elif "特种" in src: data["职业"] = "特种"
            else:
                script_tag = soup.find("script", string=re.compile(r"var char_info"))
                if script_tag:
                    match = re.search(r'"class"\s*:\s*"([^"]+)"', script_tag.string)
                    if match:
                        data["职业"] = match.group(1)

            rarity_img = soup.select_one(".charstar img")
            if rarity_img and rarity_img.get("src"):
                rarity_text = rarity_img["src"].split("_")[-1].split(".")[0]
                data["稀有度"] = int(rarity_text) if rarity_text.isdigit() else 6

            attr_header = soup.find("span", id="属性")
            if attr_header:
                parent_h2 = attr_header.find_parent("h2")
                extra_attr_table = parent_h2.find_next("table", class_="char-extra-attr-table")
                if extra_attr_table:
                    th_map = {}
                    for row in extra_attr_table.find_all("tr"):
                        ths = row.find_all('th')
                        tds = row.find_all('td')
                        if len(ths) == len(tds) and len(ths) > 0:
                            for i in range(len(ths)):
                                th_map[ths[i].text.strip()] = tds[i].text.strip()
                    data["再部署时间"] = th_map.get("再部署时间", "")
                    data["cost_progression"] = th_map.get("初始部署费用", "")
                    data["阻挡数"] = th_map.get("阻挡数", "")
                    data["攻击间隔"] = th_map.get("攻击间隔", "")
                
                attr_table = parent_h2.find_next("table", class_="char-base-attr-table")
                if attr_table:
                    rows = attr_table.find("tbody").find_all("tr")
                    key_map = {"生命上限": "hp", "攻击": "atk", "防御": "def", "法术抗性": "res"}
                    for row in rows[1:]:
                        cols = row.find_all("td")
                        attr_name_th = row.find("th")
                        if not cols or not attr_name_th: continue
                        attr_name = attr_name_th.text.strip()
                        if attr_name in key_map:
                            attr_key = key_map[attr_name]
                            data["attributes"][attr_key] = [c.text.strip() for c in cols[:-1] if c.text.strip()]
                            trust_val = cols[-1].text.strip()
                            if trust_val:
                                data["trust_bonus"][attr_key] = trust_val
            
            self._parse_html_for_fallback(html_content, data)

            # [最终兼容性修正] 以下是针对天赋、潜能、技能的最终修正逻辑
            
            # --- 天赋解析 ---
            talent_header = soup.find("span", id="天赋")
            if talent_header:
                data["天赋"] = []
                current_element = talent_header.find_parent("h2")
                for sibling in current_element.find_next_siblings():
                    if sibling.name == 'h2': break
                    tables_to_check = []
                    if sibling.name == 'section': # 移动版：在section内部查找
                        tables_to_check = sibling.find_all('table', class_='wikitable')
                    elif sibling.name == 'table' and 'wikitable' in sibling.get('class', []): # 桌面版：本身就是table
                        tables_to_check.append(sibling)
                    
                    for table in tables_to_check:
                        for row in table.find_all("tr")[1:]:
                            cols = row.find_all("td")
                            if len(cols) >= 3 and "备注" not in row.text:
                                data["天赋"].append({"名称": cols[0].text.strip(), "条件": cols[1].text.strip(), "描述": " ".join(cols[2].text.strip().split())})

            # --- 潜能解析 ---
            potential_header = soup.find("span", id="潜能提升")
            if potential_header:
                data["潜能"] = []
                current_element = potential_header.find_parent("h2")
                
                # 潜能表格通常只有一个，逻辑可以简化
                search_area = current_element.find_next_sibling()
                if search_area:
                    potential_table = search_area if search_area.name == 'table' else search_area.find('table')
                    if potential_table:
                        for row in potential_table.find_all("tr"):
                            cols = row.find_all(["th", "td"])
                            if len(cols) == 2:
                                data["潜能"].append({"等级": cols[0].text.strip(), "描述": cols[1].text.strip()})

            # --- 技能解析 ---
            skill_header = soup.find("span", id="技能")
            if skill_header:
                current_element = skill_header.find_parent("h2")
                skill_tables = []
                for sibling in current_element.find_next_siblings():
                    if sibling.name == 'h2': break
                    if sibling.name == 'section': # 移动版
                        skill_tables.extend(sibling.find_all('table', class_='wikitable'))
                    elif sibling.name == 'table' and 'wikitable' in sibling.get('class', []): # 桌面版
                        skill_tables.append(sibling)
                
                for i, table in enumerate(skill_tables):
                    if i >= 3: break
                    skill_num = i + 1
                    skill_data = {}
                    header_row = table.find("tr")
                    if not header_row or not header_row.find("big"): continue
                    skill_data["名称"] = header_row.find("big").text.strip()
                    sp_info = header_row.text
                    skill_data["回复类型"] = ("受击回复" if "受击回复" in sp_info else "攻击回复" if "攻击回复" in sp_info else "自动回复")
                    skill_data["触发类型"] = ("自动触发" if "自动触发" in sp_info else "手动触发")
                    skill_levels = {}
                    for row in table.find_all("tr")[2:]:
                        cols = row.find_all(["th", "td"])
                        if len(cols) >= 5 and "备注" not in row.text:
                            level_text = cols[0].text.strip().replace("专精 ", "Rank ")

                            # [修改] 清理 duration 字段，只保留数字
                            duration_text = cols[4].text.strip()
                            duration_match = re.search(r'[\d\.]+', duration_text)
                            duration_val = duration_match.group() if duration_match else "0"

                            skill_levels[level_text] = { "description": " ".join(cols[1].text.strip().split()), "initial_sp": cols[2].text.strip(), "sp_cost": cols[3].text.strip(), "duration": duration_val }
                    skill_data["levels"] = skill_levels
                    data[f"技能 {skill_num}"] = skill_data

            return data
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"error": f"解析本地HTML文件时发生严重错误: {e}"}
        
# data_loader.py -> 替换此函数

    def parse_html_prts(self, html_content):
        """[在线解析最终修正版 V5]
        修正了属性表格的定位逻辑和稀有度的后备获取方案。
        """
        try:
            log_to_file("parser_input_content.html", html_content)
            soup = BeautifulSoup(html_content, "html.parser")
            data = {"attributes": {}, "trust_bonus": {}}

            # --- 基础信息解析 ---
            name_tag = soup.select_one(".pathnav2-right") or \
                       soup.find("div", class_="charname") or \
                       soup.find("h1", id="firstHeading")
            if name_tag:
                data["干员名称"] = name_tag.text.strip()
            else:
                raise ValueError("未能找到干员名称")

            script_tag = soup.find("script", string=re.compile(r"var char_info"))
            if script_tag:
                rarity_match = re.search(r'"star"\s*:\s*(\d+)', script_tag.string)
                if rarity_match:
                    data["稀有度"] = int(rarity_match.group(1)) + 1
                
                class_match = re.search(r'"class"\s*:\s*"([^"]+)"', script_tag.string)
                if class_match:
                    data["职业"] = class_match.group(1)

            # --- 属性解析 (已根据HTML文件结构进行最终修正) ---
            attr_header = soup.find("span", id="属性")
            if attr_header:
                parent_h2 = attr_header.find_parent("h2")
                
                # [核心修正] 查找h2的下一个兄弟节点，这个节点就是包含所有属性表格的<section>
                section_container = parent_h2.find_next_sibling("section")
                
                if section_container:
                    extra_attr_table = section_container.find("table", class_="char-extra-attr-table")
                    if extra_attr_table:
                        th_map = {th.text.strip(): td.text.strip() for th, td in zip(extra_attr_table.find_all("th"), extra_attr_table.find_all("td"))}
                        data["再部署时间"] = th_map.get("再部署时间", "")
                        data["cost_progression"] = th_map.get("初始部署费用", "")
                        data["阻挡数"] = th_map.get("阻挡数", "")
                        data["攻击间隔"] = th_map.get("攻击间隔", "")
                    
                    attr_table = section_container.find("table", class_="char-base-attr-table")
                    if attr_table:
                        rows = attr_table.find("tbody").find_all("tr")
                        key_map = {"生命上限": "hp", "攻击": "atk", "防御": "def", "法术抗性": "res"}
                        for row in rows[1:]:
                            cols = row.find_all("td")
                            attr_name_th = row.find("th")
                            if not cols or not attr_name_th: continue
                            
                            attr_name = attr_name_th.text.strip()
                            if attr_name in key_map:
                                attr_key = key_map[attr_name]
                                # 保留空字符串以维持列表结构
                                attr_values = [c.text.strip() for c in cols[:-1]]
                                data["attributes"][attr_key] = attr_values
                                
                                trust_val = cols[-1].text.strip()
                                if trust_val:
                                    data["trust_bonus"][attr_key] = trust_val
            
            # --- 其他解析部分保持不变 ---
            self._parse_html_for_fallback(html_content, data)
            talent_header = soup.find("span", id="天赋")
            if talent_header:
                data["天赋"] = []
                current_element = talent_header.find_parent("h2")
                for sibling in current_element.find_next_siblings():
                    if sibling.name == 'h2': break
                    tables_to_check = []
                    if sibling.name == 'section':
                        tables_to_check = sibling.find_all('table', class_='wikitable')
                    elif sibling.name == 'table' and 'wikitable' in sibling.get('class', []):
                        tables_to_check.append(sibling)
                    for table in tables_to_check:
                        for row in table.find_all("tr")[1:]:
                            cols = row.find_all("td")
                            if len(cols) >= 3:
                                description_text = " ".join(cols[2].get_text(strip=True).split())
                                data["天赋"].append({"名称": cols[0].text.strip(), "条件": cols[1].text.strip(), "描述": description_text})

            potential_header = soup.find("span", id="潜能提升")
            if potential_header:
                data["潜能"] = []
                current_element = potential_header.find_parent("h2")
                search_area = current_element.find_next_sibling()
                if search_area:
                    potential_table = search_area if search_area.name == 'table' else search_area.find('table')
                    if potential_table:
                        for row in potential_table.find_all("tr"):
                            cols = row.find_all(["th", "td"])
                            if len(cols) == 2:
                                data["潜能"].append({"等级": cols[0].text.strip(), "描述": cols[1].text.strip()})

            skill_header = soup.find("span", id="技能")
            if skill_header:
                current_element = skill_header.find_parent("h2")
                skill_tables = []
                for sibling in current_element.find_next_siblings():
                    if sibling.name == 'h2': break
                    if sibling.name == 'section':
                        skill_tables.extend(sibling.find_all('table', class_='wikitable'))
                    elif sibling.name == 'table' and 'wikitable' in sibling.get('class', []):
                        skill_tables.append(sibling)
                for i, table in enumerate(skill_tables):
                    if i >= 3: break
                    skill_num = i + 1
                    header_row = table.find("tr")
                    if not header_row or not header_row.find("big"): continue
                    skill_data = {}
                    skill_data["名称"] = header_row.find("big").text.strip()
                    sp_info_tags = header_row.find_all("span", class_="mc-tooltips")
                    sp_info = " ".join(tag.text for tag in sp_info_tags)
                    skill_data["回复类型"] = ("受击回复" if "受击回复" in sp_info else "攻击回复" if "攻击回复" in sp_info else "自动回复")
                    skill_data["触发类型"] = ("自动触发" if "自动触发" in sp_info else "手动触发")
                    skill_levels = {}
                    for row in table.find_all("tr")[2:]:
                        cols = row.find_all(["th", "td"])
                        if len(cols) >= 5 and "备注" not in row.text:
                            level_text = cols[0].text.strip().replace("专精 ", "Rank ")
                            duration_text = cols[4].text.strip()
                            duration_match = re.search(r'[\d\.]+', duration_text)
                            duration_val = duration_match.group() if duration_match else "0"
                            if '无限' in duration_text: duration_val = "无限"
                            skill_levels[level_text] = {
                                "description": " ".join(cols[1].get_text(strip=True).split()),
                                "initial_sp": cols[2].text.strip(),
                                "sp_cost": cols[3].text.strip(),
                                "duration": duration_val
                            }
                    skill_data["levels"] = skill_levels
                    data[f"技能 {skill_num}"] = skill_data
            
            return data
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"error": f"使用在线解析器(parse_html_prts)时发生错误: {e}"}
```

### dps_calculator.py
```
# dps_calculator.py (已更新)
import re


class DPSCalculator:
# dps_calculator.py -> 替换此函数

    def calculate_live_stats(self, op_data, elite, level, trust, potential, options):
        stats = {}
        key_map_rev = {"hp": "生命上限", "atk": "攻击力", "def": "防御"}
        
        # 确保稀有度已正确获取
        rarity = op_data.get("稀有度", 1)

        for attr in ["hp", "atk", "def"]:
            try:
                # 过滤掉空字符串，然后转换为整数
                attr_values_str = op_data.get("attributes", {}).get(attr, [])
                attr_values = [int(x) for x in attr_values_str if x]

                # [核心修正] 增加健壮性检查，防止列表索引越界
                if not attr_values or elite + 1 >= len(attr_values):
                    # 如果列表为空或索引超出范围，直接使用最后一个有效值
                    base_stat = attr_values[-1] if attr_values else 0
                else:
                    min_level_stat, max_level_stat = (
                        attr_values[elite],
                        attr_values[elite + 1],
                    )
                    level_caps = {
                        6: [50, 80, 90], 5: [50, 70, 80], 4: [45, 60, 70],
                        3: [40, 55, 70], 2: [30, 55], 1: [30]
                    }
                    caps = level_caps.get(rarity, [30])
                    # 再次检查精英等级是否有效
                    if elite >= len(caps):
                        base_stat = max_level_stat
                    else:
                        max_level_for_elite = caps[elite]
                        if level == 1:
                            base_stat = min_level_stat
                        elif level >= max_level_for_elite:
                            base_stat = max_level_stat
                        else:
                            base_stat = round(
                                min_level_stat
                                + (max_level_stat - min_level_stat)
                                * (level - 1)
                                / (max_level_for_elite - 1)
                            )

                if options.get("calc_trust"):
                    trust_bonus_str = op_data.get("trust_bonus", {}).get(attr, "0")
                    trust_bonus = int(trust_bonus_str) if trust_bonus_str else 0
                    base_stat += trust_bonus * (trust / 100)
                
                if options.get("calc_potential"):
                    potential_bonuses = op_data.get("潜能", [])
                    for i in range(potential - 1):
                        if i < len(potential_bonuses):
                            desc = potential_bonuses[i]["描述"]
                            if key_map_rev.get(attr) in desc and "+" in desc:
                                bonus_match = re.search(r"\+(\d+)", desc)
                                if bonus_match:
                                    base_stat += int(bonus_match.group(1))
                
                stats[attr] = round(base_stat)
            except (IndexError, ValueError, TypeError) as e:
                print(f"Error calculating base stat for {attr}: {e}")
                stats[attr] = 0
        
        try:
            res_values_str = op_data.get("attributes", {}).get("res", [])
            res_values = [int(x) for x in res_values_str if x]
            if not res_values or elite + 1 >= len(res_values):
                 stats["res"] = res_values[-1] if res_values else 0
            else:
                 stats["res"] = res_values[elite + 1]
        except (ValueError, IndexError):
            stats["res"] = 0

        return stats

    def calculate_dps(self, op_data, live_stats, skill_choice, skill_level_str, enemy_stats, all_buffs):
        """
        [REWRITTEN] 遵循PRTS公式重写的核心DPS计算函数
        """
        # 1. 初始属性
        base_atk = live_stats.get("atk", 0)
        base_atk_interval = float(op_data.get("攻击间隔", "1").replace("s", ""))
        enemy_def = enemy_stats.get("def", 0)
        enemy_res = enemy_stats.get("res", 0)

        # 2. 汇总所有来源的Buff
        # 【BUG修复】在此处补全所有可能从UI传入的键，以防止KeyError
        total_buffs = {
            "direct_atk_flat": 0,
            "direct_atk_pct": 0,
            "final_atk_flat": 0,
            "direct_def_flat": 0,   # 补全
            "direct_def_pct": 0,    # 补全
            "final_def_flat": 0,    # 补全
            "aspd": 0,
            "interval": 0.0,
            "phys_dmg_mult": 1.0,
            "arts_dmg_mult": 1.0,
        }
        
        for buff_source in all_buffs.values():
            for key, value in buff_source.items():
                if "mult" in key:  # 伤害倍率是乘算
                    total_buffs[key] *= value / 100.0
                else:  # 其他是加算
                    total_buffs[key] += value

        # 3. 应用属性基本公式计算最终攻击力
        # Af = Ft * [(A + Dp) * (1 + Dt) + Fp]
        # 注: 此处简化了Ft(最终乘算)，因为它极少见且通常用于debuff。
        # A (基础攻击力)
        A = base_atk
        # Dp (直接加算)
        Dp = total_buffs["direct_atk_flat"]
        # Dt (直接乘算)
        Dt = total_buffs["direct_atk_pct"] / 100.0
        # Fp (最终加算 / 鼓舞)
        Fp = total_buffs["final_atk_flat"]

        final_atk = (A + Dp) * (1 + Dt) + Fp

        # 4. 计算最终攻击间隔 (攻速公式)
        # T = T0 / (CLAMP(S, 10, 600) / 100)
        S = 100 + total_buffs["aspd"]
        clamped_aspd = min(max(S, 10), 600)
        T0 = base_atk_interval - total_buffs["interval"]
        actual_atk_interval = (
            T0 / (clamped_aspd / 100.0) if clamped_aspd > 0 else float("inf")
        )

        # 5. 计算单次伤害 (伤害公式)
        damage_type = "法术" if "法术伤害" in op_data.get("特性-描述", "") else "物理"

        base_phys_damage = 0
        base_arts_damage = 0

        if damage_type == "物理":
            base_phys_damage = max(final_atk - enemy_def, final_atk * 0.05)
        else:  # 法术
            base_arts_damage = final_atk * max(0, (100 - enemy_res) / 100.0)

        final_phys_damage = base_phys_damage * total_buffs["phys_dmg_mult"]
        final_arts_damage = base_arts_damage * total_buffs["arts_dmg_mult"]

        total_damage_per_hit = final_phys_damage + final_arts_damage

        # 6. 计算最终DPS
        dps = (
            total_damage_per_hit / actual_atk_interval
            if actual_atk_interval > 0
            else float("inf")
        )

        # 7. 格式化输出
        result_text = f"--- {skill_choice} ---\n"
        result_text += f"基础攻击力: {A:.0f}\n"
        result_text += f"总直接加算(Dp): +{Dp}, 总直接乘算(Dt): +{Dt*100:.0f}%\n"
        result_text += f"总最终加算(Fp): +{Fp} (鼓舞)\n"
        result_text += f"最终攻击力: {final_atk:.1f}\n"
        result_text += "----\n"
        result_text += f"最终攻击速度: {clamped_aspd:.0f}\n"
        result_text += f"最终攻击间隔: {actual_atk_interval:.3f}s\n"
        result_text += "----\n"
        result_text += f"伤害类型: {damage_type}\n"
        result_text += f"物理/法术伤害倍率: {total_buffs['phys_dmg_mult']:.2f} / {total_buffs['arts_dmg_mult']:.2f}\n"
        result_text += (
            f"Damage Per Hit (对 {enemy_def}防 {enemy_res}抗): {total_damage_per_hit:.1f}\n"
        )
        result_text += f"Damage Per Second: {dps:.1f}\n"

        # [新增] 计算技能总伤害的逻辑
        total_damage_text = ""
        # 检查是否在计算技能 (而不是普攻)
        if skill_choice != "普攻":
            skill_data = op_data.get(skill_choice, {})
            level_info = skill_data.get("levels", {}).get(skill_level_str, {})
            
            try:
                # 尝试获取技能持续时间
                duration = float(level_info.get("duration", 0))
            except (ValueError, TypeError):
                duration = 0.0

            # 仅当持续时间大于0时才计算总伤害
            if duration > 0 and actual_atk_interval > 0:
                num_hits = duration / actual_atk_interval
                total_skill_damage = total_damage_per_hit * num_hits
                total_damage_text = f"技能总伤害 ({duration:.1f}s): {total_skill_damage:.0f}\n"

        # 将总伤害文本追加到最终结果
        result_text += total_damage_text
        return result_text
```

