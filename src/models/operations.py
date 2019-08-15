import psycopg2
from api import db
from aux import logger_instance
from errors import Error, FATAL, BADPARAMS

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


def result_to_year(r):
    from .year import Year
    return Year(r["year"])


def result_to_month(r):
    from .month import Month
    return Month(r["month"])


def results_to_events(results):
    return [(result_to_event(e).__dict__) for e in results]


def results_to_countries(results):
    return [(result_to_country(e).__dict__) for e in results]


def results_to_measures(results, description=False):
    return [(result_to_measure(e, description).__dict__) for e in results]


def aggregate(aggregation, results):
    try:
        entity = AGGREGATIONS[aggregation].get('main_entity')
        main_func = AGGREGATIONS[aggregation].get('main_function')
        pivot_func = AGGREGATIONS[aggregation].get('pivot_function')
    except KeyError:
        raise Error(BADPARAMS)
    if pivot_func is None:
        return aggregate_single_dimension(entity, main_func, results)
    else:
        return aggregate_multiple_dimensions(entity, main_func, pivot_func,
                                             results)


def aggregate_single_dimension(entity, main_func, results):
    data = []
    for r in results:
        obj = main_func(r)
        obj.value = r["value"]
        data.append(obj.__dict__)
    return data


def aggregate_multiple_dimensions(entity, main_func, pivot_func, results):
    data = []
    tmp = []

    for i, r in enumerate(results):
        if i == 0:
            # we can't do cur=results[0] outsise--it moves IterBetter's pointer
            cur = r
        if r[entity] != cur[entity]:
            obj = main_func(cur)
            obj.data = tmp
            data.append(obj.__dict__)
            tmp = []
            cur = r
        piv = pivot_func(r)
        piv.value = r["value"]
        tmp.append(piv.__dict__)
    try:
        obj = main_func(cur)
        obj.data = tmp
        data.append(obj.__dict__)
    except NameError:
        # we need to run the above with the last element of IterBetter, if it
        # fails it means that no results were iterated
        pass
    return data


def results_to_measure_aggregation(results):
    return aggregate('measure', results)


def results_to_measure_country_aggregation(results):
    return aggregate('measure_country', results)


def results_to_country_measure_aggregation(results):
    return aggregate('country_measure', results)


def results_to_measure_year_aggregation(results):
    return aggregate('measure_year', results)


def results_to_year_measure_aggregation(results):
    return aggregate('year_measure', results)


def results_to_measure_month_aggregation(results):
    return aggregate('measure_month', results)


def results_to_month_measure_aggregation(results):
    return aggregate('month_measure', results)


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
