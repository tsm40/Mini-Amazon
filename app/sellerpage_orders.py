from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import SubmitField, IntegerField, StringField, SelectField, DecimalField

from .models.inventory import Inventory
from .models.purchase import Purchase
from .models.user import User
from .models.order import Order
from .models.refund import Refund

from flask import Blueprint
bp = Blueprint('sellerpage_orders', __name__)


class DisplayedPurchase():
    def __init__(self, purchase, name, address):
        self.purchase = purchase
        self.name = name
        self.address = address


class OrdersForm(FlaskForm):
    oid = IntegerField('')
    bid = IntegerField('')
    pid = IntegerField('')
    order_amount = IntegerField('')
    time_purchased = StringField('')
    fulfill = SubmitField('Fulfill')


class SearchForm(FlaskForm):
    filter = SelectField('Filter Type', choices = ["Status", "Search For"])
    value = StringField('Buyer ID')
    search = SubmitField('Search')

class RefundsForm(FlaskForm):
    id = IntegerField('')
    uid = IntegerField('')
    value = DecimalField('')
    accept = SubmitField('Accept')

@bp.route('/sellerpage_orders', methods=['GET', 'POST'])
def load_page(): 
    orders = build_displayed_purchases(current_user.id, "sid")
    sid = current_user.firstname

    search_form = SearchForm()
    orders_form = OrdersForm()
    refunds_form = RefundsForm()

    if search_form.search.data and search_form.validate():
        if search_form.filter.data == "Status":
            orders.sort(key = lambda x : x.purchase.status)
        else:
            if search_form.value.data:
                orders =  build_displayed_purchases(search_form.value.data, "uid")
            else:
                return redirect(url_for('sellerpage_orders.load_page')) 

    if orders_form.fulfill.data and orders_form.validate():
        fulfill_order(orders_form)
        return redirect(url_for('sellerpage_orders.load_page'))

    if refunds_form.accept.data and refunds_form.validate():
        Refund.accept_request(refunds_form.id.data, refunds_form.uid.data,
        refunds_form.value.data, current_user.id)
        return redirect(url_for('sellerpage_orders.load_page'))

    refund_requests = Refund.get_by_sid(current_user.id)

    return render_template('sellerpage_orders.html', orders=orders, orders_form=orders_form, 
        sid=sid, search_form=search_form, refund_requests=refund_requests,
        refunds_form=refunds_form)

def fulfill_order(orders_form):
    oid = orders_form.oid.data
    bid = orders_form.bid.data
    pid = orders_form.pid.data
    time_purchased = orders_form.time_purchased.data
    sid = current_user.id

    Purchase.update_status(oid, True)
    Order.update_status(bid, pid, sid, time_purchased, True)


def find_addresses(orders):
    addresses = []
    for order in orders:
        addresses.append(User.get_address(order.uid))
    
    return addresses


def build_displayed_purchases(id, flag):
    orders = Purchase.get_all_by_sid(id)
    if flag == "uid":
        orders = Purchase.get_all_by_uid(id)
    names = [User.get_name(x.uid) for x in orders]
    addresses = find_addresses(orders)
    ret = []
    for i in range(len(orders)):
        displayed_purchase = DisplayedPurchase(orders[i], names[i], addresses[i])
        ret.append(displayed_purchase)
    
    return ret