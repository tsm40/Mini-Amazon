\COPY Users FROM 'Users.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.users_id_seq',
                         (SELECT MAX(id)+1 FROM Users),
                         false);

\COPY Products FROM 'Products.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.products_id_seq',
                         (SELECT MAX(id)+1 FROM Products),
                         false);

\COPY Purchases FROM 'Purchases.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.purchases_id_seq',
                         (SELECT MAX(id)+1 FROM Purchases),
                         false);

\COPY Inventory FROM 'Inventory.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.inventory_id_seq',
                         (SELECT MAX(id)+1 FROM Inventory),
                         false);

\COPY Cart FROM 'Cart.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.cart_id_seq',
                         (SELECT MAX(id)+1 FROM Cart),
                         false);        
                         
\COPY Coupons FROM 'Coupons.csv' WITH DELIMITER ',' NULL '' CSV 
SELECT pg_catalog.setval('public.coupons_id_seq',
                         (SELECT MAX(id)+1 FROM Coupons),
                         false);

\COPY Orders FROM 'Orders.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.orders_id_seq',
                         (SELECT MAX(id)+1 FROM Orders),
                         false);   
                         
\COPY Reviews FROM 'Reviews.csv' WITH DELIMITER ',' NULL '' CSV 
SELECT pg_catalog.setval('public.reviews_id_seq',
                         (SELECT MAX(id)+1 FROM Reviews),
                         false);

\COPY Votes FROM 'Votes.csv' WITH DELIMITER ',' NULL '' CSV 
SELECT pg_catalog.setval('public.votes_id_seq',
                         (SELECT MAX(id)+1 FROM Votes),
                         false);                

\COPY Refunds FROM 'Refunds.csv' WITH DELIMITER ',' NULL '' CSV 
SELECT pg_catalog.setval('public.refunds_id_seq',
                         (SELECT MAX(id)+1 FROM Refunds),
                         false);       