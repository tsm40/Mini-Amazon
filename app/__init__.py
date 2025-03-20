from flask import Flask
from flask_login import LoginManager
from .config import Config
from .db import DB


login = LoginManager()
login.login_view = 'users.login'


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.db = DB(app)
    login.init_app(app)


    from .add_to_inventory import bp as add_to_inventory_bp
    app.register_blueprint(add_to_inventory_bp)
    
    from .cartspage import bp as cartspage_bp
    app.register_blueprint(cartspage_bp)

    from .checkoutpage import bp as checkoutpage_bp
    app.register_blueprint(checkoutpage_bp)

    from .index import bp as index_bp
    app.register_blueprint(index_bp)

    from .orderpage import bp as orderpage_bp
    app.register_blueprint(orderpage_bp)

    from .orderspage import bp as orderspage_bp
    app.register_blueprint(orderspage_bp)

    from .product_listing import bp as product_listing_bp
    app.register_blueprint(product_listing_bp)

    from .productpage import bp as productpage_bp
    app.register_blueprint(productpage_bp)

    from .review_modify import bp as review_modify_bp
    app.register_blueprint(review_modify_bp)
    
    from .sellerpage import bp as sellerpage_bp
    app.register_blueprint(sellerpage_bp)

    from .sellerpage_add_product import bp as sellerpage_add_product_bp
    app.register_blueprint(sellerpage_add_product_bp)

    from .sellerpage_inventory import bp as sellerpage_inventory_bp
    app.register_blueprint(sellerpage_inventory_bp)

    from .sellerpage_orders import bp as sellerpage_orders_bp
    app.register_blueprint(sellerpage_orders_bp)

    from .userpage_modify import bp as userpage_modify_bp
    app.register_blueprint(userpage_modify_bp)

    from .users import bp as user_bp
    app.register_blueprint(user_bp)
        
    return app
