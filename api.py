'''
Description: An api that takes http metrics from Cloudflare
and outputs them monthly into slack
'''
import argparse
import json
import os
import sys
import logging
import pendulum
import requests
from dotenv import load_dotenv
import sqlite_data

load_dotenv()

# setup a basic parser for dev testing
parser = argparse.ArgumentParser(
    description='Process Our Monthly Cloudflare Datae')
parser.add_argument('--testing', default=False, action='store_true',
                    help='Use when running locally for dev/testing.')

args = parser.parse_args()
#print(args.testing)

# constants / dictionaries used
DICT_MONTH = {1: 'Janruary', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June',
              7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November',
              12: 'December'}
# DICT_METR = {'requests' : 0, 'bandwidth' : 1, 'visits' : 2, 'views' : 3}
URLCLOUD = "https://api.cloudflare.com/client/v4/graphql"
URLSLACK = os.environ.get('URLSLACK')

def stringify_data(date):
    '''Purpose: returns date in a string format to manipulate'''
    cur_data = sqlite_data.get_data_by_date(
        date.to_date_string())  # test value used: '2022-06-01'
    print(cur_data)

    return cur_data

# time must be run with last months intention

def month_diff():
    '''Purpose: to calculate the month-over-month difference
    between requests, bandwidth, visits and views'''
    data_list = stringify_data(first_month_time)

    request_diff = round((float(HTTP_REQUESTS - data_list[0])) / data_list[0] * 100, 2)
    band_diff = round((float(BANDWIDTH - data_list[1])) / data_list[1] * 100, 2)
    visits_diff = round((float(VISITS - data_list[2])) / data_list[2] * 100, 2)
    view_diff = round((float(VIEWS - data_list[3])) / data_list[3] * 100, 2)

    list_diff = [request_diff, band_diff, visits_diff, view_diff]

    for each in list_diff:
        print(each)

    # return a list of diffs
    return list_diff

# set emoji list


def set_emojis():
    '''Purpose: returns stringified list with emoji
    states (representing fluctuation) to be represented in slack'''
    emojis = ["", "", "", ""]
    count = 0

    # figure out if increase or decrease in difference
    for each in percentages:
        if each > 0:
            emojis[count] = "arrow_upper_right"
        elif each == 0:
            emojis[count] = "arrow_right"
        else:
            emojis[count] = "arrow_lower_right"
        count += 1

    return emojis


now = pendulum.now()
time = pendulum.parse((str)(now))
# subtract by an extra day to account for exclusion of boundaries
# will account from second day of the month as not all months have 30 days
prevtime = time.subtract(days=31)

first_month_time = time.subtract(days=1)
first_month_time = time.subtract(days=first_month_time.day)

# Test print
# print(time.to_date_string())
# print(prevtime.to_date_string())

#configure logging output
logging.basicConfig(level=logging.DEBUG)


# We may not be representing current day
# payload used for Cloudflare API
PAYLOAD_CLOUD = """query{
    viewer{
        accounts(filter: {
            accountTag: ""
        }
        )
        {
            httpRequestsOverviewAdaptiveGroups(filter: {
                date_gt: $gt
                date_lt: $lt
            },
            limit: 100
            orderBy: [date_ASC])
            {
                dimensions {
                    date
                }
                sum {
                    requests
                    pageViews
                    bytes
                    visits
                }
            }
        }
    }
    
}"""

cloudflare_request_variables = {'gt': prevtime.to_date_string(), 'lt': time.to_date_string()}

xAuthKey = os.environ.get('X_AUTH_KEY')
xAuthEmail = os.environ.get('X_AUTH_EMAIL')
headers = {
    'cookie': "__cfruid=",
    'Content-Type': "application/json",
    'X-Auth-Key': xAuthKey,
    'X-Auth-Email': xAuthEmail
}

# Request data from JSON payload
response = requests.request("POST", URLCLOUD,\
    json={"query": PAYLOAD_CLOUD, "variables":cloudflare_request_variables}, headers=headers)
data = response.json() if response and response.status_code == 200 else None

logging.debug("Request from Cloudflare is successfully recieved.")

HTTP_REQUESTS = 0
VIEWS = 0
BANDWIDTH = 0
VISITS = 0

# create dictionary for JSON code
dictCloud = \
    json.loads(response.text)["data"]["viewer"]["accounts"][0]["httpRequestsOverviewAdaptiveGroups"]

