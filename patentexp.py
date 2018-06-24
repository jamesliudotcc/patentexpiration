"""
Uses USPTO Open Data API to collect patent data and calculate the expiration date of a patent by patent number
"""
import json
import maya
import re
from collections import namedtuple
from uspto.pbd.client import UsptoPairBulkDataClient
from calendar import month_name

def get_patent_data_by_number(patent_number):
    """Returns a named tuple of all of the relevant patent data from the USPTO API

    """
    def find_terminal_disclaimer(term_Json):
        """Returns True if a terminal disclaimer is found in 
        the patentTermJSON information, False otherwise"""
        if term_Json == {}:
            return False
        list_of_history_data = term_Json[
                                      'patentTermAdjustmentData'][
                                      'patentTermAdjustmentHistoryData'
                                      ]
        for docket_entry in list_of_history_data:
            if docket_entry['caseActionDescriptionText'] == 'Terminal Disclaimer Filed':
                return True
        return False 
    
    client = UsptoPairBulkDataClient()

    APIResult = client.search(patent_number)
    patent_information = APIResult['docs'][0]
    try:
        patent_term_json = patent_information['patentTermJson']
        patent_term_dictionary = json.loads(patent_term_json)
    except KeyError:
        patent_term_dictionary = {} #catch when the patentTermJson doesn't exist,
                                    #such as in pre '99 patents where it doesn't apply

    patent=namedtuple('patent',['p_number',
                                'title',
                                'filing_date',
                                'issue_date',
                                'term_adjustment',
                                'terminal_disclaimer',])

    patent.number = patent_number
    patent.title = patent_information['patentTitle']
    patent.filing_date = patent_information['appFilingDate']
    patent.issue_date = patent_information['patentIssueDate']
    if patent_term_dictionary == {}:
        patent.term_adjustment = 0
    else:
        patent.term_adjustment = patent_term_dictionary['patentTermAdjustmentData']['adjustmentTotalQuantity']
    patent.terminal_disclaimer = find_terminal_disclaimer(patent_term_dictionary)

    return patent

def pretty_number(ugly_number):
    """Returns a large number with commas inserted. Patent numbers are unreadable otherwise.
    """
    ugly_number = int(ugly_number)
    return "{:,}".format(ugly_number)

def under_five_million_shortcut(patent_number):
    """Returns a string representation for the under five million shortcut
    """
    return (f'You asked me to calculate the expiration for patent number '
        f'{pretty_number(patent_number)}, which is a ridiculously low number. '
        f'That patent is totally expired. I didn\'t even have to query '
        f'the USPTO.')

def before_june_8_1995(patent):
    """Returns a string representation for patents was filed before June 8, 1995.
    Takes a Patent named tuple, which is what is returned by the GetPatentByNumber
    function.
    """
    patent_issue_date = maya.parse(patent.issue_date)
    patent_filing_date = maya.parse(patent.filing_date)
    issue_plus_seventeen = patent_issue_date.add(years=17)
    filing_plus_twenty = patent_filing_date.add(years=20)

    boilerplate1 = (f'You asked me to calculate the expiration date for patent number '
                f'{pretty_number(patent.number)}, with patent title, "{patent.title}". ')
    boilerplate2 = (f'Filing was on {month_name[patent_filing_date.month]} '
                f'{patent_filing_date.day}, {patent_filing_date.year}. Twenty years '
                f'after was {filing_plus_twenty.year}. The patent was issued on '
                f'{month_name[patent_issue_date.month]} {patent_issue_date.day}, '
                f'{patent_issue_date.year}. Seventeen years later was'
                f'{issue_plus_seventeen.year}. Patent term expires the later of those dates. '
                f'Patent term adjustment does not apply to patents filed before 1999.')

    if issue_plus_seventeen > filing_plus_twenty:
        return (boilerplate1 +
                f'The patent expires on {month_name[issue_plus_seventeen.month]} '
                f'{issue_plus_seventeen.day}, {issue_plus_seventeen.year}. '
               + boilerplate2)
    else:
        return (boilerplate1 +
                f'The patent expires on {month_name[filing_plus_twenty.month]} '
                f'{filing_plus_twenty.day}, {filing_plus_twenty.year}. '
                + boilerplate2)

def after_june_8_1995(patent):
    """Returns a string representation for patents was filed after June 8, 1995.
    Takes a Patent named tuple, which is what is returned by the GetPatentByNumber
    function.
    """
    patent_issue_date = maya.parse(patent.issue_date)
    patent_expire_date = patent_issue_date.add(years=20)
    patent_expire_date = patent_expire_date.add(days=patent.term_adjustment)

    return (f'You asked me to calculate the expiration date for patent number '
        f'{pretty_number(patent.number)}, with patent title,"{patent.title}". '
        f'The patent expires on '
        f'{month_name[patent_expire_date.month]} {patent_expire_date.day}, '
        f'{patent_expire_date.year}. The patent was granted on ' 
        f'{month_name[patent_issue_date.month]} {patent_issue_date.day}, '
        f'{patent_issue_date.year}, and would ordinarily last for 20 years. '
        f'There were {patent.term_adjustment} days of patent term adjustment'
        f' applied.')

june_8_1995 = maya.parse('June 8, 1995')

patent_number = 50000000

if int(patent_number) < 5000000:
    result = under_five_million_shortcut(patent_number)
else:
    try:
        patent = get_patent_data_by_number(patent_number)
        if maya.parse(patent.filing_date) <= june_8_1995:
            result = before_june_8_1995(patent)
        else:
            result = after_june_8_1995(patent)
    except IndexError:
        result = f'Sorry, patent number {pretty_number(patent_number)} cannot be found in PAIR.'

print(result)

#result_from_API = GetPatentDataByNumber(9675757)
#print(result_from_API.terminal_disclaimer)

#need to check for non-PTO delays on website: https://www.uspto.gov/patent/laws-and-regulations/patent-term-extension/patent-terms-extended-under-35-usc-156
#website says this is on PAIR, so check a few to make sure those can be programmed in.
#This assumes that all the times are at 0:00:00.000 UTC, which there is no reason
#    for it not to be. This needs to be tested with patents granted on June 8, 1995.
#    For now, I am moving on and ignoring this problem.