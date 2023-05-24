from django.db import models
from django.utils.timezone import now


# Create your models here.

class CarMake(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    
    def __str__(self):
        return self.name + " : " + self.description


class CarModel(models.Model):
    T_SEDAN = 'Sedan'
    T_SUV = 'SUV'
    T_WAGON = 'Wagon'
    T_RV = 'RV'
    TYPE_OPTIONS = [
        (T_SEDAN, 'Sedan'),
        (T_SUV, 'Sport Utility Vehicle'),
        (T_WAGON, 'Wagon'),
        (T_RV, 'Recreational Vehicle')
    ]

    make = models.ForeignKey(CarMake, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    dealer_id = models.IntegerField()
    type = models.CharField(
        max_length = 30,
        choices = TYPE_OPTIONS,
        default = T_SEDAN
    )
    year = models.DateField()

    def __str__(self):
        return  (self.make.name + " : " if self.make is not None else "") + self.name


# <HINT> Create a plain Python class `CarDealer` to hold dealer data
class CarDealer:
    def __init__(self, address, city, full_name, id, lat, long, short_name, st, state, zip):
        self.address = address
        self.city = city
        self.full_name = full_name
        self.id = id
        self.lat = lat
        self.long = long
        self.short_name = short_name
        self.st = st
        self.state = state
        self.zip = zip

    def __str__(self):
        return "Dealer name: " + self.full_name

# <HINT> Create a plain Python class `DealerReview` to hold review data
class DealerReview:
    def __init__(self, dealership, name, purchase, review, purchase_date, car_make, car_model, car_year, id, sentiment): 
        self.dealership = dealership
        self.name = name
        self.purchase = purchase
        self.review = review
        self.purchase_date = purchase_date
        self.car_make = car_make
        self.car_model = car_model
        self.car_year = car_year
        self.id = id
        self.sentiment = sentiment
    
    def __str__(self):
        return "Review by " + self.name + ": " + self.review