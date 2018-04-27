import uuid
import logging
import psycopg2
from errors import NotFound, NotAllowed

class Event(object):
    def __init__(self, event_id, uri, measure, timestamp, value, country, uploader):
        self.event_id  = str(event_id) if event_id else str(uuid.uuid4())
        self.URI       = str(uri)
        self.measure   = str(measure)
        self.timestamp = timestamp.strftime('%Y-%m-%dT%H:%M:%S%z')
        self.value     = int(value)
        self.country   = str(country) if country else None
        self.uploader  = str(uploader)

    def save(self, connection):
        try:
            c = connection.cursor()
            c.execute('''INSERT INTO event (event_id, uri, measure_id,
                                            timestamp, country_id,
                                            value, uploader_id)
                         VALUES (%s, %s, %s, %s, %s, %s, %s);''', \
                      (self.event_id, self.URI, self.measure, self.timestamp, \
                       self.country, self.value, self.uploader))
            success = connection.commit()
            c.close()
            return success
        except (Exception, psycopg2.DatabaseError) as error:
            logging.error(error)
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
            logging.error(error)
            raise NotFound()
        finally:
            if c is not None:
                c.close()
