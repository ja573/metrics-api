CREATE TABLE continent(
  continent_code char(2) PRIMARY KEY NOT NULL,
  continent_name varchar(255) NOT NULL
);

CREATE TABLE country(
  country_id char(22) PRIMARY KEY NOT NULL,
  country_code char(2) NOT NULL,
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
  namespace varchar(255) PRIMARY KEY NOT NULL,
  definition_url varchar(255) NOT NULL
);

CREATE TABLE uploader(
  uploader_id varchar(255) PRIMARY KEY NOT NULL,
  uploader_name varchar(255) NOT NULL
);

CREATE TABLE namespace_uploader(
  namespace varchar(255) NOT NULL REFERENCES namespace(namespace),
  uploader_id varchar(255) NOT NULL REFERENCES uploader(uploader_id),
  PRIMARY KEY(namespace, uploader_id)
);

CREATE TABLE measure(
  measure_id varchar(255) PRIMARY KEY NOT NULL,
  namespace varchar(255) NOT NULL REFERENCES namespace(namespace),
  source_name varchar(255) NOT NULL REFERENCES source(source_name),
  type_name varchar(255) NOT NULL REFERENCES type(type_name)
);

CREATE TABLE event(
  event_id uuid PRIMARY KEY NOT NULL,
  uri text NOT NULL,
  measure_id varchar(255) NOT NULL REFERENCES measure(measure_id),
  timestamp timestamp with time zone NOT NULL,
  value integer NOT NULL,
  country_id char(22) NULL REFERENCES country(country_id),
  uploader_id varchar(255) NOT NULL REFERENCES uploader(uploader_id),
  UNIQUE(uri, measure_id, timestamp, country_id)
);
CREATE UNIQUE INDEX event_uri_measure_id_timestamp_country_id_null_key ON event (uri, measure_id, timestamp)
WHERE country_id IS NULL;

