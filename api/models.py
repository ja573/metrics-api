import uuid
import logging
import os
import psycopg2

from errors import NotFound, NotAllowed


logger = logging.getLogger(__name__)


def database_handle():

    db_host = os.environ['POSTGRES_HOST']
    db_name = os.environ['POSTGRES_DB']
    db_user = os.environ['POSTGRES_USER']
    db_passwd = os.environ['POSTGRES_PASSWORD']

    dbconfig = (
        "dbname='{db_name}' user='{db_user}' host='{db_host}' "
        "password='{db_passwd}'".format(**locals())
    )
    try:
        return psycopg2.connect(dbconfig)
    except psycopg2.OperationalError as error:
        logger.error(error)
        raise


class Event(object):
    def __init__(self, event_id, uri, measure, timestamp, value, country, uploader):
        self.event_id  = str(event_id) if event_id else str(uuid.uuid4())
        self.URI       = str(uri)
        self.measure   = str(measure)
        self.timestamp = timestamp.strftime('%Y-%m-%dT%H:%M:%S%z')
        self.value     = int(value)
        self.country   = str(country) if country else None
        self.uploader  = str(uploader)

        self.connection = database_handle()

    def save(self):
        try:
            c = self.connection.cursor()
            statement = (
                "INSERT INTO event (event_id, uri, measure_id,"
                "timestamp, country_id, value, uploader_id) VALUES "
                "('%s', '%s', '%s', '%s', '%s', '%s', '%s');" % (
                    self.event_id, self.URI, self.measure, self.timestamp,
                    self.country, self.value, self.uploader
                )
            )
            c.execute(statement)
            success = self.connection.commit()
            c.close()
            return success
        except (Exception, psycopg2.DatabaseError) as error:
            logging.error(error)
            raise NotFound()
        finally:
            if c is not None:
                c.close()

    def get_events(self, key):
        try:
            c = self.connection.cursor()
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
