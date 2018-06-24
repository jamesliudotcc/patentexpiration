import json
import maya
from nested_lookup import nested_lookup
from calendar import month_name

def generate_string_answer_from_json(patent_as_dict):
    """Takes a dict generated from a json and creates a string explaining patent term"""

    patent_title = nested_lookup('inventionTitle', patent_as_dict)[0]['content'][0]

    patent_number = int(nested_lookup('patentNumber', patent_as_dict)[0])
    patent_number_pretty = "{:,}".format(patent_number)
    patent_grant_date = maya.parse(nested_lookup('grantDate', patent_as_dict)[0])
    patent_adjustment_quant = nested_lookup('adjustmentTotalQuantity', patent_as_dict)[0]
    patent_expire_date = patent_grant_date.add(years=20)
    patent_expire_date = patent_expire_date.add(days=patent_adjustment_quant)

    result = (f'You asked me to calculate the expiration date for patent number '
        f'{patent_number_pretty}, with patent title,"{patent_title}". The patent expires on '
        f'{month_name[patent_expire_date.month]} {patent_expire_date.day}, '
        f'{patent_expire_date.year}. The patent was granted on ' 
        f'{month_name[patent_grant_date.month]} {patent_grant_date.day}, '
        f'{patent_grant_date.year}, and would ordinarily last for 20 years. There were '
        f'{patent_adjustment_quant} days of patent term adjustment applied.')

    return result

with open('2008.json') as f:
    patent_json_file = f.read()

patent_as_dict = json.loads(patent_json_file)

print("\n")
print(generate_string_answer_from_json(patent_as_dict))