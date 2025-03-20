from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
import datetime
from decimal import *

from app.models.product import Product
from .models.inventory import Inventory
from .models.cart import Cart
from .models.user import User
from .models.purchase import Purchase
from .models.order import Order
from .models.coupon import Coupon


from flask import Blueprint
bp = Blueprint('checkoutpage', __name__)

total = 0

class CouponForm(FlaskForm):
    id = IntegerField()
    submit_coupon = SubmitField('Apply')


class SubmitForm(FlaskForm):
    submit_cart = SubmitField('Confirm Order')


@bp.route('/checkoutpage', methods=['GET', 'POST'])
def load_page():
    uid = current_user.id
    cid = request.args.get('cid') if request.args.get('cid') else 0 # Coupon with id = 0 is no discount
    cart = Cart.get_all_by_uid(uid)
    prices = Cart.get_prices(cart)
    prices = [prices[x] * cart[x].quantity for x in range(len(prices))]
    total =  calculate_discount(sum(prices), cid)

    coupon_form = CouponForm()
    if coupon_form.submit_coupon.data not in [0,""] and coupon_form.validate():
        total =  calculate_discount(sum(prices), cid)
        cid = coupon_form.id.data
        if Coupon.get(cid):
            if not Coupon.has_used(uid, cid):
                total = calculate_discount(total, cid)
                return redirect(url_for('checkoutpage.load_page') + '?cid=' + str(cid))
            else:
                flash('This Coupon Has Been Used')
        else:
            flash('Please Enter A Valid Coupon')

    new_prices = [calculate_discount(x, cid) for x in prices]
    new_prices_display = [f'{x} x 0.{100 - Coupon.get_discount(cid)} => {calculate_discount(x, cid)}' for x in prices]
    submit_form = SubmitForm()
    if submit_form.submit_cart.data and submit_form.validate():
        if cid != 0: # Only add the user to the Coupon user-used list if it's not the 0 id
            Coupon.add_user(cid, uid)
        
        submit_cart(uid, cart, total, new_prices, cid, cart.)
        return redirect(url_for('orderspage.load_page'))
    return render_template('checkoutpage.html', 
        cart=cart, prices = new_prices_display if cid not in ["0",""] else prices, num_items=len(cart), total=total, coupon_form=coupon_form, submit_form=submit_form)

def submit_cart(uid, cart, total, prices, cid):
    oid = Order.last_used_id() + 1
    for i in range(len(cart)):
        item = cart[i]
        buy_time = datetime.datetime.now()
        modify_inventory(item.sid, item.pid, item.quantity)
        Purchase.create_purchase(uid, item.pid, item.sid, 
            buy_time, item.quantity, False)
        Order.insert(oid, item.uid, item.pid, item.sid, 
            datetime.datetime.now(), item.quantity, buy_time, False, cid)
    
    User.modify_balance(uid, -1 * int(total))
    User.modify_balance(item.sid, int(total))
    Cart.clear_cart(uid)

    
def modify_inventory(sid, pid, quantity):
    stock = Inventory.get_quantity(sid, pid)
    if stock == quantity:
        Inventory.delete(sid, pid)
    else:
        Inventory.reduce(sid, pid, stock - quantity)

def calculate_discount(num, cid):
    return num * ((100 - Decimal(Coupon.get_discount(cid))) / Decimal(100))
    



        