from flask import current_app as app
from flask_wtf import FlaskForm
from wtforms import SubmitField, IntegerField
from wtforms.validators import DataRequired

from .inventory import Inventory
from .product import Product

class AddtoCartForm(FlaskForm):
    seller = IntegerField('')
    quantity = IntegerField('Filter Value', validators=[DataRequired()]) 
    submit_to_cart = SubmitField('Submit')

class Cart:
    """
    This is just a TEMPLATE for Cart, you should change this by adding or 
        replacing new columns, etc. for your design.
    """
    def __init__(self, id, uid, pid, sid, quantity):
        self.id = id
        self.uid = uid
        self.pid = pid
        self.sid = sid
        self.quantity = quantity


    @staticmethod
    def get(id):
        rows = app.db.execute('''
        SELECT *
        FROM Cart
        WHERE id = :id
        ''', id=id)

        return Cart(*(rows[0])) if rows else None


    @staticmethod
    def get_all_by_uid(uid):
        rows = app.db.execute('''
        SELECT *
        FROM Cart
        WHERE uid = :uid
        ''', uid=uid)

        return [Cart(*row) for row in rows]

    @staticmethod
    def get_by_sid_for_pid(sid, pid, uid):
        rows = app.db.execute('''
        SELECT id, uid, sid, pid, quantity
        FROM Cart
        WHERE sid = :sid AND pid = :pid AND uid = :uid
        ''', sid=sid, pid = pid, uid=uid)

        return [Cart(*row) for row in rows][0] if rows else None


    @staticmethod
    def add_to_cart(uid, pid, quantity, sid):
        existing_entry = Cart.get_by_sid_for_pid(sid, pid, uid)
        if existing_entry:
            Cart.modify_quantity(existing_entry.id, min(existing_entry.quantity + quantity, Inventory.get_quantity(sid, pid)))
        else:
            existing_entry = app.db.execute('''
                INSERT INTO Cart(id, uid, pid, sid, quantity)
                VALUES(:id, :uid, :pid, :sid, :quantity)
                RETURNING id
                ''',
                id = app.db.execute('''
                SELECT MAX(id)
                FROM Cart
                ''')[0][0] + 1,
                uid = uid,
                pid = pid,
                sid = sid,
                quantity = quantity)
        existing_entry = Cart.get_by_sid_for_pid(sid, pid, uid)
        return Cart.get(existing_entry.id)
    

    @staticmethod
    def modify_quantity(id, new_quantity):
        app.db.execute('''
        UPDATE Cart
        SET quantity = :new_quantity
        WHERE id = :id''', id=id, new_quantity=new_quantity)

    
    @staticmethod
    def delete(id):
        app.db.execute('''
        DELETE FROM Cart
        WHERE id = :id''', id=id)
    

    @staticmethod
    def get_prices(cart):
        prices = []
        for item in cart:
            prices.append(Product.get_price(item.pid, item.sid))
        
        return prices
    

    @staticmethod
    def clear_cart(uid):
        app.db.execute('''
        DELETE FROM Cart
        WHERE uid = :uid''', uid=uid)
    

    @staticmethod
    def size():
        size = app.db.execute('''
        SELECT COUNT(*)
        FROM CART''')

        return size[0][0]
    

    @staticmethod
    def all():
        rows = app.db.execute('''
        SELECT *
        FROM CART''')

        return [Cart(*row) for row in rows]