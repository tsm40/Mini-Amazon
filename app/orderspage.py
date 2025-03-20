from flask import render_template, request
from flask_login import current_user
from decimal import *

from .models.order import Order
from .models.coupon import Coupon

from flask import Blueprint
bp = Blueprint('orderspage', __name__)


class OrderWrapper():
    def __init__(self, oid, orders, total_price, time_created, fulfilled, num_orders):
        self.oid = oid
        self.oid_str = str(oid)
        self.total_price = total_price
        self.orders = orders
        self.num_orders = num_orders
        self.time_created = time_created
        self.fulfilled = fulfilled
    

@bp.route('/orderspage', methods=['GET', 'POST'])
def load_page():
    orders = Order.get_dictionary_form(current_user.id)
    [print([(y.price, y.quantity) for y in orders[x]]) for x in orders]
    order_wrappers = sorted([OrderWrapper(
                        oid, 
                        orders[oid],
                        sum([(y.price) for y in orders[oid]]),
                        min([x.time_created for x in orders[oid]]),
                        orders[oid][0].status,
                        len(orders[oid])
                        ) for oid in orders], key = lambda x : x.time_created, reverse = True)
    return render_template('orderspage.html', order_wrappers=order_wrappers)


