from werkzeug.security import generate_password_hash
import csv
from faker import Faker
import copy
import datetime
import csv


num_users = 10
num_products = 250 # Highest number that still works with amazon data is 10000
num_purchases = 8
num_reviews = 8
num_coupons = 4

Faker.seed(0)
fake = Faker()

sellers = {} # dictionary that stores what products each seller sells and how many of each prod
product_dir = {} # dictionary that stores what sellers sell a prod
bought_prod = {} # user : prods bought
bought_from = {} # user : sellers bought from
non_sellers = [] # list of uids which are non sellers
plaintext_pwds = [] # list of plaintext passwords indexed by user (for testing)
products = {}
carts = {} # user: cart items
votes = {} # dictionary of uids: list of tuples (review_id, vote (+1 or -1))

num_votes = 0

def get_csv_writer(f):
    return csv.writer(f, dialect='unix')


def gen_users(num_users): 
    with open('./db/data/Users.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Users...', end=' ', flush=True)

        for uid in range(num_users):
            if uid % 10 == 0:
                print(f'{uid}', end=' ', flush=True)

            profile = fake.profile()
            email = profile['mail']
            plain_password = f'pass{uid}'
            password = generate_password_hash(plain_password)
            name_components = profile['name'].split(' ')
            firstname = name_components[0]
            lastname = name_components[-1]
            fullname = firstname + ' ' + lastname
            address = fake.address()
            balance = f'{str(fake.random_int(max=10000))}.{fake.random_int(max=99):02}'
            isSeller = ''
            if uid == 0:
                isSeller = 'true'
            else:
                isSeller = fake.random_element(elements=('true', 'false'))
            if isSeller is 'true':
                 sellers[uid] = []
            else:
                non_sellers.append(uid)

                bought_from[uid] = []
                bought_prod[uid] = []

            writer.writerow([uid, email, address, password, firstname, lastname, balance, isSeller])
            plaintext_pwds.append(plain_password)

        print(f'{num_users} generated')
    return

class amazonProductInfo:
    def __init__(self, name, price, category, image, description):
        self.name = name
        self.price = price
        self.category = category
        self.image = image
        self.description = description

def create_products(sellers, product_dir, num_products):
    print(len('Make sure this fits by entering your model number.'))
    with open("./amazon_data.csv", 'r') as file:
        csvreader = csv.reader(file)
        amazon_prods = [amazonProductInfo(row[1], row[7], row[4], row[15], row[10]) for row in csvreader]
        amazon_prods.pop(0)
        generated_names = set()

        for pid in range(num_products):
            amazon_product = amazon_prods[pid]


            name = str(amazon_product.name)
            if name in generated_names:
                instance = 1
                while f'{name} ({instance})' in generated_names:
                    instance += 1
                name = f'{name} ({instance})'
            generated_names.add(name)
            


            price = str(amazon_product.price)
            price = price.replace(',','')
            if len(price) != price.find("."):
                price = price[1:price.find(".") + 3]
            checker = price.replace('.','',1).isdigit()
            price = price if checker else "15.15"

            available = True
            category = fake.random_element(elements=('cat1', 'cat2', 'cat3', 'cat4', 'cat5', 'cat6', 'cat7'))
            category = amazon_product.category


            image = str(amazon_product.image)
            image = image.split("|")[0]

            if image.find('https://images-na.ssl-images-amazon.com/images/') == -1:
                image_num = fake.random_int(min=0, max=num_products)
                image = 'https://picsum.photos/200/200?' + str(image_num)


            rating = f'{str(fake.random_int(max=5, min=0))}.{str(fake.random_int(max=9, min=0))}' # TODO: needs to match rating of prod
            while float(rating.strip(' "')) > 5.0:
                rating = f'{str(fake.random_int(max=5, min=0))}.{str(fake.random_int(max=9, min=0))}'
            desc = amazon_product.description[52:]
            creator = fake.random_element(elements=list(sellers.keys()))

            # update the map
            if creator not in sellers.keys():
                sellers[creator] = []
            sellers[creator].append([pid, fake.random_int(max=1000, min=0)]) # creator = seller and sells this prod 
            if pid not in product_dir.keys():
                product_dir[pid] = []
            product_dir[pid].append(creator)

            # update local version of Product db for later use
            products[pid] = {'name': name, 'price': price, 'available': available, 'category': category,
                'image': image, 'rating': rating, 'desc': desc, 'creator': creator}
    print(len(generated_names))
    return
    #         amazon_product = amazon_prods[amazon_product_index]
    #         name = amazon_product.name
    #         price = amazon_product.price
    #         available = True
    #         category = amazon_product.category
    #         image = amazon_product.image
    #         rating = f'{str(fake.random_int(max=5, min=0))}.{str(fake.random_int(max=9, min=0))}'
    #         while float(rating.strip(' "')) > 5.0:
    #             rating = f'{str(fake.random_int(max=5, min=0))}.{str(fake.random_int(max=9, min=0))}'
    #         desc = amazon_product.description
    #         creator = fake.random_element(elements=list(sellers.keys()))

    #         # update the map
    #         if creator not in sellers.keys():
    #             sellers[creator] = []
    #         sellers[creator].append([pid, fake.random_int(max=1000, min=0)])# creator = seller and sells this prod 
    #         if pid not in product_dir.keys():
    #             product_dir[pid] = []
    #         product_dir[pid].append(creator)

    #         # update local version of Product db for later use
    #         products[pid] = {'name': name, 'price': price, 'available': available, 'category': category,
    #             'image': image, 'rating': rating, 'desc': desc, 'creator': creator}
    #     file.close()

    # return
        
        # generate data
        # name = fake.sentence(nb_words=4)[:-1]
        # price = f'{str(fake.random_int(max=50000))}.{fake.random_int(max=99):02}'
        # available = True
        # category = fake.random_element(elements=('cat1', 'cat2', 'cat3', 'cat4', 'cat5', 'cat6', 'cat7'))
        # image_num = fake.random_int(min=0, max=num_products)
        # image = 'https://picsum.photos/200/200?' + str(image_num)
        # rating = f'{str(fake.random_int(max=5, min=0))}.{str(fake.random_int(max=9, min=0))}' # TODO: needs to match rating of prod
        # while float(rating.strip(' "')) > 5.0:
        #     rating = f'{str(fake.random_int(max=5, min=0))}.{str(fake.random_int(max=9, min=0))}'
        # desc = fake.sentence(nb_words=10)[:-1]
        # creator = fake.random_element(elements=list(sellers.keys()))

        # # update the map
        # if creator not in sellers.keys():
        #     sellers[creator] = []
        # sellers[creator].append([pid, fake.random_int(max=1000, min=0)])# creator = seller and sells this prod 
        # if pid not in product_dir.keys():
        #     product_dir[pid] = []
        # product_dir[pid].append(creator)

        # # update local version of Product db for later use
        # products[pid] = {'name': name, 'price': price, 'available': available, 'category': category,
        #     'image': image, 'rating': rating, 'desc': desc, 'creator': creator}

