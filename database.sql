DROP TABLE IF EXISTS urls;
DROP TABLE IF EXISTS url_checks;

CREATE TABLE urls (
  id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  name VARCHAR(255) UNIQUE NOT NULL,
  created_at DATE NOT NULL
);

CREATE TABLE url_checks (
  id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  url_id bigint REFERENCES urls (id),
  status_code VARCHAR(255) NOT NULL,
  h1 VARCHAR(255),
  title VARCHAR(255),
  description TEXT,
  created_at DATE NOT NULL
);
