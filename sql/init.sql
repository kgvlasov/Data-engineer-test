CREATE SCHEMA data;

CREATE TABLE data.data (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  value TEXT NOT NULL
);

INSERT INTO data.data (name, value) VALUES ('foo', 'bar');
INSERT INTO data.data (name, value) VALUES ('baz', 'qux');
