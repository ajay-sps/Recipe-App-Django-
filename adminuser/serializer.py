from rest_framework import serializers
from adminuser.models import Category, Rating,Ingredient,Recipe,Recipe,Recipe_Ingredient



class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id","name","categoryImage","is_active"]




class IngredientSerializer(serializers.ModelSerializer):
    image2 = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Ingredient
        fields = ["id","name","image","image2","is_active"]
    def get_image2(self, obj):
        if  str(obj.image).startswith("http"):
            return str(obj.image)
        else:
            return None
        



class RecipeListSerializer(serializers.ModelSerializer):
    category_name=serializers.CharField(source='category.name', read_only=True)
    class Meta:
        model = Recipe
        fields = ["id","name","thumbnail","category_name"]




class Recipe_IngredientSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category.name', read_only=True)
    creator = serializers.CharField(source='user.first_name', read_only=True)
    review_count = serializers.SerializerMethodField()


    ingredients = serializers.SerializerMethodField()
    class Meta:
        model = Recipe
        fields = ["id","name","thumbnail","creator","calculated_rating","is_active","category","description","youtube_link","dateModified","review_count","ingredients"]

    def get_ingredients(self,obj):
        objects=Recipe_Ingredient.objects.filter(recipe = obj)
        data={}
        for items in objects:
            data[items.ingredient.name]=items.quantity
        return data

    def get_review_count(self,obj):
        reviewCount= Rating.objects.filter(recipe = obj.id).count()
        return(reviewCount)

