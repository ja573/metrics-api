import logging
import psycopg2
from errors import NotFound, NotAllowed

class Event(object):
    def __init__(self, object_uri, measure, timestamp, value, country, uploader):
        self.object_uri = str(object_uri)
        self.measure   = str(measure)
        self.timestamp = timestamp.strftime('%Y-%m-%dT%H:%M:%S%z')
        self.value     = int(value)
        self.country   = str(country)
        self.uploader  = int(uploader)

    def save(self, connection):
        try:
            c = connection.cursor()
            c.execute('''INSERT INTO event (uri, measure_id, timestamp,
                                            country_code, value, uploader_id)
                         VALUES (%s, %s, %s, %s, %s, %s);''', \
                      (self.object_uri, self.measure, self.timestamp, \
                       self.country, self.value, self.uploader))
            success = connection.commit()
            c.close()
            return success
        except (Exception, psycopg2.DatabaseError) as error:
            logging.debug(error)
            raise NotFound()
        finally:
            if c is not None:
                c.close()

    @staticmethod
    def get_events(connection, key):
        try:
            c = connection.cursor()
            c.execute("SELECT * FROM event WHERE uri = %s;", (key,))
            result = c.fetchall()
            c.close()
            return result
        except (Exception, psycopg2.DatabaseError) as error:
            logging.debug(error)
            raise NotFound()
        finally:
            if c is not None:
                c.close()
