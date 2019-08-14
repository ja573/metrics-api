import psycopg2
from api import db
from aux import logger_instance
from errors import Error, FATAL

logger = logger_instance(__name__)


class Event():
    def __init__(self, event_id, work_uri, measure_uri, timestamp, value,
                 event_uri=None, country_uri=None, uploader_uri=''):
        self.event_id = event_id
        self.work_uri = work_uri
        self.measure_uri = measure_uri
        self.timestamp = timestamp.strftime('%Y-%m-%dT%H:%M:%S%z')
        self.value = int(value)
        self.event_uri = event_uri
        self.country_uri = country_uri
        self.uploader_uri = uploader_uri

    def save(self):
        try:
            q = '''INSERT INTO event (event_id, work_uri, measure_uri,
                      timestamp, value, event_uri, country_uri, uploader_uri)
                    VALUES ($event_id, $work_uri, $measure_uri, $timestamp,
                      $value, $event_uri, $country_uri, $uploader_uri)
                    ON CONFLICT DO NOTHING;'''
            vals = dict(event_id=self.event_id, work_uri=self.work_uri,
                        measure_uri=self.measure_uri, timestamp=self.timestamp,
                        value=self.value, event_uri=self.event_uri,
                        country_uri=self.country_uri,
                        uploader_uri=self.uploader_uri)
            db.query(q, vals)
        except (Exception, psycopg2.DatabaseError) as error:
            logger.debug(error)
            raise Error(FATAL)

    @staticmethod
    def get_from_event_id(event_id):
        params = dict(event_id=event_id)
        clause = "AND event_id = $event_id"
        return Event.get_all(clause, params)

    @staticmethod
    def get_all(clause, params):
        try:
            q = '''SELECT * FROM event WHERE 1=1 ''' + clause + '''
                   ORDER BY timestamp;'''
            return db.query(q, params)
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            raise Error(FATAL)

    @staticmethod
    def aggregate_by_measure(clause, params):
        try:
            q = '''SELECT
                     measure_uri,
                     namespace,
                     source,
                     type,
                     version,
                     SUM(value) as value
                   FROM event INNER JOIN measure USING(measure_uri)
                   WHERE 1=1 ''' + clause + '''
                   GROUP BY measure_uri, namespace, source, type, version
                   ORDER BY measure_uri;'''
            result = db.query(q, params)
            return result
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            raise Error(FATAL)

    @staticmethod
    def aggregate_by_measure_country(clause, params):
        try:
            q = '''SELECT
                     measure_uri,
                     namespace,
                     source,
                     type,
                     version,
                     country_uri,
                     country_code,
                     country_name,
                     continent_code,
                     SUM(value) as value
                   FROM event
                     INNER JOIN measure USING(measure_uri)
                     LEFT JOIN country USING(country_uri)
                   WHERE 1=1 ''' + clause + '''
                   GROUP BY measure_uri, namespace, source, type, version,
                      country_uri, country_code, country_name, continent_code
                   ORDER BY measure_uri, country_uri;'''
            result = db.query(q, params)
            return result
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            raise Error(FATAL)

    @staticmethod
    def aggregate_by_country_measure(clause, params):
        try:
            q = '''SELECT
                     country_uri,
                     country_code,
                     country_name,
                     continent_code,
                     measure_uri,
                     namespace,
                     source,
                     type,
                     version,
                     SUM(value) as value
                   FROM event
                     INNER JOIN measure USING(measure_uri)
                     LEFT JOIN country USING(country_uri)
                   WHERE 1=1 ''' + clause + '''
                   GROUP BY country_uri, country_code, country_name,
                      continent_code, measure_uri, namespace, source,
                      type, version
                   ORDER BY country_uri, measure_uri;'''
            result = db.query(q, params)
            return result
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            raise Error(FATAL)

    @staticmethod
    def aggregate_by_measure_year(clause, params):
        try:
            q = '''SELECT
                     measure_uri,
                     namespace,
                     source,
                     type,
                     version,
                     to_char(timestamp, 'YYYY') as year,
                     SUM(value) as value
                   FROM event
                     INNER JOIN measure USING(measure_uri)
                   WHERE 1=1 ''' + clause + '''
                   GROUP BY measure_uri, namespace, source, type, version, year
                   ORDER BY measure_uri, year;'''
            result = db.query(q, params)
            return result
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            raise Error(FATAL)

    @staticmethod
    def aggregate_by_year_measure(clause, params):
        try:
            q = '''SELECT
                     to_char(timestamp, 'YYYY') as year,
                     measure_uri,
                     namespace,
                     source,
                     type,
                     version,
                     SUM(value) as value
                   FROM event
                     INNER JOIN measure USING(measure_uri)
                   WHERE 1=1 ''' + clause + '''
                   GROUP BY year, measure_uri, namespace, source, type, version
                   ORDER BY year, measure_uri;'''
            result = db.query(q, params)
            return result
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            raise Error(FATAL)

    @staticmethod
    def aggregate_by_measure_month(clause, params):
        try:
            q = '''SELECT
                     measure_uri,
                     namespace,
                     source,
                     type,
                     version,
                     to_char(timestamp, 'MM') as month,
                     SUM(value) as value
                   FROM event
                     INNER JOIN measure USING(measure_uri)
                   WHERE 1=1 ''' + clause + '''
                   GROUP BY measure_uri, namespace, source, type, version,
                     month
                   ORDER BY measure_uri, month;'''
            result = db.query(q, params)
            return result
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            raise Error(FATAL)

    @staticmethod
    def aggregate_by_month_measure(clause, params):
        try:
            q = '''SELECT
                     to_char(timestamp, 'MM') as month,
                     measure_uri,
                     namespace,
                     source,
                     type,
                     version,
                     SUM(value) as value
                   FROM event
                     INNER JOIN measure USING(measure_uri)
                   WHERE 1=1 ''' + clause + '''
                   GROUP BY month, measure_uri, namespace, source, type,
                     version
                   ORDER BY month, measure_uri;'''
            result = db.query(q, params)
            return result
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            raise Error(FATAL)