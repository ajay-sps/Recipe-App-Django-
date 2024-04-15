from rest_framework.views import APIView
from adminuser.models import Request
from recipe.pagination import PagePagination 
from users.serializer import RequestSerializer
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.permissions  import IsAdminUser
from django.contrib import messages
import math


class RequestsList(LoginRequiredMixin,APIView):
    permission_classes =[IsAdminUser]
    def get(self, request):
        request_obj = Request.objects.all().order_by("-id")
        paginator = PagePagination()
        results = paginator.paginate_queryset(request_obj , request , view=self)
        serializer= RequestSerializer(results ,many=True)
        page_number=request.GET.get("page","1")
        data = paginator.get_paginated_response(serializer.data).data
        data["page"]=page_number
        data["last_page"]=math.ceil(request_obj.count()/paginator.get_page_size(request))
        return render(request, "requests.html",{"data":data})
    



class RequestsUpdateStatus(LoginRequiredMixin,APIView):
    permission_classes =[IsAdminUser]
    def get(self,request):
        try:
            id = request.GET.get("id")
            status = request.GET.get("status")
            Request.objects.filter(id=id).update(status=status)
            messages.success(request,"Status Updated successfully!!!")
            return redirect("/adminuser/requests/")
        except Exception as e:
            print(str(e))
            return render(request, "adminuser/requests.html",{'error': str(e)})