from rest_framework.views import APIView
from django.shortcuts import render,redirect
import requests ,json ,math
from adminuser.models import Recipe,Category, User,Ingredient, Recipe_Ingredient
from recipe.pagination import PagePaginationAdmin
from adminuser.serializer import RecipeListSerializer,Recipe_IngredientSerializer
from rest_framework.response import Response
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.permissions import IsAdminUser
from django.contrib import messages




class ListRecipe(LoginRequiredMixin,APIView):
    permission_classes =[IsAdminUser]
    def get(self,request):
        try:
            name=request.GET.get("search_data","")
            recipe=Recipe.objects.filter(name__icontains=name).order_by("-id")
            paginator = PagePaginationAdmin()
            results = paginator.paginate_queryset(recipe , request , view=self)
            serializer= RecipeListSerializer(results ,many=True)

            page_number=request.GET.get("page","1")
            data = paginator.get_paginated_response(serializer.data).data
            data["page"]=page_number
            data["last_page"]=math.ceil(recipe.count()/paginator.get_page_size(request))

            for item in data['results']:
                if item['thumbnail'].startswith("/http"):
                    item['thumbnail'] = item['thumbnail'][1:]
                    item['thumbnail'] = item['thumbnail'].replace("%3A",":/")
                else:
                    pass
            return render(request,"recipe/recipe.html" ,{'data': data})
            # return Response(data)
        except Exception as e:
            # return Response(str(e))
            return render(request,"recipe/recipe.html" ,{'data': str(e)})





class AddRecipe(LoginRequiredMixin,APIView):
    permission_classes =[IsAdminUser]
    def get(self, request):
        return render(request, "recipe/add_recipe.html")

    def post(self, request):
        try:
             
            #search by name
            data1=requests.get(f"https://www.themealdb.com/api/json/v1/1/search.php?s={request.data['mainIngredient']}") 
            #search by ingredient
            data = requests.get(f"https://www.themealdb.com/api/json/v1/1/filter.php?i={request.data['mainIngredient']}")
            data1 = json.loads(data1.content) 
            data = json.loads(data.content)   
            data1['search_item']=request.data['mainIngredient']
            try:
                for items in data["meals"]:
                    data1["meals"].append(items)
            except Exception as e:
                pass
            recipes= Recipe.objects.values_list("idMeal",flat=True)
            for item in data1["meals"]:
                if item["idMeal"] in recipes:
                    item["exists"]=True
                else:
                    item["exists"]=False


            return render(request, "recipe/add_recipe.html", {'data': data1})
        except Exception as e:
            return render(request, "recipe/add_recipe.html")




# recipe description


class Description(LoginRequiredMixin,APIView):
    permission_classes =[IsAdminUser]
    def get(self, request):
        try:
            item = request.GET.get("search_item")
            recipedata = requests.get(
                f"https://www.themealdb.com/api/json/v1/1/filter.php?i={item}")
            recipedata = json.loads(recipedata.content)

            id = request.GET.get("idMeal")
            data = requests.get(
                f'https://www.themealdb.com/api/json/v1/1/lookup.php?i={id}')
            data = json.loads(data.content)
            data = data['meals'][0]
            ingredient = {}
            for num in range(1,21):
                item1 = "strIngredient"+str(num)
                item2 = "strMeasure"+str(num)
                if data[item1] and data[item2]:
                    ingredient[data[item1]]=data[item2]
                else:
                    pass
            data["ingredient"] = ingredient
            try:
                data["searchMeals"] = recipedata["meals"][0:5]
            except Exception as e:
                pass
            return render(request, "recipe/recipe_description.html", {"data": data})
        except Exception as e :
            return render(request, "recipe/recipe_description.html", {"errors": str(e)})






class AddRecipeToDB(LoginRequiredMixin,APIView):
    permission_classes =[IsAdminUser]
    def get(self, request):
        try:
            id = request.GET.get("idMeal")
            data = requests.get(
                f'https://www.themealdb.com/api/json/v1/1/lookup.php?i={id}')
            data = json.loads(data.content)
            data = data['meals'][0]
            recipe = Recipe.objects.filter(idMeal=id)

            if recipe:
                messages.success(request, "Recipe already exists, Try another recipe")
                return redirect('/adminuser/add/recipe/')
            else:
                try:
                    Category.objects.create(name = data['strCategory'] ,categoryImage = "/static/No_Image.jpg")
                except:
                    category_object = Category.objects.get(name=data['strCategory'])
                    recipe_object = Recipe.objects.create(name=data['strMeal'], thumbnail=data['strMealThumb'], idMeal=data['idMeal'], is_approved=True, user=User.objects.filter(roles__name="admin").first(), category=category_object,description=data['strInstructions'],youtube_link=data['strYoutube'],is_active=True)
                    for num in range(1,21):
                        item1 = "strIngredient"+str(num)
                        item2 = "strMeasure"+str(num)

                        if data[item1] and data[item2]:
                            ingredient=Ingredient.objects.filter(name=data[item1])[0]

                            if ingredient:
                                Recipe_Ingredient.objects.create(ingredient=ingredient,recipe=recipe_object,quantity= data[item2])
                            else:
                                ingredient = Ingredient.objects.create(name = data[item1], image = "/static/No_Image.jpg")
                                Recipe_Ingredient.objects.create(ingredient=ingredient,recipe=recipe_object,quantity= data[item2])      
                        else:
                            pass
                    messages.success(request, "Recipe added successfully !!!")
                    return redirect('/adminuser/recipe/')
                
        except Exception as e:
            print(str(e))
            return render(request, "recipe/recipe_description.html", {"errors": str(e)})






class DescriptionDB(LoginRequiredMixin,APIView):
    permission_classes =[IsAdminUser]
    def get(self, request):
        try:
            id = request.GET.get("id")
            recipe = Recipe.objects.get(id=id)
            serializer = Recipe_IngredientSerializer(recipe)

            item = serializer.data
            if item['thumbnail'].startswith("/http"):
                item['thumbnail'] = item['thumbnail'][1:]
                item['thumbnail'] = item['thumbnail'].replace("%3A", ":/")
            else:
                pass
          
            similar_recipe = Recipe.objects.filter(category__name = item['category']).order_by("?")[:6]
            
            serializer2 = RecipeListSerializer(similar_recipe, many=True)
            for item2 in serializer2.data:
                if item2['thumbnail'].startswith("/http"):
                    item2['thumbnail'] = item2['thumbnail'][1:]
                    item2['thumbnail'] = item2['thumbnail'].replace("%3A", ":/")
                else:
                    pass



            try:
                item['similar_items']=serializer2.data
            except Exception as e:
                pass       
            return render(request, "recipe/recipe_descriptionDB.html", {"data": item})
        
        except Exception as e:
            return render(request, "recipe/recipe_descriptionDB.html", {"errors": str(e)})









class DeleteRecipe(LoginRequiredMixin,APIView):
    permission_classes =[IsAdminUser]
    def get(self,request):
        id = request.GET.get("id")


        recipeObj=Recipe.objects.get(id=id)
        if recipeObj.is_active==True:

            recipeObj.is_active=False
            recipeObj.save()
        else:
            recipeObj.is_active=True
            recipeObj.save()
        return redirect(f"/adminuser/recipe/description/?id={id}")