import sys

from PyQt5 import QtWidgets, QtCore, QtGui, sip

import Database
from UI import packing_ui
from UI import add_item_ui
from UI import add_category_ui
from UI import add_list_ui
import functools


def block_signals(func):
    """Decorator which block signals in treeWidget."""

    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        self.treeWidget.blockSignals(True)
        value = func(self, *args, **kwargs)
        self.treeWidget.blockSignals(False)
        return value

    return wrapper


class MainWindow(QtWidgets.QMainWindow, packing_ui.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setFixedSize(807, 622)
        self.setWindowTitle("Packing")

        self.ColorForSelectedItem = QtGui.QColor(0, 127, 0, 255)
        self.ColorForNotSelectedItem = QtGui.QColor(255, 0, 0, 255)

        self.comboBox.addItems(Database.db.get_table_names_for_user())
        self.current_tree_name = Database.db.get_system_name_by_user_name(self.comboBox.currentText())
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
        self.treeWidget.itemChanged.connect(self.update_item)
        self.comboBox.currentTextChanged.connect(self.change_current_tree)

        self.add_list_dialog = AddListWindow()
        self.add_category_dialog = AddCategoryWindow()

        self.add_list_dialog.closeDialog.connect(self.enable_buttons)
        self.add_category_dialog.closeDialog.connect(self.enable_buttons)

    def add_list(self):
        """Opens dialog window for adding new list"""
        self.disable_buttons()
        self.add_list_dialog.show()

    def delete_list(self):
        """Deletes current list from db and comboBox with names of trees"""
        Database.db.drop_table(self.current_tree_name)
        self.comboBox.removeItem(self.comboBox.currentIndex())
        self.comboBox.update()

    def add_category(self):
        """Opens dialog window for adding new category"""
        self.disable_buttons()
        self.add_category_dialog.show()

    def add_item(self):
        """Opens dialog window for adding new item in category"""
        roots_names = Database.db.get_roots_from_table_for_treeWidget(window.current_tree_name)
        if roots_names:
            self.add_item_dialog = AddItemWindow()
            self.add_item_dialog.closeDialog.connect(self.enable_buttons)
            self.disable_buttons()
            self.add_item_dialog.show()
        else:
            self.show_system_message("Сначала добавьте категорию")

    def closeEvent(self, event):
        """Closes all windows on exit"""
        try:
            self.add_item_dialog.close()
        except AttributeError:
            pass
        self.add_category_dialog.close()
        self.add_list_dialog.close()
        self.close()

    def show_menu(self):
        self.tool_menu.exec_(self.toolButton.mapToGlobal(QtCore.QPoint(31, 0)))

    def enable_buttons(self):
        self.tool_menu.setEnabled(True)
        self.Add_category_button.setEnabled(True)
        self.Add_item_button.setEnabled(True)
        self.Delete_button.setEnabled(True)
        self.comboBox.setEnabled(True)

    def disable_buttons(self):
        self.tool_menu.setEnabled(False)
        self.Add_category_button.setEnabled(False)
        self.Add_item_button.setEnabled(False)
        self.Delete_button.setEnabled(False)
        self.comboBox.setEnabled(False)

    def change_current_tree(self):
        """When current item in combobox changes this func calls create_tree func"""
        if self.comboBox.count() > 0:
            self.current_tree_name = Database.db.get_system_name_by_user_name(self.comboBox.currentText())
            self.create_tree()

    def create_tree(self):
        """Shows tree from db with name 'current_tree_name'.
        Each element contents data at role 0x100 {"id": int, "parent_id": int (None for root),"path": str}"""
        self.treeWidget.clear()
        header_item = QtWidgets.QTreeWidgetItem([" ", "Кол-во", "Вес"])
        header_item.setTextAlignment(1, QtCore.Qt.AlignHCenter)
        header_item.setTextAlignment(2, QtCore.Qt.AlignHCenter)
        self.treeWidget.setHeaderItem(header_item)

        self.treeWidget.setColumnWidth(0, 417)
        self.treeWidget.setColumnWidth(1, 100)
        self.treeWidget.setColumnWidth(2, 100)

        table = Database.db.get_table_for_treeWidget(self.current_tree_name)
        for data in table:
            if data[1] is None:
                top_element = QtWidgets.QTreeWidgetItem([data[3]])
                top_element.setData(0, 0x0100, {"id": data[0], "parent_id": None, "path": data[2]})
                top_element.setFlags(QtCore.Qt.ItemIsEditable |
                                     QtCore.Qt.ItemIsEnabled)
                self.treeWidget.addTopLevelItem(top_element)
            else:
                data_dict = eval(data[3])
                element = QtWidgets.QTreeWidgetItem([str(data_dict["title"]), str(data_dict["amount"]),
                                                     str(data_dict["weight"])])
                element.setData(0, 0x100, {"id": data[0], "parent_id": data[1], "path": data[2]})
                element.setTextAlignment(0, QtCore.Qt.AlignLeft)
                element.setTextAlignment(1, QtCore.Qt.AlignHCenter)
                element.setTextAlignment(2, QtCore.Qt.AlignHCenter)
                element.setFlags(QtCore.Qt.ItemIsEditable |
                                 QtCore.Qt.ItemIsEnabled)
                parent_name = Database.db.get_data_by_id_from_table_for_treeWidget(data[1], self.current_tree_name)[3]
                self.treeWidget.findItems(parent_name, QtCore.Qt.MatchExactly, 0)[0].addChild(element)

            self.treeWidget.header().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
            self.treeWidget.expandAll()
            self.lcd_number_update()

    def lcd_number_update(self):
        """Updates total weight"""
        iterator = QtWidgets.QTreeWidgetItemIterator(self.treeWidget)
        visited = []
        total_weight = 0
        while iterator.value():
            item = iterator.value()
            if item.parent() and item not in visited:
                visited.append(item)
                total_weight += int(item.text(2))
            iterator += 1
        self.lcdNumber.display(total_weight / 1000)
        self.lcdNumber.update()

    def add_category_in_tree(self, category_id: int):
        """Adds root from db in tree with data at role 0x100 {"id": int, "parent_id": None, "path": str}"""
        data = Database.db.get_data_by_id_from_table_for_treeWidget(category_id, self.current_tree_name)
        category_item = QtWidgets.QTreeWidgetItem([data[3]])
        category_item.setData(0, 0x100, {"id": data[0], "parent_id": None, "path": data[2]})

        category_item.setFlags(QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)
        self.treeWidget.addTopLevelItem(category_item)

    def add_item_in_tree(self, item_id: int):
        """Adds item from db in tree with data in column 0 at role 0x100 {"id": int, "parent_id": int, "path": str}"""
        data = Database.db.get_data_by_id_from_table_for_treeWidget(item_id, self.current_tree_name)
        data_dict = eval(data[3])
        element = QtWidgets.QTreeWidgetItem([str(data_dict["title"]), str(data_dict["amount"]),
                                             str(data_dict["weight"])])
        element.setData(0, 0x100, {"id": data[0], "parent_id": data[1], "path": data[2]})
        element.setFlags(QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)
        element.setTextAlignment(0, QtCore.Qt.AlignLeft)
        element.setTextAlignment(1, QtCore.Qt.AlignHCenter)
        element.setTextAlignment(2, QtCore.Qt.AlignHCenter)
        parent_name = Database.db.get_data_by_id_from_table_for_treeWidget(data[1], self.current_tree_name)[3]
        parent = self.treeWidget.findItems(parent_name, QtCore.Qt.MatchExactly, 0)[0]
        parent.addChild(element)
        parent_index = self.treeWidget.indexOfTopLevelItem(parent)
        self.check_if_all_items_are_selected(parent_index)
        self.lcd_number_update()

    def update_item(self):
        """Update item after PyQT signal itemChanged in treeWidget.
        Use @block_signals if you don't want the function to work """
        path = self.treeWidget.currentItem().data(0, 0x100)["path"]
        if not self.treeWidget.currentItem().parent():
            title = self.treeWidget.currentItem().text(0)
            if Database.db.update_element_in_table_for_treeWidget(path, title, self.current_tree_name):
                self.show_system_message("Категория переименованна")
            else:
                self.create_tree()
                self.show_system_message("Изменения отменены")
        else:
            title = self.treeWidget.currentItem().text(0)
            amount = int(self.treeWidget.currentItem().text(1))
            weight = int(self.treeWidget.currentItem().text(2))
            parent_id = self.treeWidget.currentItem().data(0, 0x100)["parent_id"]
            if Database.db.update_element_in_table_for_treeWidget(path,
                                                                  {"title": title, "amount": amount, "weight": weight},
                                                                  self.current_tree_name,
                                                                  parent_id):
                self.show_system_message("Изменения внесены")
            else:
                self.create_tree()
                self.show_system_message("Изменения отменены")
        self.lcd_number_update()

    def delete_selected_item(self):
        """Deletes currentItem from db and tree"""
        if self.treeWidget.currentItem():
            path = self.treeWidget.currentItem().data(0, 0x0100)["path"]
            Database.db.delete_element_from_table_for_treeWidget(path, self.current_tree_name)
            sip.delete(self.treeWidget.currentItem())
            self.treeWidget.update()
            self.treeWidget.setCurrentItem(None)
            self.lcd_number_update()
            self.show_system_message("Элемент удалён")
        else:
            self.show_system_message("Выберите элемент для удаления")

    @block_signals
    def select_item(self, *args):
        """Changes color of item in tree (not for roots) and set data in column 0 at role 0x200 if item is selected.
        *args used because of unexpected QModelIndex in arguments when @block_signals used."""
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
            top_level_item_index = self.treeWidget.indexOfTopLevelItem(self.treeWidget.currentItem().parent())
            self.check_if_all_items_are_selected(top_level_item_index)

    @block_signals
    def check_if_all_items_are_selected(self, index: int):
        """If all items in category are selected, changes color of category"""
        iterator = QtWidgets.QTreeWidgetItemIterator(self.treeWidget)
        visited = []
        self.treeWidget.topLevelItem(index).setForeground(0, self.ColorForSelectedItem)
        while iterator.value():
            item = iterator.value()
            if item not in visited and item.parent() == self.treeWidget.topLevelItem(index):
                visited.append(item)
                if not item.data(0, 0x200):
                    self.treeWidget.topLevelItem(index).setForeground(0, self.ColorForNotSelectedItem)
                    break
            iterator += 1
        self.treeWidget.update()

    def show_system_message(self, text: str):
        """Shows any message in QTextBrowser"""
        try:
            self.App_info.clear()
            self.App_info.append(text)
        except Exception as error:
            print(error.__class__.__name__)


class AddListWindow(QtWidgets.QDialog, add_list_ui.Ui_Add_list):
    closeDialog = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Добавление списка")
        self.buttonBox.accepted.connect(self.ok_button)
        self.buttonBox.rejected.connect(self.close_window)
        self.lineEdit.setFocus()

    def ok_button(self):
        """Creates list if name not in db"""
        list_name = self.lineEdit.text()
        if list_name not in Database.db.get_table_names_for_user() and len(list_name) > 0:
            system_name = Database.db.add_table_in_master(list_name)
            Database.db.create_table_for_treeWidget(system_name)
            window.comboBox.addItem(list_name)
            window.comboBox.setCurrentIndex(window.comboBox.count() - 1)
            window.comboBox.update()
            window.show_system_message("Список создан")
        else:
            window.show_system_message("Пожалуйста, введите другое название списка")
        self.close()

    def close_window(self):
        self.close()

    def closeEvent(self, event):
        self.closeDialog.emit()


class AddCategoryWindow(QtWidgets.QDialog, add_category_ui.Ui_Add_category):
    closeDialog = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setFixedSize(389, 102)
        self.setWindowTitle("Добавление категории")
        self.buttonBox.accepted.connect(self.ok_button)
        self.buttonBox.rejected.connect(self.close_window)
        self.lineEdit.setFocus()

    def ok_button(self):
        """Works if new root inserted into table"""
        category_name = self.lineEdit.text()
        if len(category_name) > 0 \
                and Database.db.insert_new_root_into_table_for_treeWidget(category_name, window.current_tree_name):
            category_id = Database.db.get_id_by_root_name_from_table_for_treeWidget(category_name,
                                                                                    window.current_tree_name)
            window.add_category_in_tree(category_id)
            window.treeWidget.update()
            window.show_system_message("Категория добавлена")
        else:
            window.show_system_message("Неправильное название для категории, возможно такая уже есть")
        window.enable_buttons()

    def close_window(self):
        self.close()

    def closeEvent(self, event):
        self.closeDialog.emit()


class AddItemWindow(QtWidgets.QDialog, add_item_ui.Ui_add_item):
    closeDialog = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setFixedSize(598, 177)
        self.setWindowTitle("Добавление предмета")
        self.tableWidget.setColumnWidth(0, 300)
        self.tableWidget.setColumnWidth(1, 149)
        self.tableWidget.setColumnWidth(2, 120)
        self.tableWidget.setRowHeight(0, 30)
        self.tableWidget.setRowHeight(1, 30)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        self.tableWidget.setFocus()
        self.close_button.clicked.connect(self.close_window)
        self.add_button.clicked.connect(self.add_item)
        self.roots_names = Database.db.get_roots_from_table_for_treeWidget(window.current_tree_name)
        for root_id, root in self.roots_names:
            self.select_category.addItem(root, root_id)

    def close_window(self):
        self.close()

    def add_item(self):
        """Adds item if there is no such item in db"""

        title = self.tableWidget.item(0, 0).text()
        amount = self.tableWidget.item(0, 1).text()
        weight = self.tableWidget.item(0, 2).text()

        if title == '' or amount == '' or weight == '':
            window.show_system_message("Поля не заполнены")
            return

        try:
            category_id = self.select_category.currentData()
            amount = int(amount)
            weight = int(weight)

        except ValueError:
            window.show_system_message("Введены неправильные значения")
            return

        if Database.db.insert_new_item_into_table_for_treeWidget(category_id,
                                                                 {"title": title,
                                                                  "amount": amount,
                                                                  "weight": weight},
                                                                 window.current_tree_name):
            item_id = Database.db.get_id_by_content_from_table_for_treeWidget(category_id,
                                                                              {"title": title,
                                                                               "amount": amount,
                                                                               "weight": weight},
                                                                              window.current_tree_name)
            window.add_item_in_tree(item_id)
            window.show_system_message("Вещь добавлена в список")
        else:
            window.show_system_message("Запись не сделана, такая запись уже есть")

        self.tableWidget.clearContents()
        self.tableWidget.setFocus()

    def closeEvent(self, event):
        self.closeDialog.emit()


app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()


def run_app():
    app.exec()
