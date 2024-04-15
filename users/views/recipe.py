from rest_framework.views import APIView
from django.shortcuts import render, redirect
from adminuser.models import Category, Reports, CommentsLike, CommentsDislike, Comments, Rating, Recipe, Favourites, Request, Recipe_Ingredient, Ingredient
from adminuser.serializer import CategorySerializer, Recipe_IngredientSerializer
from users.serializer import RequestSerializer, RecipeListSerializer, CreateRecipeSerializer, FavouritesSerializer
from django.contrib.auth.mixins import LoginRequiredMixin
from recipe.pagination import PagePagination
from django.contrib import messages
from users.tasks import send_email_task
from recipe.settings import EMAIL_HOST_USER
from django.template.loader import render_to_string
from django.core.mail import send_mail
# from adminuser.documents import RecipeDocument
from elasticsearch_dsl import Search
from decouple import config
from twilio.rest import Client
from django.db.models import Q

import math


class Home(APIView):
    
    def get(self, request):
        try:
            data = {}
            ######## category ########
            category = Category.objects.filter(is_active=True).values().order_by("?")
            for items in category:
                if str(items["categoryImage"]).startswith("static"):
                    items["categoryImage"] = "/" + str(items["categoryImage"])
            data["category"] = category

            trending_recipe = Recipe.objects.filter(is_approved=True, is_active=True).order_by('-calculated_rating').values("id", "name", "thumbnail")[:5]
            for k in trending_recipe:
                if k['thumbnail'].startswith('static'):
                    k['thumbnail'] = '/' + k['thumbnail']



            recipe = Recipe.objects.filter(is_approved=True, is_active=True).order_by('?').values("id", "name", "thumbnail")
            for k in recipe:
                if k['thumbnail'].startswith('static'):
                    k['thumbnail'] = '/' + k['thumbnail']
            paginator = PagePagination()
            results = paginator.paginate_queryset(recipe, request, view=self)
            paginated_data = paginator.get_paginated_response(results).data
            data["recipe"] = paginated_data
            page_number = request.GET.get("page", "1")
            data["recipe"]["page"] = page_number
            data["recipe"]["last_page"] = math.ceil(
                recipe.count()/paginator.get_page_size(request))

            return render(request, "users/home.html", {"data": data,"trending_recipe":trending_recipe})
        except Exception as e:
            print(str(e))
            return render(request, "users/home.html", {"data": data})





############################ About Us ###################################

class AboutUs(APIView):
    def get(self, request):
            return render(request, "users/about_us.html")
       
        


class SearchRecipe(APIView):
    def get(self, request):
        try:
            name = request.GET.get("search_data", "")
            recipe = Recipe.objects.filter(Q(name__icontains=name,  is_active=True, is_approved=True)|Q(category__name__icontains=name,  is_active=True, is_approved=True)).order_by("-id")
            
            # recipe1 = RecipeDocument.search().query('prefix', name=name)
            # response = recipe1.execute()
            # for hit in response.hits:
            #     print(hit.to_dict())

            paginator = PagePagination()
            results = paginator.paginate_queryset(recipe, request, view=self)
            serializer = RecipeListSerializer(results, many=True)

            page_number = request.GET.get("page", "1")
            data = paginator.get_paginated_response(serializer.data).data
            data["search_data"] = name
            data["page"] = page_number
            data["last_page"] = math.ceil(
                recipe.count()/paginator.get_page_size(request))

            for item in data['results']:
                if item['thumbnail'].startswith("/http"):
                    item['thumbnail'] = item['thumbnail'][1:]
                    item['thumbnail'] = item['thumbnail'].replace("%3A", ":/")
                else:
                    pass
            return render(request, "users/search_recipe.html", {'data': data})
            # return Response(data)
        except Exception as e:
            # return Response(str(e))
            return render(request, "users/search_recipe.html", {'data': str(e)})



