import sys

from PyQt5 import QtWidgets, QtCore, QtGui, sip

import Database
import add_category_ui
import add_item_ui
import add_list_ui
import packing_ui


class Application(QtWidgets.QMainWindow, packing_ui.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.ColorForSelectedItem = QtGui.QColor(0, 127, 0, 255)
        self.ColorForNotSelectedItem = QtGui.QColor(255, 0, 0, 255)

        self.comboBox.addItems(Database.db.get_tables_names_from_db())
        self.current_tree_name = self.comboBox.currentText()
        self.tool_menu = QtWidgets.QMenu()
        self.add_list_action = QtWidgets.QAction("Добавить список")
        self.add_list_action.triggered.connect(self.add_list)
        self.delete_list_action = QtWidgets.QAction("Удалить список")
        self.delete_list_action.triggered.connect(self.delete_list)
        self.tool_menu.addAction(self.add_list_action)
        self.tool_menu.addAction(self.delete_list_action)
        self.toolButton.setMenu(self.tool_menu)
        self.toolButton.clicked.connect(self.show_menu)

        self.create_tree()

        self.Add_category_button.clicked.connect(self.add_category)
        self.Add_item_button.clicked.connect(self.add_item)
        self.Delete_button.clicked.connect(self.delete_selected_item)
        self.treeWidget.clicked.connect(self.select_item)
        self.treeWidget.itemChanged.connect(self.change_item)
        self.comboBox.currentTextChanged.connect(self.change_current_tree)

    def add_list(self):
        dialog = AddListWindow()
        dialog.exec()

    def add_category(self):
        dialog = AddCategoryWindow()
        dialog.show()
        dialog.exec()

    def add_item(self):
        dialog = AddItemWindow()
        dialog.show()
        dialog.exec()

    def delete_list(self):
        Database.db.drop_table_for_treeWidget(self.current_tree_name)
        self.comboBox.removeItem(self.comboBox.currentIndex())
        self.comboBox.update()

    def show_menu(self):
        self.tool_menu.exec_(self.toolButton.mapToGlobal(QtCore.QPoint(31, 0)))

    def change_current_tree(self):
        self.current_tree_name = self.comboBox.currentText()
        self.create_tree()

    def create_tree(self):
        self.treeWidget.clear()
        header_item = QtWidgets.QTreeWidgetItem([" ", "Количество", "Общий вес"])
        header_item.setTextAlignment(1, QtCore.Qt.AlignHCenter)
        header_item.setTextAlignment(2, QtCore.Qt.AlignHCenter)
        self.treeWidget.setHeaderItem(header_item)

        self.treeWidget.setColumnWidth(0, 300)
        self.treeWidget.setColumnWidth(1, 100)
        self.treeWidget.setColumnWidth(2, 150)

        table = Database.db.get_table_for_treeWidget(self.current_tree_name)
        for data in table:
            if data[1] is None:
                element = QtWidgets.QTreeWidgetItem([data[3]])
                element.setData(0, 0x0100, {"id": data[0], "path": data[2]})
                element.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsDragEnabled |
                                 QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
                self.treeWidget.addTopLevelItem(element)
            else:
                data_dict = eval(data[3])
                element = QtWidgets.QTreeWidgetItem([str(data_dict["title"]), str(data_dict["amount"]),
                                                    str(data_dict["weight"])])
                element.setData(0, 0x100, {"id": data[0], "parent_id": data[1], "path": data[2]})
                element.setTextAlignment(0, QtCore.Qt.AlignLeft)
                element.setTextAlignment(1, QtCore.Qt.AlignHCenter)
                element.setTextAlignment(2, QtCore.Qt.AlignHCenter)
                element.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsDragEnabled |
                                 QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
                parent_name = Database.db.get_data_by_id_from_table_for_treeWidget(data[1], self.current_tree_name)[3]
                self.treeWidget.findItems(parent_name, QtCore.Qt.MatchExactly, 0)[0].addChild(element)

            self.treeWidget.header().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
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
        category_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsDragEnabled |
                               QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
        self.treeWidget.addTopLevelItem(category_item)

    def add_item_in_tree(self, item_id):
        data = Database.db.get_data_by_id_from_table_for_treeWidget(item_id, self.current_tree_name)
        data_dict = eval(data[3])
        element = QtWidgets.QTreeWidgetItem([str(data_dict["title"]), str(data_dict["amount"]),
                                             str(data_dict["weight"])])
        element.setData(0, 0x100, {"id": data[0], "parent_id": data[1], "path": data[2]})
        element.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsDragEnabled |
                         QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
        element.setTextAlignment(0, QtCore.Qt.AlignLeft)
        element.setTextAlignment(1, QtCore.Qt.AlignHCenter)
        element.setTextAlignment(2, QtCore.Qt.AlignHCenter)
        parent_name = Database.db.get_data_by_id_from_table_for_treeWidget(data[1], self.current_tree_name)[3]
        self.treeWidget.findItems(parent_name, QtCore.Qt.MatchExactly, 0)[0].addChild(element)

        self.lcd_number_update()

    def change_item(self):
        path = self.treeWidget.currentItem().data(0, 0x100)["path"]
        if not self.treeWidget.currentItem().parent():
            title = self.treeWidget.currentItem().text(0)
            Database.db.update_element_in_table_for_treeWidget(path, title, self.current_tree_name)
        else:
            title = self.treeWidget.currentItem().text(0)
            amount = int(self.treeWidget.currentItem().text(1))
            weight = int(self.treeWidget.currentItem().text(2))
            Database.db.update_element_in_table_for_treeWidget(path,
                                                               {"title": title, "amount": amount, "weight": weight},
                                                               self.current_tree_name)
        self.lcd_number_update()

    def delete_selected_item(self):
        try:
            path = self.treeWidget.currentItem().data(0, 0x0100)["path"]
            Database.db.delete_element_from_table_for_treeWidget(path, self.current_tree_name)
            sip.delete(self.treeWidget.currentItem())
            self.treeWidget.update()
            self.lcd_number_update()
        except Exception as error:
            self.show_system_message(error.__class__.__name__)

    def select_item(self):
        self.treeWidget.currentItem().setSelected(False)
        if self.treeWidget.currentItem().parent():
            self.treeWidget.blockSignals(True)
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
            self.treeWidget.blockSignals(False)

    def show_system_message(self, text):
        try:
            self.App_info.clear()
            self.App_info.append(text)
        except Exception as error:
            print(error.__class__.__name__)


class AddListWindow(QtWidgets.QDialog, add_list_ui.Ui_Add_list):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.buttonBox.accepted.connect(self.ok_button)

    def ok_button(self):
        list_name = self.lineEdit.text()
        if list_name not in Database.db.get_tables_names_from_db():
            Database.db.create_table_for_treeWidget(list_name)
            window.comboBox.addItem(list_name)
            window.comboBox.update()


class AddCategoryWindow(QtWidgets.QDialog, add_category_ui.Ui_Add_category):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.buttonBox.accepted.connect(self.ok_button)

    def ok_button(self):
        category_name = self.lineEdit.text()
        if Database.db.insert_new_root_into_table_for_treeWidget(category_name, window.current_tree_name):
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
        self.tableWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        self.close_button.clicked.connect(self.close_window)
        self.add_button.clicked.connect(self.add_item)
        self.roots_names = Database.db.get_roots_from_table_for_treeWidget(window.current_tree_name)
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
            if Database.db.insert_new_item_into_table_for_treeWidget(category_id,
                                                                     {"title": title, "amount": amount, "weight": weight},
                                                                     window.current_tree_name):
                item_id = Database.db.get_id_by_content_from_table_for_treeWidget(category_id,
                                                                                  {"title": title, "amount": amount, "weight": weight},
                                                                                  window.current_tree_name)
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