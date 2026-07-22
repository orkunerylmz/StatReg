"""
StatReg — İstatistiksel Regresyon Analiz Uygulaması
Yüksek Estetikli Alt-Kart Yapısında Tablo Düzenleme Araçları.
"""

import sys
import os
import pyqtgraph as pg
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QTabWidget, QPushButton, QLabel,
    QFileDialog, QMessageBox, QSplitter, QScrollArea, QHeaderView,
    QFrame, QGroupBox, QListWidget, QDialog, QStatusBar, QGridLayout,
    QAbstractItemView, QGraphicsBlurEffect, QInputDialog, QLineEdit,
)
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt
import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import f

from theme import (
    Colors, get_stylesheet, apply_pyqtgraph_theme,
    style_plot_widget, setup_light_palette, FONT_FAMILY_MONO
)


# --- Bileşenler ------------------------------------------------------------------

class StatCard(QFrame):
    """Metrik / İstatistik Kartı."""
    def __init__(self, label: str, value: str, parent=None):
        super().__init__(parent)
        self.setObjectName("card_frame")
        self.setMinimumWidth(140)

        layout = QVBoxLayout(self)
        layout.setSpacing(4)
        layout.setContentsMargins(16, 12, 16, 12)

        self.name_label = QLabel(label.upper())
        self.name_label.setObjectName("stat_label")
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        self.value_label = QLabel(value)
        self.value_label.setObjectName("stat_value")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        layout.addWidget(self.name_label)
        layout.addWidget(self.value_label)


class SectionHeader(QWidget):
    """Bölüm Başlığı ve Alt Açıklaması."""
    def __init__(self, title: str, subtitle: str = "", parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 6)
        layout.setSpacing(2)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("section_title")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self.title_label)

        if subtitle:
            self.subtitle_label = QLabel(subtitle)
            self.subtitle_label.setObjectName("section_subtitle")
            self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            layout.addWidget(self.subtitle_label)


from PyQt6.QtGui import QPainter, QBrush, QPen, QPixmap

class EmptyStateCard(QFrame):
    """Beyaz sayfa zemininde öne çıkan, ferah ve net standart uyarı kartı."""
    def __init__(self, title: str, description: str, parent=None):
        super().__init__(parent)
        self.setFixedSize(580, 200)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #F8FAFC;
                border: 1px solid #E2E8F0;
                border-radius: 16px;
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(14)
        layout.setContentsMargins(48, 40, 48, 40)

        # Başlık (Silik ve Resmi Slate 600)
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            font-size: 16px;
            font-weight: 600;
            color: #475569;
            background: transparent;
            border: none;
            letter-spacing: -0.1px;
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Açıklama Metni (Silik Slate 400)
        desc_label = QLabel(description)
        desc_label.setStyleSheet(f"""
            font-size: 13px;
            color: #94A3B8;
            background: transparent;
            border: none;
            line-height: 1.5;
        """)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)