def gen_products(num_products, products):
    with open('./db/data/Products.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Products...', end=' ', flush=True)

        for pid in products:
            product = products[pid]
            writer.writerow([pid, product['name'], product['price'], product['available'], product['category'], 
                product['desc'], product['image'], product['creator'], product['rating']])
    
        print(f'{num_products} generated')
    return 


def gen_inventory(sellers, num_products):
    unseen_prods = num_products
    seller_names = list(sellers.keys())
    counter = 0

    with open('./db/data/Inventory.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Inventory...', end=' ', flush=True)

        for seller in sellers:
            for prod in sellers[seller]:
                writer.writerow([counter, seller, prod[0], prod[1]])

                counter += 1
                unseen_prods -= 1
        
        print('inventory generated')
    return


def gen_purchases(num_purchases, sellers, product_dir): 
    with open('./db/data/Purchases.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Purchases...', end=' ', flush=True)

        local_sellers = copy.deepcopy(sellers)
        i = 1
        print("BEFORE LOOP")
        while i < num_purchases:
            if i % 100 == 0:
                print(f'{id}', end=' ', flush=True)

            uid = fake.random_element(elements=non_sellers)
            pid = fake.random_int(min=0, max=num_products-1)
            sid_quantity = find_valid_seller(local_sellers, product_dir, pid, uid)
            sid = sid_quantity[0]
            quantity = sid_quantity[1]
            time_purchased = fake.date_time()
            time_fulfilled = fake.date_time()

            if sid == -1 or quantity == -1:
                continue

            writer.writerow([i, uid, pid, sid, time_purchased, quantity, False, time_fulfilled])

            bought_from[uid].append([sid, pid])
            bought_prod[uid].append([pid, quantity])

            i += 1

        print(f'{num_purchases} generated')
    return


def create_carts(num_users, bought_from, bought_prod, carts):
    id = 0
    for user in non_sellers:
            if user % 10 == 0:
                print(f'{user}', end=' ', flush=True) 

            carts[user] = []

            for seller_tuple in bought_from[user]:
                pid = seller_tuple[1]
                sid = seller_tuple[0]
                quantity = 0
                for prod_tuple in bought_prod[user]:
                    if prod_tuple[0] == pid:
                        quantity = prod_tuple[1]
                        break
        
                carts[user].append([id, user, pid, sid, quantity])
                id += 1
    return 


def gen_carts(carts):
    with open('./db/data/Cart.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Cart...', end= ' ', flush=True)

        for user in carts:
            cart = carts[user]
            for item in cart:        
                writer.writerow([item[0], item[1], item[2], item[3], item[4]])
                 
        print(f'{len(non_sellers)} generated')
    return

def gen_orders(carts):
    with open('./db/data/Orders.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Orders...', end= ' ', flush=True)

        id = 0
        oid = 0
        for user in carts:
            for item in carts[user]:
                writer.writerow([id, oid, user, item[2], item[3], fake.date_time(), item[4], fake.date_time(), False, fake.random_int(max = num_coupons - 1)])
                id += 1 
            oid += 1

        print(f'{id} generated')
    return


