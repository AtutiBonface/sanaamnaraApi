from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static

from . import views


urlpatterns = [
    path('',views.Index, name='index'),
    path('accounts/register/', views.RegisterUser,),
    path('accounts/login/', views.LoginUser,),
    path('accounts/users', views.profileUser),#logged in user's profile
    path('accounts/follow', views.FollowUser,),
    path('pins/list', views.PinsList),
    path('pins/list/<int:id>', views.PinsList),#save pin
    path('pins/create', views.CreatePin),#create
    path('pins/owner', views.IndividualPins),
    path('pins/owner/<int:id>', views.IndividualPins), #delete   
    path('pins/saved', views.PinsSaved),
    path('pins/saved/<int:id>', views.PinsSaved),#delete
    path('pins/search', views.AllSerches),
    path('pins/popular-searches', views.popularSerches),
    path('pins/recent-searches', views.recentSerches),
    path('pins/reviews', views.UsersReviewsView),
    
]
urlpatterns += static(settings.MEDIA_URL , document_root =settings.MEDIA_ROOT)