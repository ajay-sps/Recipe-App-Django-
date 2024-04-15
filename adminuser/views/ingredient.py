from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from adminuser.serializer import IngredientSerializer
from adminuser.models import Ingredient
from django.contrib import messages
from django.shortcuts import redirect
from recipe.pagination import PagePagination
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.permissions import IsAdminUser
import requests
import json
import math

        

# class ListIngredient(LoginRequiredMixin,APIView):
    # permission_classes =[IsAdminUser]
  
#     def get(self,request):        
#         try:
#             name=request.GET.get("search_data" , "")
#             ingredient=Ingredient.objects.filter(name__icontains=name)
#             paginator = PagePagination()
#             results = paginator.paginate_queryset( ingredient , request , view=self)
#             serializer= IngredientSerializer(results ,many=True)
#             page_number=request.GET.get("page","")
#             data = paginator.get_paginated_response(serializer.data).data
#             data["page"]=page_number
#             data["last_page"]=math.ceil(ingredient.count()/paginator.get_page_size(request))
            
#             return render(request,"ingredient/ingredient.html" ,{'data':data})
#         except Exception as e:
#             # return Response(str(e))
#             return render(request,"ingredient/ingredient.html" ,{'errors':str(e)})


class ListIngredient(LoginRequiredMixin,APIView):
    permission_classes =[IsAdminUser]
  
    def get(self,request):        
        try:
            name=request.GET.get("search_data" , "")
            ingredient = Ingredient.objects.filter(name__icontains=name).order_by("-is_active")
            serializer = IngredientSerializer(ingredient , many=True)
            for index, item in enumerate(serializer.data):
                item['srno'] = index+1
            paginator = PagePagination()
            results = paginator.paginate_queryset( serializer.data , request , view=self)
            page_number=request.GET.get("page","1")
            data = paginator.get_paginated_response(results).data
            data["page"]=page_number
            data["last_page"]=math.ceil(ingredient.count()/paginator.get_page_size(request))

            return render(request,"ingredient/ingredient.html" ,{'data':data})
        except Exception as e:
            return render(request,"ingredient/ingredient.html" ,{'errors':str(e)})



class AddIngredient(LoginRequiredMixin,APIView):
    permission_classes =[IsAdminUser]
    def get(self,request):
        ingredient=Ingredient.objects.all()
        serializer= IngredientSerializer(ingredient ,many=True)
        return render(request,"ingredient/add_ingredient.html" ,{'data': serializer.data})
    

    
    def post(self,request):
        try:
            data = {
                    "name": request.data["ingredient_name"],
                    "image": request.data["ingredient_image"]               
                }
            serializer=IngredientSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                messages.success(request, f"ingredient '{data['name']}' created Successfully!!!")
                return redirect ('/adminuser/add/ingredient/')
            else:
                return render(request, "ingredient/add_ingredient.html", {"errors": serializer.errors})    
        except Exception as e:
            return render(request, 'ingredient/add_ingredient.html', {"errors": str(e)})


class FetchIngredient(LoginRequiredMixin,APIView):
    permission_classes =[IsAdminUser]
    def get(self,request):        
        try:
            apidata = requests.get("http://www.themealdb.com/api/json/v1/1/list.php?i=list")   
            apidata = json.loads(apidata.content)
            data=apidata['meals']
            count=0
            for items in data:
                if not Ingredient.objects.filter(id_ingrediant=items["idIngredient"]):
                    count += 1
                    image_url = f"http://www.themealdb.com/images/ingredients/{items['strIngredient']}.png"

                    Ingredient.objects.create(name=items["strIngredient"],image=image_url,id_ingrediant=items["idIngredient"])
                    
            messages.success(request, f"{count} Ingredients added")
            return redirect('/adminuser/ingredient/')
  
        except Exception as e:
            return render(request, 'ingredient/add_ingredient.html', {"errors": str(e)})






class DeleteIngredient(LoginRequiredMixin,APIView):
    permission_classes =[IsAdminUser]
    def get(self,request,id):
        item=Ingredient.objects.get(id=id)
        if item.is_active:
            item.is_active=False
        else:
            item.is_active=True
        item.save()
        return redirect ('/adminuser/ingredient/')


class UpdateIngredient(LoginRequiredMixin,APIView):
    permission_classes =[IsAdminUser]
    def get(self, request, id):
        ingredient = Ingredient.objects.get(id=id)
        serializer = IngredientSerializer(ingredient)
        return render(request, "ingredient/update_ingredient.html", {"formdata": serializer.data})


    def post(self, request, id):      
        try:
            data={
                "name":request.data['ingredient_name'],
                "image":request.data['ingredient_image'],
            }


            ingredient = Ingredient.objects.get(id=id)
            serializer = IngredientSerializer(ingredient, data)

            if serializer.is_valid():
                serializer.save()
                messages.success(request,"ingredient Updated Successfully")
                return redirect ('/adminuser/ingredient/')
            else:
                return render(request, 'ingredient/add_ingredient.html', {"errors": serializer.errors})

        except Exception as e:
                return render(request, 'ingredient/add_ingredient.html', {"errors": serializer.errors})
