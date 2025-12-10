create database if not exists olist;

use olist;

CREATE TABLE if not exists customers (
    customer_id VARCHAR(50),
    customer_unique_id VARCHAR(50),
    customer_zip_code_prefix INT,
    customer_city VARCHAR(100),
    customer_state VARCHAR(5),
    state_name VARCHAR(50),
    region VARCHAR(50)
);

CREATE TABLE if not exists geolocation (
    geolocation_zip_code_prefix INT,
    latitude DECIMAL(10,6),
    longtitude DECIMAL(10,6)
);

CREATE TABLE if not exists orders (
    order_id VARCHAR(50),
    customer_id VARCHAR(50),
    order_status VARCHAR(50),
    order_purchase_timestamp DATETIME,
    order_approved_at DATETIME,
    order_delivered_carrier_date DATETIME,
    order_delivered_customer_date DATETIME,
    order_estimated_delivery_date DATETIME,
    invalid_approve TINYINT,
    invalid_carrier TINYINT,
    invalid_customer_delivery TINYINT
);

CREATE TABLE if not exists order_items (
    order_id VARCHAR(50),
    order_item_id INT,
    product_id VARCHAR(50),
    seller_id VARCHAR(50),
    shipping_limit_date DATETIME,
    price DECIMAL(10,2),
    freight_value DECIMAL(10,2)
);

CREATE TABLE if not exists payments (
    order_id VARCHAR(50),
    payment_type VARCHAR(50),
    payment_installments INT,
    payment_value DECIMAL(10,2)
);

CREATE TABLE if not exists products (
    product_id VARCHAR(50),
    product_weight_g DECIMAL(10,2),
    product_length_cm DECIMAL(10,2),
    product_height_cm DECIMAL(10,2),
    product_width_cm DECIMAL(10,2),
    product_category_name VARCHAR(100)
);

CREATE TABLE if not exists reviews (
    review_id VARCHAR(50),
    order_id VARCHAR(50),
    review_score INT,
    review_comment_message TEXT
);

CREATE TABLE if not exists sellers (
    seller_id VARCHAR(50),
    seller_zip_code_prefix INT,
    seller_city VARCHAR(100),
    seller_state VARCHAR(5),
    state_name VARCHAR(50),
    region VARCHAR(50)
);

-- Xóa dữ liệu cũ trong tất cả bảng
-- DROP TABLE IF EXISTS order_payments;
-- DROP TABLE IF EXISTS order_items;
-- DROP TABLE IF EXISTS reviews;
-- DROP TABLE IF EXISTS orders;
-- DROP TABLE IF EXISTS customers;
-- DROP TABLE IF EXISTS geolocation;
-- DROP TABLE IF EXISTS products;
-- DROP TABLE IF EXISTS sellers;






select * from customers;
select * from geolocation;
select count(*) from orders;
select * from order_items;
select * from payments;
select * from products;
select * from reviews;
select * from sellers;






