--SQLite table schema

USE WMGInvent;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username STRING,
    password STRING,
    admin INT;
);

CREATE TABLE IF NOT EXISTS cars (
    id INT AUTO_INCREMENT PRIMARY KEY,
    make STRING,
    model STRING,
    year INT,
    registration STRING,
    status STRING,
    path_to_image STRING,
);

CREATE TABLE IF NOT EXISTS changes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    car_id INT,
    change STRING, 
    date_start STRING,
    date_end STRING,
    user_id INT,
);
