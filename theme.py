"""
StatReg — Tema ve Stil Sistemi
Temiz, Apple-Tarzı Profesyonel Sidebar Düzeni.
"""

from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt


class Colors:
    # Arka Planlar
    BG_WINDOW = "#F8FAFC"
    BG_SIDEBAR = "#FFFFFF"
    BG_CARD = "#FFFFFF"
    BG_SECTION = "#F8FAFC"
    BG_CARD_HOVER = "#F1F5F9"
    BG_INPUT = "#FFFFFF"

    # Aksan Renkleri
    ACCENT_PRIMARY = "#4F46E5"
    ACCENT_PRIMARY_HOVER = "#4338CA"
    ACCENT_PRIMARY_LIGHT = "#EEF2FF"
    ACCENT_PRIMARY_BORDER = "#818CF8"

    # Durum Renkleri
    SUCCESS_BG = "#ECFDF5"
    SUCCESS_BORDER = "#A7F3D0"
    SUCCESS_TEXT = "#047857"

    DANGER_BG = "#FEF2F2"
    DANGER_BORDER = "#FECDD3"
    DANGER_TEXT = "#B91C1C"

    # Metin Renkleri
    TEXT_PRIMARY = "#0F172A"
    TEXT_SECONDARY = "#475569"
    TEXT_MUTED = "#94A3B8"
    TEXT_ON_ACCENT = "#FFFFFF"

    # Çerçeveler
    BORDER_LIGHT = "#F1F5F9"
    BORDER = "#E2E8F0"
    BORDER_STRONG = "#CBD5E1"
    BORDER_ACCENT = "#818CF8"

    # Tablo
    TABLE_ROW_ALT = "#FAFAFC"
    TABLE_ROW_HOVER = "#EEF2FF"
    TABLE_HEADER_BG = "#F8FAFC"
    TABLE_SELECTION = "#E0E7FF"
    TABLE_GRID = "#E2E8F0"


FONT_FAMILY = '-apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", Roboto, sans-serif'
FONT_FAMILY_MONO = '"SF Mono", "Cascadia Code", "Consolas", monospace'


