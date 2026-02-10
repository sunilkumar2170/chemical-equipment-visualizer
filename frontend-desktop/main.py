import sys
import requests
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QFileDialog, QTableWidget,
                             QTableWidgetItem, QLabel, QLineEdit, QMessageBox)
from PyQt5.QtCore import Qt

API_URL = 'http://localhost:8000/api'

class LoginWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle('Login')
        self.setGeometry(100, 100, 400, 200)
        
        layout = QVBoxLayout()
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('Username')
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('Password')
        self.password_input.setEchoMode(QLineEdit.Password)
        
        login_btn = QPushButton('Login')
        login_btn.clicked.connect(self.login)
        
        layout.addWidget(QLabel('Username:'))
        layout.addWidget(self.username_input)
        layout.addWidget(QLabel('Password:'))
        layout.addWidget(self.password_input)
        layout.addWidget(login_btn)
        
        self.setLayout(layout)
    
    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        try:
            response = requests.get(
                f'{API_URL}/datasets/',
                auth=(username, password)
            )
            if response.status_code == 200:
                self.main_window.set_credentials(username, password)
                self.main_window.show()
                self.close()
            else:
                QMessageBox.warning(self, 'Error', 'Login failed!')
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.username = None
        self.password = None
        self.init_ui()
    
    def set_credentials(self, username, password):
        self.username = username
        self.password = password
    
    def init_ui(self):
        self.setWindowTitle('Chemical Equipment Visualizer - Desktop')
        self.setGeometry(100, 100, 1200, 800)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        
        # Upload section
        upload_layout = QHBoxLayout()
        self.file_label = QLabel('No file selected')
        select_btn = QPushButton('Select CSV')
        select_btn.clicked.connect(self.select_file)
        upload_btn = QPushButton('Upload')
        upload_btn.clicked.connect(self.upload_file)
        
        upload_layout.addWidget(self.file_label)
        upload_layout.addWidget(select_btn)
        upload_layout.addWidget(upload_btn)
        
        # Stats labels
        self.stats_label = QLabel()
        
        # Table
        self.table = QTableWidget()
        
        # Chart canvas
        self.figure, self.axes = plt.subplots(1, 2, figsize=(10, 4))
        self.canvas = FigureCanvasQTAgg(self.figure)
        
        # PDF button
        self.pdf_btn = QPushButton('Download PDF Report')
        self.pdf_btn.clicked.connect(self.download_pdf)
        self.pdf_btn.setEnabled(False)
        
        layout.addLayout(upload_layout)
        layout.addWidget(self.stats_label)
        layout.addWidget(self.canvas)
        layout.addWidget(self.table)
        layout.addWidget(self.pdf_btn)
        
        central_widget.setLayout(layout)
        
        self.selected_file = None
        self.current_dataset_id = None
    
    def select_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'Select CSV', '', 'CSV Files (*.csv)')
        if filename:
            self.selected_file = filename
            self.file_label.setText(filename)
    
    def upload_file(self):
        if not self.selected_file:
            QMessageBox.warning(self, 'Error', 'Please select a file first')
            return
        
        try:
            with open(self.selected_file, 'rb') as f:
                files = {'file': f}
                response = requests.post(
                    f'{API_URL}/datasets/upload_csv/',
                    files=files,
                    auth=(self.username, self.password)
                )
            
            if response.status_code == 200:
                data = response.json()
                self.display_data(data)
                self.current_dataset_id = data['data']['id']
                self.pdf_btn.setEnabled(True)
                QMessageBox.information(self, 'Success', 'File uploaded successfully!')
            else:
                QMessageBox.warning(self, 'Error', 'Upload failed!')
        
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))
    
    def display_data(self, data):
        stats = data['statistics']
        
        # Display stats
        stats_text = f"""
        Total Equipment: {stats['total_count']}
        Average Flowrate: {stats['avg_flowrate']:.2f}
        Average Pressure: {stats['avg_pressure']:.2f}
        Average Temperature: {stats['avg_temperature']:.2f}
        """
        self.stats_label.setText(stats_text)
        
        # Display table
        rows = data['rows']
        self.table.setRowCount(len(rows))
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature'])
        
        for i, row in enumerate(rows):
            self.table.setItem(i, 0, QTableWidgetItem(str(row['Equipment Name'])))
            self.table.setItem(i, 1, QTableWidgetItem(str(row['Type'])))
            self.table.setItem(i, 2, QTableWidgetItem(str(row['Flowrate'])))
            self.table.setItem(i, 3, QTableWidgetItem(str(row['Pressure'])))
            self.table.setItem(i, 4, QTableWidgetItem(str(row['Temperature'])))
        
        # Display charts
        self.axes[0].clear()
        self.axes[1].clear()
        
        # Pie chart
        equip_dist = stats['equipment_distribution']
        self.axes[0].pie(equip_dist.values(), labels=equip_dist.keys(), autopct='%1.1f%%')
        self.axes[0].set_title('Equipment Distribution')
        
        # Bar chart
        params = ['Flowrate', 'Pressure', 'Temperature']
        values = [stats['avg_flowrate'], stats['avg_pressure'], stats['avg_temperature']]
        self.axes[1].bar(params, values)
        self.axes[1].set_title('Average Parameters')
        
        self.canvas.draw()
    
    def download_pdf(self):
        if not self.current_dataset_id:
            return
        
        try:
            response = requests.get(
                f'{API_URL}/datasets/{self.current_dataset_id}/generate_pdf/',
                auth=(self.username, self.password)
            )
            
            if response.status_code == 200:
                filename, _ = QFileDialog.getSaveFileName(self, 'Save PDF', f'report_{self.current_dataset_id}.pdf', 'PDF Files (*.pdf)')
                if filename:
                    with open(filename, 'wb') as f:
                        f.write(response.content)
                    QMessageBox.information(self, 'Success', 'PDF downloaded successfully!')
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    login_window = LoginWindow(main_window)
    login_window.show()
    sys.exit(app.exec_())