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