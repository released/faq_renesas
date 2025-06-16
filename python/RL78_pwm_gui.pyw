import sys
import json
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QVBoxLayout,
    QHBoxLayout, QTabWidget, QTableWidget, QTableWidgetItem,
    QPushButton
)
from PyQt5.QtCore import Qt

CONFIG_FILE = "config.json"
DEFAULT_TDR_MASTER = "7CF"

def load_last_tdr_master():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                return data.get("tdr_master", DEFAULT_TDR_MASTER)
        except:
            pass
    return DEFAULT_TDR_MASTER

def save_last_tdr_master(value):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump({"tdr_master": value.upper()}, f)
    except:
        pass

class PWMCalcTab(QWidget):
    def __init__(self, sync_callback=None):
        super().__init__()
        self.sync_callback = sync_callback  # 傳入 table_tab 同步更新
        self.init_ui()

    def init_ui(self):
        self.master_input = QLineEdit()
        self.slave_input = QLineEdit()
        self.duty_input = QLineEdit()
        self.clear_button = QPushButton("Clear")
        self.reset_button = QPushButton("Load Default")

        self.master_input.setPlaceholderText("0 ~ FFFF")
        self.slave_input.setPlaceholderText("0 ~ FFFF")
        self.duty_input.setPlaceholderText("0.0 ~ 100.0")

        self.result_label = QLabel("")
        self.result_label.setAlignment(Qt.AlignCenter)

        self.last_changed = None

        self.master_input.textChanged.connect(lambda: self.on_change("master"))
        self.slave_input.textChanged.connect(lambda: self.on_change("slave"))
        self.duty_input.textChanged.connect(lambda: self.on_change("duty"))
        self.clear_button.clicked.connect(self.clear_fields)
        self.reset_button.clicked.connect(self.load_default)

        layout = QVBoxLayout()
        layout.addLayout(self._row("TDR_master (Hex):", self.master_input))
        layout.addLayout(self._row("TDR_slave (Hex):", self.slave_input))
        layout.addLayout(self._row("Duty (%):", self.duty_input))

        button_row = QHBoxLayout()
        button_row.addWidget(self.clear_button)
        button_row.addWidget(self.reset_button)
        layout.addLayout(button_row)

        layout.addSpacing(5)
        layout.addWidget(self.result_label)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(4)
        self.setLayout(layout)

    def _row(self, label_text, widget):
        row = QHBoxLayout()
        label = QLabel(label_text)
        label.setFixedWidth(120)
        row.addWidget(label)
        row.addWidget(widget)
        return row

    def set_master_value(self, hex_value):
        self.master_input.setText(hex_value)

    def clear_fields(self):
        self.master_input.clear()
        self.slave_input.clear()
        self.duty_input.clear()
        self.result_label.clear()

    def load_default(self):
        self.master_input.setText(DEFAULT_TDR_MASTER)
        if self.sync_callback:
            self.sync_callback(DEFAULT_TDR_MASTER)

    def on_change(self, source):
        self.last_changed = source
        self.recalculate()

    def recalculate(self):
        try:
            master_text = self.master_input.text().strip()
            slave_text = self.slave_input.text().strip()
            duty_text = self.duty_input.text().strip()

            if master_text:
                save_last_tdr_master(master_text)
            master = int(master_text, 16) if master_text else None

            if master is None or not (0 <= master <= 0xFFFF):
                self.result_label.setText("Please enter valid TDR_master (0~FFFF)")
                return

            if self.last_changed == "duty" and duty_text:
                duty = float(duty_text)
                if not (0 <= duty <= 100):
                    raise ValueError
                slave = int((duty / 100.0) * (master + 1))
                self.slave_input.blockSignals(True)
                self.slave_input.setText(f"{slave:04X}")
                self.slave_input.blockSignals(False)
                self.result_label.setText(f"From Duty={duty:.2f}% → TDR_slave = {slave:04X}")

            elif self.last_changed == "slave" and slave_text:
                slave = int(slave_text, 16)
                if not (0 <= slave <= 0xFFFF):
                    raise ValueError
                duty = slave / (master + 1) * 100
                self.duty_input.blockSignals(True)
                self.duty_input.setText(f"{duty:.2f}")
                self.duty_input.blockSignals(False)
                self.result_label.setText(f"From TDR_slave={slave:04X} → Duty = {duty:.2f}%")

            elif self.last_changed == "master":
                self.result_label.setText("Please enter Duty or TDR_slave")

        except ValueError:
            self.result_label.setText("Invalid input, please enter valid hex or number")


class PWMTableTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.master_input = QLineEdit()
        self.master_input.setPlaceholderText("TDR_master (Hex)")
        self.master_input.textChanged.connect(self.generate_tables)

        self.tables = []
        ranges = [(1, 25), (26, 50), (51, 75), (76, 100)]
        colors = ["#F0F8FF", "#FFF8DC", "#E6FFE6", "#FFE6E6"]

        self.table_layout = QHBoxLayout()
        for i, (start, end) in enumerate(ranges):
            table = QTableWidget(end - start + 1, 2)
            table.setHorizontalHeaderLabels(["Duty", "TDR_slave"])
            table.verticalHeader().setVisible(False)
            table.setEditTriggers(QTableWidget.NoEditTriggers)

            table.setStyleSheet(f"""
                QHeaderView::section {{ font-weight: bold; font-size: 10px; }}
                QTableWidget {{ font-size: 10px; background-color: {colors[i]}; }}
            """)
            table.setFixedWidth(200)
            table.setFixedHeight(25 * 40 + 30)
            table.setColumnWidth(0, 70)
            table.setColumnWidth(1, 110)

            for row in range(25):
                table.setRowHeight(row, 22)

            self.tables.append((table, start, end))
            self.table_layout.addWidget(table)

        # 緊湊上方欄位
        input_row = QHBoxLayout()
        label = QLabel("TDR_master (Hex):")
        label.setFixedWidth(120)
        input_row.addWidget(label)
        input_row.addWidget(self.master_input)

        layout = QVBoxLayout()
        layout.addLayout(input_row)
        layout.addLayout(self.table_layout)
        layout.setSpacing(2)
        layout.setContentsMargins(10, 5, 10, 5)
        self.setLayout(layout)

    def set_master_value(self, hex_value):
        self.master_input.setText(hex_value)

    def generate_tables(self):
        try:
            master_text = self.master_input.text().strip()
            save_last_tdr_master(master_text)

            master = int(master_text, 16) if master_text else None
            if master is None or not (0 <= master <= 0xFFFF):
                return

            for table, start, end in self.tables:
                for i, percent in enumerate(range(start, end + 1)):
                    slave = int((percent / 100.0) * (master + 1))
                    duty_item = QTableWidgetItem(f"{percent}%")
                    slave_item = QTableWidgetItem(f"{slave:04X}")
                    duty_item.setTextAlignment(Qt.AlignCenter)
                    slave_item.setTextAlignment(Qt.AlignCenter)
                    table.setItem(i, 0, duty_item)
                    table.setItem(i, 1, slave_item)
        except:
            pass

class MainApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RL78 PWM Duty Tool")
        self.setFixedSize(1024, 840)

        tabs = QTabWidget()
        # self.calc_tab = PWMCalcTab()
        self.table_tab = PWMTableTab()
        self.calc_tab = PWMCalcTab(sync_callback=self.table_tab.set_master_value)
        tabs.addTab(self.calc_tab, "Duty Calculator")
        tabs.addTab(self.table_tab, "Lookup Table (1–100%)")

        layout = QVBoxLayout()
        layout.addWidget(tabs)
        self.setLayout(layout)

        # 載入最後值
        last_value = load_last_tdr_master()
        self.calc_tab.set_master_value(last_value)
        self.table_tab.set_master_value(last_value)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())
