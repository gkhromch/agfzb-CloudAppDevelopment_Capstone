from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import CarDealer, CarModel
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf, post_request, get_dealer_name_by_id
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import time
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


URL_GET_DEALERS = "https://eu-de.functions.appdomain.cloud/api/v1/web/f89e9565-488f-4043-9a66-2e3caf2fd23c/dealership-package/get-dealership"
URL_GET_REVIEWS = "https://eu-de.functions.appdomain.cloud/api/v1/web/f89e9565-488f-4043-9a66-2e3caf2fd23c/dealership-package/get-review"
URL_POST_REVIEW = "https://eu-de.functions.appdomain.cloud/api/v1/web/f89e9565-488f-4043-9a66-2e3caf2fd23c/dealership-package/post-review"

# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/about.html', context)


# Create a `contact` view to return a static contact page
def contact(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/contact.html', context)

# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    username = request.POST['username']
    password = request.POST['psw']
    user = authenticate(username=username, password=password)
    if user is not None:
        login(request, user)
        return redirect('djangoapp:index')
    else:
        context['message'] = "Invalid username or password."
        return render(request, 'djangoapp/index.html', context)


# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')


# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("djangoapp:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'djangoapp/registration.html', context)



# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
#    if request.method == "GET":
    dealerships = get_dealers_from_cf(URL_GET_DEALERS)

    context = {}
    context["dealers"] = dealerships
    return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
#    if request.method == "GET":
    reviews = get_dealer_reviews_from_cf(URL_GET_REVIEWS, dealer_id)

    context = {}
    context["reviews"] = reviews
    context["dealer_id"] = dealer_id
    context["dealer_name"] = get_dealer_name_by_id(URL_GET_DEALERS, dealer_id)
    return render(request, 'djangoapp/dealer_details.html', context)


# Create a `add_review` view to submit a review
def add_review(request, dealer_id):
    if not request.user.is_authenticated:
        return HttpResponse("Only authenticated users can leave reviews. Please log in.")
    
    context = {}
    context["dealer_id"] = dealer_id
    context["dealer_name"] = get_dealer_name_by_id(URL_GET_DEALERS, dealer_id)


    if request.method == "GET": #Get cars for the drop-down list
        cars = []
        car_models = CarModel.objects.filter(dealer_id=dealer_id)
        for car in car_models:
            cars.append(car)

        context["cars"] = cars
        return render(request, 'djangoapp/add_review.html', context)

    
    if request.method == "POST":
        review = {}
        purchase_check = request.POST.get('purchasecheck', False)

        review["dealership"] = dealer_id
        review["name"] = request.user.first_name + " " + request.user.last_name
        review["purchase"] = purchase_check
        review["review"] = request.POST['content']
        review["id"] = int(time.time())             #more or less unique id

        if purchase_check:
            review["purchase"] = True
            review["purchase_date"] = request.POST['purchasedate']
            if request.POST['car']:             
                car = CarModel.objects.get(id=request.POST['car'])
                review["car_model"] = car.name
                review["car_make"] = car.make.name

                date = datetime.strptime(request.POST['purchasedate'], "%Y-%m-%d")
                review["car_year"] = date.year
                print(date.year)

        json_payload = {"review": review}

        try:
            response = post_request(URL_POST_REVIEW, json_payload, dealerId=dealer_id)
            return redirect("djangoapp:dealer_details", dealer_id=dealer_id)
        except:
            return HttpResponse("Cannot submit the review")
            

