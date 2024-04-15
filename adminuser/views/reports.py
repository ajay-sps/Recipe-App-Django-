from rest_framework.views import APIView
from adminuser.models import Reports,Recipe
from recipe.pagination import PagePagination 
from users.serializer import ReportsSerializer,RecipeListSerializer
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.permissions import IsAdminUser
from django.contrib import messages
from django.db.models import Count

import math


class ReportsList(LoginRequiredMixin,APIView):
    permission_classes =[IsAdminUser]
    def get(self, request):

        reports_obj = Reports.objects.values("recipe").distinct()
        recipe_objects = Recipe.objects.filter(id__in=reports_obj)
        paginator = PagePagination()
        results = paginator.paginate_queryset(recipe_objects , request , view=self)
        serializer= RecipeListSerializer(results ,many=True)
        for item in serializer.data:
            if item['thumbnail'].startswith("/http"):
                item['thumbnail'] = item['thumbnail'][1:]
                item['thumbnail'] = item['thumbnail'].replace("%3A",":/")
            item["count"] = Reports.objects.filter(recipe__id = item['id']).count()
            item["status"] = Reports.objects.filter(recipe__id = item['id'])[0].status

        page_number=request.GET.get("page","1")
        data = paginator.get_paginated_response(serializer.data).data
        data["page"]=page_number
        data["last_page"]=math.ceil(reports_obj.count()/paginator.get_page_size(request))

        return render(request, "reports.html",{"data":data})
    



class ReportsUpdateStatus(LoginRequiredMixin,APIView):
    permission_classes =[IsAdminUser]
    def get(self,request):
        try:
            id = request.GET.get("id")
            status = request.GET.get("status")
            Reports.objects.filter(recipe=id).update(status=status)
            messages.success(request,"Status Updated successfully!!!")
            return redirect("/adminuser/reports/")
        except Exception as e:
            print(str(e))
            return render(request, "adminuser/reports.html",{'error': str(e)})
        


        

class ReportsDescription(LoginRequiredMixin,APIView):
    permission_classes =[IsAdminUser]
    def get(self, request):
        id = request.GET.get('id')
        reports_obj = Reports.objects.filter(recipe=id)
       

        return render(request, "reports_description.html",{"data":reports_obj})