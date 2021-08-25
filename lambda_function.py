# August 2021
# https://github.com/geduldig/TwitterAPI
# https://docs.aws.amazon.com/lambda/latest/dg/python-package.html


import requests
import json
from datetime import datetime, timedelta
from TwitterAPI import TwitterAPI


def GetProductLifecycleMatrixJSON():
    url = 'https://auth.esp.vmware.com/api/auth/v1/tokens'
    custom_header = {
        "Content-Type": "application/json"
    }

    json_body = {
        "grant_type":"client_credentials",
        "client_id":"plm-prod-auth",
        "client_secret":"84e0f320-5c9d-4ced-a99b-3cc0a7ad64a9"
    }

    r = requests.post(url,headers = custom_header, json = json_body)
    data = (r.text).split("\"")

    url = 'https://plm.esp.vmware.com/api/v1/release_stream/lifecycle_matrix/?to=08/25/2021'

    custom_header = {
        "Accept":"application/json",
        "X-Auth-Key":data[3]
    }

    r2 = requests.get(url,headers = custom_header)

    return r2.text


def sendOutput(product, reason, days):
    tag = "#ProductLifecycleMatrix"
    tagUrl = "https://lifecycle.vmware.com"
    if days == 0:
        # print(product, "reaches", reason, "TODAY.", tagUrl, tag)
        tweet_text = f'{product} reaches {reason} TODAY. {tagUrl} {tag}'
    else:    
        # print(product, "reaches", reason, "in", days, "days.", tagUrl, tag)
        tweet_text = f'{product} reaches {reason} in {days} days. {tagUrl} {tag}'

    # TWEET_TEXT = "Ce n'est pas un tweet tweet."
    print(tweet_text)

    consumer_key="<your_api_key>"
    consumer_secret="<your_api_secret>"
    access_token_key="<your_access_token_key>"
    access_token_secret="<your_access_token_secret>"
    api = TwitterAPI(consumer_key, 
                    consumer_secret,
                    access_token_key,
                    access_token_secret)

    r = api.request('statuses/update', {'status': tweet_text})
    print('SUCCESS' if r.status_code == 200 else 'PROBLEM: ' + r.text)


def significantDate(plmrecord):

    # print(plmrecord)
    today = datetime.now().date()

    # How many days in advanced to check.
    daysWarning = [0, 30, 90, 180, 365]    # Set this on when to trigger alerts. Days before event.
    futureDate = [0] * len(daysWarning)    # Prepare array to store futureDates

    # Set future days to check. 
    for i in range(len(daysWarning)):
        futureDate[i] = today + timedelta(days = daysWarning[i])

    for i in range(len(futureDate)):
        # Check End of support dates
        if datetime.strptime(plmrecord["end_support_date"], "%Y-%m-%d").date() == futureDate[i]:
            sendOutput(plmrecord["name"],"end of general support", daysWarning[i])
    
        # Check end of technical guidance
        if plmrecord["end_tech_guidance_date"] != None: # Some records have null
            if datetime.strptime(plmrecord["end_tech_guidance_date"], "%Y-%m-%d").date() == futureDate[i]:
                sendOutput(plmrecord["name"],"end of technical guidance", daysWarning[i])
         

def lambda_handler(event, context):

    plmdata  = json.loads(GetProductLifecycleMatrixJSON())

    for i in range(len(plmdata["supported"])):
        # print(plmdata["unsupported"][i]["name"])
        significantDate(plmdata["supported"][i])

    print("Processed ", i, "records")
