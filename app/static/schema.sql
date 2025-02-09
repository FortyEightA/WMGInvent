DROP TABLE IF EXISTS users;
Create TABLE users(
    id serial primary key,
    username varchar(50) unique not null,
    password varchar(50) not null
);
