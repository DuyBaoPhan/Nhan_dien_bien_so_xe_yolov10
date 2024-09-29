import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PIL import Image
import cv2
import numpy as np
import csv
import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from detect import process_image, update_csv_file

class CameraThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)

    def run(self):
        cap = cv2.VideoCapture(0)

        while True:
            ret, frame = cap.read()
            if ret:
                self.change_pixmap_signal.emit(frame)
            QThread.msleep(30)

        cap.release()

class PlotWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Biểu Đồ Thống Kê")
        self.setGeometry(200, 200, 800, 600)

        self.figure = plt.Figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def update_plot(self, data):
        self.ax.clear()
        dates, counts_in, counts_out = data

        width = 0.4
        x = np.arange(len(dates))

        self.ax.bar(x - width/2, counts_in, width, label='Xe vào', color='blue')
        self.ax.bar(x + width/2, counts_out, width, label='Xe ra', color='red')

        self.ax.set_xlabel('Ngày')
        self.ax.set_ylabel('Số xe')
        self.ax.set_title('Số xe vào và ra trong tháng')
        self.ax.set_xticks(x)
        self.ax.set_xticklabels(dates, rotation=45, ha='right')
        self.ax.legend()

        self.canvas.draw()

class YearlyPlotWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Biểu Đồ Thống Kê Theo Tháng")
        self.setGeometry(200, 200, 800, 600)

        self.figure = plt.Figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def update_plot(self, data):
        self.ax.clear()
        months, counts_in, counts_out = data

        width = 0.4
        x = np.arange(len(months))

        self.ax.bar(x - width/2, counts_in, width, label='Xe vào', color='blue')
        self.ax.bar(x + width/2, counts_out, width, label='Xe ra', color='red')

        self.ax.set_xlabel('Tháng')
        self.ax.set_ylabel('Số xe')
        self.ax.set_title('Số xe vào và ra trong năm')
        self.ax.set_xticks(x)
        self.ax.set_xticklabels(months, rotation=45, ha='right')
        self.ax.legend()

        self.canvas.draw()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()
        self.camera_thread = CameraThread()
        self.camera_thread.change_pixmap_signal.connect(self.update_image)
        self.camera_thread.start()

        self.recent_plates = []
        self.load_recent_plates()
        self.update_total_count()

        self.plot_window = PlotWindow()
        self.plot_window.hide()  # Hide the window initially

        self.yearly_plot_window = YearlyPlotWindow()
        self.yearly_plot_window.hide()  # Hide the window initially

    def initUI(self):
        self.setWindowTitle("License Plate Detection")
        self.setGeometry(100, 100, 1600, 900)

        main_layout = QVBoxLayout(self)

        # Tạo QLabel cho tiêu đề
        self.title_label = QLabel("Nhận diện biển số", self)
        self.title_label.setAlignment(Qt.AlignCenter)  # Căn giữa tiêu đề
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
    
        # Thêm tiêu đề vào layout chính
        main_layout.addWidget(self.title_label, alignment=Qt.AlignCenter)

        camera_detect_layout = QHBoxLayout()

        self.camera_label = QLabel(self)
        self.camera_label.setMinimumSize(640, 480)
        camera_detect_layout.addWidget(self.camera_label)

        self.detect_label = QLabel(self)
        self.detect_label.setMinimumSize(640, 480)
        camera_detect_layout.addWidget(self.detect_label)

        main_layout.addLayout(camera_detect_layout)

        self.capture_button = QPushButton("Chụp ảnh", self)
        self.capture_button.clicked.connect(self.capture_image)
        self.capture_button.setMinimumWidth(100)
        self.capture_button.setStyleSheet("font-size: 16px; padding: 10px;")
        main_layout.addWidget(self.capture_button, alignment=Qt.AlignCenter)

        self.status_label = QLabel(self)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 18px;")
        main_layout.addWidget(self.status_label)

        self.search_layout = QHBoxLayout()
        self.search_line_edit = QLineEdit(self)
        self.search_line_edit.setPlaceholderText("Nhập biển số cần tìm...")
        self.search_line_edit.setMaximumWidth(200)
        self.search_line_edit.textChanged.connect(self.on_search_text_changed)
        self.search_layout.addWidget(self.search_line_edit)

        self.search_button = QPushButton("Tìm kiếm", self)
        self.search_button.setMaximumWidth(100)
        self.search_button.setMinimumWidth(80)
        self.search_button.clicked.connect(self.search_plate)
        self.search_layout.addWidget(self.search_button)
        main_layout.addLayout(self.search_layout)

        self.plates_table = QTableWidget(self)
        self.plates_table.setColumnCount(3)
        self.plates_table.setHorizontalHeaderLabels(["Thời gian", "Biển số", "Trạng thái"])
        self.plates_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.plates_table.setMaximumHeight(150)
        main_layout.addWidget(self.plates_table)

        self.total_count_label = QLabel(self)
        self.total_count_label.setAlignment(Qt.AlignCenter)
        self.total_count_label.setStyleSheet("font-size: 18px;")
        main_layout.addWidget(self.total_count_label)

        button_layout = QHBoxLayout()

        self.show_plot_button = QPushButton("Biểu đồ thống kê tháng", self)
        self.show_plot_button.setMinimumWidth(200)
        self.show_plot_button.setStyleSheet("font-size: 16px; padding: 10px;")
        self.show_plot_button.clicked.connect(self.show_plot_window)
        button_layout.addWidget(self.show_plot_button)

        self.show_yearly_plot_button = QPushButton("Biểu đồ thống kê năm", self)
        self.show_yearly_plot_button.setMinimumWidth(200)
        self.show_yearly_plot_button.setStyleSheet("font-size: 16px; padding: 10px;")
        self.show_yearly_plot_button.clicked.connect(self.show_yearly_plot_window)
        button_layout.addWidget(self.show_yearly_plot_button)

        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)


    def show_plot_window(self):
        self.update_plot()
        self.plot_window.show()

    def show_yearly_plot_window(self):
        self.update_yearly_plot()
        self.yearly_plot_window.show()

    def capture_image(self):
        frame = self.last_frame.copy()
        image_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        processed_image, recognized_texts, found_plate, status = process_image(image_pil)

        if found_plate:
            if recognized_texts:
                recognized_text = ''.join(recognized_texts).replace(" ", "")
                update_csv_file([recognized_text], status)
                self.status_label.setText(f"Xe biển số {recognized_text} đã đi {status}")
                current_time = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
                self.add_to_recent_plates(current_time, recognized_text, status)
                self.update_total_count()  # Update the total count whenever a car is detected
                self.update_plot()  # Update the plot data whenever a car is detected
            else:
                print("Không nhận diện được ký tự trên biển số.")

            processed_image = cv2.cvtColor(processed_image, cv2.COLOR_BGR2RGB)
            h, w, ch = processed_image.shape
            bytes_per_line = ch * w
            convert_to_qt_format = QImage(processed_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(convert_to_qt_format)
            self.detect_label.setPixmap(pixmap)
        else:
            print("Không tìm thấy biển số xe trong hình ảnh.")
            self.status_label.setText("Không tìm thấy biển số xe trong hình ảnh.")

    def update_image(self, frame):
        self.last_frame = frame.copy()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        convert_to_qt_format = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(convert_to_qt_format)
        self.camera_label.setPixmap(pixmap)

    def load_recent_plates(self):
        self.clear_table()
        with open('number_plate.csv', mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            rows = list(reader)[-5:]

        for row in reversed(rows):
            self.add_to_recent_plates(row[0], row[1], row[2])

    def add_to_recent_plates(self, time, plate_number, status):
        if self.plates_table.rowCount() >= 5:
            self.plates_table.removeRow(self.plates_table.rowCount() - 1)

        self.plates_table.insertRow(0)
        self.plates_table.setItem(0, 0, QTableWidgetItem(time))
        self.plates_table.setItem(0, 1, QTableWidgetItem(plate_number))
        self.plates_table.setItem(0, 2, QTableWidgetItem(status))

    def search_plate(self):
        search_text = self.search_line_edit.text().strip().upper()
        if not search_text:
            self.load_recent_plates()
            return

        found = False
        with open('number_plate.csv', mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) >= 3 and row[1].strip() == search_text:
                    self.clear_table()
                    self.add_to_recent_plates(row[0], row[1], row[2])
                    found = True
                    break

        if not found:
            QMessageBox.warning(self, "Không tìm thấy", f"Không tìm thấy biển số xe '{search_text}' trong danh sách.")

    def clear_table(self):
        while self.plates_table.rowCount() > 0:
            self.plates_table.removeRow(0)

    def on_search_text_changed(self):
        if not self.search_line_edit.text().strip():
            self.load_recent_plates()

    def update_total_count(self):
        count = 0
        with open('number_plate.csv', mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) >= 3:
                    if row[2] == 'vào':
                        count += 1
                    elif row[2] == 'ra':
                        count -= 1
        self.total_count_label.setText(f"Tổng số xe trong bãi: {count}")

    def update_plot(self):
        data = self.get_monthly_data()
        self.plot_window.update_plot(data)

    def update_yearly_plot(self):
        data = self.get_yearly_data()
        self.yearly_plot_window.update_plot(data)

    def get_monthly_data(self):
        today = datetime.date.today()
        first_day_of_month = today.replace(day=1)

        dates = []
        counts_in = []
        counts_out = []

        for day in range((today - first_day_of_month).days + 1):
            date = first_day_of_month + datetime.timedelta(days=day)
            date_str = date.strftime('%Y-%m-%d')
            dates.append(date_str)

            count_in = 0
            count_out = 0

            with open('number_plate.csv', mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                for row in reader:
                    if len(row) >= 3:
                        record_date = datetime.datetime.strptime(row[0], "%d-%m-%Y %H:%M:%S").date()
                        if record_date == date:
                            if row[2] == 'vào':
                                count_in += 1
                            elif row[2] == 'ra':
                                count_out += 1

            counts_in.append(count_in)
            counts_out.append(count_out)

        return dates, counts_in, counts_out

    def get_yearly_data(self):
        today = datetime.date.today()
        first_day_of_year = today.replace(month=1, day=1)

        months = []
        counts_in = []
        counts_out = []

        for month in range(1, 13):
            date = first_day_of_year.replace(month=month)
            month_str = date.strftime('%Y-%m')
            months.append(month_str)

            count_in = 0
            count_out = 0

            with open('number_plate.csv', mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                for row in reader:
                    if len(row) >= 3:
                        record_date = datetime.datetime.strptime(row[0], "%d-%m-%Y %H:%M:%S").date()
                        if record_date.year == today.year and record_date.month == month:
                            if row[2] == 'vào':
                                count_in += 1
                            elif row[2] == 'ra':
                                count_out += 1

            counts_in.append(count_in)
            counts_out.append(count_out)

        return months, counts_in, counts_out

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
