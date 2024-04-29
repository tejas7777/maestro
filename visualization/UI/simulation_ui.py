import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtCore import QTimer, QEventLoop
import redis
import json

class SimulationUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.redis = redis.Redis(host='localhost', port=6379, db=0)
        # self.setWindowTitle("Microservices System Simulation")
        # self.setGeometry(100, 100, 800, 600)

        # # Setup the display area for service status
        # self.log = QTextEdit(self)
        # self.log.setGeometry(50, 50, 700, 400)

        self.initUI()


    # def initUI(self):
    #     self.setWindowTitle("Microservices System Simulation")
    #     self.setGeometry(100, 100, 800, 600)  # Window size and position
    #     #self.setStyleSheet("background-color: #333; color: #eee; font-size: 16px;")

    #     # Central widget with layout
    #     centralWidget = QWidget(self)
    #     self.setCentralWidget(centralWidget)
    #     layout = QVBoxLayout(centralWidget)

    #     # Time display
    #     self.timeDisplay = QLabel("Time: --:--:--")
    #     self.timeDisplay.setStyleSheet("font-size: 18px; padding: 10px;")
    #     layout.addWidget(self.timeDisplay)

    #     # Setup the table for service status
    #     self.table = QTableWidget()
    #     self.table.setColumnCount(5)  # Set the number of columns
    #     self.table.setHorizontalHeaderLabels(['Instance ID', 'CPU Usage', 'Requests Processed', 'Status', 'Instance Type'])
    #     self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    #     self.table.setStyleSheet("gridline-color: #ccc;")
    #     layout.addWidget(self.table)

    # def update_ui(self):
    #     data = self.get_data()

    #     # Update the time display
    #     time_data = data.get('time', {}).get('data', {})
    #     if time_data:
    #         self.timeDisplay.setText(f"Time: Day {time_data.get('day', '--')}, Hour {time_data.get('hour', '--')}, Minute {time_data.get('minuite', '--')}")

    #     # Clear existing rows
    #     self.table.setRowCount(0)

    #     # Populate the table with new data
    #     for instance_id, details in data.get('instances', {}).items():
    #         row_position = self.table.rowCount()
    #         self.table.insertRow(row_position)

    #         self.table.setItem(row_position, 0, QTableWidgetItem(instance_id))
    #         cpu_usage_percentage = (details.get('cpu_usage', 0) / details.get('max_cpu', 500)) * 100
    #         self.table.setItem(row_position, 1, QTableWidgetItem(f"{cpu_usage_percentage:.2f}%"))
    #         self.table.setItem(row_position, 2, QTableWidgetItem(str(details.get('requests_processed', 0))))
    #         status = 'Down' if details.get('status', 0) == 0 else 'Up'
    #         self.table.setItem(row_position, 3, QTableWidgetItem(status))
    #         self.table.setItem(row_position, 4, QTableWidgetItem(details.get('instance_type', 'Unknown')))

    def initUI(self):
        self.setWindowTitle("Microservices System Simulation")
        self.setGeometry(100, 100, 800, 600)
        #self.setStyleSheet("background-color: #333; color: #eee; font-size: 16px;")

        centralWidget = QWidget(self)
        self.setCentralWidget(centralWidget)
        layout = QVBoxLayout(centralWidget)

        self.timeDisplay = QLabel("Time: --:--:--")
        self.timeDisplay.setStyleSheet("font-size: 18px; padding: 10px;")
        layout.addWidget(self.timeDisplay)
        # System-wide data display
        self.systemDataDisplay = QLabel("System Data: Loading...")
        self.systemDataDisplay.setStyleSheet("font-size: 16px; padding: 10px;")
        layout.addWidget(self.systemDataDisplay)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(['Instance ID', 'Resource Usage', 'Requests Processed', 'Status', 'Instance Type'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

    def update_ui(self):
        data = self.get_data()

        # Update the time and system data display
        time_data = data.get('time', {}).get('data', {})
        self.timeDisplay.setText(f"Time: Day {time_data.get('day', '--')}, Hour {time_data.get('hour', '--')}, Minute {time_data.get('minuite', '--')}")

        system_data = data.get('system_data', {})
        system_info = (f"Avg CPU: {round(system_data.get('avg_cpu', '--'),2)}"
                    f"Total Requests Processed: {system_data.get('total_requests_processed', '--')}, "
                    f"Unprocessed Requests: {system_data.get('total_requests_unprocessed', '--')}")
        self.systemDataDisplay.setText(f"System Data: {system_info}")

        # Prepare and sort data list for the table
        instances = [
            (
                instance_id,
                ( details.get('cpu_usage', 0) / details.get('max_cpu', 500) ) * 100,
                details.get('requests_processed', 0),
                'Down' if details.get('status', 0) == 0 else 'Up',
                details.get('instance_type', 'Unknown')
            )
            for instance_id, details in data.get('instances', {}).items()
        ]
        instances.sort(key=lambda x: x[1], reverse=True)  # Sort by CPU usage

        # Update the table
        self.table.setRowCount(0)
        for instance in instances:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            for col, item in enumerate(instance):
                if col == 1:  # Format CPU usage as percentage
                    self.table.setItem(row_position, col, QTableWidgetItem(f"{item:.2f}%"))
                else:
                    self.table.setItem(row_position, col, QTableWidgetItem(str(item)))


    def get_data(self):
        # Fetch data from KeyDB
        json_data = self.redis.get('maestro_meta_data')
        print(f"maestro_meta_data",json_data)
        if json_data:
            # Deserialize the JSON string into a dictionary
            data = json.loads(json_data)
        else:
            data = {}
        
        return data


    def run_ui(self):
        # This is a placeholder for where you might handle a loop or triggers to update the UI
        while True:
            self.update_ui()
            # Sleep for a certain interval before updating again
            QApplication.processEvents()
            QApplication.processEvents()
            self.delay(1000)

    def delay(self, milliseconds):
        loop = QEventLoop()
        QTimer.singleShot(milliseconds, loop.quit)
        loop.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SimulationUI()
    window.show()
    window.run_ui()
    sys.exit(app.exec_())
