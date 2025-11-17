-- ,Customer_ID,Gender,Age,Occupation,City_Category,Stay_In_Current_City_Years,Marital_Status
-- ,Product_ID,Product_Category,price$,storeID,supplierID,storeName,supplierName
-- ,orderID,Customer_ID,Product_ID,quantity,date

drop database if exists db;
create database db;
use db;

create table Customer(
    surrogate_id int primary key auto_increment,
    id int,
    -- male, female, other, undefined
    gender enum ('M','F','O','U' ),
    age varchar(30),
    occupation int, -- ? idk why it has numbers
    city_category enum ('A','B','C' ),
    stay_in_current_city_years int,
    marital_status boolean,
    valid_from timestamp,
    valid_to TIMESTAMP,
    is_current boolean,
    hash_value varchar(200)
);

create table Product(
    surrogate_id int primary key auto_increment,
    id varchar(50),
    product_category varchar(100),
    price decimal(10,2),
    supplier_id int,
    store_id int,
    valid_from timestamp,
    valid_to TIMESTAMP,
    is_current boolean,
    hash_value varchar(200)
);

create table Supplier(
    surrogate_id int primary key auto_increment,
    id int,
    supp_name varchar(255),
    valid_from timestamp,
    valid_to TIMESTAMP,
    is_current boolean,
    hash_value varchar(200)
);

create table Store(
    surrogate_id int primary key auto_increment,
    id int,
    store_name varchar(255),
    valid_from timestamp,
    valid_to TIMESTAMP,
    is_current boolean,
    hash_value varchar(200)
);


create table Transaction_fact(
    id int primary key,
    customer_id int, 
    product_id VARCHAR(50),
    store_id int,
    supplier_id int,
    date date,

    quantity int,

    gender enum ('M','F','O','U' ),
    age varchar(30),
    occupation int,
    city_category enum ('A','B','C' ),
    stay_in_current_city_years int,
    marital_status boolean,

    product_category varchar(100),
    price decimal(10,2),

    day int,
    month int,
    quarter int,
    year int,
    is_weekend boolean,
    supp_name varchar(255),
    store_name varchar(255),

    -- foreign key (date) references Time_(date),
    foreign key (customer_id) references Customer(surrogate_id),
    foreign key (product_id) references Product(surrogate_id),
    foreign key (store_id) references Store(surrogate_id),
    foreign key (supplier_id) references Supplier(surrogate_id)
);