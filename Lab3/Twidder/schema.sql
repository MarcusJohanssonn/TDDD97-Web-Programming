CREATE TABLE IF NOT EXISTS user(email varchar(30), password varchar(30),
firstname varchar(30), familyname varchar(30),
gender varchar(30), city varchar(30), country varchar(30), PRIMARY KEY(email) );

CREATE TABLE IF NOT EXISTS active_users(email varchar(30), token varchar(30));

CREATE TABLE IF NOT EXISTS messages(id integer primary key autoincrement, message varchar(30), sender varchar(30), reciever varchar(30));