# --- Ana Pencere -----------------------------------------------------------------

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.df = pd.DataFrame()
        self.loaded_file_name = ""
        self.analysis_count = 0

        self._init_window()
        self._init_statusbar()
        self._init_ui()

    def _init_window(self):
        self.setWindowTitle("StatReg — İstatistiksel Regresyon Analizi")
        self.setMinimumSize(1240, 780)
        self.resize(1300, 820)

    def _init_statusbar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.status_rows_label = QLabel("Satır: 30")
        self.status_cols_label = QLabel("Sütun: 15")
        self.status_file_label = QLabel("Dosya: Yüklenmedi")
        self.status_analysis_label = QLabel("Durum: Hazır")

        self.status_bar.addWidget(self.status_rows_label)
        self.status_bar.addWidget(self._status_sep())
        self.status_bar.addWidget(self.status_cols_label)
        self.status_bar.addWidget(self._status_sep())
        self.status_bar.addWidget(self.status_file_label)
        self.status_bar.addPermanentWidget(self.status_analysis_label)

    def _status_sep(self):
        sep = QLabel("•")
        sep.setStyleSheet("color: #CBD5E1; font-size: 10px; padding: 0 6px;")
        return sep

    def _update_status(self):
        filled_df = self._get_dataframe_from_table()
        filled_rows = filled_df.shape[0] if not filled_df.empty else 0
        filled_cols = filled_df.shape[1] if not filled_df.empty else 0

        if filled_rows > 0:
            self.status_rows_label.setText(f"Dolu Satır: {filled_rows}")
            self.status_cols_label.setText(f"Dolu Sütun: {filled_cols}")
        else:
            self.status_rows_label.setText(f"Satır: {self.table.rowCount()}")
            self.status_cols_label.setText(f"Sütun: {self.table.columnCount()}")

        if self.loaded_file_name:
            self.status_file_label.setText(f"Dosya: {self.loaded_file_name}")
        else:
            self.status_file_label.setText("Dosya: Manuel Giriş")

    # -- Yardımcı Metodlar -------------------------------------------------------

    def _add_sidebar_divider(self, layout):
        """Sidebar bölümleri arasına ince ayraç çizgisi ekler."""
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #F0F2F5; max-height: 1px; margin: 0px;")
        layout.addWidget(line)

    # -- Arayüz Düzeni -----------------------------------------------------------

    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ------------------------------------------------------------------------
        # 1. SOL YAN PANEL (SIDEBAR - 350px, Temiz Düz Bölüm Tasarımı)
        # ------------------------------------------------------------------------
        sidebar_container = QFrame()
        sidebar_container.setObjectName("sidebar_frame")
        sidebar_container.setFixedWidth(350)

        sidebar_scroll = QScrollArea(sidebar_container)
        sidebar_scroll.setWidgetResizable(True)
        sidebar_scroll.setFrameShape(QFrame.Shape.NoFrame)
        sidebar_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        sidebar_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        sidebar_content = QWidget()
        sidebar_layout = QVBoxLayout(sidebar_content)
        sidebar_layout.setContentsMargins(24, 28, 24, 28)
        sidebar_layout.setSpacing(0)

        # ── Logo & Başlık ──
        logo_label = QLabel("StatReg")
        logo_label.setObjectName("sidebar_logo")
        sidebar_layout.addWidget(logo_label)

        sidebar_layout.addSpacing(2)

        sub_label = QLabel("İstatistiksel Regresyon Analizi")
        sub_label.setObjectName("sidebar_subtitle")
        sidebar_layout.addWidget(sub_label)

        sidebar_layout.addSpacing(24)

        # ═══════════════════════════════════════════════════════
        # BÖLÜM 1 — VERİ İÇE AKTARMA
        # ═══════════════════════════════════════════════════════
        lbl_s1 = QLabel("VERİ İÇE AKTARMA")
        lbl_s1.setObjectName("sidebar_section_title")
        sidebar_layout.addWidget(lbl_s1)

        sidebar_layout.addSpacing(8)

        lbl_s1_desc = QLabel(
            "Bilgisayarınızdan CSV veya Excel formatında\n"
            "veri seti yükleyin."
        )
        lbl_s1_desc.setObjectName("sidebar_desc")
        lbl_s1_desc.setWordWrap(True)
        sidebar_layout.addWidget(lbl_s1_desc)

        sidebar_layout.addSpacing(10)

        btn_load = QPushButton("Dosya Yükle")
        btn_load.setToolTip("CSV, XLSX veya XLS dosyası seçin")
        btn_load.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_load.setStyleSheet("""
            QPushButton {
                background-color: #EEF2FF !important;
                color: #4F46E5 !important;
                border: 1px solid #C7D2FE;
                border-radius: 7px;
                font-weight: 600;
                padding: 10px 16px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #E0E7FF !important;
                border-color: #818CF8;
            }
            QPushButton:pressed {
                background-color: #C7D2FE !important;
            }
        """)
        btn_load.clicked.connect(self.load_file)
        sidebar_layout.addWidget(btn_load)

        # ── Ayraç ──
        sidebar_layout.addSpacing(20)
        self._add_sidebar_divider(sidebar_layout)
        sidebar_layout.addSpacing(20)

        # ═══════════════════════════════════════════════════════
        # BÖLÜM 2 — REGRESYON ANALİZİ
        # ═══════════════════════════════════════════════════════
        lbl_s2 = QLabel("REGRESYON ANALİZİ")
        lbl_s2.setObjectName("sidebar_section_title")
        sidebar_layout.addWidget(lbl_s2)

        sidebar_layout.addSpacing(8)

        lbl_s2_desc = QLabel(
            "Bağımlı (Y) ve bağımsız (X) değişkenleri\n"
            "belirleyerek model oluşturun."
        )
        lbl_s2_desc.setObjectName("sidebar_desc")
        lbl_s2_desc.setWordWrap(True)
        sidebar_layout.addWidget(lbl_s2_desc)

        sidebar_layout.addSpacing(10)

        btn_regress = QPushButton("Analizi Başlat")
        btn_regress.setToolTip("Doğrusal regresyon modelini çalıştırın")
        btn_regress.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_regress.setStyleSheet("""
            QPushButton {
                background-color: #4F46E5 !important;
                color: #FFFFFF !important;
                border: none;
                border-radius: 8px;
                padding: 11px 18px;
                font-size: 13px;
                font-weight: 700;
            }
            QPushButton:hover {
                background-color: #4338CA !important;
                color: #FFFFFF !important;
            }
            QPushButton:pressed {
                background-color: #3730A3 !important;
                color: #FFFFFF !important;
            }
        """)
        btn_regress.clicked.connect(self.run_regression_flow)
        sidebar_layout.addWidget(btn_regress)

        # ── Ayraç ──
        sidebar_layout.addSpacing(20)
        self._add_sidebar_divider(sidebar_layout)
        sidebar_layout.addSpacing(20)

        # ═══════════════════════════════════════════════════════
        # BÖLÜM 3 — TABLO DÜZENLEME
        # ═══════════════════════════════════════════════════════
        lbl_s3 = QLabel("TABLO DÜZENLEME")
        lbl_s3.setObjectName("sidebar_section_title")
        sidebar_layout.addWidget(lbl_s3)

        sidebar_layout.addSpacing(14)

        # ── Satır İşlemleri ──
        lbl_row = QLabel("Satır İşlemleri")
        lbl_row.setObjectName("sidebar_sub_title")
        sidebar_layout.addWidget(lbl_row)

        sidebar_layout.addSpacing(4)

        lbl_row_desc = QLabel("Tablonun sonuna satır ekleyin veya seçili satırı silin.")
        lbl_row_desc.setObjectName("sidebar_desc")
        lbl_row_desc.setWordWrap(True)
        sidebar_layout.addWidget(lbl_row_desc)

        sidebar_layout.addSpacing(8)

        hbox_r = QHBoxLayout()
        hbox_r.setSpacing(8)
        btn_add_row = QPushButton("+ Satır Ekle")
        btn_add_row.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add_row.clicked.connect(self.add_row)
        hbox_r.addWidget(btn_add_row)

        btn_del_row = QPushButton("− Satır Sil")
        btn_del_row.setObjectName("danger_button")
        btn_del_row.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_del_row.clicked.connect(self.remove_row)
        hbox_r.addWidget(btn_del_row)
        sidebar_layout.addLayout(hbox_r)

        sidebar_layout.addSpacing(16)

        # ── Sütun İşlemleri ──
        lbl_col = QLabel("Sütun İşlemleri")
        lbl_col.setObjectName("sidebar_sub_title")
        sidebar_layout.addWidget(lbl_col)

        sidebar_layout.addSpacing(4)

        lbl_col_desc = QLabel("Tabloya yeni değişken sütunu ekleyin veya seçili sütunu silin.")
        lbl_col_desc.setObjectName("sidebar_desc")
        lbl_col_desc.setWordWrap(True)
        sidebar_layout.addWidget(lbl_col_desc)

        sidebar_layout.addSpacing(8)

        hbox_c = QHBoxLayout()
        hbox_c.setSpacing(8)
        btn_add_col = QPushButton("+ Sütun Ekle")
        btn_add_col.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add_col.clicked.connect(self.add_column)
        hbox_c.addWidget(btn_add_col)

        btn_del_col = QPushButton("− Sütun Sil")
        btn_del_col.setObjectName("danger_button")
        btn_del_col.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_del_col.clicked.connect(self.remove_column)
        hbox_c.addWidget(btn_del_col)
        sidebar_layout.addLayout(hbox_c)

        sidebar_layout.addSpacing(6)



        sidebar_layout.addStretch()

        # ── Tabloyu Sıfırla (Alt Kısım) ──
        self._add_sidebar_divider(sidebar_layout)
        sidebar_layout.addSpacing(16)

        lbl_clr = QLabel("SIFIRLAMA")
        lbl_clr.setObjectName("sidebar_section_title")
        sidebar_layout.addWidget(lbl_clr)

        sidebar_layout.addSpacing(8)

        lbl_clr_desc = QLabel("Tüm veri hücrelerini ve matris yapısını temizler.")
        lbl_clr_desc.setObjectName("sidebar_desc")
        lbl_clr_desc.setWordWrap(True)
        sidebar_layout.addWidget(lbl_clr_desc)

        sidebar_layout.addSpacing(8)

        btn_clear = QPushButton("Tüm Tabloyu Sıfırla")
        btn_clear.setObjectName("danger_button")
        btn_clear.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_clear.clicked.connect(self.clear_table)
        sidebar_layout.addWidget(btn_clear)

        sidebar_scroll.setWidget(sidebar_content)

        container_layout = QVBoxLayout(sidebar_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.addWidget(sidebar_scroll)

        main_layout.addWidget(sidebar_container)

        # ------------------------------------------------------------------------
        # 2. SAĞ İÇERİK ALANI (ORTALANMIŞ SEKMELER VE 25PX KAVİSLİ SAYFALAR)
        # ------------------------------------------------------------------------
        content_container = QWidget()
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(16, 16, 16, 16)
        content_layout.setSpacing(0)

        # Standalone Ortalanmış QTabBar (Kaydırma Ok Butonları Tamamen Devre Dışı)
        from PyQt6.QtWidgets import QStackedWidget, QTabBar
        self.tab_bar = QTabBar()
        self.tab_bar.setUsesScrollButtons(False)
        self.tab_bar.setExpanding(False)
        self.tab_bar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.tab_bar.addTab("Veri Tablosu")
        self.tab_bar.addTab("Regresyon Analizi")
        self.tab_bar.addTab("Görselleştirme")

        # Sekme Butonlarını Sayfada Tam Ortala (Alt Border Çizgisi Yok)
        tab_bar_wrapper = QHBoxLayout()
        tab_bar_wrapper.setContentsMargins(0, 0, 0, 0)
        tab_bar_wrapper.addStretch(1)
        tab_bar_wrapper.addWidget(self.tab_bar)
        tab_bar_wrapper.addStretch(1)

        content_layout.addLayout(tab_bar_wrapper)

        # İçerik Yığını (QStackedWidget)
        self.stack_widget = QStackedWidget()
        self.tab_bar.currentChanged.connect(self.stack_widget.setCurrentIndex)

        # --- Helper for 25px Rounded Page Containers ---
        def wrap_in_page_container(child_widget: QWidget) -> QFrame:
            container = QFrame()
            container.setObjectName("page_container")
            layout = QVBoxLayout(container)
            layout.setContentsMargins(6, 6, 6, 6)
            layout.setSpacing(0)
            layout.addWidget(child_widget)
            return container

        # --- Tab 1: Veri Tablosu ---
        self.tab_data = QWidget()
        tab_data_layout = QVBoxLayout(self.tab_data)
        tab_data_layout.setContentsMargins(10, 10, 10, 10)

        # RAHAT, ULTRA İNCE SCROLLBAR'LI TABLO
        self.table = QTableWidget(30, 15)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(True)
        self.update_excel_column_headers()

        # Sütun ve Satır Yükseklikleri / Sıkışmama Standartları
        self.table.horizontalHeader().setDefaultSectionSize(110)
        self.table.verticalHeader().setDefaultSectionSize(34)
        self.table.horizontalHeader().setMinimumSectionSize(75)

        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.verticalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)

        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.table.itemChanged.connect(lambda item: self._update_status())
        self.table.horizontalHeader().sectionDoubleClicked.connect(self.edit_column_header)

        tab_data_layout.addWidget(self.table)

        # --- Tab 2: Regresyon Analizi ---
        self.tab_regression = QWidget()
        self.tab_regression_layout = QVBoxLayout(self.tab_regression)
        self.tab_regression_layout.setContentsMargins(22, 22, 22, 22)
        self.tab_regression_layout.setSpacing(18)

        # Boş Durum Kartı — Regresyon
        self.tab_regression_layout.addStretch(1)

        reg_empty_wrapper = QHBoxLayout()
        reg_empty_wrapper.addStretch(1)
        reg_empty_wrapper.addWidget(EmptyStateCard(
            "Henüz Analiz Yapılmadı",
            "Regresyon sonuçlarını görüntülemek için sol menüden 'Analizi Başlat' butonuna tıklayın."
        ))
        reg_empty_wrapper.addStretch(1)

        self.tab_regression_layout.addLayout(reg_empty_wrapper)
        self.tab_regression_layout.addStretch(1)

        self.scroll_regression = QScrollArea()
        self.scroll_regression.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_regression.setWidgetResizable(True)
        self.scroll_regression.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_regression.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_regression.setWidget(self.tab_regression)

        # --- Tab 3: Görselleştirme ---
        self.tab_chart = QWidget()
        self.tab_chart_layout = QVBoxLayout(self.tab_chart)
        self.tab_chart_layout.setContentsMargins(22, 22, 22, 22)
        self.tab_chart_layout.setSpacing(14)

        # Boş Durum Kartı — Grafik
        self.tab_chart_layout.addStretch(1)

        chart_empty_wrapper = QHBoxLayout()
        chart_empty_wrapper.addStretch(1)
        chart_empty_wrapper.addWidget(EmptyStateCard(
            "Henüz Grafik Oluşturulmadı",
            "Grafiği görüntülemek için sol menüden 'Analizi Başlat' butonuna tıklayın."
        ))
        chart_empty_wrapper.addStretch(1)

        self.tab_chart_layout.addLayout(chart_empty_wrapper)
        self.tab_chart_layout.addStretch(1)

        self.scroll_chart = QScrollArea()
        self.scroll_chart.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_chart.setWidgetResizable(True)
        self.scroll_chart.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_chart.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_chart.setWidget(self.tab_chart)

        # Sayfaları Yığına Ekle (25px kavisli page_container ile sarılı)
        self.stack_widget.addWidget(wrap_in_page_container(self.tab_data))
        self.stack_widget.addWidget(wrap_in_page_container(self.scroll_regression))
        self.stack_widget.addWidget(wrap_in_page_container(self.scroll_chart))

        content_layout.addWidget(self.stack_widget)
        main_layout.addWidget(content_container, stretch=1)

    def edit_column_header(self, logical_index: int = -1):
        """Sütun başlığını (çift tıklandığında veya butonla) yeniden adlandırır."""
        if logical_index < 0:
            logical_index = self.table.currentColumn()

        if logical_index < 0 or logical_index >= self.table.columnCount():
            QMessageBox.warning(self, "Uyarı", "Lütfen yeniden adlandırılacak sütunu seçin.")
            return

        header_item = self.table.horizontalHeaderItem(logical_index)
        old_name = header_item.text() if header_item and header_item.text() else self.get_excel_column_name(logical_index)

        new_name, ok = QInputDialog.getText(
            self, "Sütun İsmini Değiştir",
            f"'{old_name}' sütunu için yeni bir başlık ismi girin:",
            QLineEdit.EchoMode.Normal, old_name
        )

        if ok and new_name.strip():
            self.table.setHorizontalHeaderItem(logical_index, QTableWidgetItem(new_name.strip()))
            self._update_status()

    # ==========================================================================
    #  TABLO İŞLEMLERİ (EXCEL SÜTUN İSİMLENDİRME STANDARDI A, B, C...)
    # ==========================================================================

    @staticmethod
    def get_excel_column_name(col_idx: int) -> str:
        """Sayısal indeksi Excel alfabetik sütun adına dönüştürür (0 -> A, 25 -> Z, 26 -> AA)"""
        result = ""
        col_idx += 1
        while col_idx > 0:
            col_idx, remainder = divmod(col_idx - 1, 26)
            result = chr(65 + remainder) + result
        return result

    def update_excel_column_headers(self):
        """Tablo sütunlarına varsayılan Excel tarzı alfabetik isimler atar."""
        headers = []
        for c in range(self.table.columnCount()):
            header_item = self.table.horizontalHeaderItem(c)
            if header_item and header_item.text() and not header_item.text().startswith("Değişken_"):
                headers.append(header_item.text())
            else:
                headers.append(self.get_excel_column_name(c))
        self.table.setHorizontalHeaderLabels(headers)

    def add_column(self):
        col_count = self.table.columnCount()
        self.table.insertColumn(col_count)
        for row in range(self.table.rowCount()):
            item = QTableWidgetItem("")
            item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, col_count, item)
        self.update_excel_column_headers()
        self._update_status()

    def add_row(self):
        row_count = self.table.rowCount()
        self.table.insertRow(row_count)
        for col in range(self.table.columnCount()):
            item = QTableWidgetItem("")
            item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row_count, col, item)
        self._update_status()

    def remove_column(self):
        current_column = self.table.currentColumn()
        if current_column >= 0:
            self.table.removeColumn(current_column)
            self.update_excel_column_headers()
            self._update_status()
        else:
            QMessageBox.warning(self, "Uyarı", "Lütfen silinecek sütunu seçin.")

    def remove_row(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            self.table.removeRow(current_row)
            self._update_status()
        else:
            QMessageBox.warning(self, "Uyarı", "Lütfen silinecek satırı seçin.")

    def clear_table(self):
        self.table.clear()
        self.update_excel_column_headers()
        self._restore_empty_states()
        self._update_status()

    # ==========================================================================
    #  DOSYA YÜKLEME
    # ==========================================================================

    def load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Veri Dosyası Seç", "", "CSV / Excel Dosyaları (*.csv *.xlsx *.xls)"
        )
        if not file_path:
            return

        ext = os.path.splitext(file_path)[1].lower()

        try:
            if ext == ".csv":
                self.df = pd.read_csv(file_path)
            elif ext in [".xlsx", ".xls"]:
                self.df = pd.read_excel(file_path, engine='openpyxl')
            else:
                QMessageBox.warning(self, "Hata", "Desteklenmeyen dosya formatı!")
                return
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Dosya okunamadı:\n{str(e)}")
            return

        self.loaded_file_name = os.path.basename(file_path)

        self.table.setRowCount(self.df.shape[0])
        self.table.setColumnCount(self.df.shape[1])

        # Başlıklar
        self.table.setHorizontalHeaderLabels(list(self.df.columns))

        # Hücre Verileri
        for row in range(self.df.shape[0]):
            for col in range(self.df.shape[1]):
                val = self.df.iat[row, col]
                text_val = "" if pd.isna(val) else str(val)
                item = QTableWidgetItem(text_val)
                item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.table.setItem(row, col, item)

        self._update_status()
        self.status_bar.showMessage(f"Veri seti başarıyla yüklendi: {self.loaded_file_name}", 5000)

    def _move_to_indep(self):
        for item in self.all_cols_list.selectedItems():
            self.all_cols_list.takeItem(self.all_cols_list.row(item))
            self.independent_list.addItem(item.text())

    def _move_from_indep(self):
        for item in self.independent_list.selectedItems():
            self.independent_list.takeItem(self.independent_list.row(item))
            self.all_cols_list.addItem(item.text())

    def _move_to_dep(self):
        for item in self.all_cols_list.selectedItems():
            self.all_cols_list.takeItem(self.all_cols_list.row(item))
            self.dependent_list.addItem(item.text())

    def _auto_move_item(self, item):
        self.all_cols_list.takeItem(self.all_cols_list.row(item))
        if self.independent_list.count() == 0:
            self.independent_list.addItem(item.text())
        elif self.dependent_list.count() == 0:
            self.dependent_list.addItem(item.text())
        else:
            self.independent_list.addItem(item.text())

    def _move_from_dep(self):
        for item in self.dependent_list.selectedItems():
            self.dependent_list.takeItem(self.dependent_list.row(item))
            self.all_cols_list.addItem(item.text())

    def _get_dataframe_from_table(self) -> pd.DataFrame:
        """Tablodaki (dosyadan yüklenen veya elle girilen) verileri DataFrame olarak toplar."""
        row_count = self.table.rowCount()
        col_count = self.table.columnCount()

        if row_count == 0 or col_count == 0:
            return pd.DataFrame()

        headers = []
        for col in range(col_count):
            header_item = self.table.horizontalHeaderItem(col)
            if header_item and header_item.text().strip():
                header_name = header_item.text().strip()
            else:
                header_name = self.get_excel_column_name(col)
            headers.append(header_name)

        data = []
        for row in range(row_count):
            row_data = []
            has_val = False
            for col in range(col_count):
                item = self.table.item(row, col)
                if item and item.text():
                    val_str = item.text().strip().replace(',', '.')
                else:
                    val_str = ""
                if val_str != "":
                    has_val = True
                row_data.append(val_str)
            if has_val:
                data.append(row_data)

        if not data:
            return pd.DataFrame()

        df = pd.DataFrame(data, columns=headers)

        # Sayısal Dönüştürme (Virgül ve Nokta Desteği)
        numeric_df = pd.DataFrame()
        for col_name in df.columns:
            converted = pd.to_numeric(df[col_name].astype(str).str.replace(',', '.'), errors='coerce')
            if converted.notna().sum() > 0:
                numeric_df[col_name] = converted

        numeric_df.dropna(axis=0, how="all", inplace=True)
        return numeric_df

    # ==========================================================================
    #  ANALİZ AKIŞI DİAYALOGLARI
    # ==========================================================================

    def run_regression_flow(self):
        # Her zaman tablodaki (elle girilenler dahil) güncel verileri oku
        table_df = self._get_dataframe_from_table()
        if not table_df.empty:
            self.df = table_df

        if self.df is None or self.df.empty:
            QMessageBox.warning(self, "Uyarı", "Lütfen tabloya veri girin veya bir dosya yükleyin!")
            return

        cols = list(self.df.columns)
        if len(cols) < 2:
            QMessageBox.warning(self, "Uyarı", "Regresyon analizi için tabloda en az 2 geçerli sayısal sütun olmalıdır.")
            return

        # Değişken Seçim Diyaloğu (Modern Yüksek Estetikli Tasarım)
        dialog = QDialog(self)
        dialog.setWindowTitle("Değişken Seçimi — Regresyon Analizi")
        dialog.setFixedSize(600, 500)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #FFFFFF;
            }
            QLabel#dlg_title {
                font-size: 17px;
                font-weight: 800;
                color: #0F172A;
            }
            QLabel#dlg_subtitle {
                font-size: 12px;
                color: #64748B;
            }
            QLabel#group_label {
                font-size: 11px;
                font-weight: 700;
                color: #475569;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            QListWidget {
                background-color: #F8FAFC;
                border: 1px solid #E2E8F0;
                border-radius: 10px;
                padding: 6px;
                font-size: 13px;
                outline: none;
            }
            QListWidget::item {
                background-color: #FFFFFF;
                border: 1px solid #F1F5F9;
                border-radius: 6px;
                padding: 7px 10px;
                margin-bottom: 4px;
                color: #334155;
                font-weight: 500;
            }
            QListWidget::item:hover {
                background-color: #EEF2FF;
                border-color: #C7D2FE;
                color: #4F46E5;
            }
            QListWidget::item:selected {
                background-color: #4F46E5;
                color: #FFFFFF;
                font-weight: 700;
                border: none;
            }
            QPushButton#transfer_btn {
                background-color: #F8FAFC;
                color: #334155;
                font-weight: 700;
                font-size: 11.5px;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                padding: 7px 12px;
                min-width: 85px;
            }
            QPushButton#transfer_btn:hover {
                background-color: #EEF2FF;
                color: #4F46E5;
                border-color: #C7D2FE;
            }
        """)

        dlg_layout = QVBoxLayout(dialog)
        dlg_layout.setContentsMargins(24, 22, 24, 22)
        dlg_layout.setSpacing(16)

        # Başlık ve Bilgi Kutusu Metni
        title_box = QVBoxLayout()
        title_box.setSpacing(6)

        lbl_main = QLabel("Değişken Yapılandırması")
        lbl_main.setObjectName("dlg_title")
        title_box.addWidget(lbl_main)

        info_box = QLabel("Değişkenleri fare ile sürükleyip bırakarak veya üzerine çift tıklayarak X ve Y alanlarına aktarabilirsiniz.")
        info_box.setWordWrap(True)
        info_box.setStyleSheet("""
            font-size: 11.5px;
            color: #4338CA;
            background-color: #EEF2FF;
            border: 1px solid #C7D2FE;
            border-radius: 8px;
            padding: 8px 12px;
        """)
        title_box.addWidget(info_box)
        dlg_layout.addLayout(title_box)

        lists_hbox = QHBoxLayout()
        lists_hbox.setSpacing(14)

        # Sürükle - Bırak (Drag & Drop) Yardımcısı
        def _enable_drag_drop(lw: QListWidget):
            lw.setDragEnabled(True)
            lw.setAcceptDrops(True)
            lw.setDropIndicatorShown(True)
            lw.setDefaultDropAction(Qt.DropAction.MoveAction)
            lw.setDragDropMode(QListWidget.DragDropMode.DragDrop)

        # 1. Mevcut Sütunlar
        vbox_all = QVBoxLayout()
        vbox_all.setSpacing(6)
        lbl_all = QLabel("TÜM DEĞİŞKENLER")
        lbl_all.setObjectName("group_label")
        vbox_all.addWidget(lbl_all)

        self.all_cols_list = QListWidget()
        _enable_drag_drop(self.all_cols_list)
        self.all_cols_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.all_cols_list.addItems(cols)
        self.all_cols_list.itemDoubleClicked.connect(self._auto_move_item)
        vbox_all.addWidget(self.all_cols_list)
        lists_hbox.addLayout(vbox_all, stretch=1)

        # 2. Seçilenler (Bağımsız X ve Bağımlı Y)
        vbox_selected = QVBoxLayout()
        vbox_selected.setSpacing(12)

        # X Grubu
        vbox_x = QVBoxLayout()
        vbox_x.setSpacing(6)
        lbl_x = QLabel("BAĞIMSIZ DEĞİŞKEN (X)")
        lbl_x.setObjectName("group_label")
        vbox_x.addWidget(lbl_x)

        self.independent_list = QListWidget()
        _enable_drag_drop(self.independent_list)
        self.independent_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.independent_list.itemDoubleClicked.connect(self._move_from_indep)
        vbox_x.addWidget(self.independent_list)
        vbox_selected.addLayout(vbox_x)

        # Y Grubu
        vbox_y = QVBoxLayout()
        vbox_y.setSpacing(6)
        lbl_y = QLabel("BAĞIMLI DEĞİŞKEN (Y)")
        lbl_y.setObjectName("group_label")
        vbox_y.addWidget(lbl_y)

        self.dependent_list = QListWidget()
        _enable_drag_drop(self.dependent_list)
        self.dependent_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.dependent_list.itemDoubleClicked.connect(self._move_from_dep)
        vbox_y.addWidget(self.dependent_list)
        vbox_selected.addLayout(vbox_y)

        lists_hbox.addLayout(vbox_selected, stretch=1)
        dlg_layout.addLayout(lists_hbox)

        # Alt Butonlar
        btn_box = QHBoxLayout()
        btn_box.setSpacing(10)
        btn_box.addStretch()

        btn_cancel = QPushButton("İptal")
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #F1F5F9;
                color: #64748B;
                font-weight: 600;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                padding: 9px 20px;
            }
            QPushButton:hover {
                background-color: #E2E8F0;
                color: #334155;
            }
        """)
        btn_cancel.clicked.connect(dialog.reject)
        btn_box.addWidget(btn_cancel)

        btn_ok = QPushButton("Analizi Çalıştır")
        btn_ok.setStyleSheet("""
            QPushButton {
                background-color: #4F46E5;
                color: #FFFFFF;
                font-weight: 700;
                border: none;
                border-radius: 8px;
                padding: 9px 22px;
            }
            QPushButton:hover {
                background-color: #4338CA;
            }
        """)
        btn_ok.clicked.connect(dialog.accept)
        btn_box.addWidget(btn_ok)

        dlg_layout.addLayout(btn_box)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        independent_items = [self.independent_list.item(i).text() for i in range(self.independent_list.count())]
        dependent_items = [self.dependent_list.item(i).text() for i in range(self.dependent_list.count())]

        if len(independent_items) != 1 or len(dependent_items) != 1:
            QMessageBox.warning(self, "Uyarı", "Lütfen tam olarak 1 bağımsız (X) ve 1 bağımlı (Y) değişken seçin.")
            return

        x_col = independent_items[0]
        y_col = dependent_items[0]

        try:
            x = pd.to_numeric(self.df[x_col], errors='coerce').dropna()
            y = pd.to_numeric(self.df[y_col], errors='coerce').dropna()
            min_len = min(len(x), len(y))
            x = x.iloc[:min_len]
            y = y.iloc[:min_len]
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Seçilen sütun verileri sayısal değil: {e}")
            return

        self._calculate_regression(x.values, y.values)
        self.independent_col = x_col
        self.dependent_col = y_col

        # İlk Analizde Boş Durum Kartlarını Temizle ve Alt Esneme Ekle
        if self.analysis_count == 0:
            self._clear_layout(self.tab_regression_layout)
            self._clear_layout(self.tab_chart_layout)
            self.tab_regression_layout.addStretch(1)
            self.tab_chart_layout.addStretch(1)

        self.analysis_count += 1

        self._display_regression_results()
        self._display_chart(x_col, y_col)

        self.status_analysis_label.setText("Durum: Analiz Tamamlandı")
        self.status_bar.showMessage(f"Analiz #{self.analysis_count} tamamlandı. R-Kare = {self.r_kare:.4f}", 8000)

        self.tab_bar.setCurrentIndex(1)

    # ==========================================================================
    #  HESAPLAMA MATEMATİĞİ
    # ==========================================================================

    def _calculate_regression(self, x, y):
        def sum_val(v): return np.sum(v)
        def mean_val(v): return np.mean(v)
        def sqrt_val(v): return v ** 0.5
        def sq_val(v): return v * v

        self.n = len(x)

        self.sum_y = sum_val(y)
        self.sum_x = sum_val(x)
        self.mult = x * y
        self.sum_mult = sum_val(self.mult)
        self.square_x = sq_val(x)
        self.square_y = sq_val(y)
        self.sum_squ_x = sum_val(self.square_x)
        self.sum_squ_y = sum_val(self.square_y)
        self.mean_x = mean_val(x)
        self.mean_y = mean_val(y)
        self.xoakt = sum_val(sq_val(x - self.mean_x))
        self.yoakt = sum_val(sq_val(y - self.mean_y))
        self.xyct = sum_val((x - self.mean_x) * (y - self.mean_y))
        self.b1 = self.xyct / self.xoakt
        self.b0 = self.mean_y - (self.b1 * self.mean_x)
        self.rkt = self.b1 * self.xyct
        self.rakt = self.yoakt - self.rkt
        self.rko = self.rkt / 1
        self.rako = self.rakt / (self.n - 2)
        self.sb1 = sqrt_val(self.rako / self.xoakt)
        self.th = self.b1 / self.sb1
        self.r_kare = self.rkt / self.yoakt
        self.r = sqrt_val(self.r_kare)

        self.pred = self.b0 + (self.b1 * x)
        self.e = y - self.pred
        self.rss = sum_val(sq_val(self.e))
        self.varyans = self.rss / (self.n - 2)
        self.se = sqrt_val(self.varyans * ((1 / self.n) + (sq_val(self.mean_x) / self.xoakt)))
        self.ti = self.b0 / self.se
        self.ph = 2 * (1 - stats.t.cdf(self.th, self.n - 2))
        self.pi = 2 * (1 - stats.t.cdf(self.ti, self.n - 2))
        self.f_val = self.rko / self.rako
        self.prob = f.sf(self.f_val, 1, self.n - 2)

    # ==========================================================================
    #  SONUÇ TABLOLARI VE KARTLAR
    # ==========================================================================

    def _restore_empty_states(self):
        """Tüm analiz geçmişini temizler ve varsayılan boş durum kartlarını geri yükler."""
        self.analysis_count = 0
        self._clear_layout(self.tab_regression_layout)
        self._clear_layout(self.tab_chart_layout)

        # Regresyon boş kartı
        self.tab_regression_layout.addStretch(1)
        reg_empty_wrapper = QHBoxLayout()
        reg_empty_wrapper.addStretch(1)
        reg_empty_wrapper.addWidget(EmptyStateCard(
            "Henüz Analiz Yapılmadı",
            "Regresyon sonuçlarını görüntülemek için sol menüden 'Analizi Başlat' butonuna tıklayın."
        ))
        reg_empty_wrapper.addStretch(1)
        self.tab_regression_layout.addLayout(reg_empty_wrapper)
        self.tab_regression_layout.addStretch(1)

        # Grafik boş kartı
        self.tab_chart_layout.addStretch(1)
        chart_empty_wrapper = QHBoxLayout()
        chart_empty_wrapper.addStretch(1)
        chart_empty_wrapper.addWidget(EmptyStateCard(
            "Henüz Grafik Oluşturulmadı",
            "Grafiği görüntülemek için sol menüden 'Analizi Başlat' butonuna tıklayın."
        ))
        chart_empty_wrapper.addStretch(1)
        self.tab_chart_layout.addLayout(chart_empty_wrapper)
        self.tab_chart_layout.addStretch(1)

    # ==========================================================================
    #  SONUÇ TABLOLARI VE KARTLAR (GEÇMİŞ STOKLAMA)
    # ==========================================================================

    def _display_regression_results(self):
        # TEK VE SABİT CONTAINER (Analize Ait Tüm Başlık, Tablo ve Sonuçlar Tek Bir Çerçevede)
        run_box = QFrame()
        run_box.setObjectName("analysis_run_container")
        run_box.setStyleSheet("""
            QFrame#analysis_run_container {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 16px;
            }
        """)

        run_layout = QVBoxLayout(run_box)
        run_layout.setContentsMargins(22, 22, 22, 22)
        run_layout.setSpacing(14)

        # 1. Üst Başlık Satırı (Akordeon Buton, Düzenle Butonu ve Gizle Butonu)
        header_top_layout = QHBoxLayout()
        header_top_layout.setSpacing(8)

        run_title = f"ANALİZ #{self.analysis_count}"

        btn_accordion = QPushButton(f"▼ {run_title}")
        btn_accordion.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_accordion.setToolTip("Genişlet / Daralt")
        btn_accordion.setStyleSheet("""
            QPushButton {
                font-size: 11px;
                font-weight: 800;
                color: #FFFFFF;
                background-color: #4F46E5;
                border-radius: 6px;
                padding: 5px 12px;
            }
            QPushButton:hover {
                background-color: #4338CA;
            }
        """)
        header_top_layout.addWidget(btn_accordion)

        btn_rename = QPushButton("Düzenle")
        btn_rename.setToolTip("Analiz Başlığını Yeniden Adlandır")
        btn_rename.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_rename.setStyleSheet("""
            QPushButton {
                font-size: 11px;
                font-weight: 600;
                color: #64748B;
                background-color: #F1F5F9;
                border: 1px solid #E2E8F0;
                border-radius: 6px;
                padding: 4px 10px;
            }
            QPushButton:hover {
                background-color: #E2E8F0;
                color: #334155;
            }
        """)
        header_top_layout.addWidget(btn_rename)

        header_top_layout.addStretch()

        # Bulanıklaştırma (Blur / Gizle) Buton Düğmesi
        btn_blur = QPushButton("Gizle")
        btn_blur.setFixedWidth(75)
        btn_blur.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_blur.setStyleSheet("""
            QPushButton {
                font-size: 11px;
                font-weight: 700;
                color: #64748B;
                background-color: #F1F5F9;
                border: 1px solid #E2E8F0;
                border-radius: 6px;
                padding: 4px 0px;
            }
            QPushButton:hover {
                background-color: #E2E8F0;
                color: #334155;
            }
        """)
        header_top_layout.addWidget(btn_blur)

        run_layout.addLayout(header_top_layout)

        # 2. Alt Satır Değişken Etiketleri (Bağımsız, Bağımlı, Gözlem Sayısı)
        pills_layout = QHBoxLayout()
        pills_layout.setSpacing(10)

        pill_x = QLabel(f"Bağımsız (X): <b style='color:#1E293B;'>{self.independent_col}</b>")
        pill_x.setStyleSheet("""
            font-size: 12px;
            color: #64748B;
            background-color: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 6px;
            padding: 4px 10px;
        """)
        pills_layout.addWidget(pill_x)

        pill_y = QLabel(f"Bağımlı (Y): <b style='color:#1E293B;'>{self.dependent_col}</b>")
        pill_y.setStyleSheet("""
            font-size: 12px;
            color: #64748B;
            background-color: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 6px;
            padding: 4px 10px;
        """)
        pills_layout.addWidget(pill_y)

        pill_n = QLabel(f"Gözlem (N): <b style='color:#1E293B;'>{self.n}</b>")
        pill_n.setStyleSheet("""
            font-size: 12px;
            color: #64748B;
            background-color: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 6px;
            padding: 4px 10px;
        """)
        pills_layout.addWidget(pill_n)

        pills_layout.addStretch()
        run_layout.addLayout(pills_layout)

        # Bulanıklaştırılabilir Gövde Kapsayıcısı (Body Widget)
        body_widget = QWidget()
        body_layout = QVBoxLayout(body_widget)
        body_layout.setContentsMargins(0, 4, 0, 0)
        body_layout.setSpacing(14)

        def _toggle_regression_collapse():
            is_visible = body_widget.isVisible()
            body_widget.setVisible(not is_visible)
            symbol = "▶" if is_visible else "▼"
            btn_accordion.setText(f"{symbol} {run_title}")
            if is_visible:
                btn_accordion.setStyleSheet("""
                    QPushButton {
                        font-size: 11px;
                        font-weight: 800;
                        color: #4F46E5;
                        background-color: #EEF2FF;
                        border: 1px solid #C7D2FE;
                        border-radius: 6px;
                        padding: 5px 12px;
                    }
                    QPushButton:hover {
                        background-color: #E0E7FF;
                    }
                """)
            else:
                btn_accordion.setStyleSheet("""
                    QPushButton {
                        font-size: 11px;
                        font-weight: 800;
                        color: #FFFFFF;
                        background-color: #4F46E5;
                        border-radius: 6px;
                        padding: 5px 12px;
                    }
                    QPushButton:hover {
                        background-color: #4338CA;
                    }
                """)

        btn_accordion.clicked.connect(_toggle_regression_collapse)

        def _rename_regression():
            nonlocal run_title
            new_title, ok = QInputDialog.getText(
                self, "Analiz İsmini Değiştir", "Yeni Analiz İsmi:",
                QLineEdit.EchoMode.Normal, run_title
            )
            if ok and new_title.strip():
                run_title = new_title.strip()
                symbol = "▼" if body_widget.isVisible() else "▶"
                btn_accordion.setText(f"{symbol} {run_title}")

        btn_rename.clicked.connect(_rename_regression)

        def _toggle_regression_blur():
            if body_widget.graphicsEffect() is None:
                blur = QGraphicsBlurEffect()
                blur.setBlurRadius(25)
                body_widget.setGraphicsEffect(blur)
                body_widget.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
                btn_blur.setText("Göster")
                btn_blur.setStyleSheet("""
                    QPushButton {
                        font-size: 11px;
                        font-weight: 700;
                        color: #4F46E5;
                        background-color: #EEF2FF;
                        border: 1px solid #C7D2FE;
                        border-radius: 6px;
                        padding: 4px 0px;
                    }
                    QPushButton:hover {
                        background-color: #E0E7FF;
                    }
                """)
            else:
                body_widget.setGraphicsEffect(None)
                body_widget.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
                btn_blur.setText("Gizle")
                btn_blur.setStyleSheet("""
                    QPushButton {
                        font-size: 11px;
                        font-weight: 700;
                        color: #64748B;
                        background-color: #F1F5F9;
                        border: 1px solid #E2E8F0;
                        border-radius: 6px;
                        padding: 4px 0px;
                    }
                    QPushButton:hover {
                        background-color: #E2E8F0;
                        color: #334155;
                    }
                """)

        btn_blur.clicked.connect(_toggle_regression_blur)

        # 2. İstatistik Kartları (R, R2, N, F)
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(12)

        card_r = StatCard("R", f"{self.r:.4f}")
        card_r2 = StatCard("R-Kare", f"{self.r_kare:.4f}")
        card_n = StatCard("Gözlem (N)", str(self.n))
        card_f = StatCard("F İstatistiği", f"{self.f_val:.3f}")

        for card in [card_r, card_r2, card_n, card_f]:
            card.setStyleSheet("QFrame { background-color: #F8FAFC; border: none; border-radius: 8px; }")
            cards_layout.addWidget(card)
        cards_layout.addStretch()

        cards_widget = QWidget()
        cards_widget.setLayout(cards_layout)
        body_layout.addWidget(cards_widget)

        # 3. Regresyon Katsayıları Tablosu
        coef_header = SectionHeader("Regresyon Katsayıları")
        body_layout.addWidget(coef_header)

        table_coef = QTableWidget(2, 5)
        table_coef.setObjectName("result_table")
        table_coef.setStyleSheet("QTableWidget { border: none !important; background: transparent; }")
        table_coef.setAlternatingRowColors(True)
        table_coef.setMaximumHeight(105)
        table_coef.setMinimumHeight(105)
        table_coef.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table_coef.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table_coef.verticalHeader().setVisible(False)
        table_coef.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table_coef.setHorizontalHeaderLabels(["Variable", "Coefficient (b)", "Std. Error", "t Value", "p Value"])

        coef_data = [
            ["Constant (Intercept)", f"{self.b0:.4f}", f"{self.se:.4f}", f"{self.ti:.4f}", f"{self.pi:.4f}"],
            [self.independent_col, f"{self.b1:.4f}", f"{self.sb1:.4f}", f"{self.th:.4f}", f"{self.ph:.4f}"],
        ]

        for row_idx, row_data in enumerate(coef_data):
            for col_idx, val in enumerate(row_data):
                item = QTableWidgetItem(val)
                align = Qt.AlignmentFlag.AlignLeft if col_idx == 0 else Qt.AlignmentFlag.AlignCenter
                item.setTextAlignment(align | Qt.AlignmentFlag.AlignVCenter)

                if col_idx == 4:
                    try:
                        p_val = float(val)
                        if p_val < 0.05:
                            item.setBackground(QColor("#ECFDF5"))
                            item.setForeground(QColor("#047857"))
                    except ValueError:
                        pass

                table_coef.setItem(row_idx, col_idx, item)

        body_layout.addWidget(table_coef)

        # 4. Varyans Analizi (ANOVA) Tablosu
        anova_header = SectionHeader("Varyans Analizi (ANOVA)")
        body_layout.addWidget(anova_header)

        table_anova = QTableWidget(3, 6)
        table_anova.setObjectName("result_table")
        table_anova.setStyleSheet("QTableWidget { border: none !important; background: transparent; }")
        table_anova.setAlternatingRowColors(True)
        table_anova.setMaximumHeight(135)
        table_anova.setMinimumHeight(135)
        table_anova.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table_anova.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table_anova.verticalHeader().setVisible(False)
        table_anova.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table_anova.setHorizontalHeaderLabels(
            ["Source", "Sum of Squares (SS)", "df", "Mean Square (MS)", "F Value", "p Value"]
        )

        anova_data = [
            ["Regression", f"{self.rkt:.4f}", "1", f"{self.rko:.4f}",
             f"{self.f_val:.4f}", f"{self.prob:.4f}"],
            ["Residual (Error)", f"{self.rakt:.4f}", str(self.n - 2), f"{self.rako:.4f}", "", ""],
            ["Total", f"{self.yoakt:.4f}", str(self.n - 1), "", "", ""],
        ]

        for row_idx, row_data in enumerate(anova_data):
            for col_idx, val in enumerate(row_data):
                item = QTableWidgetItem(val)
                align = Qt.AlignmentFlag.AlignLeft if col_idx == 0 else Qt.AlignmentFlag.AlignCenter
                item.setTextAlignment(align | Qt.AlignmentFlag.AlignVCenter)

                if row_idx == 0 and col_idx == 5 and val:
                    try:
                        p_val = float(val)
                        if p_val < 0.05:
                            item.setBackground(QColor("#ECFDF5"))
                            item.setForeground(QColor("#047857"))
                    except ValueError:
                        pass

                table_anova.setItem(row_idx, col_idx, item)

        body_layout.addWidget(table_anova)

        # 5. Regresyon Denklemi Kartı
        eq_sign = "+" if self.b1 >= 0 else "-"
        b1_abs = abs(self.b1)
        equation_text = f"Y = {self.b0:.4f} {eq_sign} {b1_abs:.4f} × {self.independent_col}"

        eq_frame = QFrame()
        eq_frame.setStyleSheet("QFrame { background-color: #F8FAFC; border: none; border-radius: 8px; padding: 12px 16px; }")
        eq_layout = QVBoxLayout(eq_frame)
        eq_layout.setContentsMargins(14, 10, 14, 10)

        eq_title = QLabel("MODEL REGRESYON DENKLEMİ")
        eq_title.setObjectName("stat_label")
        eq_layout.addWidget(eq_title)

        eq_label = QLabel(equation_text)
        eq_label.setStyleSheet(f"""
            font-size: 15px;
            font-weight: 700;
            color: {Colors.ACCENT_PRIMARY};
            font-family: {FONT_FAMILY_MONO};
            padding-top: 2px;
        """)
        eq_layout.addWidget(eq_label)

        body_layout.addWidget(eq_frame)

        run_layout.addWidget(body_widget)

        # En Yeni Analizi En Üste Ekle (Stoklama Yapısı)
        self.tab_regression_layout.insertWidget(0, run_box)

    # ==========================================================================
    #  GRAFİK (GEÇMİŞ STOKLAMA)
    # ==========================================================================

    def _display_chart(self, x_col: str, y_col: str):
        # TEK VE SABİT CONTAINER (Analize Ait Tüm Grafik Çıktısı Tek Bir Çerçevede)
        chart_box = QFrame()
        chart_box.setObjectName("chart_run_container")
        chart_box.setStyleSheet("""
            QFrame#chart_run_container {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 16px;
            }
        """)
        chart_layout = QVBoxLayout(chart_box)
        chart_layout.setContentsMargins(22, 22, 22, 22)
        chart_layout.setSpacing(14)

        # 1. Üst Başlık Satırı (Akordeon Buton, Düzenle Butonu ve Gizle Butonu — Grafik)
        header_top_layout = QHBoxLayout()
        header_top_layout.setSpacing(8)

        chart_title = f"ANALİZ #{self.analysis_count} GRAFİĞİ"

        btn_chart_accordion = QPushButton(f"▼ {chart_title}")
        btn_chart_accordion.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_chart_accordion.setToolTip("Genişlet / Daralt")
        btn_chart_accordion.setStyleSheet("""
            QPushButton {
                font-size: 11px;
                font-weight: 800;
                color: #FFFFFF;
                background-color: #4F46E5;
                border-radius: 6px;
                padding: 5px 12px;
            }
            QPushButton:hover {
                background-color: #4338CA;
            }
        """)
        header_top_layout.addWidget(btn_chart_accordion)

        btn_chart_rename = QPushButton("Düzenle")
        btn_chart_rename.setToolTip("Grafik Başlığını Yeniden Adlandır")
        btn_chart_rename.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_chart_rename.setStyleSheet("""
            QPushButton {
                font-size: 11px;
                font-weight: 600;
                color: #64748B;
                background-color: #F1F5F9;
                border: 1px solid #E2E8F0;
                border-radius: 6px;
                padding: 4px 10px;
            }
            QPushButton:hover {
                background-color: #E2E8F0;
                color: #334155;
            }
        """)
        header_top_layout.addWidget(btn_chart_rename)

        header_top_layout.addStretch()

        # Bulanıklaştırma (Blur / Gizle) Buton Düğmesi — Grafik
        btn_chart_blur = QPushButton("Gizle")
        btn_chart_blur.setFixedWidth(75)
        btn_chart_blur.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_chart_blur.setStyleSheet("""
            QPushButton {
                font-size: 11px;
                font-weight: 700;
                color: #64748B;
                background-color: #F1F5F9;
                border: 1px solid #E2E8F0;
                border-radius: 6px;
                padding: 4px 0px;
            }
            QPushButton:hover {
                background-color: #E2E8F0;
                color: #334155;
            }
        """)
        header_top_layout.addWidget(btn_chart_blur)

        chart_layout.addLayout(header_top_layout)

        # 2. Alt Satır Değişken Etiketleri (Bağımsız, Bağımlı, Gözlem Sayısı)
        pills_layout = QHBoxLayout()
        pills_layout.setSpacing(10)

        pill_x = QLabel(f"Bağımsız (X): <b style='color:#1E293B;'>{x_col}</b>")
        pill_x.setStyleSheet("""
            font-size: 12px;
            color: #64748B;
            background-color: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 6px;
            padding: 4px 10px;
        """)
        pills_layout.addWidget(pill_x)

        pill_y = QLabel(f"Bağımlı (Y): <b style='color:#1E293B;'>{y_col}</b>")
        pill_y.setStyleSheet("""
            font-size: 12px;
            color: #64748B;
            background-color: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 6px;
            padding: 4px 10px;
        """)
        pills_layout.addWidget(pill_y)

        pill_n = QLabel(f"Gözlem (N): <b style='color:#1E293B;'>{self.n}</b>")
        pill_n.setStyleSheet("""
            font-size: 12px;
            color: #64748B;
            background-color: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 6px;
            padding: 4px 10px;
        """)
        pills_layout.addWidget(pill_n)

        pills_layout.addStretch()
        chart_layout.addLayout(pills_layout)

        # Bulanıklaştırılabilir Grafik Gövdesi (Chart Body)
        chart_body = QWidget()
        chart_body_layout = QVBoxLayout(chart_body)
        chart_body_layout.setContentsMargins(0, 4, 0, 0)
        chart_body_layout.setSpacing(0)

        def _toggle_chart_collapse():
            is_visible = chart_body.isVisible()
            chart_body.setVisible(not is_visible)
            symbol = "▶" if is_visible else "▼"
            btn_chart_accordion.setText(f"{symbol} {chart_title}")
            if is_visible:
                btn_chart_accordion.setStyleSheet("""
                    QPushButton {
                        font-size: 11px;
                        font-weight: 800;
                        color: #4F46E5;
                        background-color: #EEF2FF;
                        border: 1px solid #C7D2FE;
                        border-radius: 6px;
                        padding: 5px 12px;
                    }
                    QPushButton:hover {
                        background-color: #E0E7FF;
                    }
                """)
            else:
                btn_chart_accordion.setStyleSheet("""
                    QPushButton {
                        font-size: 11px;
                        font-weight: 800;
                        color: #FFFFFF;
                        background-color: #4F46E5;
                        border-radius: 6px;
                        padding: 5px 12px;
                    }
                    QPushButton:hover {
                        background-color: #4338CA;
                    }
                """)

        btn_chart_accordion.clicked.connect(_toggle_chart_collapse)

        def _rename_chart():
            nonlocal chart_title
            new_title, ok = QInputDialog.getText(
                self, "Grafik İsmini Değiştir", "Yeni Grafik İsmi:",
                QLineEdit.EchoMode.Normal, chart_title
            )
            if ok and new_title.strip():
                chart_title = new_title.strip()
                symbol = "▼" if chart_body.isVisible() else "▶"
                btn_chart_accordion.setText(f"{symbol} {chart_title}")

        btn_chart_rename.clicked.connect(_rename_chart)

        def _toggle_chart_blur():
            if chart_body.graphicsEffect() is None:
                blur = QGraphicsBlurEffect()
                blur.setBlurRadius(25)
                chart_body.setGraphicsEffect(blur)
                chart_body.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
                btn_chart_blur.setText("Göster")
                btn_chart_blur.setStyleSheet("""
                    QPushButton {
                        font-size: 11px;
                        font-weight: 700;
                        color: #4F46E5;
                        background-color: #EEF2FF;
                        border: 1px solid #C7D2FE;
                        border-radius: 6px;
                        padding: 4px 0px;
                    }
                    QPushButton:hover {
                        background-color: #E0E7FF;
                    }
                """)
            else:
                chart_body.setGraphicsEffect(None)
                chart_body.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
                btn_chart_blur.setText("Gizle")
                btn_chart_blur.setStyleSheet("""
                    QPushButton {
                        font-size: 11px;
                        font-weight: 700;
                        color: #64748B;
                        background-color: #F1F5F9;
                        border: 1px solid #E2E8F0;
                        border-radius: 6px;
                        padding: 4px 0px;
                    }
                    QPushButton:hover {
                        background-color: #E2E8F0;
                        color: #334155;
                    }
                """)

        btn_chart_blur.clicked.connect(_toggle_chart_blur)

        plot_widget = pg.PlotWidget()
        plot_widget.setMinimumHeight(680)
        plot_widget.setTitle(
            f"<span style='font-size: 13pt; font-weight: 700; color: #0F172A;'>{x_col} &nbsp;vs&nbsp; {y_col} &nbsp;&nbsp;•&nbsp;&nbsp; SERPME DİYAGRAMI VE REGRESYON ÇİZGİSİ</span><br/>"
        )
        plot_widget.setLabel('bottom', f"<br/><span style='font-size: 11pt; font-weight: 600; color: #475569;'>BAĞIMSIZ DEĞİŞKEN (X): &nbsp; <b style='color:#4F46E5;'>{x_col}</b></span>")
        plot_widget.setLabel('left', f"<span style='font-size: 11pt; font-weight: 600; color: #475569;'>BAĞIMLI DEĞİŞKEN (Y): &nbsp; <b style='color:#4F46E5;'>{y_col}</b></span><br/>")
        style_plot_widget(plot_widget)

        a = pd.to_numeric(self.df[x_col], errors='coerce').dropna().to_numpy()
        b = pd.to_numeric(self.df[y_col], errors='coerce').dropna().to_numpy()
        min_len = min(len(a), len(b))
        a = a[:min_len]
        b = b[:min_len]

        scatter = pg.ScatterPlotItem(
            x=a, y=b,
            pen=pg.mkPen('#3730A3', width=1.5),
            brush=pg.mkBrush('#6366F1'),
            size=12,
            symbol='o',
        )
        plot_widget.addItem(scatter)

        sort_idx = np.argsort(a)
        pred_sorted = self.pred[sort_idx]
        a_sorted = a[sort_idx]

        plot_widget.plot(
            a_sorted, pred_sorted,
            pen=pg.mkPen('#4F46E5', width=3.0, style=Qt.PenStyle.SolidLine),
        )

        chart_body_layout.addWidget(plot_widget)
        chart_layout.addWidget(chart_body)

        # En Yeni Analiz Grafiğini En Üste Ekle (Stoklama Yapısı)
        self.tab_chart_layout.insertWidget(0, chart_box)

    def _clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self._clear_layout(child.layout())


if __name__ == "__main__":
    apply_pyqtgraph_theme()

    app = QApplication(sys.argv)
    setup_light_palette(app)
    app.setStyleSheet(get_stylesheet())

    window = MainWindow()
    window.show()
    sys.exit(app.exec())
