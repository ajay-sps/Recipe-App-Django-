from django.shortcuts import render
from rest_framework.views import APIView
from django.shortcuts import render, redirect
from users.serializer import UserSerializer, updateUserSerializer, fullUserProfileSerializer
# from rest_framework.response import Response
from django.http import HttpResponse
from users.models import User, UserProfile
from django.template.loader import render_to_string
from django.core.mail import send_mail
from recipe.settings import EMAIL_HOST_USER
from django.utils.crypto import get_random_string
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django .contrib import messages
from users.tasks import send_email_task
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.permissions import IsAdminUser
from decouple import config
import os
from twilio.rest import Client



class SignUp(APIView):
    def get(self, request):
        return render(request, 'signup.html')

    def send_email(self, subject, sender, receiver, message, link):
        template = render_to_string(
            'emailTemplates/email-template.html', {'name': message, 'verificationlink': link})
        send_mail(subject, message=message, from_email=sender,recipient_list=[receiver], html_message=template)

    def post(self, request):
        try:
            data = request.data
            userdata = {
                'first_name': data.get('first_name', ''),
                'last_name':  data.get('last_name', ''),
                'username':  data.get('username', ''),
                'userprofilee': {
                    'profession': data.get('profession', ''),
                },
                'password': make_password(data.get('password')),
                'is_active': 0
            }

            serializer = UserSerializer(data=userdata, partial=True)
            username = User.objects.filter(username=request.data['username'])
            if not username:
                if serializer.is_valid():
                    user = serializer.save()
                else:
                    return render(request, "signup.html", {"errors": serializer.errors})
                # return render(request, "signup.html", {"message": 'A user with this email already Exists', 'data': data})
            else:
                if username.first().is_active==True:
                    return render(request, "signup.html", {"message": 'A user with this email already Exists', 'data': data})
                else:
                    user =username.first()

            code = get_random_string(length=10)
            profile = user.userprofile
            profile.verification_code = code
            profile.save()
            self.send_email('Verify your mail', EMAIL_HOST_USER,
                            request.data['username'], request.data['first_name'], f"{config('site_base_url')}/user/verification/{code}")
            return render(request, "signup.html", {"message": "A verification mail has been sent"})
                
        except Exception as e:
            msg = {"data": str(
                e), "message": "some error occured", "status": 500}
            return render(request, "signup.html", {"message": str(e)})


class VerifyEmail(APIView):
    def get(self, request, code):
        try:
            userprofile = UserProfile.objects.get(verification_code=code)
            if userprofile:
                userr = userprofile.user
                userr.is_active = True
                userr.save()
                userprofile.verification_code = None
                userprofile.save()
                return HttpResponse('Email Verified')
            else:
                return HttpResponse('unable to verify email')
        except Exception as e:
            print(str(e))
            return redirect('/')


class Login(APIView):

    def get(self, request):
        return render(request, "login.html")

    def post(self, request):
        try:
            username = request.data['username']
            password = request.data['password']

            user = authenticate(self, username=username, password=password)
            if user:
                if user.is_active:
                    login(request, user)
                    if user.is_superuser:
                        return redirect("/adminuser/recipe/")
                    else:
                       
                        # client = Client(config('TWILIO_ACCOUNT_SID'), config('TWILIO_AUTH_TOKEN'))
                        # message = client.messages \
                        #     .create(
                        #         body='You have successfully signed in!!!',
                        #         from_='+17622495195',
                        #         to='+919588797029'
                        #     )
                        
                        return redirect("/home/")
                else:
                    return render(request, "login.html", {"message": "Please verify your email"})
            else:
                return render(request, "login.html", {"message": "Unauthorised User"})
        except Exception as e:
            print(str(e))
            return redirect('/')









class ForgotPassword(APIView):

    def get(self, request):
        return render(request, "users/forgot_password.html")
    
    def post(self, request):
        try:
           
            email = request.data['email']
            user = User.objects.filter(username = email)
            if user:
                user_obj = User.objects.get(username = email)
                token = get_random_string(length=10)

                user_obj.userprofile.verification_code = token
                user_obj.userprofile.save()
                template = render_to_string('emailTemplates/email_forgot_password.html',{'resetlink': f"{config('site_base_url')}/resetpassword/{token}"})
                # send_email_task.delay(subject="Reset Your Password",message='',from_email=EMAIL_HOST_USER ,recipient_list=[email],template=template)
                
                send_mail(subject="Reset Your Password",message='',from_email=EMAIL_HOST_USER ,recipient_list=[email],html_message=template)
                
                return render(request, "users/forgot_password.html", {"message": "A reset password link has been sent to your email"})
            else:
                return render(request, "users/forgot_password.html", {"errors": "This email doesn't exist"})
        except Exception as e:
            return redirect('/')



class ResetPassword(APIView):

    def get(self, request , token):
        return render(request, "users/reset_password.html")
    
    def post(self, request,token):
        try:
            password1 = request.data['password1']
            userprofile =  UserProfile.objects.filter(verification_code = token)

            if userprofile:
                userprofile[0].user.set_password(make_password(password1))
                userprofile[0].verification_code = None
                userprofile[0].save()
                messages.success(request,"Password Changed successfully!!! ")
                return redirect("/")
            else:
                return HttpResponse("link expired.........")
        except Exception as e:
            print(str(e))
            return redirect('/')







class LogOutUser(LoginRequiredMixin,APIView):
    def get(self, request):
        logout(request)
        return redirect("/")



class Profile(LoginRequiredMixin,APIView):
    def get(self, request):
        data= User.objects.get(id = request.user.id)
        return render(request, "users/profile.html",{"data":data})
    


class EditProfile(LoginRequiredMixin,APIView):
    def get(self, request):
        data= User.objects.get(id = request.user.id)
        # data1=UserProfile.objects.get(user = data)
        # serializer = fullUserProfileSerializer(data1)
        # print(data1)
        # print(serializer.data)
        return render(request, "users/edit_profile.html",{"data":data})
    

    def post(self,request):
        
        data=request.data
        modified_data = {
            "first_name": data.get("first_name",""),
            "last_name"  : data.get("last_name",""),
            "profile": {
                        "profession" :data.get("profession",""),
                        "profilePic" : data.get("profilePic",""),
                        "phone" : data.get("phone",""),
                        "about" : data.get("about",""),
                        "address" : data.get("address",""),
                        "city" : data.get("city",""),
                        "state" : data.get("state",""),
                        "zip" : data.get("zip",""),
                        }
        }

        serializer = updateUserSerializer(request.user , modified_data)
        if serializer.is_valid():
            serializer.save()
        else:
            print(serializer.errors)
            return render(request, "users/edit_profile.html",{"errors":serializer.errors})
        messages.success(request,"User profile updated successfully")
        return redirect("/profile/edit/")