class SearchByCategory(APIView):
    def get(self, request):
        id = request.GET.get("categoryid")
        recipe = Recipe.objects.filter(category=id, is_approved=True, is_active=True).order_by('-id')

        paginator = PagePagination()
        results = paginator.paginate_queryset(recipe, request, view=self)
        serializer = RecipeListSerializer(results, many=True)

        page_number = request.GET.get("page", "1")
        data = paginator.get_paginated_response(serializer.data).data
        data["categoryid"] = id
        data["page"] = page_number
        data["last_page"] = math.ceil(
            recipe.count()/paginator.get_page_size(request))

        for item in data['results']:
            if item['thumbnail'].startswith("/http"):
                item['thumbnail'] = item['thumbnail'][1:]
                item['thumbnail'] = item['thumbnail'].replace("%3A", ":/")
            else:
                pass
        return render(request, "users/recipebycategory.html", {'data': data})




class RecipeDescription(LoginRequiredMixin, APIView):
    def get(self, request):
        try:
            id = request.GET.get("id")
            recipe = Recipe.objects.get(id=id)
            serializer = Recipe_IngredientSerializer(recipe)
            item = serializer.data
            item["isFavourite"] = Favourites.objects.filter(
                user=request.user, recipe=recipe)
            if item['thumbnail'].startswith("/http"):
                item['thumbnail'] = item['thumbnail'][1:]
                item['thumbnail'] = item['thumbnail'].replace("%3A", ":/")
            else:
                pass

            ############ similar-items ###############

            similar_recipe = Recipe.objects.filter(
                category__name=item['category']).exclude(id=id).order_by("?")[:5]
            serializer2 = RecipeListSerializer(similar_recipe, many=True)

            for items in serializer2.data:
                if items["thumbnail"]:
                    if items['thumbnail'].startswith("/http"):
                        items['thumbnail'] = items['thumbnail'][1:]
                        items['thumbnail'] = items['thumbnail'].replace(
                            "%3A", ":/")
            try:
                item['similar_items'] = serializer2.data
            except Exception as e:
                pass

            ############ Comments ###############

            comments = Comments.objects.filter(recipe=id)
            lst = []
            for k in comments:
                like_exist, dislike_exist = False, False
                for l in k.commentslike.all():
                    if l.user == request.user:
                        like_exist = True

                for m in k.commentsdislike.all():
                    if m.user == request.user:
                        dislike_exist = True

                lst.append({'comment': k, "like": like_exist,
                           "dislike": dislike_exist})

            return render(request, "users/description.html", {"data": item, "comment": lst})
        except Exception as e:
            print(str(e))
            return render(request, "users/description.html", {"errors": str(e)})


################################### FAVOURITE##################################


class AddFavourites(LoginRequiredMixin, APIView):
    def get(self, request):
        try:
            id = request.GET.get("id")
            user = request.user
            recipe = Recipe.objects.get(id=id)
            if Favourites.objects.filter(recipe__id=id,user =user):
                pass
            else:
                Favourites.objects.create(user=user, recipe=recipe)
            # return render(request,"users/search_recipe.html" ,{'data': id})
            return redirect(f"/recipe/description/?id={id}")
        except Exception as e:
            print(str(e))
            return render(request, "users/search_recipe.html", {'data': str(e)})


class ListFavourites(LoginRequiredMixin, APIView):
    def get(self, request):
        try:
            user = request.user.id
            data = Favourites.objects.filter(user=user)
            serializer = FavouritesSerializer(data, many=True)

            for item in list(serializer.data):
                if item['recipe']['thumbnail'].startswith("/http"):
                    item['recipe']['thumbnail'] = item['recipe']['thumbnail'][1:]
                    item['recipe']['thumbnail'] = item['recipe']['thumbnail'].replace(
                        "%3A", ":/")
            return render(request, "users/favourites.html", {'data': serializer.data})
        except Exception as e:
            return render(request, "users/favourites.html", {'data': str(e)})


class DeleteFavourites(LoginRequiredMixin, APIView):
    def get(self, request):
        try:
            id = request.GET.get("id")
            favourite_obj = Favourites.objects.get(id=id)
            favourite_obj.delete()
            return redirect("/favourites")
        except Exception as e:
            return render(request, "users/favourites.html", {'data': str(e)})


################################### CREATE RECIPE ##################################


