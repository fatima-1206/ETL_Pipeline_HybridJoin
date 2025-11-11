-- ,Customer_ID,Gender,Age,Occupation,City_Category,Stay_In_Current_City_Years,Marital_Status
-- ,Product_ID,Product_Category,price$,storeID,supplierID,storeName,supplierName
-- ,orderID,Customer_ID,Product_ID,quantity,date

drop database if exists projdb;
create database projdb;
use projdb;

create table Customer(
    id int primary key,
    -- male, female, other, undefined
    gender enum ('M','F','O','U' ),
    age int,
    occupation int, -- ? idk why it has numbers
    city_category enum ('A','B','C' ),
    stay_in_current_city_years int,
    marital_status boolean
);

-- store and supplier could be seperate dimension tables but as the transaction data does not contain the foregin keys, we will not be able to link them

create table Product(
    id int primary key,
    product_category varchar(100),
    price decimal(10,2),
    store_id int,
    supplier_id int,
    store_name varchar(255),
    supplier_name varchar(255)
);


create table Transaction_fact(
    id int primary key,
    customer_id int, 
    product_id int, 
    quantity int,
    date date,
    foreign key (customer_id) references Customer(id),
    foreign key (product_id) references Product(id)
);