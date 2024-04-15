from django.contrib import admin
from django.urls import path, include
from users.views.userprofile import SignUp,Login ,ForgotPassword, ResetPassword, VerifyEmail ,LogOutUser ,Profile,EditProfile
from users.views.recipe import Home,AboutUs,PaymentSuccess, SearchByCategory,ReportRecipe,GiveRating,RequestRecipe,RequestDelete , MyRecipes,MyRecipeDelete, CreateRecipe,RecipeDescription,ListFavourites,SearchRecipe,AddFavourites, DeleteFavourites,CreateComment,LikeComment,DislikeComment,DeleteComment

urlpatterns = [
    path('signup/', SignUp.as_view()),
    path('', Login.as_view()),
    path('logout',LogOutUser.as_view()),
    path('forgotpassword',ForgotPassword.as_view()),
    path('resetpassword/<str:token>',ResetPassword.as_view()),

    path('user/verification/<str:code>',VerifyEmail.as_view()),
    
    
######################### Recipe ####################

    
    path('search/bycategory/',SearchByCategory.as_view()),
    path('home/',Home.as_view()),
    path('aboutus/',AboutUs.as_view()),
    path('recipe/description/',RecipeDescription.as_view()),
    path('search/recipe/',SearchRecipe.as_view()),
    path('add/tofavourite/',AddFavourites.as_view()),
    path('favourites/',ListFavourites.as_view()),
    path('favourites/delete/',DeleteFavourites.as_view()),
    path('create/recipe/',CreateRecipe.as_view()),
    path('my_recipes/',MyRecipes.as_view()),
    path('myrecipe/delete/',MyRecipeDelete.as_view()),
    path('request/',RequestRecipe.as_view()),
    path('delete/request/',RequestDelete.as_view()),
    path('recipe/giveRating/',GiveRating.as_view()),
    path('recipe/report/',ReportRecipe.as_view()),


######################### USER PROFILE ####################

    path('profile/',Profile.as_view()),
    path('profile/edit/',EditProfile.as_view()),

######################### COMMENTS ####################
    
    path('recipe/comment/',CreateComment.as_view()),
    path('recipe/comment/like/',LikeComment.as_view()),
    path('recipe/comment/dislike/',DislikeComment.as_view()),
    path('recipe/comment/delete/',DeleteComment.as_view()),


######################### PAYMENT ####################

    path('payment/success/',PaymentSuccess.as_view()),









]   