# nest to get to individual data points
for day in dictCloud:
    HTTP_REQUESTS += day["sum"]["requests"]
    VIEWS += day["sum"]["pageViews"]
    BANDWIDTH += day["sum"]["bytes"]
    VISITS += day["sum"]["visits"]

#
# conversions/calculations
#
VIEWS /= 1000000
VIEWS = round(VIEWS, 1)

HTTP_REQUESTS /= 1000000
HTTP_REQUESTS = round(HTTP_REQUESTS, 1)

VISITS /= 1000000
VISITS = round(VISITS, 2)

BANDWIDTH /= (1024**2)  # 1000 at some points closer than 1024
BANDWIDTH /= 1000
BANDWIDTH = round(BANDWIDTH, 1)

logging.debug("Metrics are successfully parsed from a JSON dictionary and calculated.")

#
# Ensures data is not added if it is not the first day of the month OR the previous
# date is equal to the current date
#
# Test values used: '2022-06-01' as prevtime
# '2022-06-01' as prevtime
# '2022-07-01' as time
#
if not args.testing:
    index = (time.to_date_string().find("01"))
    # checks if it is the first month of the day
    if index != 8:
        logging.error("Date could not be added to the database.")
        sys.exit()
    else:
        # checks if date already exists in the datafile
        if sqlite_data.get_data_by_date(time.to_date_string()) is None:
            # add current metrics to db file
            sqlite_data.add_entry(HTTP_REQUESTS, BANDWIDTH,
                                 VISITS, VIEWS, time.to_date_string())
            sqlite_data.push_file()
            logging.info("Date was pushed onto the database.")
        else:
            logging.info("Date already exists in the database. Using older metrics.")


# get difference between current and previous statistics
percentages = month_diff()

# convert list elements
#[float(i) for i in percentages]

emoji_list = set_emojis()

print("Percentages calculated and emojis set.")

slack_request_variables = {
    'month': DICT_MONTH[time.month],
    'http_requests': HTTP_REQUESTS,
    'requests_emoji': emoji_list[0],
    'requests_change_percentage': percentages[0],
    'bandwidth': BANDWIDTH,
    'bandwidth_emoji': emoji_list[1],
    'bandwidth_change_percentage': percentages[1],
    'visitors': VISITS,
    'visitors_emoji': emoji_list[2],
    'visitors_change_percentage': percentages[2],
    'views': VIEWS,
    'views_emoji': emoji_list[3],
    'views_change_percentage': percentages[3]
}
# payload for SLACK (output design) - TODO: change to f-string
payloadSlack = {
    "blocks": [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": ":exclamation: " + slack_request_variables['month']\
                     + "Fun Facts!:exclamation:",
                "emoji": True
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "Last month across our platform and customer tracking URLs we served:"
            }
        },
        {
            "type": "divider"
        },
        {
            "type": "section",
            "text": {
                "type": "plain_text",
                "text": "- " + str(slack_request_variables['http_requests'])+" Million Requests :"\
                    + slack_request_variables['requests_emoji'] + ": "\
                    + str(slack_request_variables['requests_change_percentage']) + "%\n - " \
                    + str(slack_request_variables['bandwidth']) + "Gigabytes of Data :"\
                    + slack_request_variables['bandwidth_emoji'] + ":"
                    + str(slack_request_variables['bandwidth_change_percentage']) + "%\n -" \
                    + str(slack_request_variables['visitors']) + " Million Unique Visitors :"\
                    + slack_request_variables['visitors_emoji'] + ": "\
                    + str(slack_request_variables['visitors_change_percentage']) + "%\n - "\
                    + str(slack_request_variables['views']) + " Million Page Views :"\
                    + slack_request_variables['views_emoji'] + ": "\
                    + str(slack_request_variables['views_change_percentage']) + "%",
                "emoji": True
            }
        }
    ]
}

logging.debug("Payload syntax for slack message formatting passed.")

# post data points into slack
# uncomment to post
if not args.testing:
    output = requests.post(url=URLSLACK, data=json.dumps(payloadSlack))
    logging.info("Endpoint request was sent to slack.")

# push file back to s3 and close connection
sqlite_data.close()

# Note: Data does not match with the shown data on the Cloudflare Analytics FE.
# Assumed due to the subcategory being in BETA (not properly developed API)