class CreateRecipe(LoginRequiredMixin, APIView):
    def get(self, request):
        try:
            category = Category.objects.filter(is_active=True).values('id', 'name')
            return render(request, "users/create_recipe.html", {'data': category})
        except Exception as e:
            return render(request, "users/create_recipe.html", {'data': str(e)})

    def post(self, request):
        try:
            category = Category.objects.filter(is_active=True).values('id', 'name')
            ingredient = request.data.getlist('ingredient')
            quantity = request.data.getlist('quantity')

            serializer = CreateRecipeSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
            else:
                return render(request, "users/create_recipe.html", {'errors': serializer.errors})
            for i, j in zip(ingredient, quantity):
                if Ingredient.objects.filter(name=i):
                    ingredient_obj = Ingredient.objects.get(name=i)
                else:
                    ingredient_obj = Ingredient.objects.create(name=i)

                if not Recipe_Ingredient.objects.filter(ingredient=ingredient_obj, recipe=serializer.instance):
                    Recipe_Ingredient.objects.create(
                        ingredient=ingredient_obj, recipe=serializer.instance, quantity=j)
            template = render_to_string(
                "emailTemplates/email_Receipe_create.html", {"name": request.user.first_name})
            # send_email_task.delay('Hooray!!! Recipe Created', '', EMAIL_HOST_USER, [
            #                       request.user.username], template)

            send_mail(subject="Hooray!!! Recipe Created",message='',from_email=EMAIL_HOST_USER ,recipient_list=[request.user.username],html_message=template)


#             client = Client(config('TWILIO_ACCOUNT_SID'), config('TWILIO_AUTH_TOKEN'))
#             message = client.messages.create(
#                     body=f'''
# Hello {request.user.first_name},
# Thank you for creating the recipe : {request.data['name']} !!! 
# Your recipe has been forwarded to admin for review.
# We are looking forward for your future contributions.
# Have a good day!!!''',
#                     from_='+17622495195',
#                     to='+919815430168'
#                 )

            return render(request, "users/create_recipe.html", {'data': category, 'message': 'Request submitted Successfully'})
        except Exception as e:
            print(str(e))
            return render(request, "users/create_recipe.html", {'data': category, 'message': str(e),"values":request.data })



####################################### MyRecipes ######################################


class MyRecipes(LoginRequiredMixin, APIView):
    def get(self, request):
        try:
            user = request.user
            data = Recipe.objects.filter(user=user).order_by("-id")
            return render(request, "users/my_recipes.html", {'data': data})
            # return redirect(f"/recipe/description/?id={id}")
        except Exception as e:
            return render(request, "users/my_recipes.html", {'data': str(e)})


class MyRecipeDelete(LoginRequiredMixin, APIView):
    def get(self, request):
        try:
            id = request.GET.get("id")
            recipe_obj = Recipe.objects.get(id=id)
            recipe_ingredient_obj = Recipe_Ingredient.objects.filter(
                recipe=recipe_obj)
            recipe_ingredient_obj.delete()
            recipe_obj.delete()
            return redirect("/my_recipes/")
        except Exception as e:
            return render(request, "users/my_recipes.html", {'error': str(e)})


##################################### REQUEST RECIPE ###############################

class RequestRecipe(LoginRequiredMixin, APIView):
    def get(self, request):

        request_obj = Request.objects.filter(user=request.user)
        paginator = PagePagination()
        results = paginator.paginate_queryset(request_obj, request, view=self)
        serializer = RequestSerializer(results, many=True)
        page_number = request.GET.get("page", "1")
        data = paginator.get_paginated_response(serializer.data).data
        data["page"] = page_number
        data["last_page"] = math.ceil(
            request_obj.count()/paginator.get_page_size(request))
        return render(request, "users/request.html", {"data": data})

    def post(self, request):
        data = request.data
        Request.objects.create(
            user=request.user, name=data['name'], description=data['description'])
        messages.success(request, "Request submitted successfully!!!")
        return redirect("/request/")


class RequestDelete(LoginRequiredMixin, APIView):
    def get(self, request):
        try:
            id = request.GET.get("id")
            request_obj = Request.objects.get(id=id)
            # recipe_ingredient_obj = Recipe_Ingredient.objects.filter(recipe=recipe_obj)
            # recipe_ingredient_obj.delete()
            request_obj.delete()
            messages.success(request, "Request Deleted successfully!!!")
            return redirect("/request/")
        except Exception as e:
            return render(request, "users/request.html", {'error': str(e)})


