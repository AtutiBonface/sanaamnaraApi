from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import get_user_model, authenticate
from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse
from .serializer import RegisterUserSerializer, LoginUserSerializer , PinSerializer , UsersReviewSerializer
from .models import Pin, UsersReview, SavedPins, Follow

## rest_framework  imports

from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token



# Create your views here.

User = get_user_model()

local_domain = 'http://localhost:4200/assets/posts/'
online_domain = 'im.imaginekenya.site/'

domain = f'{local_domain}'
def Index(request):
    return HttpResponse('Worked successfully!')

@csrf_exempt
def RegisterUser(request):
    
    if request.method == 'POST':
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        
        user_cred = {
            'email': email,
            'username': username,
            'password': password
        }
        
        serializer = RegisterUserSerializer(data= user_cred)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                token, created = Token.objects.get_or_create(user=user)
                message = {
                    'success': 'User created!'
                }
                return JsonResponse(message, safe=False, status= 201)
            
        else: 
            if  User.objects.filter(username = username).exists():
                message = {
                    'error': 'Username taken!'
                 }
                return JsonResponse(message, status=401)
                
            elif  User.objects.filter(email = email).exists():
                message = {
                    'error': 'Email is already registered!'
                 }
                
                return JsonResponse(message,  status=401)
            
            else:
                message = {
                    'error': 'Failed to register, try again!'
                }
                return JsonResponse(message, status=401)
                
        
    return HttpResponse('Wrong method used!',status=401)
    
