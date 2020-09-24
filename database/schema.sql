-- Create database
CREATE DATABASE auth;
\c auth;

-- Create table of users
CREATE TABLE users (
   id  BIGSERIAL PRIMARY KEY NOT NULL,
   email    VARCHAR(200) UNIQUE NOT NULL,
   password VARCHAR(20) NOT NULL CHECK(char_length(password) > 5)
);
