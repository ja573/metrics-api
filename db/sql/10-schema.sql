CREATE TABLE continent(
  continent_code char(2) PRIMARY KEY NOT NULL,
  continent_name varchar(255) NOT NULL
);

CREATE TABLE country(
  country_code char(2) PRIMARY KEY NOT NULL,
  country_name varchar(255) NOT NULL,
  continent_code char(2) NOT NULL REFERENCES continent(continent_code)
);

CREATE TABLE type(
  type_name varchar(255) PRIMARY KEY NOT NULL
);

CREATE TABLE source(
  source_name varchar(255) PRIMARY KEY NOT NULL
);

CREATE TABLE namespace(
  domain_name varchar(255) PRIMARY KEY NOT NULL,
  definition_url varchar(255) NOT NULL
);

CREATE TABLE uploader(
  uploader_id serial PRIMARY KEY NOT NULL,
  uploader_name varchar(255) NOT NULL
);

CREATE TABLE namespace_uploader(
  domain_name varchar(255) NOT NULL REFERENCES namespace(domain_name),
  uploader_id integer NOT NULL REFERENCES uploader(uploader_id),
  PRIMARY KEY(domain_name, uploader_id)
);

CREATE TABLE measure(
  measure_id varchar(255) PRIMARY KEY NOT NULL,
  domain_name varchar(255) NOT NULL REFERENCES namespace(domain_name),
  source_name varchar(255) NOT NULL REFERENCES source(source_name),
  type_name varchar(255) NOT NULL REFERENCES type(type_name)
);

CREATE TABLE event(
  id varchar(255) NOT NULL,
  measure_id varchar(255) NOT NULL REFERENCES measure(measure_id),
  timestamp timestamp with time zone NOT NULL,
  value integer NOT NULL,
  country_code char(2) NOT NULL REFERENCES country(country_code),
  uploader_id integer NOT NULL REFERENCES uploader(uploader_id),
  PRIMARY KEY(id, measure_id, timestamp, country_code)
);

