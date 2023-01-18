import sys

from PyQt5.QtSql import QSqlDatabase, QSqlQuery
from PyQt5.QtWidgets import (QMainWindow, QApplication, QVBoxLayout, QHBoxLayout, QSplitter,
                             QFormLayout, QLabel, QFrame, QPushButton,
                             QMenu, QAction, QMenuBar, QWidget, QDialog, QDialogButtonBox, QLineEdit)
from PyQt5.QtCore import Qt
from PyQt5.QtGui  import QFont, QIcon


class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        self.con = QSqlDatabase.addDatabase("QSQLITE")
        self.con.setDatabaseName("contacts.sqlite")

        self.create_body()
        self.create_menu_bar()

    def create_menu_bar(self):
        menu_bar = QMenuBar(self)

        file_menu = QMenu("File", self)
        file_menu.addAction(QAction("New", self))
        file_menu.addAction(QAction("Open", self))
        file_menu.addAction(QAction("Save", self))
        file_menu.addAction(QAction("Save As", self))
        menu_bar.addMenu(file_menu)

        help_menu = QMenu("Help", self)
        help_menu.addAction(QAction("Help", self))
        help_menu.addAction(QAction("About", self))
        menu_bar.addMenu(help_menu)

        self.setMenuBar(menu_bar)

    def create_body(self):
        tablesList = QWidget()
        tablesList.setStyleSheet("background-color: blue;")

        self.tl_VBoxLay = QVBoxLayout()
        tlNameBox = QHBoxLayout()
        tlName = QWidget()
        tlName.setStyleSheet("background-color: red;")

        tl_label = QLabel("Tables")
        tlNameBox.addWidget(tl_label)
        add_Btn = QPushButton("+", self)
        add_Btn.setMaximumSize(25, 25)
        add_Btn.clicked.connect(self.add_button_clicked)
        tlNameBox.addWidget(add_Btn)
        reload_Btn = QPushButton("↻", self)
        reload_Btn.setMaximumSize(25, 25)
        reload_Btn.clicked.connect(self.reload_button_clicked)
        tlNameBox.addWidget(reload_Btn)

        tlName.setLayout(tlNameBox)
        tlName.setMaximumSize(tlNameBox.sizeHint())

        self.tl_VBoxLay.addWidget(tlName)
        self.tl_VBoxLay.setAlignment(Qt.AlignTop)
        tablesList.setLayout(self.tl_VBoxLay)
        tablesList.setMaximumWidth(self.tl_VBoxLay.sizeHint().width())

        toDoListIBox = QFrame()
        toDoListIBox.setFrameShape(QFrame.StyledPanel)
        toDoListIBox.setMinimumSize(300, 300)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(tablesList)
        splitter.addWidget(toDoListIBox)

        self.vbox = QVBoxLayout()
        self.vbox.addWidget(splitter)
        self.setCentralWidget(splitter)
        self.tablesBtn_lst = []
        if not self.con.open():
            print("Database not open")
            sys.exit(1)

    def add_button_clicked(self):
        dlg = CustomDialog()
        if dlg.exec():
            print("Success!")
            self.tableName = dlg.tableName
            self.create_new_table()
        else:
            print("Cancel!")

    def create_new_table(self):
        createTableQuery = QSqlQuery()
        if not createTableQuery.exec(
            f"""
            CREATE TABLE IF NOT EXISTS {self.tableName} (
                id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
                time INTEGER,
                toDo VARCHAR(50),
                isDone INTEGER NOT NULL
            )
            """
        ):
            print("Table not created")
        self.reload_button_clicked()

    def reload_button_clicked(self):
        self.tables = self.con.tables()
        print(self.tables)
        print(self.tablesBtn_lst)
        for i in self.tables:
            if i not in self.tablesBtn_lst:
                self.create_new_button(i)
                self.tablesBtn_lst.append(i)

        for i in self.tablesBtn_lst:
            if i not in self.tables:
                self.remove_button(i)
                self.tablesBtn_lst.remove(i)

    def create_new_button(self, name):
        button = QPushButton(name)
        button.clicked.connect(self.open_table)
        button.setStyleSheet("background: white;")
        self.tl_VBoxLay.addWidget(button)

    def remove_button(self, name):
        for i in range(self.tl_VBoxLay.count()):
            widget = self.tl_VBoxLay.itemAt(i).widget()
            if isinstance(widget, QPushButton) and widget.text() == name:
                self.tl_VBoxLay.removeWidget(widget.objectName())

    def open_table(self):
        name = self.sender().text()
        getInfoQuery = QSqlQuery()
        if not getInfoQuery.exec(
                f"""
                    SELECT time, toDo, isDone FROM {name}
                    """
        ):
            print("Info not taken")
        data = []
        while getInfoQuery.next():
            l = []
            for i in range(3):
                l += [getInfoQuery.value(i)]
            data.append(l)

class CustomDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("HELLO!")

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)

        self.layout = QVBoxLayout()
        message = QLabel("Name table")
        self.tableName_le = QLineEdit()
        self.tableName = ""
        self.layout.addWidget(message)
        self.layout.addWidget(self.tableName_le)
        self.layout.addWidget(self.buttonBox)
        self.tableName = self.tableName_le.text()

        self.buttonBox.accepted.connect(self.ok_button_clicked)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.setLayout(self.layout)
    def ok_button_clicked(self):
        self.tableName = self.tableName_le.text()
        s = ""
        for i in self.tableName:
            if i == " ":
                s += "_"
                continue
            s += i
        self.tableName = s
        print(self.tableName)

if __name__ == '__main__':
    app = QApplication(sys.argv)                                  # <---

    win = Window()
    win.setWindowTitle('ToDoList')
    win.setWindowIcon(QIcon("icon.png"))
    win.setGeometry(300, 150, 500, 300)
    win.show()
    app.exec_()