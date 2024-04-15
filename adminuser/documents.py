# from django_elasticsearch_dsl import Document,fields
# from django_elasticsearch_dsl.registries import registry
# from adminuser.models import Recipe,User,Category

# @registry.register_document
# class RecipeDocument(Document):

#     category = fields.ObjectField(properties={
#             'id': fields.IntegerField(),
#             'name': fields.TextField(),
#             'description': fields.TextField(),
#         })
    
#     class Index:
#         name = 'recipes'
#         settings = {
#             "number_of_shards":1,
#             "number_of_replicas":0
#         }
#     class Django:
#         model = Recipe
#         # user = fields.KeywordField()
#         fields = [
#             'name','thumbnail', "idMeal",  "calculated_rating" , "is_approved"  ,"description" ,"youtube_link" ,"dateModified" ,"is_active"    ]
