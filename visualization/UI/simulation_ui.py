import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtCore import QTimer, QEventLoop, Qt
import redis
import json
import math


class Toast(QWidget):
    def __init__(self, message, duration=2000):
        super().__init__()
        self.setWindowFlags(Qt.SplashScreen | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowOpacity(0.9)

        layout = QVBoxLayout()
        label = QLabel(message, self)
        label.setStyleSheet(
            "background-color: rgba(0, 0, 0, 160); color: white; font-size: 16px; padding: 10px; border-radius: 8px;")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        self.setLayout(layout)

        QTimer.singleShot(duration, self.close)

    def display(self, parent):
        parent_geometry = parent.frameGeometry()
        self.move(
            int(parent_geometry.x() + parent_geometry.width() / 2 - self.width() / 2),
            int(parent_geometry.y() + parent_geometry.height() - self.height() - 10)
        )
        self.show()

class SimulationUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.redis = redis.Redis(host='localhost', port=6379, db=0)

        self.initUI()


    def initUI(self):
        self.setWindowTitle("Microservices System Simulation")
        self.setGeometry(100, 100, 800, 600)

        centralWidget = QWidget(self)
        self.setCentralWidget(centralWidget)
        layout = QVBoxLayout(centralWidget)

        self.timeDisplay = QLabel("Time: --:--:--")
        self.timeDisplay.setStyleSheet("font-size: 18px; padding: 10px;")
        layout.addWidget(self.timeDisplay)
        #System-wide data display
        self.systemDataDisplay = QLabel("Loading...")
        self.systemDataDisplay.setStyleSheet("font-size: 16px; padding: 10px;")
        layout.addWidget(self.systemDataDisplay)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(['Instance ID', 'Resource Usage', 'Requests Processed', 'Status', 'Instance Type', 'DB Instance'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        #Databases Table
        self.databasesTable = QTableWidget()
        self.databasesTable.setColumnCount(4)
        self.databasesTable.setHorizontalHeaderLabels(['DB Instance ID', 'Connections', 'Disk IO', 'Status'])
        self.databasesTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.databasesTable)

    def update_ui(self):
        data = self.get_data()

        time_data = data.get('time', {}).get('data', {})
        self.timeDisplay.setText(f"Time: Day {time_data.get('day', '--')}, Hour {time_data.get('hour', '--')}, Minute {time_data.get('minuite', '--')}")
        system_data = data.get('system_data', {})
        
        avg_cpu = system_data.get('avg_cpu', '--')
        if isinstance(avg_cpu, float):
            cpu_info = f"Avg CPU: {avg_cpu:.2f} "
        else:
            cpu_info = f"Avg CPU: {avg_cpu} "

        drop_rate = system_data.get('request_drop_rate', '--')
        if drop_rate != '--':
            #Limit the drop rate to two decimals
            drop_rate = round(float(drop_rate), 2)

        system_info = (f"{cpu_info}, "
                f"Total Requests Processed: {system_data.get('total_requests_processed', '--')}, "
                # f"Unprocessed Requests: {system_data.get('total_requests_unprocessed', '--')}, "
                f"Request Drop Rate %: {drop_rate}"
                )
        self.systemDataDisplay.setText(f"{system_info}")

        #Prepare and sort data list for the table
        instances = [
            (
                instance_id,
                ( details.get('cpu_usage', 0) / details.get('max_cpu', 500) ) * 100,
                details.get('requests_processed', 0),
                'Down' if details.get('status', 0) == 0 else 'Up',
                details.get('instance_type', 'Unknown'),
                details.get('database_instance', 'None')
            )
            for instance_id, details in data.get('instances', {}).items()
        ]
        instances.sort(key=lambda x: x[1], reverse=True)  # Sort by CPU usage

        #Update the table
        self.table.setRowCount(0)
        for instance in instances:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            for col, item in enumerate(instance):
                if col == 1:
                    self.table.setItem(row_position, col, QTableWidgetItem(f"{item:.2f}%"))
                else:
                    self.table.setItem(row_position, col, QTableWidgetItem(str(item)))

        #DATA BASE Table
        databases = [
            (
                db_id,
                details.get('current_connections', 0),
                details.get('disk_io_usage', 0),
                details.get('status', '--')
            )
            for db_id, details in data.get('database_services', {}).items()
        ]

        databases.sort(key=lambda x: x[1], reverse=True)

        self.databasesTable.setRowCount(0)
        for db in databases:
            row_position = self.databasesTable.rowCount()
            self.databasesTable.insertRow(row_position)
            for col, item in enumerate(db):
                self.databasesTable.setItem(row_position, col, QTableWidgetItem(str(item)))




    def get_data(self):
        #Fetch data from KeyDB
        json_data = self.redis.get('maestro_meta_data')
        print(f"maestro_meta_data",json_data)
        if json_data:
            #Deserialize the JSON string into a dictionary
            data = json.loads(json_data)
        else:
            data = {}
        
        return data

    def run_ui(self):
        while True:
            self.update_ui()
            QApplication.processEvents()
            QApplication.processEvents()
            self.delay(1000)

    def delay(self, milliseconds):
        loop = QEventLoop()
        QTimer.singleShot(milliseconds, loop.quit)
        loop.exec_()

    def showToast(self, message):
        toast = Toast(message)
        toast.display(self)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SimulationUI()
    window.show()
    window.run_ui()
    sys.exit(app.exec_())
