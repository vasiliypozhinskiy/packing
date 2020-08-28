from PyQt5 import QtWidgets, QtCore, QtGui, sip
import packing_ui, add_category_ui, add_item_ui
import Database
import sys


class Application(QtWidgets.QMainWindow, packing_ui.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.ColorForSelectedItem = QtGui.QColor(0, 127, 0, 255)
        self.ColorForNotSelectedItem = QtGui.QColor(255, 0, 0, 255)

        self.create_tree()

        self.Add_category_button.clicked.connect(self.add_category)
        self.Add_item_button.clicked.connect(self.add_item)
        self.Delete_button.clicked.connect(self.delete_selected_item)
        self.treeWidget.clicked.connect(self.select_item)

    def add_category(self):
        dialog = AddCategoryWindow()
        dialog.show()
        dialog.exec()

    def add_item(self):
        dialog = AddItemWindow()
        dialog.show()
        dialog.exec()

    def create_tree(self):
        header_item = QtWidgets.QTreeWidgetItem([" ", "Количество", "Общий вес"])
        header_item.setTextAlignment(1, QtCore.Qt.AlignHCenter)
        header_item.setTextAlignment(2, QtCore.Qt.AlignHCenter)
        self.treeWidget.setHeaderItem(header_item)
        table = Database.db.get_table_tree()
        for data in table:
            if data[1] is None:
                element = QtWidgets.QTreeWidgetItem([data[3]])
                element.setData(0, 0x0100, {"id": data[0], "path": data[2]})
                self.treeWidget.addTopLevelItem(element)
            else:
                data_dict = eval(data[3])
                element = QtWidgets.QTreeWidgetItem([str(data_dict["title"]), str(data_dict["amount"]),
                                                    str(data_dict["amount"] * data_dict["weight"])])
                element.setData(0, 0x100, {"id": data[0], "parent_id": data[1], "path": data[2]})
                element.setTextAlignment(0, QtCore.Qt.AlignLeft)
                element.setTextAlignment(1, QtCore.Qt.AlignHCenter)
                element.setTextAlignment(2, QtCore.Qt.AlignHCenter)
                parent_name = Database.db.get_data_by_id(data[1])[3]
                self.treeWidget.findItems(parent_name, QtCore.Qt.MatchExactly, 0)[0].addChild(element)

            self.treeWidget.setColumnWidth(0, 300)
            self.treeWidget.setColumnWidth(1, 100)
            self.treeWidget.setColumnWidth(2, 100)
            self.treeWidget.expandAll()
            self.lcd_number_update()

    def lcd_number_update(self):
        iterator = QtWidgets.QTreeWidgetItemIterator(self.treeWidget)
        visited = []
        total_weight = 0
        while iterator.value():
            item = iterator.value()
            if item.parent() and item not in visited:
                visited.append(item)
                total_weight += int(item.text(2))
            iterator += 1
        self.lcdNumber.display(total_weight/1000)
        self.lcdNumber.update()

    def add_category_in_tree(self, category_name):
        category_item = QtWidgets.QTreeWidgetItem([category_name])
        self.treeWidget.addTopLevelItem(category_item)

    def add_item_in_tree(self, item_id):
        data = Database.db.get_data_by_id(item_id)
        data_dict = eval(data[3])
        element = QtWidgets.QTreeWidgetItem([str(data_dict["title"]), str(data_dict["amount"]),
                                             str(data_dict["amount"] * data_dict["weight"])])
        element.setData(0, 0x100, {"id": data[0], "parent_id": data[1], "path": data[2]})
        element.setTextAlignment(0, QtCore.Qt.AlignLeft)
        element.setTextAlignment(1, QtCore.Qt.AlignHCenter)
        element.setTextAlignment(2, QtCore.Qt.AlignHCenter)
        parent_name = Database.db.get_data_by_id(data[1])[3]
        self.treeWidget.findItems(parent_name, QtCore.Qt.MatchExactly, 0)[0].addChild(element)

        self.lcd_number_update()

    def delete_selected_item(self):
        try:
            path = self.treeWidget.currentItem().data(0, 0x0100)["path"]
            Database.db.delete_element(path)
            sip.delete(self.treeWidget.currentItem())
            self.treeWidget.update()
            self.lcd_number_update()
        except Exception as error:
            self.show_system_message(error.__class__.__name__)

    def select_item(self):
        self.treeWidget.currentItem().setSelected(False)
        if self.treeWidget.currentItem().parent():
            if self.treeWidget.currentItem().data(0, 0x200):
                self.treeWidget.currentItem().setData(0, 0x200, False)
                self.treeWidget.currentItem().setForeground(0, self.ColorForNotSelectedItem)
                self.treeWidget.currentItem().setForeground(1, self.ColorForNotSelectedItem)
                self.treeWidget.currentItem().setForeground(2, self.ColorForNotSelectedItem)
            else:
                self.treeWidget.currentItem().setData(0, 0x200, True)
                self.treeWidget.currentItem().setForeground(0, self.ColorForSelectedItem)
                self.treeWidget.currentItem().setForeground(1, self.ColorForSelectedItem)
                self.treeWidget.currentItem().setForeground(2, self.ColorForSelectedItem)

            iterator = QtWidgets.QTreeWidgetItemIterator(self.treeWidget)
            visited = []
            self.treeWidget.currentItem().parent().setForeground(0, self.ColorForSelectedItem)
            while iterator.value():
                item = iterator.value()
                if item not in visited and item.parent() == self.treeWidget.currentItem().parent():
                    visited.append(item)
                    if not item.data(0, 0x200):
                        self.treeWidget.currentItem().parent().setForeground(0, self.ColorForNotSelectedItem)
                        break
                iterator += 1

            self.treeWidget.update()

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
        self.buttonBox.accepted.connect(self.ok_button)

    def ok_button(self):
        category_name = self.lineEdit.text()
        if Database.db.insert_new_root_into_table_tree(category_name):
            window.add_category_in_tree(category_name)
            window.treeWidget.update()


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
            if Database.db.insert_new_item_into_table_tree(category_id,
                                                           {"title": title, "amount": amount, "weight": weight}):
                item_id = Database.db.get_id_by_content(category_id,
                                                        {"title": title, "amount": amount, "weight": weight})
                window.add_item_in_tree(item_id)
            else:
                window.show_system_message("Запись не сделана")

            self.tableWidget.clearContents()

        except AttributeError:
            window.show_system_message("Не все поля заполнены")
        except ValueError:
            window.show_system_message("Введите правильные значения")


app = QtWidgets.QApplication(sys.argv)
window = Application()
window.show()


def run_app():
    app.exec()