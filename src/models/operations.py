import psycopg2
from api import db
from aux import logger_instance
from errors import Error, FATAL

logger = logger_instance(__name__)


def result_to_event(r):
    from .event import Event
    return Event(r["event_id"], r["work_uri"], r["measure_uri"],
                 r["timestamp"], r["value"], r["event_uri"],
                 r["country_uri"], r["uploader_uri"])


def result_to_country(r):
    from .country import Country
    return Country(r["country_uri"], r["country_code"], r["country_name"],
                   r["continent_code"])


def result_to_measure(r, description=False):
    from .measure import Measure
    measure = Measure(r["measure_uri"], r["namespace"], r["source"], r["type"],
                      r["version"])
    if description:
        measure.load_description()
    return measure


def result_to_date_part(year=None, month=None):
    from .datepart import Datepart
    return Datepart(year=year, month=month)


def result_to_year(r):
    return result_to_date_part(year=r["year"])


def result_to_month(r):
    return result_to_date_part(month=r["month"])


def results_to_events(results):
    return [(result_to_event(e).__dict__) for e in results]


def results_to_countries(results):
    return [(result_to_country(e).__dict__) for e in results]


def results_to_measures(results, description=False):
    return [(result_to_measure(e, description).__dict__) for e in results]


def do_query(query, params):
    try:
        return db.query(query, params)
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        raise Error(FATAL)


AGGREGATIONS = {
    'measure': {
        'main_entity': 'measure_uri',
        'main_function': result_to_measure
    },
    'measure_country': {
        'main_entity': 'measure_uri',
        'main_function': result_to_measure,
        'pivot_function': result_to_country
    },
    'country_measure': {
        'main_entity': 'country_uri',
        'main_function': result_to_country,
        'pivot_function': result_to_measure
    },
    'measure_year': {
        'main_entity': 'measure_uri',
        'main_function': result_to_measure,
        'pivot_function': result_to_year
    },
    'year_measure': {
        'main_entity': 'year',
        'main_function': result_to_year,
        'pivot_function': result_to_measure
    },
    'measure_month': {
        'main_entity': 'measure_uri',
        'main_function': result_to_measure,
        'pivot_function': result_to_month
    },
    'month_measure': {
        'main_entity': 'month',
        'main_function': result_to_month,
        'pivot_function': result_to_measure
    }
}
