from flask import current_app as app
from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField, StringField, SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

class VoteForm(FlaskForm):
    rid = IntegerField('')
    upvote = SubmitField('\u2191')
    downvote = SubmitField('\u2193')

class Vote:
    
    def __init__(self, id, uid, rid, vote):
        self.id = id
        self.uid = uid
        self.rid = rid
        self.vote = vote

    @staticmethod
    def get(id):
        rows = app.db.execute('''
SELECT *
FROM Votes
WHERE id = :id
''',
                              id=id)
        return Vote(*(rows[0])) if rows else None  

    @staticmethod
    def get_all_by_rid(rid):
        rows = app.db.execute('''
SELECT *
FROM Votes
WHERE rid = :rid
''',
                              rid=rid)
        return [Vote(*row) for row in rows]


    @staticmethod
    def get_by_uid_rid(uid, rid):
        rows = app.db.execute("""
            SELECT vote
            FROM Votes
            WHERE uid = :uid
            AND rid = :rid
            """,
            uid=uid, rid=rid)
        if len(rows) > 0:
            return rows[0][0]
        return None

    @staticmethod
    def submit_new_vote(uid, rid, field): # ask if when modify table does csv need to be modify as well
        if field == "Upvote":
            rows = app.db.execute("""
                INSERT INTO Votes(id, uid, rid, vote)
                VALUES(:id, :uid, :rid, :vote)
                RETURNING id
                """,
                id= app.db.execute("""
                SELECT MAX(id)
                FROM Votes
                """)[0][0] + 1,
                uid=uid,
                rid=rid,
                vote=1
                )
        else:
            rows = app.db.execute("""
                INSERT INTO Votes(id, uid, rid, vote)
                VALUES(:id, :uid, :rid, :vote)
                RETURNING id
                """,
                id= app.db.execute("""
                SELECT MAX(id)
                FROM Votes
                """)[0][0] + 1,
                uid=uid,
                rid=rid,
                vote=-1
                )
            id = rows[0][0]
            return Vote.get(id)
    
    @staticmethod
    def modify(uid, rid, option):
        if option == "Upvote":
            rows = app.db.execute("""
                UPDATE Votes
                SET vote = 1
                WHERE uid = :uid 
                AND rid = :rid
            """, uid = uid, rid = rid)
        elif option == "Downvote":
            rows = app.db.execute("""
                UPDATE Votes
                SET vote = -1
                WHERE uid = :uid 
                AND rid = :rid
            """, uid = uid, rid = rid)
        elif option == "Remove":
            rows = app.db.execute("""
            DELETE FROM Votes
            WHERE uid = :uid 
                AND rid = :rid
            """, uid = uid, rid = rid)
            return None
        rows = app.db.execute("""
                SELECT *
                FROM Votes
                WHERE uid = :uid 
                AND rid = :rid
            """, uid = uid, rid = rid)
        return Vote(*(rows[0])) if rows is not None else None