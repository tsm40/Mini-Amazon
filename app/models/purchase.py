from flask import current_app as app

from .product import Product


class Purchase:
    def __init__(self, id, uid, pid, sid, time_purchased, quantity, status, time_fulfilled):
        self.id = int(id)
        self.uid = int(uid)
        self.pid = int(pid)
        self.sid = int(sid)
        self.time_purchased = time_purchased
        self.quantity = quantity
        self.status = bool(status)
        self.time_fulfilled = time_fulfilled


    @staticmethod
    def get(id):
        rows = app.db.execute('''
        SELECT id, uid, pid, time_purchased
        FROM Purchases
        WHERE id = :id
        ''', id=id)
        return Purchase(*(rows[0])) if rows else None


    @staticmethod
    def get(uid, pid, sid, time_purchased):
        rows = app.db.execute('''
        SELECT id, uid, pid, sid, time_purchased, quantity, status, time_fulfilled
        FROM Purchases
        WHERE uid = :uid
        AND pid = :pid
        AND sid = :sid
        AND time_purchased = :time_purchased''', uid=uid, pid=pid, sid=sid, time_purchased=time_purchased)

        return [Purchase(*row) for row in rows]


    @staticmethod
    def get_all_by_uid_since(uid, since):
        rows = app.db.execute('''
SELECT id, uid, pid, sid, time_purchased, quantity, status, time_fulfilled
FROM Purchases
WHERE uid = :uid
AND time_purchased >= :since
ORDER BY time_purchased DESC
''',
                              uid=uid,
                              since=since)
        return [Purchase(*row) for row in rows]

    @staticmethod
    def uid_purchased_pid(uid, pid):
        rows = app.db.execute("""
            SELECT id
            FROM Purchases
            WHERE uid = :uid
            AND pid = :pid
            """, 
            uid=uid, pid=pid)
        return len(rows) > 0


    @staticmethod
    def get_all_by_uid(uid):
        rows = app.db.execute('''
        SELECT id, uid, pid, sid, time_purchased, quantity, status, time_fulfilled
        FROM Purchases
        WHERE uid = :uid
        ORDER BY time_purchased DESC''', uid=uid)

        return [Purchase(*row) for row in rows]


    @staticmethod
    def get_all_by_sid(sid):
        rows = app.db.execute('''
        SELECT id, uid, pid, sid, time_purchased, quantity, status, time_fulfilled
        FROM Purchases
        WHERE sid = :sid
        ORDER BY time_purchased DESC''', sid=sid)

        return [Purchase(*row) for row in rows]


    @staticmethod
    def get_uid(oid):
        uid = app.db.execute('''
        SELECT uid
        FROM Purchases
        WHERE id = :oid''', oid=oid)

        return uid[0][0]


    @staticmethod
    def get_pid(oid):
        pid = app.db.execute('''
        SELECT pid 
        FROM Purchases
        WHERE id = :oid''', oid=oid)

        return pid[0][0]

    @staticmethod
    def get_quantity(oid):
        quantity = app.db.execute('''
        SELECT quantity
        FROM Purchases
        WHERE id = :oid''', oid=oid)

        return quantity[0][0]


    @staticmethod
    def update_status(oid, new_status):
        app.db.execute('''
        UPDATE Purchases
        SET status = :new_status
        WHERE id = :oid''', oid=oid, new_status=new_status)

    
    @staticmethod
    def update_quantity(oid, quantity):
        app.db.execute('''
        UPDATE Purchases
        SET quantity = :quantity
        WHERE id = :oid''', quantity=quantity, oid=oid)
    

    @staticmethod
    def size():
        size = app.db.execute('''
        SELECT COUNT(*)
        FROM Purchases''')

        return size[0][0]


    @staticmethod
    def create_purchase(uid, pid, sid, time_purchased, quantity, status):
        id = Purchase.size() + 1
        app.db.execute('''
        INSERT INTO Purchases(id, uid, pid, sid, time_purchased, quantity, status)
        VALUES (:id, :uid, :pid, :sid, :time_purchased, :quantity, :status)''',
        id=id, uid=uid, pid=pid, sid=sid, time_purchased=time_purchased, 
        quantity=quantity, status=status)
    

    @staticmethod
    def get_status(uid, pid, sid, time_purchased):
        purchase = Purchase.get(uid, pid, sid, time_purchased)[0]

        return purchase.status
    

    @staticmethod
    def get_time_fulfilled(uid, pid, sid, time_purchased):
        purchase = Purchase.get(uid, pid, sid, time_purchased)[0]

        return purchase.time_fulfilled

    @staticmethod
    def has_uid_bought_from_sid(uid, sid):
        rows = app.db.execute('''
        SELECT * 
        FROM Purchases
        WHERE uid = :uid AND sid = :sid
        ''', uid = uid, sid=sid)
        return rows
    

    @staticmethod
    def get_sales(sid):
        prods = Purchase.get_all_by_sid(sid)
        names = [Product.get_name(prod.pid) for prod in prods]
        temp = {}
        for i in range(len(prods)):
            if names[i] not in temp.keys():
                temp[names[i]] = 0
            temp[names[i]] += prods[i].quantity
        
        sales = []
        for p in temp:
            sales.append(tuple((p, temp[p])))
        sales = sorted(sales, key=lambda x: x[1], reverse=True)
        
        return sales
