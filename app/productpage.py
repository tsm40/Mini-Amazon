from flask import render_template, redirect, flash, url_for, request
from flask_login import current_user

from .models.product import Product
from .models.inventory import Inventory
from .models.cart import Cart, AddtoCartForm
from .models.user import User
from .models.purchase import Purchase
from .models.review import Review, ReviewChangeForm, ReviewAddForm
from .models.vote import Vote, VoteForm
from datetime import datetime

from flask import Blueprint
bp = Blueprint('productpage', __name__)

class ReviewInfo:
    def __init__(self, review):
        self.review = review
        self.reviewer_name = User.get_name(self.review.uid)
        self.reviewed_name = User.get_name(self.review.rid) if self.review.is_seller else Product.get_name(self.review.rid)[0]
        
class productReviewInfo:
    def __init__(self, name, content, rating):
        self.reviewer_name = name
        self.content = content
        self.rating = rating

class sellerListingInfo():
    def __init__(self, name, id, quantity, rating):
        self.seller_name = name
        self.id = id
        self.quantity = quantity
        self.rating = rating



@bp.route('/productpage', methods=['GET', 'POST'])
def load_product():
    
    product = Product.get(request.args.get("pid"))
    user_review = Review.get_by_uid_rid(current_user.id, product.id, False) if current_user.is_authenticated else None
    inventory = Inventory.get_entry_by_pid(product.id)
    # self, id, rating, content, review_time, uid, rid, is_seller

    review_form = ReviewChangeForm()
    review_add_form = ReviewAddForm()
    add_to_cart_form = AddtoCartForm()
    vote_form = VoteForm()

    if (vote_form.downvote.data or vote_form.upvote.data) and vote_form.validate():
        user_vote = Vote.get_by_uid_rid(current_user.id, vote_form.rid.data) if current_user.is_authenticated else None
        if vote_form.upvote.data:
            if user_vote == 1:
                Vote.modify(current_user.id, vote_form.rid.data, 'Remove')
            elif user_vote == -1:
                    Vote.modify(current_user.id, vote_form.rid.data, 'Upvote')
            else:
                Vote.submit_new_vote(current_user.id, vote_form.rid.data, 'Upvote')
        elif vote_form.downvote.data:
            if user_vote == -1:
                Vote.modify(current_user.id, vote_form.rid.data, 'Remove')
            elif user_vote == 1:
                    Vote.modify(current_user.id, vote_form.rid.data, 'Downvote')
            else:
                Vote.submit_new_vote(current_user.id, vote_form.rid.data, 'Downvote')
        return redirect(url_for('productpage.load_product')  + '?pid=' + str(product.id))


    if review_add_form.submit_review.data and review_add_form.validate():
        if not user_review:
            Review.submit_new_review(review_add_form.rating.data,review_add_form.content.data, datetime.now(), current_user.id, product.id, False)
        return redirect(url_for('productpage.load_product')  + '?pid=' + str(product.id))

    review = Review.get_all_by_pid(product.id)
    sellerReviews = [ReviewInfo(x) for x in review]
    sellers = [sellerListingInfo(User.get_name(x.uid), x.uid, x.quantity, User.get_rating(x.uid)) for x in inventory]
    vote_status = {}
    if current_user.is_authenticated:
        for rev in review:  # calculate user's vote status for each review
            vote_status[rev.id] = Vote.get_by_uid_rid(current_user.id, rev.id)

        if add_to_cart_form.submit_to_cart.data or add_to_cart_form.validate():
            if current_user.is_authenticated:
                Cart.add_to_cart(current_user.id, product.id, min(add_to_cart_form.quantity.data, Inventory.get_quantity(add_to_cart_form.seller.data, product.id)), add_to_cart_form.seller.data)
            else: 
                return redirect(url_for('users.login'))
        elif add_to_cart_form.submit_to_cart.data:
            print("here")
        elif add_to_cart_form.validate():
            print("now here")
        else:
            print("this one")
    has_bought = None

    if current_user.is_authenticated:
        has_bought = Purchase.uid_purchased_pid(current_user.id, product.id)

    return render_template('productpage.html',
    product = product,
    inventory = sellers,
    review = sellerReviews,
    user_review = user_review,
    review_form = review_form,
    review_add_form = review_add_form,
    vote_form = vote_form,
    vote_status = vote_status,
    add_to_cart_form = add_to_cart_form,
    has_bought = has_bought,
    is_seller = bool(User.get(current_user.id).seller) if current_user.is_authenticated else None,
    can_add=Inventory.is_uid_selling_pid(current_user.id, product.id) if current_user.is_authenticated else None
    )
