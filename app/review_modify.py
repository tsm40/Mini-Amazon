from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

from .models.product import Product
from .models.review import Review, ReviewChangeForm
from .models.user import User

from flask import Blueprint
bp = Blueprint('review_modify', __name__)

class ReviewInfo:
    def __init__(self, review):
        self.review = review
        self.reviewed_name = User.get_name(self.review.rid) if self.review.is_seller else Product.get_name(self.review.rid)[0]

@bp.route('/review_modify', methods=['GET', 'POST'])
def load_page(): 
    review = ReviewInfo(Review.get(request.args.get("id")))
    user = User.get(current_user.id)
    previous_url = request.args.get("purl")
    previous_page_type = previous_url[0]
    previous_id = previous_url[1:]
    if int(current_user.id) != review.review.uid:
        return render_template("not_review.html")
    else:
        review_form = ReviewChangeForm()
        if review_form.validate_on_submit():
            if (review_form.field.data == "Remove" and review_form.value.data != "Remove") or (review_form.field.data == "Rating" and review_form.value.data not in ["0","1","2","3","4","5"]):
                flash("Incorrect Input Detected")
            else:
                Review.modify(review.review.id, review_form.field.data, review_form.value.data)
                if review_form.field.data == "Remove":
                    if previous_page_type == "p":
                        return redirect(url_for('productpage.load_product') + '?pid=' + previous_id)
                    elif previous_page_type == "u":
                        return redirect(url_for('users.userpage') + '?uid=' + previous_id)
                else:
                    return redirect(url_for('review_modify.load_page')  + '?id=' + str(review.review.id) + '&purl=' + previous_url) 
        return render_template('review_modify.html',
            user=user,
            review = review,
            review_form=review_form,
            previous_page_type = previous_page_type,
            previous_id = previous_id)