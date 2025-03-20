from flask import current_app as app
from decimal import *

from .product import Product
from .coupon import Coupon


class Order:
    def __init__(self, id, oid, uid, pid, sid, time_fulfilled, quantity, time_created, status, cid):
        self.id = id
        self.oid = oid
        self.uid = uid
        self.pid = pid
        self.sid = sid
        self.time_fulfilled = time_fulfilled
        self.quantity = quantity
        self.time_created = time_created
        self.status = status
        self.price = Product.get_price(pid, Product.get(pid).creator) * quantity * ((100 - Decimal(Coupon.get_discount(cid))) / Decimal(100))
        self.cid = cid
    

    @staticmethod
    def get_all_by_uid(uid):
        rows = app.db.execute('''
        SELECT *
        FROM Orders
        WHERE uid = :uid
        ''', uid=uid)

        return [Order(*row) for row in rows]
    

    @staticmethod
    def get_all_by_oid(oid):
        rows = app.db.execute('''
        SELECT *
        FROM Orders
        WHERE oid = :oid
        ''', oid=oid)

        return [Order(*row) for row in rows]
    

    @staticmethod
    def insert( oid, uid, pid, sid, time_fulfilled, quantity, time_created, status, cid):
        app.db.execute('''
        INSERT INTO Orders(id, oid, uid, pid, sid, time_fulfilled, quantity, time_created, status, cid)
        VALUES (:id, :oid, :uid, :pid, :sid, :time_fulfilled, :quantity, :time_created, :status, :cid)''',
        id = app.db.execute('''
                SELECT MAX(id)
                FROM Orders
                ''')[0][0] + 1, oid=oid, uid=uid, pid=pid, sid=sid, time_fulfilled=time_fulfilled, 
            quantity=quantity, time_created=time_created, status=status, cid=cid)
    

    @staticmethod
    def last_used_id():
        id = app.db.execute('''
        SELECT MAX(oid)
        FROM Orders''')[0][0]

        return id
    

    @staticmethod
    def get_dictionary_form(uid):
        rows = app.db.execute('''
        SELECT *
        FROM Orders
        WHERE uid = :uid
        ''', uid=uid)
        rows = [Order(*row) for row in rows]

        ret = {}
        for r in rows:
            if r.oid not in ret.keys():
                ret[r.oid] = []
            ret[r.oid].append(r)
        
        return ret


    @staticmethod
    def get_price(oid):
        prices = []
        rows = Order.get_all_by_oid(oid)
        for item in rows:
            prices.append(Product.get_price(item.pid, item.sid))
        prices = [prices[x] * rows[x].quantity for x in range(len(prices))]
        
        return sum(prices)
        

    @staticmethod
    def size():
        size = app.db.execute('''
        SELECT COUNT(*)
        FROM Orders''')

        return size[0][0]
    

    @staticmethod
    def update_status(uid, pid, sid, time_created, status):
        app.db.execute('''
        UPDATE Orders
        SET status = :status
        WHERE uid = :uid
        AND pid = :pid
        AND sid = :sid
        AND time_created = :time_created''', 
        uid=uid, pid=pid, sid=sid, time_created=time_created, status=status)


    