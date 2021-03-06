import sqlite3
import re
import functools


def db_connection(func):
    """Must to use this in all public methods of PackingDB"""
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        self.connection = sqlite3.connect(f"{self.db_path}")
        self.cursor = self.connection.cursor()
        self.cursor.execute("""PRAGMA foreign_keys = ON""")
        func_value = func(self, *args, **kwargs)
        self.cursor.close()
        return func_value

    return wrapper


class PackingDB:
    def __init__(self, path: str):
        self.db_path = path

    @db_connection
    def create_master_table(self):
        """The table separates the name for the user and the name for the system.
        Because of this the user can specify any name for the set."""
        self.cursor.execute(f"""CREATE TABLE IF NOT EXISTS master
(
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    table_name_for_user TEXT NOT NULL UNIQUE
)""")
        self.connection.commit()

    @db_connection
    def add_table_in_master(self, table_name_for_user: str) -> str:
        self.cursor.execute(f"""SELECT id FROM master WHERE table_name_for_user = :current_table_name""",
                            {"current_table_name": table_name_for_user})
        if not self.cursor.fetchone():
            self.cursor.execute(f"""INSERT INTO master (table_name_for_user) 
                                    VALUES (:name_for_user)""",
                                {"name_for_user": table_name_for_user})
            self.cursor.execute(f"""SELECT id FROM master 
                                    WHERE table_name_for_user = :current_table_name""",
                                {"current_table_name": table_name_for_user})
            self.connection.commit()
            return "table" + str(self.cursor.fetchone()[0])

    def delete_from_master(self, table_name_for_system: str):
        self.cursor.execute(f"""DELETE FROM master WHERE id = :id""",
                            {"id": int(table_name_for_system[5:])})

    @db_connection
    def get_system_name_by_user_name(self, table_name_for_user: str) -> str:
        self.cursor.execute(f"""SELECT id FROM master 
                                        WHERE table_name_for_user = :current_table_name""",
                            {"current_table_name": table_name_for_user})
        return "table" + str(self.cursor.fetchone()[0])

    @db_connection
    def get_table_names_for_user(self) -> list:
        """Get list of names, which user enter into program"""
        self.cursor.execute(f"""SELECT table_name_for_user FROM master""")
        table_names = []
        for row in self.cursor:
            table_names.append(row[0])
        return table_names

    @db_connection
    def create_table_for_treeWidget(self, table_name_for_system: str):
        """Сreates a table with triggers that guarantee data integrity"""
        self.cursor.execute(f"""CREATE TABLE IF NOT EXISTS {table_name_for_system}
(
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    parent_id INTEGER REFERENCES {table_name_for_system} (id),
    path TEXT NOT NULL UNIQUE DEFAULT '',
    content TEXT NOT NULL DEFAULT ''
)""")

        self.cursor.execute(f"""
    CREATE TRIGGER IF NOT EXISTS {table_name_for_system}__ai_path_set AFTER INSERT ON {table_name_for_system}
    BEGIN
        
        UPDATE {table_name_for_system}
            SET path =
                CASE
                    WHEN parent_id IS NULL THEN '.' || NEW.id || '.'
                    ELSE (
                            SELECT path || NEW.id || '.'
                            FROM {table_name_for_system}
                            WHERE id = NEW.parent_id
                        )
                END
            WHERE id = NEW.id;
    END;""")

        self.cursor.execute(f"""
    CREATE TRIGGER IF NOT EXISTS {table_name_for_system}__bd_{table_name_for_system}_remove 
    BEFORE DELETE ON {table_name_for_system}
    BEGIN

        DELETE FROM {table_name_for_system}
            WHERE path LIKE OLD.path || '_%';
    END""")

        self.cursor.execute(f"""
    CREATE TRIGGER IF NOT EXISTS {table_name_for_system}__bu_integrity_check 
    BEFORE UPDATE OF id, path ON {table_name_for_system}
    BEGIN
        SELECT
            CASE
                WHEN OLD.id != NEW.id
                    OR NEW.parent_id IS OLD.id 
                    OR NEW.path !=
                        CASE
                            WHEN NEW.parent_id IS NULL THEN '.' || OLD.id || '.'
                            ELSE (
                                    SELECT path || OLD.id || '.'
                                    FROM {table_name_for_system}
                                    WHERE id = NEW.parent_id
                                )
                        END 
                    OR NEW.path LIKE '%.' || OLD.id || '._%' 
                        THEN RAISE(ABORT, 'An attempt to damage the integrity of the {table_name_for_system}.')
            END;
    END;""")

        self.cursor.execute(f"""
    CREATE TRIGGER IF NOT EXISTS {table_name_for_system}__au_path_update 
    AFTER UPDATE OF parent_id ON {table_name_for_system}
    BEGIN
        SELECT
            CASE
                WHEN NEW.parent_id IS OLD.id 
                        THEN RAISE(ABORT, 'An attempt to damage the integrity of the {table_name_for_system}.')
            END;
        
        UPDATE {table_name_for_system}
            SET path = REPLACE(
                    path,
                    OLD.path,
                    CASE
                        WHEN NEW.parent_id IS NULL THEN '.' || OLD.id || '.'
                        ELSE (
                                SELECT path || OLD.id || '.'
                                FROM {table_name_for_system}
                                WHERE id = NEW.parent_id
                            )
                    END
                )
            WHERE path LIKE OLD.path || '%';
    END;
""")
        self.connection.commit()

    @db_connection
    def insert_new_root_into_table_for_treeWidget(self, name_of_root: str, table_name_for_system: str) -> bool:
        """Return True if new root recorded, else False"""
        self.cursor.execute(f"""SELECT id FROM {table_name_for_system} WHERE content = '{name_of_root}'""")
        if not self.cursor.fetchone():
            self.cursor.execute(f"""INSERT INTO {table_name_for_system} (content) VALUES ('{name_of_root}') """)
            self.connection.commit()
            return True
        return False

    @db_connection
    def insert_new_item_into_table_for_treeWidget(self, parent_id: int,
                                                  content: dict,
                                                  table_name_for_system: str) -> bool:
        """Returns True if new item recorded, else False.
        The content must be of the following format: {'title': str, 'amount': int, 'weight': int}"""
        pattern = r"\{'title': '.+', 'amount': \d+, 'weight': \d+\}"
        if re.findall(pattern, str(content)):
            self.cursor.execute(f"""SELECT id FROM {table_name_for_system} 
                                    WHERE parent_id = {parent_id} AND content = :content""",
                                {"content": str(content)})
            if not self.cursor.fetchone():
                self.cursor.execute(f"""INSERT INTO {table_name_for_system} (parent_id, content) 
                                        VALUES ({parent_id}, :content) """,
                                    {"content": str(content)})
                self.connection.commit()
                return True
        return False

    @db_connection
    def get_table_for_treeWidget(self, table_name_for_system: str) -> list:
        """Returns all table as list of rows (tuples)"""
        self.cursor.execute(f"""SELECT * FROM {table_name_for_system} ORDER BY parent_id""")
        content = []
        for row in self.cursor:
            content.append(row)
        return content

    @db_connection
    def get_roots_from_table_for_treeWidget(self, table_name_for_system: str) -> list:
        """Returns list of roots in format: (id: int, 'title': str)"""
        self.cursor.execute(f"""SELECT id, content FROM {table_name_for_system} WHERE parent_id IS NULL""")
        roots = []
        for row in self.cursor:
            roots.append(row)
        return roots

    @db_connection
    def get_children_of_node_from_table_for_treeWidget(self, node_id: int, table_name_for_system: str) -> list:
        self.cursor.execute(f"""SELECT id FROM {table_name_for_system} WHERE path LIKE(
                                SELECT path || '%.' FROM {table_name_for_system} WHERE id = {node_id}) ORDER BY path""")
        children_ids = []

        for children_id in self.cursor:
            children_ids.append(children_id[0])
        return children_ids

    @db_connection
    def get_data_by_id_from_table_for_treeWidget(self, element_id: int, table_name_for_system: str) -> tuple:
        """Returns data if format: (id, parent_id, path, content)
        For root content = 'title': str
        For children content like {'title': str, 'amount': int, 'weight': int}
        (It's str, not dict)"""
        self.cursor.execute(f"""SELECT * FROM {table_name_for_system} WHERE id = {element_id}""")
        data = self.cursor.fetchone()
        if data:
            return data

    @db_connection
    def get_id_by_content_from_table_for_treeWidget(self, parent_id: int, content: dict, table_name_for_system: str):
        """Tested only for children"""
        self.cursor.execute(f"""SELECT id FROM {table_name_for_system} 
                                WHERE parent_id = {parent_id} AND content = :content""",
                            {"content": str(content)})
        item_id = self.cursor.fetchone()
        if item_id:
            return item_id[0]

    @db_connection
    def get_id_by_root_name_from_table_for_treeWidget(self, name_of_root: str, table_name_for_system: str) -> int:
        self.cursor.execute(f"""SELECT id FROM {table_name_for_system} WHERE content = '{name_of_root}'""")
        root_id = self.cursor.fetchone()
        if root_id:
            return root_id[0]

    @db_connection
    def delete_element_from_table_for_treeWidget(self, path: str, table_name_for_system: str):
        self.cursor.execute(f"""DELETE FROM {table_name_for_system} WHERE path = :path""",
                            {"path": path})
        self.connection.commit()

    @db_connection
    def update_element_in_table_for_treeWidget(self, path: str,
                                               new_content,
                                               table_name_for_system: str,
                                               parent_id=None) -> bool:
        """Returns True if item updated, else False.
        For root content = title, for children in format {"title": str, "amount": int, "weight": int}"""
        pattern = r"\{'title': '.+', 'amount': \d+, 'weight': \d+\}"
        if parent_id and re.findall(pattern, str(new_content)):
            self.cursor.execute(f"""SELECT id FROM {table_name_for_system} 
                                    WHERE parent_id = :parent_id AND content = :new_content""",
                                {"new_content": str(new_content), "parent_id": parent_id})
            if not self.cursor.fetchone():
                self.cursor.execute(f"""UPDATE {table_name_for_system} SET content = :new_content WHERE path = :path""",
                                    {"path": path, "new_content": str(new_content)})
                self.connection.commit()
                return True
        elif not parent_id and new_content is str:
            self.cursor.execute(f"""SELECT id FROM {table_name_for_system} WHERE content = :new_content""")
            if not self.cursor.fetchone():
                self.cursor.execute(f"""UPDATE {table_name_for_system} SET content = :new_content WHERE path = :path""",
                                    {"path": path, "new_content": str(new_content)})
                self.connection.commit()
                return True
        return False

    @db_connection
    def drop_table(self, table_name_for_system):
        if table_name_for_system != "master":
            self.delete_from_master(table_name_for_system)
        self.cursor.execute(f"""DROP TABLE IF EXISTS {table_name_for_system}""")
        self.connection.commit()