def setup_light_palette(app):
    app.setStyle("Fusion")

    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#F8FAFC"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#0F172A"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#FFFFFF"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#FAFAFC"))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#0F172A"))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#FFFFFF"))
    palette.setColor(QPalette.ColorRole.Text, QColor("#0F172A"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#FFFFFF"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#0F172A"))
    palette.setColor(QPalette.ColorRole.BrightText, QColor("#FFFFFF"))
    palette.setColor(QPalette.ColorRole.Link, QColor("#4F46E5"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#4F46E5"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))

    app.setPalette(palette)


def get_stylesheet() -> str:
    return f"""
    * {{
        font-family: {FONT_FAMILY};
        font-size: 13px;
        color: {Colors.TEXT_PRIMARY};
        outline: none;
    }}

    QMainWindow, QDialog {{
        background-color: #F8FAFC !important;
    }}

    QWidget {{
        background-color: #F8FAFC;
    }}

    QToolTip {{
        background-color: #0F172A;
        color: #FFFFFF;
        border: none;
        border-radius: 6px;
        padding: 6px 10px;
        font-size: 12px;
    }}

    /* --- SCROLLBAR (Ultra İnce 4px, Kavisli ve Kesişim Karesiz) --- */
    QScrollBar:vertical {{
        background: transparent !important;
        width: 4px !important;
        margin: 0px !important;
        border: none !important;
    }}

    QScrollBar::handle:vertical {{
        background: #CBD5E1 !important;
        min-height: 24px !important;
        border-radius: 2px !important;
    }}

    QScrollBar::handle:vertical:hover {{
        background: #94A3B8 !important;
    }}

    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
        background: none !important;
        height: 0px !important;
        width: 0px !important;
    }}

    QScrollBar:horizontal {{
        background: transparent !important;
        height: 4px !important;
        margin: 0px !important;
        border: none !important;
    }}

    QScrollBar::handle:horizontal {{
        background: #CBD5E1 !important;
        min-width: 24px !important;
        border-radius: 2px !important;
    }}

    QScrollBar::handle:horizontal:hover {{
        background: #94A3B8 !important;
    }}

    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal,
    QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
        background: none !important;
        height: 0px !important;
        width: 0px !important;
    }}

    /* Scroll Kesişim Köşesindeki Kare Kutusunu Kaldırma */
    QAbstractScrollArea::corner {{
        background: transparent !important;
        border: none !important;
    }}

    /* --- Sol Yan Panel (Sidebar) --- */
    QFrame#sidebar_frame {{
        background-color: #FFFFFF !important;
        border-right: 1px solid {Colors.BORDER};
    }}

    QFrame#sidebar_frame QWidget {{
        background-color: transparent;
    }}

    QLabel#sidebar_logo {{
        font-size: 22px;
        font-weight: 800;
        color: {Colors.ACCENT_PRIMARY};
        letter-spacing: -0.5px;
    }}

    QLabel#sidebar_subtitle {{
        font-size: 11px;
        font-weight: 500;
        color: {Colors.TEXT_MUTED};
        letter-spacing: 0.4px;
    }}

    /* Sidebar Bölüm Başlığı */
    QLabel#sidebar_section_title {{
        font-size: 10px;
        font-weight: 700;
        color: {Colors.TEXT_MUTED};
        letter-spacing: 1px;
    }}

    /* Sidebar Açıklama Metni */
    QLabel#sidebar_desc {{
        font-size: 11px;
        font-weight: 400;
        color: {Colors.TEXT_SECONDARY};
    }}

    /* Sidebar Alt Başlık (Satır/Sütun) */
    QLabel#sidebar_sub_title {{
        font-size: 12px;
        font-weight: 600;
        color: {Colors.TEXT_PRIMARY};
    }}

    /* --- Standart Butonlar --- */
    QPushButton {{
        background-color: #FFFFFF !important;
        color: {Colors.TEXT_PRIMARY} !important;
        border: 1px solid {Colors.BORDER};
        border-radius: 7px;
        padding: 8px 14px;
        font-size: 12px;
        font-weight: 500;
        text-align: center;
    }}

    QPushButton:hover {{
        background-color: {Colors.BG_CARD_HOVER} !important;
        border-color: {Colors.BORDER_STRONG};
    }}

    QPushButton:pressed {{
        background-color: {Colors.BORDER_LIGHT} !important;
    }}

    QPushButton#danger_button {{
        background-color: #FFFFFF !important;
        color: {Colors.DANGER_TEXT} !important;
        border: 1px solid {Colors.DANGER_BORDER};
    }}

    QPushButton#danger_button:hover {{
        background-color: {Colors.DANGER_BG} !important;
        border-color: {Colors.DANGER_BORDER};
    }}

    /* --- Sayfa Kapsayıcı Çerçeveleri (25px Radius) --- */
    QFrame#page_container {{
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0;
        border-radius: 25px;
    }}

    QFrame#page_container QWidget {{
        background-color: transparent;
        border-radius: 0px;
    }}

    QTabWidget {{
        background-color: #F8FAFC !important;
    }}

    QTabWidget::tab-bar {{
        alignment: center;
    }}

    QTabWidget::pane {{
        background-color: transparent !important;
        border: none;
        top: 6px;
    }}

    QTabBar {{
        background-color: transparent !important;
        qproperty-drawBase: 0;
    }}

    /* --- QTabBar (Kesişim Çizgisiz Mor - Beyaz Sekmeler) --- */
    QTabBar::tab {{
        background-color: #FFFFFF !important;
        color: #4F46E5 !important;
        border: 1px solid #C7D2FE;
        border-bottom: none !important;
        border-top-left-radius: 8px !important;
        border-top-right-radius: 8px !important;
        border-bottom-left-radius: 0px !important;
        border-bottom-right-radius: 0px !important;
        padding: 8px 22px;
        margin-right: 4px;
        font-size: 12.5px;
        font-weight: 600;
        min-width: 120px;
        text-align: center;
    }}

    QTabBar::tab:hover {{
        background-color: #EEF2FF !important;
        color: #4338CA !important;
        border: 1px solid #818CF8;
        border-bottom: none !important;
    }}

    QTabBar::tab:selected {{
        background-color: #4F46E5 !important;
        color: #FFFFFF !important;
        font-weight: 600;
        border: 1px solid #4338CA;
        border-bottom: none !important;
        margin-bottom: -1px !important;
    }}

    /* QTabBar Kaydırma Oklarını Tamamen Gizleme */
    QTabBar::scroller {{
        width: 0px !important;
        height: 0px !important;
    }}
    QTabBar QToolButton {{
        width: 0px !important;
        height: 0px !important;
        background: transparent !important;
        border: none !important;
    }}

    /* --- VERİ TABLOSU --- */
    QTableWidget {{
        background-color: #FFFFFF !important;
        alternate-background-color: {Colors.TABLE_ROW_ALT} !important;
        gridline-color: {Colors.TABLE_GRID};
        border: none !important;
        border-radius: 0px !important;
        selection-background-color: {Colors.TABLE_SELECTION} !important;
        selection-color: {Colors.TEXT_PRIMARY} !important;
        font-size: 13px;
    }}

    QTableWidget::item {{
        padding: 6px 12px;
        border: none;
        background-color: transparent;
        color: {Colors.TEXT_PRIMARY} !important;
    }}

    QTableWidget::item:hover {{
        background-color: {Colors.TABLE_ROW_HOVER} !important;
    }}

    QTableWidget::item:selected {{
        background-color: {Colors.TABLE_SELECTION} !important;
        color: {Colors.ACCENT_PRIMARY} !important;
        font-weight: 600;
    }}

    QHeaderView {{
        background-color: #F8FAFC !important;
    }}

    QHeaderView::section {{
        background-color: #F8FAFC !important;
        color: {Colors.TEXT_SECONDARY} !important;
        border: none;
        border-right: 1px solid {Colors.BORDER};
        border-bottom: 1px solid {Colors.BORDER};
        padding: 9px 12px;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 0.3px;
    }}

    QHeaderView::section:hover {{
        background-color: #F1F5F9 !important;
        color: {Colors.TEXT_PRIMARY} !important;
    }}

    QTableCornerButton::section {{
        background-color: #F8FAFC !important;
        border: none;
        border-right: 1px solid {Colors.BORDER};
        border-bottom: 1px solid {Colors.BORDER};
    }}

    /* --- İç Kart Çerçeveleri (İç Border Yok - Soft Görünüm) --- */
    QFrame#card_frame {{
        background-color: #F8FAFC !important;
        border: none !important;
        border-radius: 10px;
        padding: 14px 18px;
    }}

    /* --- SONUÇ TABLOLARI (İç Border Yoksayıldı - Soft Görünüm) --- */
    QTableWidget#result_table {{
        background-color: #FFFFFF !important;
        alternate-background-color: #F8FAFC !important;
        gridline-color: #F1F5F9;
        border: none !important;
        border-radius: 0px !important;
        font-size: 13px;
    }}

    QTableWidget#result_table QHeaderView::section {{
        background-color: #F1F5F9 !important;
        color: #334155 !important;
        font-weight: 700;
        border: none;
        border-bottom: 1px solid #CBD5E1;
        padding: 8px 12px;
    }}

    /* --- METRİK KARTLARI --- */
    QLabel#section_title {{
        font-size: 16px;
        font-weight: 700;
        color: {Colors.TEXT_PRIMARY} !important;
        padding: 2px 0px;
    }}

    QLabel#section_subtitle {{
        font-size: 12px;
        font-weight: 400;
        color: {Colors.TEXT_SECONDARY} !important;
    }}

    QLabel#stat_value {{
        font-size: 22px;
        font-weight: 700;
        color: {Colors.ACCENT_PRIMARY} !important;
        font-family: {FONT_FAMILY_MONO};
    }}

    QLabel#stat_label {{
        font-size: 11px;
        font-weight: 600;
        color: {Colors.TEXT_MUTED} !important;
        letter-spacing: 0.5px;
    }}

    /* --- ALT STATUS BAR --- */
    QStatusBar {{
        background-color: #FFFFFF !important;
        border-top: 1px solid {Colors.BORDER};
        min-height: 28px;
        padding: 4px 20px;
    }}

    QStatusBar QLabel {{
        color: #94A3B8 !important;
        font-size: 11px;
        font-weight: 500;
        padding: 2px 8px;
        background-color: transparent !important;
    }}
    """


def apply_pyqtgraph_theme():
    import pyqtgraph as pg

    pg.setConfigOptions(
        antialias=True,
        background="#FFFFFF",
        foreground="#475569",
    )


def style_plot_widget(plot_widget):
    import pyqtgraph as pg
    from PyQt6.QtGui import QFont

    plot_widget.setBackground("#FFFFFF")
    plot_widget.showGrid(x=True, y=True, alpha=0.18)

    tick_font = QFont("Inter", 10, QFont.Weight.DemiBold)

    for axis_name in ['bottom', 'left']:
        axis = plot_widget.getAxis(axis_name)
        axis.setPen(pg.mkPen("#CBD5E1", width=1.5))
        axis.setTextPen(pg.mkPen("#475569"))
        axis.setTickFont(tick_font)
        axis.setStyle(tickLength=-6, tickTextOffset=14)

    plot_widget.getViewBox().setBorder(pg.mkPen("#E2E8F0", width=1.5))
