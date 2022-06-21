-- all users in system
CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  username VARCHAR(50) UNIQUE NOT NULL,
	password VARCHAR(102) NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  fullname VARCHAR(70) NOT NULL,
  is_officer BOOLEAN NOT NULL,
  profile_picture VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS packages (
  id SERIAL PRIMARY KEY,
  resident_id INT NOT NULL,
  delivered TIMESTAMP NOT NULL DEFAULT NOW(),
  collected TIMESTAMP,
  title VARCHAR(50) NOT NULL,
  CONSTRAINT fk_resident FOREIGN KEY(resident_id) REFERENCES users(id)
);
