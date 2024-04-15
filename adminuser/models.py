from typing import Any, Dict, Iterable, Optional, Tuple
from django.db import models
from users.models import User
from django.utils import timezone




class Ingredient(models.Model):
    name = models.CharField(max_length=255, unique=True)
    image = models.ImageField(upload_to='static/ingredients/',null=True)
    id_ingrediant = models.CharField(max_length=255, null=True, blank = True )
    is_active =models.BooleanField(default=True)



class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    categoryImage = models.ImageField(upload_to='static/category/', null=True)
    description = models.TextField(null=True, blank=True)
    is_active =models.BooleanField(default=True)
    
    def __str__(self) -> str:
        return self.name



class Recipe(models.Model):
    name = models.CharField(max_length=255)
    thumbnail = models.ImageField(upload_to='static/thumbnails/')
    idMeal = models.CharField(max_length=255,null=True)
    calculated_rating = models.FloatField(default = 0)
    is_approved = models.BooleanField(default=0)
    user = models.ForeignKey(User, null=True ,blank=True, related_name= 'recipe',on_delete=models.PROTECT)
    category = models.ForeignKey(Category, null=True ,blank=True ,related_name= 'recipe',on_delete=models.PROTECT)
    description = models.TextField()
    youtube_link = models.CharField(max_length=255, null=True)
    dateModified =models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default = True)



class Rating(models.Model):
    recipe = models.ForeignKey(Recipe, null=True ,blank=True ,related_name= 'rating',on_delete=models.PROTECT)
    rating = models.IntegerField(choices=[(1,1),(2,2),(3,3),(4,4),(5,5)])
    user = models.ForeignKey(User, related_name='rating', on_delete=models.PROTECT)


    def save(self,*args,**kwargs):
        sum=0
        ratings = Rating.objects.filter(recipe = self.recipe)
        if ratings:
            for item in ratings:
                sum = (sum+item.rating)
            sum = sum/len(ratings)
        else:
            sum=self.rating
        recipe = Recipe.objects.get(id = self.recipe.id)
        recipe.calculated_rating = round(sum,1)
        recipe.save()
        return super().save(*args,**kwargs)



class Recipe_Ingredient(models.Model):
    ingredient = models.ForeignKey(Ingredient, null=True ,blank=True ,related_name = 'recipe_Ingredient',on_delete=models.PROTECT)
    recipe = models.ForeignKey(Recipe, null=True ,blank=True ,related_name = 'recipe_Ingredient',on_delete=models.PROTECT)
    quantity = models.CharField(max_length=255)



class Reports(models.Model):
    user = models.ForeignKey(User, null=True ,blank=True ,related_name= 'reports',on_delete=models.PROTECT)
    recipe = models.ForeignKey(Recipe, null=True ,blank=True ,related_name= 'reports',on_delete=models.PROTECT)
    description= models.CharField(max_length=255)
    status = models.CharField(max_length=255 ,default="Pending")
    creation_date = models.DateField(default=timezone.now)




class Request(models.Model):
    user = models.ForeignKey(User,related_name= 'request',on_delete=models.PROTECT)
    name = models.CharField(max_length=255)
    description= models.CharField(max_length=255)
    status = models.CharField(max_length=255 ,default="Pending")
    creation_date = models.DateField(default=timezone.now)



class Favourites(models.Model):
    user = models.ForeignKey(User, null=True ,blank=True ,related_name = 'favourites',on_delete=models.PROTECT)
    recipe = models.ForeignKey(Recipe, null=True ,blank=True ,related_name = 'favourites',on_delete=models.PROTECT)



############################## COMMENTS ######################################

class Comments(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT ,related_name="comments")
    recipe = models.ForeignKey(Recipe, on_delete=models.PROTECT , related_name="comments")
    comment = models.CharField(max_length=3500)
    likes = models.IntegerField()
    dislikes =models.IntegerField()
    creation_date = models.DateField(default=timezone.now)


class CommentsLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT ,related_name="commentslike")
    comments = models.ForeignKey(Comments, on_delete=models.PROTECT , related_name="commentslike")
    like = models.BooleanField()

    def save(self,*args,**kwargs):
        comments = Comments.objects.get(id = self.comments.id)
        comments.likes = comments.likes + 1
        comments.save()
        return super().save(*args,**kwargs)
    
    def delete(self,*args,**kwargs):
        comments = Comments.objects.get(id = self.comments.id)
        comments.likes = comments.likes - 1
        comments.save()
        return super().delete(*args,**kwargs)
    
class CommentsDislike(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT ,related_name="commentsdislike")
    comments = models.ForeignKey(Comments, on_delete=models.PROTECT , related_name="commentsdislike")
    dislike = models.BooleanField()

    def save(self,*args,**kwargs):
        comments = Comments.objects.get(id = self.comments.id)
        comments.dislikes = comments.dislikes + 1
        comments.save()
        return super().save(*args,**kwargs)
    
    def delete(self,*args,**kwargs):
        comments = Comments.objects.get(id = self.comments.id)
        comments.dislikes = comments.dislikes - 1
        comments.save()
        return super().delete(*args,**kwargs)
    
    

class Payments(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT ,related_name="payments")
    Amount = models.IntegerField()
    date = models.DateField(default=timezone.now)
    payment_intent= models.CharField(max_length=3500)



