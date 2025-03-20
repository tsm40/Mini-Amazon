from flask import current_app as app

from decimal import *
from .review import Review

class Product:
    def __init__(self, id, name, price, available, category, long_description, image_link, creator, rating):
        self.id = str(id)
        self.name = name
        self.price = price
        self.available = available
        self.category = category
        self.long_description = long_description
        self.image_link = image_link
        self.creator = creator
        self.reviews = Review.get_all_by_pid(id)
        self.rating = sum([x.rating for x in self.reviews]) / len(self.reviews) if self.reviews else "No Reviews"


    @staticmethod
    def get_pid(pid):
        rows = app.db.execute('''
        SELECT name
        FROM Products
        WHERE id = :pid''', id=pid)

        return str(rows[0])


    @staticmethod
    def get(id):
        rows = app.db.execute('''
        SELECT *
        FROM Products
        WHERE id = :id
        ''', id=id)

        return Product(*(rows[0])) if rows is not None else None

    @staticmethod
    def get_name(id):
        rows = app.db.execute("""
            SELECT name
            FROM Products
            WHERE id = :id
            """,
            id=id)
        return rows[0]

    @staticmethod
    def get_num_products():
        rows = app.db.execute('''
        SELECT id, name, price, available, category, long_description, image_link, creator, rating
        FROM Products
        ''')

        return len(rows)


    @staticmethod
    def get_all(available=True):
        rows = app.db.execute('''
        SELECT id, name, price, available, category, long_description, image_link, creator, rating
        FROM Products
        WHERE available = :available
        ''', available=available)

        return [Product(*row) for row in rows]

    @staticmethod
    def get_topselling():
        product_info = app.db.execute('''
        WITH numsold_tab as (
            SELECT products.id, name, price, available, category, long_description, image_link, creator, rating, SUM(quantity) as sum_quantity
            FROM purchases, products
            WHERE purchases.pid = products.id
            GROUP BY purchases.pid, products.id, products.name
        )
        SELECT id, name, price, available, category, long_description, image_link, creator, rating, sum_quantity
        FROM numsold_tab
        WHERE sum_quantity = (SELECT MAX(sum_quantity)
                           FROM numsold_tab)
        ''')[0]
        product = Product(product_info[0],product_info[1],product_info[2],product_info[3],product_info[4],product_info[5],product_info[6],product_info[7],product_info[8])
        num_sold = product_info[9]
        return [product, num_sold]


    @staticmethod
    def get_top_k(k, available=True):
        rows = app.db.execute('''
        SELECT id, name, price, available, category, long_description, image_link, creator, rating
        FROM Products
        WHERE available = :available
        ORDER BY price DESC
        LIMIT :k
        ''', k=k, available=available)
        
        return [Product(*row) for row in rows]


    @staticmethod
    def get_query(query, val, available=True):
        

        if query == "Category":
            rows = app.db.execute('''
                SELECT id, name, price, available, category, long_description, image_link, creator, rating
                FROM Products
                WHERE available = :available and lower(category) LIKE '%' || :val || '%' 
                ''', val=val.lower(), available=available)

        elif query == "Search For":
            rows = app.db.execute('''
                SELECT id, name, price, available, category, long_description, image_link, creator, rating
                FROM Products
                WHERE lower(long_description) LIKE '%' || :val || '%' or lower(name) LIKE '%' || :val || '%'
                ''', val=val.lower(), available=available)
        else:
            rows = app.db.execute(''' 
        SELECT id, name, price, available, category, long_description, image_link, creator, rating
        FROM Products
        ''') 
        return [Product(*row) for row in rows]
    

    @staticmethod
    def add_product(name, price, available, category, long_description, image_link, creator, rating):
        try:
            id = app.db.execute('''
            SELECT MAX(id)
            FROM Products
            ''')[0][0] + 1
            app.db.execute('''
            INSERT INTO Products(id, name, price, available, category, long_description, image_link, creator, rating)
            VALUES (:id, :name, :price, :available, :category, :long_description, :image_link, :creator, :rating)
            RETURNING id''', id=id, name=name, price=price, available=available, category=category, 
                long_description=long_description, image_link=image_link, creator=creator, rating=rating)[0][0]

            return id
        except:
            return False

    
    @staticmethod
    def get_price(pid, sid):
        price = app.db.execute('''
        SELECT price
        FROM Products
        WHERE id = :pid
        AND creator = :sid''', pid=pid, sid=sid)
        return Decimal(price[0][0])


    @staticmethod
    def modify(query, val, id):
        if query == "Name":
            app.db.execute('''
                UPDATE Products
                SET name = :val
                WHERE id = :id''',
                val = val,
                id = id)
        elif query == "Price":
            app.db.execute('''
                UPDATE Products
                SET price = :val
                WHERE id = :id''',
                val = val,
                id = id)
        elif query == "Description":
            app.db.execute('''
                UPDATE Products
                SET long_description = :val
                WHERE id = :id''',
                val = val,
                id = id)
        elif query == "Image":
            app.db.execute('''
                UPDATE Products
                SET image_link = :val
                WHERE id = :id''',
                val = val,
                id = id)
        elif query == "Category":
            app.db.execute('''
                UPDATE Products
                SET category = :val
                WHERE id = :id''',
                val = val,
                id = id)
                
        
        rows = app.db.execute('''
                SELECT *
                FROM Products
                WHERE id = :id''',
                id = id)
        return Product(*(rows[0])) if rows is not None else None


