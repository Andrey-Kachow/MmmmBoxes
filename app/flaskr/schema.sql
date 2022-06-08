DROP TABLE IF EXISTS resident CASCADE;
DROP TABLE IF EXISTS officer CASCADE;
DROP TABLE IF EXISTS parcel CASCADE;

CREATE TABLE resident (
  id SERIAL PRIMARY KEY,
  username VARCHAR(50) UNIQUE NOT NULL,
	password VARCHAR(50) NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  fullname VARCHAR(70) NOT NULL
);

CREATE TABLE officer (
  id SERIAL PRIMARY KEY,
  username VARCHAR(50) UNIQUE NOT NULL,
	password VARCHAR(50) NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  fullname VARCHAR(70) NOT NULL
);

CREATE TABLE parcel (
  id SERIAL PRIMARY KEY,
  delivered TIMESTAMP,
  collected TIMESTAMP,
  title VARCHAR(50) NOT NULL,
  resident_id INTEGER REFERENCES resident (id)
);
