from django.db import models
from django.contrib.auth.models import PermissionsMixin, AbstractBaseUser, BaseUserManager

from django.utils import timezone


class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password= None, **other_fields):
        email = self.normalize_email(email)
        user = self.model(email= email, username= username, **other_fields)
        user.set_password(password)
        user.save()
        return user
        
    def create_superuser(self, email, username ,password,**other_fields):
        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_active', True)
        other_fields.setdefault('is_superuser', True)
        
        return self.create_user(email, username, password,**other_fields)
        


class User(AbstractBaseUser, PermissionsMixin):
    email = models.CharField(unique=True, blank=False , max_length=200)
    username = models.CharField(unique=True, blank=False, max_length=200)
    fullname = models.CharField(blank=True, null=True ,max_length=200)
    profile_picture = models.ImageField(upload_to='profile', null=True, blank= True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_banned = models.BooleanField(default= False)
    last_login =models.TimeField(auto_now=True, blank=True, null=True)
    start_date = models.TimeField(default=timezone.now)
    
    
    

    
    
    def __str__(self):
        return f"Username : {self.username}"
    
    
    
    USERNAME_FIELD = 'email'
    
    REQUIRED_FIELDS = ['username']
    
    
    objects = CustomUserManager()


class Follow(models.Model):
    user =   models.ForeignKey(User, on_delete=models.CASCADE,null=True, blank=True , related_name='following')   
    follower_id = models.ForeignKey(User, on_delete=models.CASCADE, blank=True , related_name='follower')
    created = models.DateTimeField(auto_now_add=True , db_index=True) 
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'follower_id'], name='unique_follower')
        ]
        
        ordering = ['-created'] 


    
# Create your models here.
class TaggedTopics(models.Model):
    name = models.CharField(max_length=100 , blank=True)   
    
    

class Pin(models.Model):
    image = models.ImageField(upload_to='posts', blank=True)
    Dimentions_height = models.IntegerField(blank=True, null= True)
    Dimentions_width = models.IntegerField(blank=True, null= True)
    title = models.CharField(max_length= 200 , blank=True , null=True)
    description = models.TextField(max_length=500 ,blank= True, null= True)
    link = models.CharField(max_length=500 , blank=True , null= True)
    creater = models.ForeignKey(User, on_delete=models.CASCADE)
    topics = models.ForeignKey('TaggedTopics', null=True, blank=True ,on_delete=models.CASCADE)
    modification_date = models.TimeField(auto_now_add=True)
    
 
class SavedPins(models.Model):
    pin = models.ForeignKey(Pin, on_delete=models.CASCADE)
    saved_by = models.ForeignKey(User, on_delete=models.CASCADE , blank=True)

class UsersReview(models.Model):
    comments = models.TextField(max_length=500, blank=True)
    likes = models.IntegerField(default=0)
    pin = models.ForeignKey(Pin, on_delete=models.CASCADE)