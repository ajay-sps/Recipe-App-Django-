from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from adminuser.serializer import CategorySerializer
from adminuser.models import Category
from django.contrib import messages
from django.shortcuts import redirect
from recipe.pagination import PagePagination
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.permissions import IsAdminUser
import requests
import json
import math




class ListCategory(LoginRequiredMixin,APIView):
    permission_classes =[IsAdminUser]
    def get(self,request):
        try:

            name=request.GET.get("search_data","")
            category=Category.objects.filter(name__icontains=name).order_by("-is_active")
            serializer= CategorySerializer(category ,many=True)
            for index, item in enumerate(serializer.data):
                item['srno'] = index+1

            paginator = PagePagination()
            results = paginator.paginate_queryset( serializer.data , request , view=self)
            page_number=request.GET.get("page","1")
            data = paginator.get_paginated_response(results).data
            data["page"]=page_number
            data["last_page"]=math.ceil(category.count()/paginator.get_page_size(request))
            
            for item in results:
                if item['categoryImage'].startswith("/http"):
                    item['categoryImage'] = item['categoryImage'][1:]
                    item['categoryImage'] = item['categoryImage'].replace("%3A",":/")
                else:
                    pass
            return render(request,"category.html" ,{'data': data})
        except Exception as e:
            return Response(str(e))




class AddCategory(LoginRequiredMixin,APIView):
    permission_classes =[IsAdminUser]
    def get(self,request):
        return render(request,"add_del_category.html")

    
    def post(self,request):
        try:
        
            data = {
                    "name": request.data["category_name"],
                    "categoryImage": request.data["category_image"]               
                }
            serializer=CategorySerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                messages.success(request, f"Category '{data['name']}' created Successfully!!!")
                return redirect ('/adminuser/add/category/')
            else:
                return render(request, "add_del_category.html", {"errors": serializer.errors})    
        except Exception as e:
            return Response(str(e))


class FetchCategory(LoginRequiredMixin,APIView):
    permission_classes =[IsAdminUser]
    def get(self,request):
        
        try:
            apidata = requests.get("https://www.themealdb.com/api/json/v1/1/categories.php")   
            apidata = json.loads(apidata.content)
            data=apidata['categories']
            count=0
            for items in data:
                category=Category.objects.filter(name=items["strCategory"])
                if category:
                    pass
                else:
                    count += 1
                    Category.objects.create(name=items["strCategory"],categoryImage=items["strCategoryThumb"])
            messages.success(request, f"{count} Categories added")
            return redirect ('/adminuser/category/')
  
        except Exception as e:
            return Response(str(e))






class DeleteCategory(LoginRequiredMixin,APIView):
    permission_classes =[IsAdminUser]
    def get(self,request,id):
        item=Category.objects.get(id=id)
        if item.is_active:
            item.is_active=False
        else:
            item.is_active=True
        item.save()
        # messages.success(request,"Category Deleted Successfully")
        return redirect ('/adminuser/category/')

  


class UpdateCategory(LoginRequiredMixin,APIView):
    permission_classes =[IsAdminUser]
    def get(self, request, id):
        category = Category.objects.get(id=id)
        serializer = CategorySerializer(category)
        return render(request, "update_category.html", {"formdata": serializer.data})


    def post(self, request, id):      
        try:
            data={
                "name":request.data['category_name'],
                "categoryImage":request.data['category_image'],
            }

            category = Category.objects.get(id=id)
            serializer = CategorySerializer(category, data)

            if serializer.is_valid():
                serializer.save()
                messages.success(request,"Category Updated Successfully")
                return redirect ('/adminuser/category/')
            else:
                return render(request, "update_category.html", {"errors": serializer.errors})

        except Exception as e:
                return render(request, "update_category.html", {"errors": serializer.errors})