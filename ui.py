import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QTextEdit, QCheckBox, QLabel,
    QTabWidget, QScrollArea, QGroupBox, QDialog, QLineEdit, QListWidgetItem
)
from PyQt6.QtCore import Qt
from Ships import *  # Assuming all DefaultShip classes are defined there
from fight_simulation import simulate_fight
from army_stat import get_statistics_normal, get_statistics_simulation

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

class CustomShipDialog(QDialog):
    def __init__(self, army_callback, army_name="Army"):
        super().__init__()
        self.setWindowTitle(f"Add Custom Ship to {army_name}")
        self.army_callback = army_callback
        self.boolean_attributes = {"sustain_damage", "bombardment", "anti_fighter_barrage"}


        self.fields = {}
        layout = QVBoxLayout()

        attributes = ["name", "cost", "hits", "combat", "move", "capacity", "sustain_damage",
                      "bombardment", "bombardment_hits", "bombardment_combat",
                      "anti_fighter_barrage", "anti_fighter_hits", "anti_fighter_combat"]

        for attr in attributes:
            row = QHBoxLayout()
            label = QLabel(attr.replace("_", " ").capitalize())
            if attr in self.boolean_attributes:
                widget = QCheckBox()
            else:
                widget = QLineEdit()
            self.fields[attr] = widget
            row.addWidget(label)
            row.addWidget(widget)
            layout.addLayout(row)

        button_row = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self.create_ship)
        button_row.addWidget(cancel_btn)
        button_row.addWidget(add_btn)

        layout.addLayout(button_row)
        self.setLayout(layout)

    def create_ship(self):
        kwargs = {}
        for key, widget in self.fields.items():
            if isinstance(widget, QCheckBox):
                kwargs[key] = widget.isChecked()
            else:
                text = widget.text().strip()
                if text.isdigit():
                    kwargs[key] = int(text)
                else:
                    try:
                        kwargs[key] = float(text)
                    except ValueError:
                        kwargs[key] = text

        custom_ship = Ship(**kwargs)
        self.army_callback(custom_ship)
        self.accept()
    
def _ship_display_name(ship: Ship) -> str:
    # Consistent label in list
    return getattr(ship, "name", ship.__class__.__name__)

def _add_ship_row(list_widget: QListWidget, ship: Ship, on_copy, on_delete):
    """
    Adds a row to a QListWidget with:
      - ship name label
      - Copy button
      - Delete button
    Stores the Ship instance in the QListWidgetItem (Qt.UserRole).
    """
    item = QListWidgetItem(list_widget)
    item.setData(Qt.ItemDataRole.UserRole, ship)

    row_widget = QWidget()
    row_layout = QHBoxLayout(row_widget)
    row_layout.setContentsMargins(6, 2, 6, 2)

    name_lbl = QLabel(_ship_display_name(ship))
    copy_btn = QPushButton("Copy")
    del_btn = QPushButton("Delete")

    copy_btn.setFixedWidth(70)
    del_btn.setFixedWidth(70)

    row_layout.addWidget(name_lbl)
    row_layout.addStretch(1)
    row_layout.addWidget(copy_btn)
    row_layout.addWidget(del_btn)

    # Connect actions (use the QListWidgetItem as stable reference)
    copy_btn.clicked.connect(lambda: on_copy(item))
    del_btn.clicked.connect(lambda: on_delete(item))

    # Finish list row
    item.setSizeHint(row_widget.sizeHint())
    list_widget.addItem(item)
    list_widget.setItemWidget(item, row_widget)

    return item

        
