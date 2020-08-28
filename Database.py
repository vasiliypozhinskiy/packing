import sqlite3
import re


def db_connection(func):
    def connect_close(self, *args, **kwargs):
        self.connection = sqlite3.connect(f"{self.db_path}")
        self.cursor = self.connection.cursor()
        self.cursor.execute("""PRAGMA foreign_keys = ON""")
        func_value = func(self, *args, **kwargs)
        self.cursor.close()
        return func_value

    return connect_close


class PackingDB:
    def __init__(self, path: str):
        self.db_path = path

    @db_connection
    def create_table_tree(self):
        self.cursor.execute(f"""CREATE TABLE IF NOT EXISTS tree
(
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    parent_id INTEGER REFERENCES tree (id),
    path TEXT NOT NULL UNIQUE DEFAULT '',
    content TEXT NOT NULL DEFAULT ''
)""")

        self.cursor.execute(f"""
    CREATE TRIGGER IF NOT EXISTS tree__ai_path_set AFTER INSERT ON tree
    BEGIN
        
        UPDATE tree
            SET path =
                CASE
                    WHEN parent_id IS NULL THEN '.' || NEW.id || '.'
                    ELSE (
                            SELECT path || NEW.id || '.'
                            FROM tree
                            WHERE id = NEW.parent_id
                        )
                END
            WHERE id = NEW.id;
    END;""")

        self.cursor.execute(f"""
    CREATE TRIGGER IF NOT EXISTS tree__bd_tree_remove BEFORE DELETE ON tree
    BEGIN

        DELETE FROM tree
            WHERE path LIKE OLD.path || '_%';
    END""")

        self.cursor.execute(f"""
    CREATE TRIGGER IF NOT EXISTS tree__bu_integrity_check BEFORE UPDATE OF id, path ON tree
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
                                    FROM tree
                                    WHERE id = NEW.parent_id
                                )
                        END 
                    OR NEW.path LIKE '%.' || OLD.id || '._%' 
                        THEN RAISE(ABORT, 'An attempt to damage the integrity of the tree.')
            END;
    END;""")

        self.cursor.execute(f"""
    CREATE TRIGGER IF NOT EXISTS tree__au_path_update AFTER UPDATE OF parent_id ON tree
    BEGIN
        SELECT
            CASE
                WHEN NEW.parent_id IS OLD.id 
                        THEN RAISE(ABORT, 'An attempt to damage the integrity of the tree.')
            END;
        
        UPDATE tree
            SET path = REPLACE(
                    path,
                    OLD.path,
                    CASE
                        WHEN NEW.parent_id IS NULL THEN '.' || OLD.id || '.'
                        ELSE (
                                SELECT path || OLD.id || '.'
                                FROM tree
                                WHERE id = NEW.parent_id
                            )
                    END
                )
            WHERE path LIKE OLD.path || '%';
    END;
""")
        self.connection.commit()

    @db_connection
    def insert_new_root_into_table_tree(self, name_of_root):
        """Return True if new root recorded, else False"""
        self.cursor.execute(f"""SELECT id FROM tree WHERE content = '{name_of_root}'""")
        if not self.cursor.fetchone():
            self.cursor.execute(f"""INSERT INTO tree (content) VALUES ('{name_of_root}') """)
            self.connection.commit()
            return True
        return False

    @db_connection
    def insert_new_item_into_table_tree(self, parent_id, content) -> bool:
        """Return True if new item recorded, else False"""
        pattern = r"\{'title': '\w+', 'amount': \d+, 'weight': \d+\}"
        if re.findall(pattern, str(content)):
            self.cursor.execute(f"""SELECT id FROM tree WHERE parent_id = {parent_id} AND content = :content""",
                                {"content": str(content)})
            if not self.cursor.fetchone():
                self.cursor.execute(f"""INSERT INTO tree (parent_id, content) VALUES ({parent_id}, :content) """,
                                    {"content": str(content)})
                self.connection.commit()
                return True
        return False

    @db_connection
    def get_table_tree(self):
        self.cursor.execute(f"""SELECT * FROM tree ORDER BY parent_id""")
        content = []
        for row in self.cursor:
            content.append(row)
        return content

    @db_connection
    def get_roots_from_tree(self) -> list:
        self.cursor.execute(f"""SELECT id, content FROM tree WHERE parent_id IS NULL""")
        roots = []
        for row in self.cursor:
            roots.append(row)
        return roots

    @db_connection
    def get_children_of_node(self, node_id) -> list:
        self.cursor.execute(f"""SELECT id FROM tree WHERE path LIKE(
                                SELECT path || '%.' FROM tree WHERE id = {node_id}) ORDER BY path""")
        children_ids = []

        for children_id in self.cursor:
            children_ids.append(children_id[0])
        return children_ids

    @db_connection
    def get_data_by_id(self, element_id):
        self.cursor.execute(f"""SELECT * FROM tree WHERE id = {element_id}""")
        data = self.cursor.fetchone()
        if data:
            return data

    @db_connection
    def drop_table_tree(self):
        self.cursor.execute("""DROP TABLE IF EXISTS tree""")
        self.connection.commit()

    @db_connection
    def get_id_by_content(self, parent_id, content):
        self.cursor.execute(f"""SELECT id FROM tree WHERE parent_id = {parent_id} AND content = :content""",
                            {"content": str(content)})
        item_id = self.cursor.fetchone()
        if item_id:
            return item_id[0]

    @db_connection
    def delete_element(self, path):
        self.cursor.execute(f"""DELETE FROM tree WHERE path = :path""",
                            {"path": path})
        self.connection.commit()


