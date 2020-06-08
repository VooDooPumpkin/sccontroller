DROP TABLE IF EXISTS contract;
DROP TABLE IF EXISTS template;
DROP TABLE IF EXISTS user;

CREATE TABLE template (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT UNIQUE NOT NULL,
  description TEXT NOT NULL,
  filename TEXT NOT NULL,
  contract_name TEXT NOT NULL,
  parameters_list json NOT NULL,
  statuses_list json NOT NULL,
  creator_guide json NOT NULL,
  users_guide json NOT NULL
);

CREATE TABLE contract (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  template_id INTEGER NOT NULL,
  parameters json,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  binary_code TEXT NOT NULL,
  abi json NOT NULL,
  address TEXT,
  status_id INTEGER NOT NULL DEFAULT 0,
  FOREIGN KEY (template_id) REFERENCES template (id)
);

CREATE INDEX idx_address ON contract (address);

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT NOT NULL UNIQUE,
  password TEXT NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);