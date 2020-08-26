from PyQt5 import QtWidgets, QtCore
import packing_ui, add_category_ui, add_item_ui
import Database
import sys


class Application(QtWidgets.QMainWindow, packing_ui.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.update_tree()

        self.Add_category_button.clicked.connect(self.add_category)
        self.Add_item_button.clicked.connect(self.add_item)
        self.Delete_button.clicked.connect(self.delete_selected_item)

    def add_category(self):
        dialog = AddCategoryWindow()
        dialog.show()
        dialog.exec()

    def add_item(self):
        dialog = AddItemWindow()
        dialog.show()
        dialog.exec()

    def update_tree(self):
        self.treeWidget.clear()
        total_weight = 0
        Header_item = QtWidgets.QTreeWidgetItem([" ", "Количество", "Общий вес"])
        Header_item.setTextAlignment(1, QtCore.Qt.AlignHCenter)
        Header_item.setTextAlignment(2, QtCore.Qt.AlignHCenter)
        self.treeWidget.setHeaderItem(Header_item)
        roots = Database.db.get_roots_from_tree()
        for node_id, root in roots:
            root_row = QtWidgets.QTreeWidgetItem([root])
            path = Database.db.get_path_by_id(node_id)
            root_row.setData(0, 0x0100, path)
            self.treeWidget.addTopLevelItem(root_row)
            rows = Database.db.get_children_of_node(node_id)
            for child_path, child in rows:
                root_row_child = QtWidgets.QTreeWidgetItem([str(child["title"]), str(child["amount"]),
                                                            str(child["amount"] * child["weight"])])
                root_row_child.setData(0, 0x0100, child_path)
                root_row_child.setTextAlignment(0, QtCore.Qt.AlignLeft)
                root_row_child.setTextAlignment(1, QtCore.Qt.AlignHCenter)
                root_row_child.setTextAlignment(2, QtCore.Qt.AlignHCenter)
                total_weight += child["amount"] * child["weight"]
                root_row.addChild(root_row_child)
        self.treeWidget.setColumnWidth(0, 300)
        self.treeWidget.setColumnWidth(1, 100)
        self.treeWidget.setColumnWidth(2, 100)
        self.treeWidget.expandAll()

        self.lcdNumber.display(total_weight/1000)

    def delete_selected_item(self):
        try:
            path = self.treeWidget.currentItem().data(0, 0x0100)
            Database.db.delete_element(path)
            self.update_tree()
        except Exception as error:
            self.show_system_message(error.__class__.__name__)

    def show_system_message(self, text):
        try:
            self.App_info.clear()
            self.App_info.append(text)
        except Exception as error:
            print(error.__class__.__name__)


class AddCategoryWindow(QtWidgets.QDialog, add_category_ui.Ui_Add_category):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.buttonBox.accepted.connect(self.Ok_button)

    def Ok_button(self):
        category_name = self.lineEdit.text()
        Database.db.insert_new_root_into_table_tree(category_name)
        window.update_tree()


class AddItemWindow(QtWidgets.QDialog, add_item_ui.Ui_add_item):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.tableWidget.setColumnWidth(0, 300)
        self.tableWidget.setColumnWidth(1, 150)
        self.tableWidget.setColumnWidth(2, 120)
        self.tableWidget.setRowHeight(0, 30)
        self.tableWidget.setRowHeight(1, 30)
        self.close_button.clicked.connect(self.close_window)
        self.add_button.clicked.connect(self.add_item)
        self.roots_names = Database.db.get_roots_from_tree()
        for root_id, root in self.roots_names:
            self.select_category.addItem(root, root_id)

    def close_window(self):
        self.close()

    def add_item(self):
        try:
            title = self.tableWidget.item(0, 0).text()
            amount = int(self.tableWidget.item(0, 1).text())
            weight = int(self.tableWidget.item(0, 2).text())
            category_id = self.select_category.currentData()
            if not Database.db.insert_new_item_into_table_tree(category_id,
                                                               {"title": title, "amount": amount, "weight": weight}):
                window.show_system_message("Запись не была сделана")
            self.tableWidget.clearContents()
            window.update_tree()
        except AttributeError:
            window.show_system_message("Не все поля заполнены")
        except ValueError:
            window.show_system_message("Введите правильные значения")


app = QtWidgets.QApplication(sys.argv)
window = Application()
window.show()



def run_app():
    app.exec()