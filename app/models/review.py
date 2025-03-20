from flask import current_app as app
from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

from .vote import Vote

class ReviewChangeForm(FlaskForm):
    field = SelectField('Filter Type', choices = ["Rating", "Description", "Remove"])
    value = StringField('Filter Value', validators=[DataRequired()])
    submit = SubmitField('Change')

class ReviewAddForm(FlaskForm):
    rating = StringField('Rating Value', validators=[DataRequired()]) 
    content = StringField('Content', validators=[DataRequired()]) 
    submit_review = SubmitField('Submit')

class Review:
    
    acceptable_ratings = ["0","1","2","3","4","5"]

    """
    This is just a TEMPLATE for Review, you should change this by adding or 
        replacing new columns, etc. for your design.
    """
    def __init__(self, id, rating, content, review_time, uid, rid, is_seller):
        self.id = id
        self.rating = rating
        self.content = content
        self.review_time = review_time
        self.uid = uid
        self.rid = rid  
        self.is_seller = is_seller
        self.votes = Vote.get_all_by_rid(id)
        self.total_votes = sum([x.vote for x in self.votes]) if self.votes else 0


    @staticmethod
    def get(id):
        rows = app.db.execute('''
SELECT id, rating, content, review_time, uid, rid, is_seller
FROM Reviews
WHERE id = :id
''',
                              id=id)
        return Review(*(rows[0])) if rows else None

    @staticmethod
    def get_all_by_uid(uid):
        rows = app.db.execute('''
SELECT id, rating, content, review_time, uid, rid, is_seller
FROM Reviews
WHERE uid = :uid
ORDER BY review_time DESC
''',
                              uid=uid)
        return [Review(*row) for row in rows]

    @staticmethod
    def get_all_by_pid(rid):
        rows = app.db.execute('''
SELECT id, rating, content, review_time, uid, rid, is_seller
FROM Reviews
WHERE rid = :rid
AND is_seller = 'False'
ORDER BY review_time DESC
''',
                              rid=rid)
        return [Review(*row) for row in rows]

    @staticmethod
    def get_all_by_sid(rid):
        rows = app.db.execute('''
SELECT id, rating, content, review_time, uid, rid, is_seller
FROM Reviews
WHERE rid = :rid
AND is_seller = 'True'
ORDER BY review_time DESC
''',
                              rid=rid)
        return [Review(*row) for row in rows]

    @staticmethod
    def get_by_uid_rid(uid, rid, isSeller):
        rows = app.db.execute("""
            SELECT *
            FROM Reviews
            WHERE uid = :uid
            AND rid = :rid AND 
            is_seller = :isSeller
            """,
            uid=uid, rid=rid, isSeller = isSeller)
        if len(rows) > 0:
            return [Review(*row) for row in rows][0]
        return None

    @staticmethod
    def submit_new_review(rating, content, review_time, uid, rid, isSeller): 
            rows = app.db.execute("""
                INSERT INTO Reviews(id, rating, content, review_time, uid, rid, is_seller)
                VALUES(:id, :rating, :content, :review_time, :uid, :rid, :is_seller)
                RETURNING id
                """,
                id= app.db.execute("""
                SELECT MAX(id)
                FROM Reviews
                """)[0][0] + 1,
                rating = rating,
                content = content,
                review_time = review_time,
                uid = uid,
                rid = rid,
                is_seller=isSeller
                )
            id = rows[0][0]
            return Review.get(id)
    
    @staticmethod
    def modify(id, field, content):
        if field == "Rating":
            rows = app.db.execute("""
                UPDATE Reviews
                SET rating = :content
                WHERE id = :rid 
            """, rid = id, content = content)
        elif field == "Description":
            rows = app.db.execute("""
                UPDATE Reviews
                SET content = :content
                WHERE id = :rid 
            """, rid = id, content = content)
        elif field == "Remove":
            rows = app.db.execute('''
            DELETE FROM Reviews
            WHERE id = :id
            ''', id = id)
            return None
        rows = app.db.execute('''
                SELECT *
                FROM Reviews
                WHERE id = :id''',
                id = id)
        return Review(*(rows[0])) if rows is not None else None

    @staticmethod
    def get_vote_by_uid_rid(uid, id):
        rows = app.db.execute("""
            SELECT vote
            FROM Votes
            WHERE uid = :uid
            AND rid = :rid
            """,
            uid=uid, rid=id)
        if len(rows) > 0:
            return rows[0][0]
        return None