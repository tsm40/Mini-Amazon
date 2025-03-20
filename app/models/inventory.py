from flask import current_app as app


class Inventory:
    """
    This is just a TEMPLATE for Inventory, you should change this by adding or 
        replacing new columns, etc. for your design.
    """
    def __init__(self, id, uid, pid, quantity):
        self.id = id
        self.uid = uid
        self.pid = pid
        self.quantity = quantity


    @staticmethod
    def get_entry_by_pid(pid):
        rows = app.db.execute('''
SELECT id, uid, pid, quantity
FROM Inventory
WHERE pid = :pid
''',
                              pid=pid)
        return rows


    @staticmethod
    def get_by_uid(uid):
        rows = app.db.execute('''
SELECT id, uid, pid, quantity
FROM Inventory
WHERE uid = :uid
''',
                              uid=uid)

        return [Inventory(*row) for row in rows] 


    @staticmethod
    def update(new_quantity, uid, pid): 
        app.db.execute('''
        UPDATE Inventory
        SET quantity = :new_quantity
        WHERE uid = :uid 
        AND pid = :pid''', new_quantity=new_quantity, uid=uid, pid=pid)
    

    @staticmethod
    def delete(uid, pid):
        app.db.execute('''
        DELETE FROM Inventory
        WHERE uid = :uid 
        AND pid = :pid''', uid=uid, pid=pid)

    
    @staticmethod
    def get_quantity(uid, pid):
        quantity = app.db.execute('''
        SELECT quantity
        FROM Inventory
        WHERE uid = :uid
        AND pid = :pid''', uid=uid, pid=pid)

        return quantity[0][0]


    @staticmethod
    def reduce(uid, pid, amount):
        quantity = app.db.execute('''
        UPDATE Inventory
        SET quantity = :amount
        WHERE uid = :uid
        AND pid = :pid''', amount=amount, uid=uid, pid=pid)

    
    @staticmethod
    def size():
        size = app.db.execute('''
        SELECT COUNT(*)
        FROM Inventory''')

        return size[0][0]


    @staticmethod
    def add_product(uid, pid, quantity):
        try:
            id = app.db.execute('''
            SELECT MAX(id)
            FROM Inventory
            ''')[0][0] + 1
            app.db.execute('''
            INSERT INTO Inventory(id, uid, pid, quantity)
            VALUES (:id, :uid, :pid, :quantity)''', id=id, uid=uid, pid=pid, quantity=quantity)
            
            return True
        except:
            return False

    @staticmethod
    def is_uid_selling_pid(uid, pid):
        rows = app.db.execute('''
        SELECT * 
        FROM Inventory
        WHERE uid = :uid AND pid = :pid
        ''', uid = uid, pid=pid)
        return rows if rows else None