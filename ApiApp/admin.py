from django.contrib import admin
from .models import User ,Pin , UsersReview , SavedPins , Follow

admin.site.register(User)
admin.site.register([Follow, UsersReview, Pin , SavedPins])

# Register your models here.
