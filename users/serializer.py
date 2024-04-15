from users.models import User, UserProfile
from rest_framework import serializers
from adminuser.models import Recipe,Request,Reports, Recipe_Ingredient,Ingredient,Favourites



class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model =UserProfile
        fields=['profession'] 


class UserSerializer(serializers.ModelSerializer):
    userprofilee = UserProfileSerializer()

    class Meta:
        model =User
        fields=['first_name','last_name','username','userprofilee','password','is_active']


    def create(self, validated_data):
        profile=validated_data.pop("userprofilee")
        user=User.objects.create(**validated_data)
        UserProfile.objects.create(user = user, **profile)
        return user 




class RecipeListSerializer(serializers.ModelSerializer):
    category_name=serializers.CharField(source='category.name', read_only=True)
    user_name=serializers.CharField(source='user.first_name', read_only=True)

    class Meta:
        model = Recipe
        fields = ["id","name","user_name", "thumbnail","category_name","calculated_rating"]
    
    


class CreateRecipeSerializer(serializers.ModelSerializer):
   
    class Meta:
        model = Recipe
        fields = ['id','name','thumbnail','user','category','description','youtube_link']

   
    
class FavouritesSerializer(serializers.ModelSerializer):
    recipe = RecipeListSerializer()
    class Meta:
        model = Favourites
        fields = ['id','user','recipe']
    

class RequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = ['id','name','description','status','creation_date']


class ReportsSerializer(serializers.ModelSerializer):
    recipe = RecipeListSerializer()
    username = serializers.CharField( source="user.name", read_only = True)
    class Meta:
        model = Reports
        fields = ['id','username','recipe','description','status','creation_date']







class fullUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["profession","profilePic","phone","about","address","city","state","zip"]

class updateUserSerializer(serializers.ModelSerializer):
    profile = fullUserProfileSerializer()
    class Meta:
        model = User
        fields = ["first_name","last_name","profile"]

    def update(self, instance, validated_data):
        profile = validated_data.pop("profile")
        # last_name = validated_data.pop("last_name")
        # instance.first_name =fname
        # instance.last_name =last_name
        User.objects.filter(id=instance.id).update(**validated_data)


        profilepicture= profile.pop('profilePic')
        userprofile =  UserProfile.objects.get(user = instance)
        userprofile.profilePic = profilepicture
        userprofile.save()
        UserProfile.objects.filter(user_id = instance).update(**profile)
        return instance