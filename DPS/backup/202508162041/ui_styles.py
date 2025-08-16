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
