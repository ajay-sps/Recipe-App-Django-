from rest_framework.views import APIView
from adminuser.models import Request,Recipe
from recipe.pagination import PagePagination 
from users.serializer import RequestSerializer,RecipeListSerializer
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.template.loader import render_to_string
from users.tasks import send_email_task
from recipe.settings import EMAIL_HOST_USER
from rest_framework.permissions import IsAdminUser
import math
from django.core.mail import send_mail


class ListApprovals(LoginRequiredMixin,APIView):
    permission_classes =[IsAdminUser]
    def get(self,request):
        try: 
            data = Recipe.objects.filter(is_active = True,is_approved=False).order_by("-id")
            serializer = RecipeListSerializer(data, many =True)
            # for item in serializer.data:
            #         item['user'] = 

            paginator = PagePagination()
            results = paginator.paginate_queryset(serializer.data , request , view=self)
            paginated_data = paginator.get_paginated_response(results).data
            page_number=request.GET.get("page","1")
            paginated_data["page"]=page_number
            paginated_data["last_page"]=math.ceil(data.count()/paginator.get_page_size(request))

            return render(request, "approvals.html",{"data":paginated_data})
        except Exception as e:
            return render(request, "approvals.html",{"errors":str(e)})





class ApproveRecipe(LoginRequiredMixin,APIView):
    permission_classes =[IsAdminUser]
    def get(self,request):
        try: 
            id = request.GET.get("id")
            recipe =Recipe.objects.get(id = id)
            Recipe.objects.filter(id=id).update(is_approved = True)

            template = render_to_string("emailTemplates/email_recipe_approved.html",{"name":recipe.user.first_name,"recipe_name":recipe.name})
            # send_email_task.delay('Hooray!!! Recipe Approved','',EMAIL_HOST_USER, [recipe.user.username] ,template)
            
            send_mail(subject="Hooray!!! Recipe Approved",message='',from_email=EMAIL_HOST_USER ,recipient_list=[request.user.username],html_message=template)
            messages.success(request,"Recipe Approved successfully !!!")

            return redirect("/adminuser/approvals/")
        except Exception as e:
            print(str(e))
            return render(request,"approvals.html",{"errors":str(e)})
        


class RejectRecipe(LoginRequiredMixin,APIView):
    permission_classes =[IsAdminUser]
    def get(self,request):
        try: 
            id = request.GET.get("id")
            reasons = request.GET.get("reason")
            Recipe.objects.filter(id=id).update(is_active = False)
            recipe =Recipe.objects.get(id=id)

            template = render_to_string("emailTemplates/email_recipe_rejected.html",{"name":recipe.user.first_name,"recipe_name":recipe.name,"reasons":reasons})
            # send_email_task.delay('Recipe Rejected','',EMAIL_HOST_USER, [recipe.user.username] ,template)

            send_mail(subject="Recipe Rejected",message='',from_email=EMAIL_HOST_USER ,recipient_list=[request.user.username],html_message=template)

            messages.success(request,"Recipe Rejected !!!")
            return redirect("/adminuser/approvals/")
        except Exception as e:
            return render(request, "approvals.html",{"errors":str(e)})