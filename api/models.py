class Event(object):
    def __init__(self, object_id, measure, timestamp, value, country, uploader):
        self.object_id = str(object_id)
        self.measure   = str(measure)
        self.timestamp = timestamp.strftime('%Y-%m-%dT%H:%M:%S%z')
        self.value     = int(value)
        self.country   = str(country)
        self.uploader  = int(uploader)

    def save(self, connection):
        try:
            c = connection.cursor()
            c.execute('''INSERT INTO event (id, measure_id, timestamp,
                                            country_code, value, uploader_id)
                         VALUES (%s, %s, %s, %s, %s, %s);''', \
                      (self.object_id, self.measure, self.timestamp, \
                       self.country, self.value, self.uploader))
            success = connection.commit()
            c.close()
            return success
        except:
            raise NotFound()

    @staticmethod
    def get_events(connection, key):
        try:
            c = connection.cursor()
            c.execute("SELECT * FROM event WHERE id = %s;", (key,))
            result = c.fetchall()
            c.close()
            return result
        except KeyError:
            raise NotFound()