if __name__ != "__main__":
    db = PackingDB("packing.db")
    db.drop_table_tree()
    db.create_table_tree()
    db.insert_new_root_into_table_tree("Аптечка")
    db.insert_new_root_into_table_tree("Еда")
    db.insert_new_item_into_table_tree(2, {'title': 'Кекс', 'amount': 5, 'weight': 100})
    db.insert_new_item_into_table_tree(2, {'title': 'Яблоко', 'amount': 1, 'weight': 100})
    db.insert_new_item_into_table_tree(2, {'title': 'Творог', 'amount': 2, 'weight': 100})
    db.insert_new_item_into_table_tree(1, {'title': 'Йод', 'amount': 3, 'weight': 100})
    db.insert_new_root_into_table_tree("Одежда")


if __name__ == "__main__":
    db = PackingDB("test.db")
    db.drop_table_tree()
    db.create_table_tree()
    db.insert_new_root_into_table_tree("Аптечка")
    db.insert_new_root_into_table_tree("Еда")
    db.insert_new_item_into_table_tree(2, {'title': 'Кекс', 'amount': 5, 'weight': 100})
    db.insert_new_item_into_table_tree(2, {'title': 'Яблоко', 'amount': 2, 'weight': 100})
    db.insert_new_item_into_table_tree(2, {'title': 'Творог', 'amount': 3, 'weight': 100})
    db.insert_new_item_into_table_tree(1, {'title': 'Йод', 'amount': 5, 'weight': 100})
    db.insert_new_root_into_table_tree("Одежда")
    db.insert_new_item_into_table_tree(3, {'title': 'Носки', 'amount': 4, 'weight': 100})
    db.insert_new_item_into_table_tree(3, {'title': 'Футболка', 'amount': 3, 'weight': 100})
    db.insert_new_item_into_table_tree(3, {'title': 'Кепка', 'amount': 1, 'weight': 100})

    print(db.get_roots_from_tree())
    # db.delete_element(".2.")
    print(db.get_table_tree())
    print(db.get_children_of_node(2))
    print(db.get_data_by_id(2))
    print(db.get_id_by_content(3, {'title': 'Кепка', 'amount': 1, 'weight': 100}))