if __name__ != "__main__":
    db = PackingDB("packing.db")
    db.create_master_table()
    default_table = db.add_table_in_master("Список по умолчанию")
    db.create_table_for_treeWidget(default_table)

if __name__ == "__main__":
    db = PackingDB("test.db")
    db.drop_table("master")
    db.create_master_table()
    # db.drop_table("tree")
    # db.drop_table("test_table")
    db.create_table_for_treeWidget("table2")
    db.insert_new_root_into_table_for_treeWidget("Аптечка", "table2")
    db.insert_new_root_into_table_for_treeWidget("Еда", "table2")
    db.insert_new_item_into_table_for_treeWidget(2, {'title': 'Кекс', 'amount': 5, 'weight': 100}, "table2")
    db.insert_new_item_into_table_for_treeWidget(2, {'title': 'Яблоко', 'amount': 2, 'weight': 100}, "table2")
    db.insert_new_item_into_table_for_treeWidget(2, {'title': 'Творог', 'amount': 3, 'weight': 100}, "table2")
    db.insert_new_item_into_table_for_treeWidget(1, {'title': 'Йод', 'amount': 5, 'weight': 100}, "table2")
    db.insert_new_root_into_table_for_treeWidget("Одежда", "table2")
    db.insert_new_item_into_table_for_treeWidget(3, {'title': 'Носки', 'amount': 4, 'weight': 100}, "table2")
    db.insert_new_item_into_table_for_treeWidget(3, {'title': 'Футболка', 'amount': 3, 'weight': 100}, "table2")
    db.insert_new_item_into_table_for_treeWidget(3, {'title': 'Кепка', 'amount': 1, 'weight': 100}, "table2")

    print(db.get_roots_from_table_for_treeWidget("table2"))
    print(db.get_table_for_treeWidget("table2"))
    print(db.get_children_of_node_from_table_for_treeWidget(2, "table2"))
    print(db.get_id_by_content_from_table_for_treeWidget(3, {'title': 'Кепка', 'amount': 1, 'weight': 100}, "table2"))

    system_name = db.add_table_in_master("имя новой таблицы")
    print(system_name)
    print(db.get_table_names_for_user())
    print(db.get_data_by_id_from_table_for_treeWidget(2, "table2"))
    print(db.get_data_by_id_from_table_for_treeWidget(10, "table2"))
    print(db.get_id_by_root_name_from_table_for_treeWidget("Еда", "table2"))