def gen_reviews(num_reviews, bought_prod, bought_from):
    with open('./db/data/Reviews.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Reviews...', end=' ', flush=True)

        prod_reviews = create_reviews(bought_prod, 0)
        seller_reviews = create_reviews(bought_from, 1)

        id = 0
        while id < num_reviews - 1:
            prod_or_seller = fake.random_int(0, 1)
            review = ''
            if prod_or_seller == 0:
                # prod
                review = fake.random_element(elements=prod_reviews)
                prod_reviews.remove(review)
            else:
                review = fake.random_element(elements=seller_reviews)
                seller_reviews.remove(review)
            for i in range(fake.random_int(min=0, max=num_users - 1)): # generating random amount of votes for this review
                voter = fake.random_int(min=0, max=num_users - 1)  # uid of voter
                vote = fake.random_int(-1, 1) # either upvote or downvote
                if vote == 0:
                    vote = 1
                if voter not in votes:
                    votes[voter] = [(id, vote)]
                elif (id, vote) not in votes[voter] and (id, -vote) not in votes[voter]:
                    votes[voter].append((id, vote))
            writer.writerow([id, review[0], review[1], review[2], review[3], review[4], review[5]])            
            id += 1

        print(f'{num_reviews} generated')
    return


def gen_coupons(num_coupons):
    with open('./db/data/Coupons.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Coupons...', end=' ', flush=True)
        writer.writerow([0, 0, ""])
        for i in range(1,num_coupons):
            discount = fake.random_element(elements=(5, 10, 15, 20, 30, 45, 50, 75, 80))

            writer.writerow([i, discount, ""])
        
        print(f'{num_coupons} generated')
    return


def create_reviews(dictionary, flag):
    reviews = []

    for user in dictionary:
        for dict_tuple in dictionary[user]:
            rating = fake.random_int(min=0, max=5)
            time = fake.date_time()
            uid = user
            rid = dict_tuple[0]
            is_seller = True
            content = ''
            if flag == 0: 
                # prod review
                content = fake.sentence(nb_words=4, 
                ext_word_list=['great', 'terrible', 'this is unusable', 
                    'I can\'t believe I bought this', 'OMG best day ever'])
                is_seller = False
            else:
                # seller review
                content = fake.sentence(nb_words=4, 
                ext_word_list=['great', 'terrible', 'awesome group', 
                    'I can\'t believe I bought from them', 'OMG best day ever'])
            
            reviews.append([rating, content, time, uid, rid, is_seller])
    
    return reviews

def gen_votes(votes):
    num_votes = 0
    with open('./db/data/Votes.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Votes...', end=' ', flush=True)

        for uid in votes:
            tups = votes[uid]
            for i in range(len(tups)):
                rid, vote = tups[i]
                writer.writerow([num_votes, uid, rid, vote]) 
                num_votes += 1
        print(f'{num_votes} generated')


def calculate_product_rating(products, reviews):
    ratings = {}
    for review in reviews:
        pid = review[4]
        rating = review[0]

        if pid not in ratings:
            ratings[pid] = {}
        
        ratings[pid].append(rating)
    
    for prod in ratings:
        products[prod][rating] = sum(ratings[prod]) / len(ratings[prod])


def find_valid_seller(local_sellers, product_dir, pid, uid):
    possible_seller = 0
    for seller in product_dir[pid]:
        if seller != uid:
            possible_seller = seller
            break
    else:
        return [-1, -1]
    seller_inventory = local_sellers[possible_seller]

    for prod_tuple in seller_inventory:
        stock = prod_tuple[1]
        if int(prod_tuple[0]) == int(pid) and stock > 0:
            quantity = fake.random_int(min=1, max=stock)

            local_sellers[possible_seller][local_sellers[possible_seller].index(prod_tuple)][1] -= quantity

            return [possible_seller, quantity]
        else:
            return [-1, -1]
        
def print_products(product_dir):
    for prod in product_dir:
        print(prod, ' sellers: ', product_dir[prod])


def print_sellers(sellers):
    for seller in sellers:
        print('THIS IS SELLER ' + str(seller))
        print(type(sellers[seller]))
        print('THIS IS SELLER VAL ' + str(sellers[seller]))
        print('THIS IS SELLER SELLER VAL ' + str(sellers[seller].values()))


def print_purchase_trail(trail, flag):
    for user in trail:
        items = trail[user]
        for item in items:
            if flag == 1:
                print('USER ' + str(user) + ' BOUGHT FROM ' + str(item))
            else:
                print('USER ' + str(user) + ' BOUGHT ITEM ' + str(item))

def print_plaintext_pwds():
    with open('./db/data/Passwords.csv', 'w') as f:
        writer = get_csv_writer(f)
        for pwd in plaintext_pwds:
            writer.writerow([pwd])



gen_users(num_users)
create_products(sellers, product_dir, num_products)
gen_inventory(sellers, num_products)
gen_purchases(num_purchases, sellers, product_dir)
create_carts(num_users, bought_from, bought_prod, carts)
gen_carts(carts)
gen_orders(carts)
gen_reviews(num_reviews, bought_prod, bought_from)
gen_products(num_products, products)
gen_votes(votes)
gen_coupons(num_coupons)
print_plaintext_pwds()