############################ RATINGS ###################################

class GiveRating(LoginRequiredMixin, APIView):
    def post(self, request):
        try:
            data = request.data
            recipe = Recipe.objects.get(id=data['id'])
            Existing_rating = Rating.objects.filter(recipe=data['id'], user=request.user)
            if not Existing_rating:
                ratingToSave = Rating.objects.create(recipe=recipe, rating=int(data['star']), user=request.user)
                ratingToSave.save()
            else:
                Existing_rating.update(rating=int(data['star']))
                Existing_rating[0].save()
            return redirect(f"/recipe/description/?id={data['id']}")

        except Exception as e:
            return redirect(f"/recipe/description/?id={data['id']}")


############################ Report ###################################


class ReportRecipe(LoginRequiredMixin, APIView):
    def post(self, request):
        try:
            data = request.data
            recipe = Recipe.objects.get(id=data['id'])

            Existing_report = Reports.objects.filter(
                recipe=data['id'], user=request.user)
            if not Existing_report:
                Reports.objects.create(
                    recipe=recipe, description=data['description'], user=request.user)
            else:
                Existing_report.update(description=data['description'])
            return redirect(f"/recipe/description/?id={data['id']}")
        except Exception as e:
            return redirect(f"/recipe/description/?id={data['id']}")


############################ Comments ###################################


class CreateComment(LoginRequiredMixin,APIView):
    def post(self, request):
        try:
            recipe = Recipe.objects.get(id=request.data['recipe'])
            comments = Comments.objects.create(
                user=request.user, recipe=recipe, comment=request.data['comment'], likes=0, dislikes=0)
            return redirect(f"/recipe/description/?id={request.data['recipe']}#comments")
        except Exception as e:
            print(str(e))
            return redirect(f"/recipe/description/?id={request.data['recipe']}#comments")


class LikeComment(LoginRequiredMixin,APIView):
    def get(self, request):
        try:
            id = request.GET.get("id")
            comments_obj = Comments.objects.get(id=id)
            recipe_id = request.GET.get("recipe")

            if CommentsLike.objects.filter(user=request.user, comments=comments_obj, like=True):
                CommentsLike.objects.get(
                    user=request.user, comments=comments_obj, like=True).delete()
            else:
                CommentsLike.objects.create(
                    user=request.user, comments=comments_obj, like=True)

            return redirect(f"/recipe/description/?id={recipe_id}#comments")
        except Exception as e:
            print(str(e))
            return redirect(f"/recipe/description/?id={recipe_id}#comments")


class DislikeComment(LoginRequiredMixin,APIView):
    def get(self, request):
        try:
            id = request.GET.get("id")
            comments_obj = Comments.objects.get(id=id)
            recipe_id = request.GET.get("recipe")
            if CommentsDislike.objects.filter(user=request.user, comments=comments_obj, dislike=True):
                CommentsDislike.objects.get(
                    user=request.user, comments=comments_obj, dislike=True).delete()

            else:
                CommentsDislike.objects.create(
                    user=request.user, comments=comments_obj, dislike=True)

            return redirect(f"/recipe/description/?id={recipe_id}#comments")
        except Exception as e:
            print(str(e))
            return redirect(f"/recipe/description/?id={recipe_id}#comments")


class DeleteComment(LoginRequiredMixin,APIView):
    def get(self, request):
        try:
            id = request.GET.get("id")
            recipe_id = request.GET.get("recipe")
            if Comments.objects.filter(user=request.user):
                try:
                    CommentsLike.objects.get(comments=id).delete()
                    CommentsDislike.objects.get(comments=id).delete()
                except:
                    pass
                Comments.objects.get(id=id).delete()

            return redirect(f"/recipe/description/?id={recipe_id}#comments")
        except Exception as e:
            print(str(e))
            return redirect(f"/recipe/description/?id={recipe_id}#comments")



############################ Payment ###################################


class PaymentSuccess(LoginRequiredMixin, APIView):
    def get(self, request):
        try:
            return render(request, "users/payment_success.html")
        except Exception as e:
            return render(request, "users/payment_success.html", {'data': str(e)})




