from aux import logger_instance
from .operations import (result_to_country, result_to_measure, result_to_year,
                         result_to_month)

logger = logger_instance(__name__)

AGGREGATIONS = {
    'measure_uri': {
        'main_entity': 'measure_uri',
        'main_function': result_to_measure
    },
    'measure_uri,country_uri': {
        'main_entity': 'measure_uri',
        'main_function': result_to_measure,
        'pivot_function': result_to_country
    },
    'country_uri,measure_uri': {
        'main_entity': 'country_uri',
        'main_function': result_to_country,
        'pivot_function': result_to_measure
    },
    'measure_uri,year': {
        'main_entity': 'measure_uri',
        'main_function': result_to_measure,
        'pivot_function': result_to_year
    },
    'year,measure_uri': {
        'main_entity': 'year',
        'main_function': result_to_year,
        'pivot_function': result_to_measure
    },
    'measure_uri,month': {
        'main_entity': 'measure_uri',
        'main_function': result_to_measure,
        'pivot_function': result_to_month
    },
    'month,measure_uri': {
        'main_entity': 'month',
        'main_function': result_to_month,
        'pivot_function': result_to_measure
    }
}


class Aggregation():
    def __init__(self, criterion):
        self.entity = AGGREGATIONS[criterion].get('main_entity')
        self.main_function = AGGREGATIONS[criterion].get('main_function')
        self.pivot_function = AGGREGATIONS[criterion].get('pivot_function')

    def is_unidimensional(self):
        return self.pivot_function is None

    def aggregate(self, data):
        return (self.unidimensional_aggregation(data)
                if self.is_unidimensional()
                else self.multidimensional_aggregation(data))

    def unidimensional_aggregation(self, data):
        output = []
        for r in data:
            obj = self.main_function(r)
            obj.value = r["value"]
            output.append(obj.__dict__)
        return output

    def multidimensional_aggregation(self, data):
        output = []
        tmp = []

        for i, r in enumerate(data):
            if i == 0:
                # if we do cur=data[0] outsise it moves IterBetter's pointer
                cur = r
            if r[self.entity] != cur[self.entity]:
                obj = self.main_function(cur)
                obj.output = tmp
                output.append(obj.__dict__)
                tmp = []
                cur = r
            piv = self.pivot_function(r)
            piv.value = r["value"]
            tmp.append(piv.__dict__)
        try:
            obj = self.main_function(cur)
            obj.output = tmp
            output.append(obj.__dict__)
        except NameError:
            # we need to run the above with the last element of IterBetter,
            # if it fails it means that no data were iterated
            pass
        return output

    @staticmethod
    def list_allowed():
        return ', '.join("'{0}'".format(x) for x in AGGREGATIONS.keys())