@csrf_exempt
def LoginUser(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        
        if email and password:
            user = authenticate(email= email, password=password)
            if user:
                token, created = Token.objects.get_or_create(user=user)
                
                message = {
                    'access_token': token.key,
                    'username': user.username
                }
                return JsonResponse(message, safe=False, status= 200)
            else: 
                if User.objects.filter(email = email).exists():
                    message = {
                    'error': "Wrong password"
                    }
                    return JsonResponse(message, status= 401)
                if not User.objects.filter(email = email).exists():
                    message = {
                    'error': "User doesn't exist!"
                    }
                    return JsonResponse(message, status= 401)
        else:
            return HttpResponse("Wrong credentials!", status= 401)
            
    return HttpResponse("Wrong method used!", status= 401)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def PinsList(request,id=0, format=None):
    user_id = request.user.id
    if request.method == 'GET':
        pins  = Pin.objects.all().order_by('?')
        user = User.objects.get(id=request.user.id)
        saved_pins = SavedPins.objects.filter(saved_by=user)
        
        
        data = [{
            'id': value.id,
            'image': f'{domain}{value.image.url[73:]}',
            'description': value.description,
            'creater': value.creater.username,
            'creater_id': value.creater.id,
            'd_height': value.Dimentions_height,
            'd_width': value.Dimentions_width,
            'saved': next((True for i in saved_pins if i.pin.id == value.id),False)# return true if pin exists in saved pins if not the return false
        }for value in pins]
        
        
        
        
    
        return JsonResponse(data, safe=False)
    elif request.method == 'PUT':
        ## saving a  pin to logged user account
        try:
            user_id = request.user.id
            user = User.objects.get(id=user_id)
            pin_id = id  
            neededpin = Pin.objects.get(id=pin_id)
            if user and neededpin and not SavedPins.objects.filter(pin =neededpin , saved_by = user).exists():
                
                
                save_pin = SavedPins.objects.create(pin=neededpin , saved_by=user) 
                save_pin.save()
                
                return JsonResponse({'success': 'saved'}, safe=False, status=200)    
        except Pin.DoesNotExist:
            message = {'error': 'pin does not exist!'} 
            return JsonResponse(message, safe=False, status=404)                       
        
        else:
            return JsonResponse({'error': 'Failed!'}, safe=False, status=404)            
        
        
    return JsonResponse({'error': 'Wrong method!'}, safe=True, status=401)
@api_view(['POST','FILES'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def CreatePin(request, format=None):
    user_id = request.user.id
    image = request.FILES['image']
    title = request.POST['title']
    description = request.POST['description']
    link = request.POST['link']
    topics = request.POST['tagged_topics']
    image_dimensions = request.POST['dimensions']
    
    width, height = image_dimensions.split('x')
    
    
    creater = User.objects.get(id= user_id)
    
    if creater and image:    
        pins = Pin.objects.create(
            title=title,
            description=description,
            link=link,
            creater=creater,
            Dimentions_height = height,
            Dimentions_width = width,
        )
        pins.image = image    
        pins.save()
        return JsonResponse({'success' :'Added successfully'},safe=False , status = 200 )
    return JsonResponse({'error': 'failed'}, safe=True, status= 401)
    
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def IndividualPins(request, id=0):

    if request.method == 'PUT':    
        
        
        current_username = request.user.username
        newusername = request.POST.get('username')
        newuser = User.objects.get(username=newusername)
        logged_in_user = request.user
        savedpins = SavedPins.objects.filter(saved_by=logged_in_user)
        pins = Pin.objects.filter(creater=logged_in_user)
        
         
        
        created = Pin.objects.filter(id=id , creater = logged_in_user)
        if created:
            created.delete()
            
            no_of_pins = pins.count()
            saved_no = savedpins.count()
            user_pins = [
                {
                    'image_url': f'{domain}{post.image.url[73:]}',
                    'title': post.title,
                    'description': post.description,
                    'id': post.id,
                    'd_height': post.Dimentions_height,
                    'd_width': post.Dimentions_width,
                } for post in pins
            ]

            user_saved_pins = [
                {
                    'image_url': f'{domain}{post.pin.image.url[73:]}',
                    'title': post.pin.title,
                    'description': post.pin.description,
                    'id': post.id,
                    'd_height': post.pin.Dimentions_height,
                    'd_width': post.pin.Dimentions_width,
                   
                } for post in savedpins
            ]

           
            
            Data = {
                'current_user': newuser == logged_in_user,
                'pins_created': user_pins,
                'posts_no': no_of_pins,
                'saved_pins': user_saved_pins,
                'saved_no': saved_no
                
            }
            
            return JsonResponse(Data, safe=False,  status=200) 
        return JsonResponse({'error': 'Did not delete!'},safe=False,  status=404) 
    
@api_view(['PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])           
def PinsSaved(request, id=0):
    
    if request.method == 'PUT':
        
        current_username = request.user.username
        newusername = request.POST.get('username')
        newuser = User.objects.get(username=newusername)
        logged_in_user = request.user

        savedpins = SavedPins.objects.filter(saved_by=logged_in_user)
        saved_no = savedpins.count()
        pins = Pin.objects.filter(creater=logged_in_user)
        no_of_pins = pins.count()
           
        
        saved = SavedPins.objects.filter(id=id , saved_by = logged_in_user)
        if saved:
            saved.delete()
            
            user_pins = [
                {
                    'image_url': f'{domain}{post.image.url[73:]}',
                    'title': post.title,
                    'description': post.description,
                    'id': post.id,
                    'd_height': post.Dimentions_height,
                    'd_width': post.Dimentions_width,
                } for post in pins
            ]

            user_saved_pins = [
                {
                    'image_url': f'{domain}{post.pin.image.url[73:]}',
                    'title': post.pin.title,
                    'description': post.pin.description,
                    'id': post.id,
                    'd_height': post.pin.Dimentions_height,
                    'd_width': post.pin.Dimentions_width,
                    'pin_id': next((i.id for i in pins if i.id == post.pin.id), 0)
                } for post in savedpins
            ]

           
            
            Data = {
                'current_user': newuser == logged_in_user,
                'pins_created': user_pins,
                'posts_no': no_of_pins,
                'saved_pins': user_saved_pins,
                'saved_no': saved_no
                
            }
            
            return JsonResponse(Data, safe=False,  status=200) 
        
        
        return JsonResponse({'error': 'Did not delete!'},safe=False,  status=404) 
    



@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def profileUser(request):
    user = request.user.username
    if request.method == 'GET':
        if user:
            return JsonResponse({'username': user}, safe= False, status = 200)
        return JsonResponse({'error': "can't find user"} , safe=False, status = 404)
    
    # sends all the users Data eg pins , followers
    elif request.method == 'POST':
                
        try:
            current_username = request.user.username
            newusername = request.POST.get('username')
            newuser = User.objects.get(username=newusername)
            logged_in_user = request.user
            
            savedpins = SavedPins.objects.filter(saved_by=newuser)
            logged_user_pins = SavedPins.objects.filter(saved_by=logged_in_user)
            saved_no = savedpins.count()
            pins = Pin.objects.filter(creater=newuser)
            no_of_pins = pins.count()
            user_followers = Follow.objects.filter(user=newuser)
            user_following = Follow.objects.filter(follower_id=newuser)

            user_followers_count = user_followers.count()
            user_following_count = user_following.count()

            followers = [
                {
                    'username': i.follower_id.username,
                    'user_id': i.follower_id.id,
                    'model_id': i.id
                } for i in user_followers
            ]

            following = [
                {
                    'username': i.user.username,
                    'user_id': i.user.id,
                    'model_id': i.id
                } for i in user_following
            ]

            user_pins = [
                {
                    'image_url': f'{domain}{post.image.url[73:]}',
                    'title': post.title,
                    'description': post.description,
                    'id': post.id,
                    'd_height': post.Dimentions_height,
                    'd_width': post.Dimentions_width,
                    'saved': next((True for i in logged_user_pins if i.pin.id == post.id),False)
                } for post in pins
            ]

            user_saved_pins = [
                {
                    'image_url': f'{domain}{post.pin.image.url[73:]}',
                    'title': post.pin.title,
                    'description': post.pin.description,
                    'id': post.id,
                    'd_height': post.pin.Dimentions_height,
                    'd_width': post.pin.Dimentions_width,
                    'saved': next((True for i in logged_user_pins if i.pin.id == post.id),False)
                } for post in savedpins
            ]

            Data = {
                'current_user': newuser == logged_in_user,
                'follower_no': user_followers_count,
                'following_no': user_following_count,
                'followers': followers,
                'following': following,
                'pins_created': user_pins,
                'posts_no': no_of_pins,
                'saved_pins': user_saved_pins,
                'saved_no': saved_no
                
            }
        except User.DoesNotExist:
            
            error_message = f"User with username  does not exist."
            return JsonResponse({'error': error_message}, status=404)

        return JsonResponse(data=Data, safe=False, status=200)
        
        
        
@csrf_exempt
def UsersReviewsView(request):
    if request.method == 'GET':
        reviews = UsersReview.objects.all()
        
       
        serializer = UsersReviewSerializer(reviews, many=True)
        
        return HttpResponse('Valid!')
       
        
    return HttpResponse('Wrong method!')
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def AllSerches(request):
    pins = Pin.objects.all().order_by('?')
    
    list = [
        {
            'id': post.id,
            'title': post.title,
            'description': post.description,
        }
        for post in pins]
    return JsonResponse(list, safe=False, status=200)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def popularSerches(request):
    return JsonResponse({'succss': 'Success'}, safe=False, status=200)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def recentSerches(request):
    return JsonResponse({'succss': 'Success'}, safe=False, status=200)



@api_view(['GET', 'POST', 'PUT'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def FollowUser(request):
    user_id = request.user.id
    if request.method == 'POST': 
        ## checkout of frontend only due to the Post selleted the owner is determined here     
        
        user = User.objects.get(id = user_id)
        
        pin_id = request.POST['post_id'] 
        
         
        
        pin = Pin.objects.get(id = pin_id) 
        
        owner = pin.creater  
        
        
        followers = Follow.objects.filter(user=owner)## they follow user
        follower_count = followers.count()
        
        following = Follow.objects.filter(follower_id=owner)
        following_count = following.count()
        
        follower_list = [ {
            'username': i.follower_id.username,
            'id': i.id
        }for i in followers ]
        
        following_list = [ {
            'username': i.user.username,
            'id': i.id
        }for i in following ]
        
        result = {
            'followers':follower_list,
            'following': following_list,
            'followers_count': follower_count,
            'following_count': following_count
            }
        
        return JsonResponse(result, status=200, safe=False)
    
    elif request.method == 'GET':
        user = User.objects.get(id = user_id)

        followers = Follow.objects.filter(user=user)## they follow user
        follower_count = followers.count()
        
        following = Follow.objects.filter(follower_id=user)
        following_count = following.count()
        
        follower_list = [ {
            'username': i.follower_id.username,
            'id': i.id
        }for i in followers ]
        
        following_list = [ {
            'username': i.user.username,
            'id': i.id
        }for i in following ]
        
        result = {
            'followers':follower_list,
            'following': following_list,
            'followers_count': follower_count,
            'following_count': following_count
            }
        
        return JsonResponse(result, status=200, safe=False)
    
    elif request.method == 'PUT':
        user_id = request.user.id
        
        user = User.objects.get(id = user_id)        
        follow_unfollow_id = request.POST['follow_id']
        
        user2 = User.objects.get(id = follow_unfollow_id)
                
        
        follow = Follow.objects.create(user=user2 ,follower_id=user)
        
        if follow.exists():
            follow.delete()
            
            return JsonResponse({'success':'Unfollowed!'}, safe=False, status = 200)    
            
        else:
            f = Follow.objects.create(user=user2 ,follower_id=user)        
            f.save()  
            return JsonResponse({'success':'Following'}, safe=False, status = 200)             
        
        return JsonResponse({'success':'Done'}, safe=False, status = 200)        
        
    else:
        
        return JsonResponse({'error':'Wrong method!'}, safe=False, status = 403)
        
    
