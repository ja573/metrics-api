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


def results_to_events(results):
    return [(result_to_event(e).__dict__) for e in results]


def results_to_countries(results):
    return [(result_to_country(e).__dict__) for e in results]


def results_to_measures(results, description=False):
    return [(result_to_measure(e, description).__dict__) for e in results]


def results_to_measure_aggregation(results):
    data = []
    for r in results:
        measure = result_to_measure(r)
        measure.value = r["value"]
        data.append(measure.__dict__)
    return data


def results_to_measure_country_aggregation(results):
    data = []
    countries = []  # temporary list of countries

    for i, r in enumerate(results):
        if i == 0:
            # we can't do cur=results[0] outsise--it moves IterBetter's pointer
            cur = r
        if r["measure_uri"] != cur["measure_uri"]:
            measure = result_to_measure(cur)
            measure.data = countries
            data.append(measure.__dict__)
            countries = []
            cur = r
        country = result_to_country(r)
        country.value = r["value"]
        countries.append(country.__dict__)
    try:
        measure = result_to_measure(cur)
        measure.data = countries
        data.append(measure.__dict__)
    except NameError:
        # we need to run the above with the last element of IterBetter, if it
        # fails it means that no results were iterated
        pass
    return data


def results_to_country_measure_aggregation(results):
    data = []
    measures = []  # temporary list of measures

    for i, r in enumerate(results):
        if i == 0:
            # we can't do cur=results[0] outsise--it moves IterBetter's pointer
            cur = r
        if r["country_uri"] != cur["country_uri"]:
            country = result_to_country(cur)
            country.data = measures
            data.append(country.__dict__)
            measures = []
            cur = r
        measure = result_to_measure(r)
        measure.value = r["value"]
        measures.append(measure.__dict__)
    try:
        country = result_to_country(cur)
        country.data = measures
        data.append(country.__dict__)
    except NameError:
        # we need to run the above with the last element of IterBetter, if it
        # fails it means that no results were iterated
        pass
    return data


def results_to_measure_year_aggregation(results):
    data = []
    years = []  # temporary list of years

    for i, r in enumerate(results):
        if i == 0:
            # we can't do cur=results[0] outsise--it moves IterBetter's pointer
            cur = r
        if r["measure_uri"] != cur["measure_uri"]:
            measure = result_to_measure(cur)
            measure.data = years
            data.append(measure.__dict__)
            years = []
            cur = r
        years.append(dict(year=r["year"], value=r["value"]))
    try:
        measure = result_to_measure(cur)
        measure.data = years
        data.append(measure.__dict__)
    except NameError:
        # we need to run the above with the last element of IterBetter, if it
        # fails it means that no results were iterated
        pass
    return data


def results_to_year_measure_aggregation(results):
    data = []
    measures = []  # temporary list of measures

    for i, r in enumerate(results):
        if i == 0:
            # we can't do cur=results[0] outsise--it moves IterBetter's pointer
            cur = r
        if r["year"] != cur["year"]:
            data.append(dict(year=cur["year"], data=measures))
            measures = []
            cur = r
        measure = result_to_measure(r)
        measure.value = r["value"]
        measures.append(measure.__dict__)
    try:
        data.append(dict(year=cur["year"], data=measures))
    except NameError:
        # we need to run the above with the last element of IterBetter, if it
        # fails it means that no results were iterated
        pass
    return data


def results_to_measure_month_aggregation(results):
    data = []
    months = []  # temporary list of months

    for i, r in enumerate(results):
        if i == 0:
            # we can't do cur=results[0] outsise--it moves IterBetter's pointer
            cur = r
        if r["measure_uri"] != cur["measure_uri"]:
            measure = result_to_measure(cur)
            measure.data = months
            data.append(measure.__dict__)
            months = []
            cur = r
        months.append(dict(month=r["month"], value=r["value"]))
    try:
        measure = result_to_measure(cur)
        measure.data = months
        data.append(measure.__dict__)
    except NameError:
        # we need to run the above with the last element of IterBetter, if it
        # fails it means that no results were iterated
        pass
    return data


def results_to_month_measure_aggregation(results):
    data = []
    measures = []  # temporary list of measures

    for i, r in enumerate(results):
        if i == 0:
            # we can't do cur=results[0] outsise--it moves IterBetter's pointer
            cur = r
        if r["month"] != cur["month"]:
            data.append(dict(month=cur["month"], data=measures))
            measures = []
            cur = r
        measure = result_to_measure(r)
        measure.value = r["value"]
        measures.append(measure.__dict__)
    try:
        data.append(dict(month=cur["month"], data=measures))
    except NameError:
        # we need to run the above with the last element of IterBetter, if it
        # fails it means that no results were iterated
        pass
    return data


def do_query(query, params):
    try:
        return db.query(query, params)
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        raise Error(FATAL)
