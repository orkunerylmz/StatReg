import sys
import pyqtgraph as pg
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import f


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

        self.df = pd.DataFrame()

        self.setWindowTitle("StatReg")
        self.setGeometry(200, 100, 1000, 600)


        
    def button1(self):
        col_count = self.table.columnCount()
        self.table.insertColumn(col_count)

        for row in range(self.table.rowCount()):
            item = QTableWidgetItem("")
            item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, col_count, item)


    def button2(self):
        row_count = self.table.rowCount()
        self.table.insertRow(row_count)
        
        for col in range(self.table.columnCount()):
            item = QTableWidgetItem("")
            item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row_count, col, item)
            

    def button3(self):
        current_column = self.table.currentColumn()
        if current_column >= 0:
            self.table.removeColumn(current_column)
            
        else:
            QMessageBox.warning(self, "Uyarı", "Silinecek sütun seçilmedi.")


    def button4(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            self.table.removeRow(current_row)
            
        else:
            QMessageBox.warning(self, "Uyarı", "Silinecek satır seçilmedi.")


    def button5(self):
        self.table.clear()
        



    def button6(self):
        
        file_path, _ = QFileDialog.getOpenFileName(self, "Dosya Seç", "", "CSV Files (*.csv)")
        
        if file_path:
        
            self.df = pd.read_csv(file_path)
            
            
            self.table.setRowCount(self.df.shape[0])
            self.table.setColumnCount(self.df.shape[1])


            # headers = [f"{col} ({dtype})" for col, dtype in zip(df.columns, df.dtypes.astype(str))]
            headers = [col for col in self.df.columns]

            self.table.setHorizontalHeaderLabels(headers)
            
        
            for row in range(self.df.shape[0]):
                for col in range(self.df.shape[1]):
                    self.table.setItem(row, col, QTableWidgetItem(str(self.df.iloc[row, col])))


    def button7(self):

        if self.table.rowCount() == 0 or self.table.columnCount() == 0:
            self.df = pd.DataFrame() 

        if hasattr(self, "df") and not self.df.empty:
            df_source = "loaded"
        else:
            data = []
            for row in range(self.table.rowCount()):
                row_data = []
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    row_data.append(item.text() if item else None)
                data.append(row_data)

            # Geçici sütun adları
            column_names = [f"Sütun {i+1}" for i in range(self.table.columnCount())]

            # DataFrame'e çevir
            df_manual = pd.DataFrame(data, columns=column_names)

            # Tüm hücreleri sayısala çevir
            df_manual = df_manual.apply(pd.to_numeric, errors="coerce")

            # Tamamen boş olan sütunları (içi hep NaN olanları) at
            df_manual.dropna(axis=1, how="all", inplace=True)

            # Tamamen boş satırları da istersen at (bu opsiyonel)
            df_manual.dropna(axis=0, how="all", inplace=True)

            # Geçerli sütun kaldı mı kontrol et
            if df_manual.shape[1] < 2:
                QMessageBox.warning(self, "Uyarı", "Yeterli sayıda geçerli sütun girilmedi.")
                return

            self.df = df_manual
            df_source = "manual"


        # Kolon seçim arayüzü
        column_headers = list(self.df.columns)

        dialog = QDialog(self)
        dialog.setWindowTitle("Sütun Seç")
        dialog.setGeometry(350, 200, 400, 400)
        layout = QVBoxLayout(dialog)

        def create_list_widget(title):
            group = QGroupBox(title)
            vbox = QVBoxLayout(group)
            list_widget = QListWidget()
            list_widget.setDragEnabled(True)
            list_widget.setAcceptDrops(True)
            list_widget.setDropIndicatorShown(True)
            list_widget.setDefaultDropAction(Qt.DropAction.MoveAction)
            list_widget.setDragDropMode(QListWidget.DragDropMode.DragDrop)
            vbox.addWidget(list_widget)
            layout.addWidget(group)
            return list_widget

        self.general_list = create_list_widget("Sütunlar")
        self.dependent_list = create_list_widget("Bağımlı Sütunlar")
        self.independent_list = create_list_widget("Bağımsız Sütunlar")

        for header in column_headers:
            self.general_list.addItem(header)

        close_button = QPushButton("Kapat")
        close_button.clicked.connect(dialog.accept)
        layout.addWidget(close_button)
        dialog.exec()

        # Sütunları kontrol et
        independent_items = [self.independent_list.item(i).text() for i in range(self.independent_list.count())]
        dependent_items = [self.dependent_list.item(i).text() for i in range(self.dependent_list.count())]

        if len(independent_items) != 1 or len(dependent_items) != 1:
            QMessageBox.warning(self, "Uyarı", "Lütfen sadece bir bağımsız ve bir bağımlı sütun seçin.")
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
            QMessageBox.critical(self, "Hata", f"Veriler sayısal değil veya hatalı: {e}")
            return





        # Regresyonu uygula
        self.regression(x.values, y.values)

        self.independent_col = independent_items[0]
        self.dependent_col = dependent_items[0]

        self.tab2_result_hbox = QHBoxLayout()
        self.tab2_title_vbox = QVBoxLayout()
        self.tab2_result_hbox.addLayout(self.tab2_title_vbox)






        self.result_table = QTableWidget(1,3)
        self.result_table.setShowGrid(True)

        self.result_table.setMinimumHeight(150)
        self.result_table.setMaximumHeight(150)
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.result_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)





        self.result_table_2 = QTableWidget(2,5)
        self.result_table_2.setShowGrid(True)







        self.result_table_3 = QTableWidget(3,6)
        self.result_table_3.setShowGrid(True)

        self.result_table_3.setMinimumHeight(175)
        self.result_table_3.setMaximumHeight(175)
        self.result_table_3.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.result_table_3.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.result_table_3.verticalHeader().setVisible(False)
        self.result_table_3.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)



        font = QFont()
        font.setBold(True)
        self.result_table.horizontalHeader().setFont(font)
        self.result_table_2.horizontalHeader().setFont(font)
        self.result_table_3.horizontalHeader().setFont(font)


        text = "REGRESYON SONUCLARI"
        self.label = QLabel(text)

        text1 = "ANOVA TEST"
        self.label1 = QLabel(text1)



        self.table_splitter = QSplitter()
        
        self.table_splitter.addWidget(self.result_table)
        self.table_splitter.addWidget(self.result_table_2)
        self.table_splitter.setSizes([350, 500])

        self.tab2_title_vbox.addWidget(self.label)
        self.tab2_title_vbox.addWidget(self.table_splitter)
        self.tab2_title_vbox.addWidget(self.label1)

        self.tab2_title_vbox.addWidget(self.result_table_3)

        self.result_table_2.setMinimumHeight(150)
        self.result_table_2.setMaximumHeight(150)
        self.result_table_2.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.result_table_2.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)


        self.result_table.verticalHeader().setVisible(False)
        self.result_table_2.verticalHeader().setVisible(False)

        self.result_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.result_table_2.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)


        self.result_table.setHorizontalHeaderLabels(["Model", "R", "R²"])

        self.item1 = QTableWidgetItem("Model")
        self.item2 = QTableWidgetItem(str(f"{self.r:.3f}"))
        self.item3 = QTableWidgetItem(str(f"{self.r_kare:.3f}"))

        self.item1.setTextAlignment(Qt.AlignmentFlag.AlignCenter) 
        self.item2.setTextAlignment(Qt.AlignmentFlag.AlignCenter) 
        self.item3.setTextAlignment(Qt.AlignmentFlag.AlignCenter) 

        self.result_table.setItem(0, 0, self.item1)
        self.result_table.setItem(0, 1, self.item2)
        self.result_table.setItem(0, 2, self.item3)

        self.result_table_2.setHorizontalHeaderLabels(["Predictor", "Estimate", "SE", "t", "p"])


        self.item4 = QTableWidgetItem("Intercept")
        self.item5 = QTableWidgetItem(str(f"{self.b0:.3f}"))
        self.item6 = QTableWidgetItem(str(f"{self.se:.3f}"))
        self.item7 = QTableWidgetItem(str(f"{self.ti:.3f}"))
        self.item8 = QTableWidgetItem(str(f"{self.pi:.3f}"))
        self.item9 = QTableWidgetItem(self.independent_col)
        self.item10 = QTableWidgetItem(str(f"{self.b1:.3f}"))
        self.item11 = QTableWidgetItem(str(f"{self.sb1:.3f}"))
        self.item12 = QTableWidgetItem(str(f"{self.th:.3f}"))
        self.item13 = QTableWidgetItem(str(f"{self.ph:.3f}"))


        self.item4.setTextAlignment(Qt.AlignmentFlag.AlignCenter) 
        self.item5.setTextAlignment(Qt.AlignmentFlag.AlignCenter) 
        self.item6.setTextAlignment(Qt.AlignmentFlag.AlignCenter) 
        self.item7.setTextAlignment(Qt.AlignmentFlag.AlignCenter) 
        self.item8.setTextAlignment(Qt.AlignmentFlag.AlignCenter) 
        self.item9.setTextAlignment(Qt.AlignmentFlag.AlignCenter) 
        self.item10.setTextAlignment(Qt.AlignmentFlag.AlignCenter) 
        self.item11.setTextAlignment(Qt.AlignmentFlag.AlignCenter) 
        self.item12.setTextAlignment(Qt.AlignmentFlag.AlignCenter) 
        self.item13.setTextAlignment(Qt.AlignmentFlag.AlignCenter) 

        self.result_table_2.setItem(0, 0, self.item4)
        self.result_table_2.setItem(0, 1, self.item5)
        self.result_table_2.setItem(0, 2, self.item6)
        self.result_table_2.setItem(0, 3, self.item7)
        self.result_table_2.setItem(0, 4, self.item8)
        self.result_table_2.setItem(1, 0, self.item9)
        self.result_table_2.setItem(1, 1, self.item10)
        self.result_table_2.setItem(1, 2, self.item11)
        self.result_table_2.setItem(1, 3, self.item12)
        self.result_table_2.setItem(1, 4, self.item13)






        self.result_table_3.setHorizontalHeaderLabels(["Model", "Sum of Squares", "df", "Mean Square", "F", "prob"])

        self.item14 = QTableWidgetItem("Regression")
        self.item15 = QTableWidgetItem(str(f"{self.rkt:.3f}"))
        self.item16 = QTableWidgetItem("1")
        self.item17 = QTableWidgetItem(str(f"{self.rko:.3f}"))
        self.item18 = QTableWidgetItem(str(f"{(self.rko / self.rako):.3f}"))
        self.item19 = QTableWidgetItem(str(f"{self.prob:.3f}"))

        self.item20 = QTableWidgetItem("Residual")
        self.item21 = QTableWidgetItem(str(f"{self.rakt:.3f}"))
        self.item22 = QTableWidgetItem(str(self.n - 2))
        self.item23 = QTableWidgetItem(str(f"{self.rako:.3f}"))
        self.item24 = QTableWidgetItem("")
        self.item25 = QTableWidgetItem("")


        self.item26 = QTableWidgetItem("Total")
        self.item27 = QTableWidgetItem(str(f"{self.yoakt:.3f}"))
        self.item28 = QTableWidgetItem(str(self.n - 1))
        self.item29 = QTableWidgetItem("")
        self.item30 = QTableWidgetItem("")
        self.item31 = QTableWidgetItem("")
        


        self.item14.setTextAlignment(Qt.AlignmentFlag.AlignCenter) 
        self.item15.setTextAlignment(Qt.AlignmentFlag.AlignCenter) 
        self.item16.setTextAlignment(Qt.AlignmentFlag.AlignCenter) 
        self.item17.setTextAlignment(Qt.AlignmentFlag.AlignCenter) 
        self.item18.setTextAlignment(Qt.AlignmentFlag.AlignCenter) 
        self.item19.setTextAlignment(Qt.AlignmentFlag.AlignCenter) 
        self.item20.setTextAlignment(Qt.AlignmentFlag.AlignCenter) 
        self.item21.setTextAlignment(Qt.AlignmentFlag.AlignCenter) 
        self.item22.setTextAlignment(Qt.AlignmentFlag.AlignCenter) 
        self.item23.setTextAlignment(Qt.AlignmentFlag.AlignCenter) 
        self.item24.setTextAlignment(Qt.AlignmentFlag.AlignCenter) 
        self.item25.setTextAlignment(Qt.AlignmentFlag.AlignCenter) 
        self.item26.setTextAlignment(Qt.AlignmentFlag.AlignCenter) 
        self.item27.setTextAlignment(Qt.AlignmentFlag.AlignCenter) 
        self.item28.setTextAlignment(Qt.AlignmentFlag.AlignCenter) 
        self.item29.setTextAlignment(Qt.AlignmentFlag.AlignCenter) 
        self.item30.setTextAlignment(Qt.AlignmentFlag.AlignCenter) 
        self.item31.setTextAlignment(Qt.AlignmentFlag.AlignCenter) 

        self.result_table_3.setItem(0, 0, self.item14)
        self.result_table_3.setItem(0, 1, self.item15)
        self.result_table_3.setItem(0, 2, self.item16)
        self.result_table_3.setItem(0, 3, self.item17)
        self.result_table_3.setItem(0, 4, self.item18)
        self.result_table_3.setItem(0, 5, self.item19)
        self.result_table_3.setItem(1, 0, self.item20)
        self.result_table_3.setItem(1, 1, self.item21)
        self.result_table_3.setItem(1, 2, self.item22)
        self.result_table_3.setItem(1, 3, self.item23)
        self.result_table_3.setItem(1, 4, self.item24)
        self.result_table_3.setItem(1, 5, self.item25)
        self.result_table_3.setItem(2, 0, self.item26)
        self.result_table_3.setItem(2, 1, self.item27)
        self.result_table_3.setItem(2, 2, self.item28)





        self.result_widget = QWidget()
        self.result_widget.setLayout(self.tab2_result_hbox)

        self.tab2_result_vbox.insertWidget(0, self.result_widget)





        
        self.plot_widget = pg.PlotWidget()

        self.plot_widget.setMinimumHeight(600)
        self.plot_widget.setMaximumHeight(600)

        a = self.df[x_col].to_numpy()
        b = self.df[y_col].to_numpy()

        min_len = min(len(a), len(b))
        a = a[:min_len]
        b = b[:min_len]


        self.plot_widget.plot(a, b, pen = None, symbol = 'o', symbolBrush = 'red', symbolSize = 10)

        self.plot_widget.plot(a, self.pred, pen=pg.mkPen('b', width=3.5))
        self.plot_widget.setBackground("w")
        self.plot_widget.showGrid(x=True, y=True)
        self.plot_widget.setTitle(f"{self.independent_col} - {self.dependent_col}", size = "20pt")
        self.plot_widget.setLabel('bottom', x_col)
        self.plot_widget.setLabel('left', y_col)

        self.tab3_vbox.insertWidget(0, self.plot_widget)


    def regression(self, x, y):


        def sum_value(value):

            sum = 0
            for num in value:
                sum += num
            return sum
        
        def mean_value(value):

            sum = 0
            for num in value:
                sum += num
            value_n = len(value)
            mean = sum / value_n

            return mean
    
        def sqrt_value(value):
            return value ** (1/2)
    
        def square_value(value):
            return value * value

        

    


        self.n = len(x) 
    
        self.sum_y = sum_value(y)
        self.sum_x = sum_value(x)
        self.mult = x*y
        self.sum_mult = sum_value(self.mult)
        self.square_x = square_value(x)
        self.square_y = square_value(y)
        self.sum_squ_x = sum_value(self.square_x)
        self.sum_squ_y = sum_value(self.square_y)
        self.mean_x = mean_value(x)
        self.mean_y = mean_value(y)
        self.xoakt = sum_value(square_value(x - self.mean_x))
        self.yoakt = sum_value(square_value(y - self.mean_y))
        self.xyct = sum_value((x - self.mean_x) * (y - self.mean_y))
        self.b1 = (self.xyct / self.xoakt)
        self.b0 = (self.mean_y) - (self.b1 * self.mean_x)
        self.rkt = self.b1 * self.xyct
        self.rakt = (self.yoakt - self.rkt)
        self.rko = (self.rkt / 1)
        self.rako = ((self.rakt) / (self.n - 2))
        self.sb1 = sqrt_value(self.rako / self.xoakt)
        self.th = (self.b1 / self.sb1)
        self.r_kare = (self.rkt / self.yoakt)
        self.r = sqrt_value(self.r_kare)

        self.pred = self.b0 + (self.b1 * x)
        self.e = y - self.pred
        self.rss = sum_value(square_value(self.e))
        self.varyans = (self.rss / (self.n - 2))
        self.se = sqrt_value(self.varyans * ((1 / self.n) + (square_value(self.mean_x) / (self.xoakt))))
        self.ti = (self.b0 / self.se)
        self.ph = 2 * (1 - stats.t.cdf(self.th, self.n-2))
        self.pi = 2 * (1 - stats.t.cdf(self.ti, self.n-2))



        self.f = (self.rko / self.rako)
        self.prob = f.sf(self.f, 1, self.n-2)








    def on_tab_changed(self, index):
        self.table.setParent(None)

        if index == 0:
            self.tab1_vbox.addWidget(self.table, stretch = 20)


        elif index == 1:
            if self.table.parent() != self.splitter:
                self.splitter.addWidget(self.table)
                self.splitter.setSizes([600,400])

        elif index == 2:
            if self.table.parent() != self.splitter:
                self.splitter.addWidget(self.table)
                self.splitter.setSizes([600,400])


    def initUI(self):

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_vbox = QVBoxLayout()
        self.main_hbox = QHBoxLayout()
        self.main_vbox.addLayout(self.main_hbox)
        self.main_vbox.setContentsMargins(0, 0, 0, 0)
        self.main_vbox.setSpacing(0)


        self.button_1 = QPushButton("Sütun Ekle")
        self.button_1.clicked.connect(self.button1)     

        self.button_2 = QPushButton("Satır Ekle")
        self.button_2.clicked.connect(self.button2)     
        
        self.button_3 = QPushButton("Sütun Sil")
        self.button_3.clicked.connect(self.button3)     
        
        self.button_4 = QPushButton("Satır Sil")
        self.button_4.clicked.connect(self.button4)     
        
        self.button_5 = QPushButton("Tabloyu Temizle")
        self.button_5.clicked.connect(self.button5)     

        self.button_6 = QPushButton("Dosya Yükle")
        self.button_6.clicked.connect(self.button6)     

        self.button_7 = QPushButton("Regresyon Hesapla")
        self.button_7.clicked.connect(self.button7)     


        self.tab_widget = QTabWidget()

        self.tab1 = QWidget()
        self.tab1_vbox = QVBoxLayout()
        self.tab1_hbox = QHBoxLayout()
        self.tab1_vbox.addLayout(self.tab1_hbox)
        self.tab1.setLayout(self.tab1_vbox)

        self.tab2 = QWidget()
        self.tab2_vbox = QVBoxLayout()
        self.tab2_button_vbox = QVBoxLayout()
        self.tab2_result_vbox = QVBoxLayout()
        self.tab2_vbox.addLayout(self.tab2_button_vbox)
        self.tab2_vbox.addLayout(self.tab2_result_vbox)
        self.tab2.setLayout(self.tab2_vbox)
        self.tab2.adjustSize() 

        self.scroll_tab2 = QScrollArea()
        self.scroll_tab2.setWidgetResizable(True)
        self.scroll_tab2.setWidget(self.tab2)

        self.tab3 = QWidget()
        self.tab3_vbox = QVBoxLayout()
        self.tab3_hbox = QHBoxLayout()
        self.tab3_vbox.addLayout(self.tab3_hbox)
        self.tab3.setLayout(self.tab3_vbox)
        self.tab3.adjustSize() 

        self.scroll_tab3 = QScrollArea()
        self.scroll_tab3.setWidgetResizable(True)
        self.scroll_tab3.setWidget(self.tab3)

        self.tab_widget.addTab(self.tab1, "Tablo İçeriği")
        self.tab_widget.addTab(self.scroll_tab2, "Regresyon Analizi")
        self.tab_widget.addTab(self.scroll_tab3, "Görselleştirme")


        self.table = QTableWidget(30, 15)
        self.table.setAlternatingRowColors(True)


        self.tab_menu_1 = QTabWidget()
        
        self.tab1_menu = QWidget()
        self.tab1_menu_hbox = QHBoxLayout()
        self.tab1_menu.setLayout(self.tab1_menu_hbox)

        self.tab2_menu = QWidget()
        self.tab2_menu_hbox = QHBoxLayout()
        self.tab2_menu.setLayout(self.tab2_menu_hbox)

        self.tab_menu_1.addTab(self.tab1_menu, "Düzenleme Araçları")
        self.tab_menu_1.addTab(self.tab2_menu, "Dosya İşlemleri")


        self.tab1_menu_hbox.addWidget(self.button_1)
        self.tab1_menu_hbox.addWidget(self.button_2)
        self.tab1_menu_hbox.addWidget(self.button_3)
        self.tab1_menu_hbox.addWidget(self.button_4)
        self.tab1_menu_hbox.addWidget(self.button_5)
        self.tab1_menu_hbox.addStretch()

        self.tab1_vbox.addWidget(self.tab_menu_1, stretch = 1)
        self.tab1_vbox.addWidget(self.table, stretch = 20)


        self.tab2_menu_hbox.addWidget(self.button_6)
        self.tab2_menu_hbox.addStretch()

        self.tab2_button_vbox.addWidget(self.button_7)
        self.tab2_vbox.addStretch()


        self.tab_widget.currentChanged.connect(self.on_tab_changed)

        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        self.main_vbox.addWidget(self.splitter)
        self.splitter.addWidget(self.tab_widget)


        self.central_widget.setLayout(self.main_vbox)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())





