import requests
import json
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth


from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions



# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
def get_request(url, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    print("params: ")
    print(kwargs)

    try:
        response = requests.get(url, kwargs, headers={'Content-Type': 'application/json'})
    except:
        print("Network exception occurred")

    status_code = response.status_code
    print("With status {} ".format(status_code))
    if not status_code == 200:
        return "" 

    json_data = json.loads(response.text)
    return json_data



# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url, json_payload, **kwargs):
    try:
        response = requests.post(url, params=kwargs, json=json_payload)
        json_data = json.loads(response.text)
        return json_data
        
    except:
        print("Network exception occurred")



# Create a get_dealers_from_cf method to get dealers from a cloud function
def get_dealers_from_cf(url):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)

    if json_result:
        # For each dealer object
        for dealer in json_result:
            dealer_doc = dealer["doc"]
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], state=dealer_doc["state"], zip=dealer_doc["zip"])
            results.append(dealer_obj)
    return results

#Gets dealer name by id
def get_dealer_name_by_id(url, id):
    json_result = get_request(url, dealerId=id)
    if json_result:
        return json_result[0]["full_name"]
    return ""


# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
def get_dealer_reviews_from_cf(url, dealerId):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url, dealerId=dealerId)

    if json_result:
        # For each dealer object
        for review in json_result["data"]["docs"]:
            review_obj = DealerReview(
                dealership = review["dealership"],
                name = review["name"],
                purchase = review["purchase"],
                review = review["review"],
                purchase_date = review.get("purchase_date", None),
                car_make = review.get("car_make", None),
                car_model = review.get("car_model", None),
                car_year = review.get("car_year", None),
                id = review["id"],
                sentiment = analyze_review_sentiments(review["review"])
            )
            results.append(review_obj)
    return results


# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative

    url = "https://api.eu-de.natural-language-understanding.watson.cloud.ibm.com/instances/b4180f6b-ccae-4fa7-a1c4-8e1305726891"
    api_key = "c0pWcXMHK31xuOnSr1lhqKNTKCUM5j9X4Xlufxd-RM0-"

    authenticator = IAMAuthenticator(api_key)
    nlu = NaturalLanguageUnderstandingV1(
        version='2022-04-07',
        authenticator=authenticator
    )
    nlu.set_service_url(url)

    try:
        response = nlu.analyze(
            text = text,
            features=Features(sentiment=SentimentOptions())).get_result()

        return response["sentiment"]["document"]['label']
    except:
        print("Network exception occurred")
        return ""