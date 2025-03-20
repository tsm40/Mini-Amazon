from flask import render_template, redirect, flash, url_for, request
from flask_login import current_user
from decimal import *

from .models.order import Order
from .models.purchase import Purchase
from .models.product import Product
from .models.user import User
from .models.coupon import Coupon
from .models.refund import Refund, RefundRequestForm

from flask import Blueprint
bp = Blueprint('orderpage', __name__)


class ItemSummary():
    def __init__(self, id, oid, pid, sid, quantity, time_fulfilled, status, cid):
        prod = Product.get(pid)
        self.id = id
        self.oid = oid
        self.pid = pid
        self.name = prod.name
        self.sid = sid
        self.seller = User.get_name(sid)
        self.unit_price = prod.price
        self.quantity = quantity
        self.total_price = self.unit_price * quantity * ((100 - Decimal(Coupon.get_discount(cid))) / Decimal(100))
        self.time_fulfilled = time_fulfilled
        self.status = status
        self.cid = cid


@bp.route('/orderpage', methods=['GET', 'POST'])
def load_page():
    oid = request.args.get('oid')
    item_summaries = []
    for item in Order.get_all_by_oid(oid):
        item_summary = ItemSummary(item.id, oid, item.pid, item.sid, 
            item.quantity, item.time_fulfilled, 
                Purchase.get_status(item.uid, item.pid, item.sid, item.time_created), item.cid)
        if item_summary.status:
            item_summary.time_fulfilled = Purchase.get_time_fulfilled(item.uid, 
                item.pid, item.sid, item.time_created)
        item_summaries.append(item_summary)

    refund_request_form = RefundRequestForm()

    if refund_request_form.validate():
        if not Refund.check_by_oid(refund_request_form.oid.data):
            Refund.new_refund_request(refund_request_form.oid.data, current_user.id,
            refund_request_form.sid.data, refund_request_form.reason.data, 
            refund_request_form.value.data)
        else:
            flash('You already submitted a refund request. Please wait to hear back from the seller.')

        print(refund_request_form.reason.data)
        return redirect(url_for('orderpage.load_page')  + '?oid=' + str(oid))

    refund_requests = Refund.get_by_uid(current_user.id)
        

    return render_template('orderpage.html', 
    item_summaries=item_summaries,
    refund_request_form=refund_request_form,
    refund_requests=refund_requests)