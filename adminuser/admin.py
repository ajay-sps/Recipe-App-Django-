from django.contrib import admin
from adminuser.models import Payments,CommentsDislike,CommentsLike,Comments,Favourites,Ingredient,Category,Recipe,Rating,Recipe_Ingredient,Reports,Request

admin.site.register(Ingredient)
admin.site.register(Category)
admin.site.register(Recipe)
admin.site.register(Rating)
admin.site.register(Recipe_Ingredient)
admin.site.register(Reports)
admin.site.register(Request)
admin.site.register(Favourites)
admin.site.register(Comments)
admin.site.register(CommentsLike)
admin.site.register(CommentsDislike)
admin.site.register(Payments)