class ArmyTab(QWidget):
    def __init__(self):
        super().__init__()
        self.army = []
        self.clipboard_ship = None  # remembers last ship to replicate

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
        
        custom_box = QHBoxLayout()
        custom_label = QLabel("Custom Ship")
        custom_btn = QPushButton("Add Custom Ship")
        custom_btn.clicked.connect(self.open_custom_dialog)
        custom_box.addWidget(custom_label)
        custom_box.addWidget(custom_btn)
        ship_controls.addLayout(custom_box)
        
        layout.addLayout(ship_controls)

        analyse_btn = QPushButton("Analyse")
        analyse_btn.clicked.connect(self.analyse_army)
        layout.addWidget(analyse_btn)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.output)
        layout.addWidget(scroll)

        btn_row = QHBoxLayout()

        delete_last_btn = QPushButton("Delete Last")
        delete_last_btn.clicked.connect(self.delete_last_ship)
        btn_row.addWidget(delete_last_btn)

        add_last_btn = QPushButton("Add Last Ship")
        add_last_btn.clicked.connect(self.add_last_ship)
        btn_row.addWidget(add_last_btn)

        clear_btn = QPushButton("Clear Army")
        clear_btn.clicked.connect(self.clear_army)
        btn_row.addWidget(clear_btn)

        layout.addLayout(btn_row)


        self.setLayout(layout)

    def _append_ship(self, ship: Ship):
        # Update clipboard to last-added ship (your “remember last ship created” requirement)
        # Store a safe template copy if you have copy(); otherwise store the object itself.
        self.clipboard_ship = ship.copy() if hasattr(ship, "copy") else ship

        self.army.append(ship)
        _add_ship_row(
            self.army_list,
            ship,
            on_copy=self.copy_ship_from_row,
            on_delete=self.delete_ship_from_row
        )    

    def add_ship(self, cls, upgraded):
        ship = cls()
        if upgraded:
            ship.upgrade(1)
        self._append_ship(ship)

    def delete_last_ship(self):
        if not self.army:
            return
        self.army.pop()
        self.army_list.takeItem(self.army_list.count() - 1)
    
    def add_last_ship(self):
        if self.clipboard_ship is None:
            return
        new_ship = self.clipboard_ship.copy() if hasattr(self.clipboard_ship, "copy") else self.clipboard_ship
        self._append_ship(new_ship)
        
    def delete_ship_from_row(self, item):
        idx = self.army_list.row(item)
        if idx < 0:
            return
        # Remove from model and UI
        del self.army[idx]
        self.army_list.takeItem(idx)

    def copy_ship_from_row(self, item):
        # Copy the ship in this row to clipboard AND immediately add a new instance to the list
        ship = item.data(Qt.ItemDataRole.UserRole)
        if ship is None:
            return

        self.clipboard_ship = ship.copy() if hasattr(ship, "copy") else ship
        new_ship = self.clipboard_ship.copy() if hasattr(self.clipboard_ship, "copy") else self.clipboard_ship
        self._append_ship(new_ship)
        
    def open_custom_dialog(self):
        dialog = CustomShipDialog(self.add_custom_ship, "Army")
        dialog.exec()
        
    def add_custom_ship(self, ship):
        self._append_ship(ship)


    def clear_army(self):
        self.army.clear()
        self.army_list.clear()

    def analyse_army(self):
        simulation =  get_statistics_simulation(self.army)
        normal = get_statistics_normal(self.army)
        normal_truncated = get_statistics_normal(self.army, use_truncated_normal=True)
        result = "Simulated statistics\n" + simulation + "\n Normal approximation Statistic:\n" + normal + "\n Normal trancated:\n" + normal_truncated 
        self.output.setPlainText(result)

