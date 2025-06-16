import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QTextEdit, QCheckBox, QLabel,
    QTabWidget, QScrollArea, QGroupBox
)
from Ships import *  # Assuming all DefaultShip classes are defined there

ship_classes = [
    DefaultCruiser,
    DefaultDreadnought,
    DefaultFlagship,
    DefaultCarrier,
    DefaultFighter,
    DefaultDestroyer,
    DefaultWarSun,
]

non_upgradeable = [DefaultFlagship, DefaultWarSun]

class ArmyTab(QWidget):
    def __init__(self):
        super().__init__()
        self.army = []

        layout = QVBoxLayout()
        self.army_list = QListWidget()
        layout.addWidget(QLabel("Army"))
        layout.addWidget(self.army_list)

        ship_controls = QVBoxLayout()
        for ship_cls in ship_classes:
            box = QHBoxLayout()
            label = QLabel(ship_cls().__class__.__name__[7:])
            add_btn = QPushButton("+")
            add_btn.setFixedWidth(40)
            if ship_cls not in non_upgradeable:
                upgrade_box = QCheckBox()
            else:
                upgrade_box = None
            add_btn.clicked.connect(lambda _, c=ship_cls, u=upgrade_box: self.add_ship(c, u.isChecked() if u else False))
            box.addWidget(label)
            if upgrade_box:
                box.addWidget(upgrade_box)
            box.addWidget(add_btn)
            ship_controls.addLayout(box)

        layout.addLayout(ship_controls)

        analyse_btn = QPushButton("Analyse")
        layout.addWidget(analyse_btn)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.output)
        layout.addWidget(scroll)

        clear_btn = QPushButton("Clear Army")
        clear_btn.clicked.connect(self.clear_army)
        layout.addWidget(clear_btn)

        self.setLayout(layout)

    def add_ship(self, cls, upgraded):
        ship = cls()
        if upgraded:
            ship.upgrade(1)
        self.army.append(ship)
        self.army_list.addItem(ship.name)

    def clear_army(self):
        self.army.clear()
        self.army_list.clear()

class SimulateTab(QWidget):
    def __init__(self):
        super().__init__()
        self.army1 = []
        self.army2 = []

        layout = QVBoxLayout()

        armies_layout = QHBoxLayout()

        # Army 1 panel
        army1_box = QVBoxLayout()
        army1_box.addWidget(QLabel("Army 1"))
        self.army1_list = QListWidget()
        army1_box.addWidget(self.army1_list)
        for ship_cls in ship_classes:
            row = QHBoxLayout()
            label = QLabel(ship_cls().__class__.__name__[7:])
            add_btn = QPushButton("+")
            add_btn.setFixedWidth(40)
            if ship_cls not in non_upgradeable:
                upgrade_box = QCheckBox()
            else:
                upgrade_box = None
            add_btn.clicked.connect(lambda _, c=ship_cls, u=upgrade_box: self.add_to_army(c, u.isChecked() if u else False, 1))
            row.addWidget(label)
            if upgrade_box:
                row.addWidget(upgrade_box)
            row.addWidget(add_btn)
            army1_box.addLayout(row)
        clear1 = QPushButton("Clear")
        clear1.clicked.connect(lambda: self.clear_army(1))
        army1_box.addWidget(clear1)

        # Army 2 panel
        army2_box = QVBoxLayout()
        army2_box.addWidget(QLabel("Army 2"))
        self.army2_list = QListWidget()
        army2_box.addWidget(self.army2_list)
        for ship_cls in ship_classes:
            row = QHBoxLayout()
            label = QLabel(ship_cls().__class__.__name__[7:])
            add_btn = QPushButton("+")
            add_btn.setFixedWidth(40)
            if ship_cls not in non_upgradeable:
                upgrade_box = QCheckBox()
            else:
                upgrade_box = None
            add_btn.clicked.connect(lambda _, c=ship_cls, u=upgrade_box: self.add_to_army(c, u.isChecked() if u else False, 2))
            row.addWidget(label)
            if upgrade_box:
                row.addWidget(upgrade_box)
            row.addWidget(add_btn)
            army2_box.addLayout(row)
        clear2 = QPushButton("Clear")
        clear2.clicked.connect(lambda: self.clear_army(2))
        army2_box.addWidget(clear2)

        armies_layout.addLayout(army1_box)
        armies_layout.addLayout(army2_box)

        layout.addLayout(armies_layout)

        simulate_btn = QPushButton("Simulate Battle")
        layout.addWidget(simulate_btn)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.output)
        layout.addWidget(scroll)

        self.setLayout(layout)

    def add_to_army(self, cls, upgraded, army_num):
        ship = cls()
        if upgraded:
            ship.upgrade(1)
        if army_num == 1:
            self.army1.append(ship)
            self.army1_list.addItem(ship.name)
        else:
            self.army2.append(ship)
            self.army2_list.addItem(ship.name)

    def clear_army(self, army_num):
        if army_num == 1:
            self.army1.clear()
            self.army1_list.clear()
        else:
            self.army2.clear()
            self.army2_list.clear()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Army Simulator")

        tabs = QTabWidget()
        tabs.addTab(ArmyTab(), "Analyse Army")
        tabs.addTab(SimulateTab(), "Simulate Battle")

        layout = QVBoxLayout()
        layout.addWidget(tabs)
        self.setLayout(layout)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