class SimulateTab(QWidget):
    def __init__(self):
        super().__init__()
        self.army1 = []
        self.army2 = []
        self.clipboard_ship = None

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
       
        custom_row1 = QHBoxLayout()
        custom_label1 = QLabel("Custom Ship")
        custom_btn1 = QPushButton("Add Custom Ship")
        custom_btn1.clicked.connect(lambda: self.open_custom_dialog(1))
        custom_row1.addWidget(custom_label1)
        custom_row1.addWidget(custom_btn1)
        army1_box.addLayout(custom_row1)
        row_btns1 = QHBoxLayout()

        del_last1 = QPushButton("Delete Last")
        del_last1.clicked.connect(lambda: self.delete_last_ship(1))
        row_btns1.addWidget(del_last1)

        add_last1 = QPushButton("Add Last Ship")
        add_last1.clicked.connect(lambda: self.add_last_ship(1))
        row_btns1.addWidget(add_last1)

        army1_box.addLayout(row_btns1)

            
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
            
        custom_row2 = QHBoxLayout()
        custom_label2 = QLabel("Custom Ship")
        custom_btn2 = QPushButton("Add Custom Ship")
        custom_btn2.clicked.connect(lambda: self.open_custom_dialog(2))
        custom_row2.addWidget(custom_label2)
        custom_row2.addWidget(custom_btn2)
        army2_box.addLayout(custom_row2)
        row_btns2 = QHBoxLayout()

        del_last2 = QPushButton("Delete Last")
        del_last2.clicked.connect(lambda: self.delete_last_ship(2))
        row_btns2.addWidget(del_last2)

        add_last2 = QPushButton("Add Last Ship")
        add_last2.clicked.connect(lambda: self.add_last_ship(2))
        row_btns2.addWidget(add_last2)

        army2_box.addLayout(row_btns2)

        
        clear2 = QPushButton("Clear")
        clear2.clicked.connect(lambda: self.clear_army(2))
        army2_box.addWidget(clear2)

        armies_layout.addLayout(army1_box)
        armies_layout.addLayout(army2_box)

        layout.addLayout(armies_layout)

        simulate_btn = QPushButton("Simulate Battle")
        simulate_btn.clicked.connect(self.simulate_battle)
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
        self._append_ship(ship, army_num)


    def clear_army(self, army_num):
        if army_num == 1:
            self.army1.clear()
            self.army1_list.clear()
        else:
            self.army2.clear()
            self.army2_list.clear()
            
            
    def open_custom_dialog(self, army_number):
        name = f"Army {army_number}"
        callback = lambda ship: self.add_custom_ship(ship, army_number)
        dialog = CustomShipDialog(callback, name)
        dialog.exec()

    def add_custom_ship(self, ship, army_number):
        self._append_ship(ship, army_number)

    def _append_ship(self, ship: Ship, army_num: int):
        # Remember last added ship globally across both armies
        self.clipboard_ship = ship.copy() if hasattr(ship, "copy") else ship

        if army_num == 1:
            self.army1.append(ship)
            _add_ship_row(
                self.army1_list,
                ship,
                on_copy=lambda item: self.copy_ship_from_row(item, 1),
                on_delete=lambda item: self.delete_ship_from_row(item, 1),
            )
        else:
            self.army2.append(ship)
            _add_ship_row(
                self.army2_list,
                ship,
                on_copy=lambda item: self.copy_ship_from_row(item, 2),
                on_delete=lambda item: self.delete_ship_from_row(item, 2),
            )

    def delete_last_ship(self, army_num: int):
        if army_num == 1:
            if not self.army1:
                return
            self.army1.pop()
            self.army1_list.takeItem(self.army1_list.count() - 1)
        else:
            if not self.army2:
                return
            self.army2.pop()
            self.army2_list.takeItem(self.army2_list.count() - 1)

    def add_last_ship(self, army_num: int):
        if self.clipboard_ship is None:
            return
        new_ship = self.clipboard_ship.copy() if hasattr(self.clipboard_ship, "copy") else self.clipboard_ship
        self._append_ship(new_ship, army_num)

    def delete_ship_from_row(self, item, army_num: int):
        if army_num == 1:
            idx = self.army1_list.row(item)
            if idx < 0:
                return
            del self.army1[idx]
            self.army1_list.takeItem(idx)
        else:
            idx = self.army2_list.row(item)
            if idx < 0:
                return
            del self.army2[idx]
            self.army2_list.takeItem(idx)

    def copy_ship_from_row(self, item, army_num: int):
        # Copy this ship to clipboard AND immediately add a new instance to the same army
        ship = item.data(Qt.ItemDataRole.UserRole)
        if ship is None:
            return

        self.clipboard_ship = ship.copy() if hasattr(ship, "copy") else ship
        new_ship = self.clipboard_ship.copy() if hasattr(self.clipboard_ship, "copy") else self.clipboard_ship
        self._append_ship(new_ship, army_num)

            
            
    def simulate_battle(self):
        result = simulate_fight([self.army1, self.army2], n_fights=10000)
        self.output.setPlainText(result)



    
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
