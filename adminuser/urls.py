from django.urls import path
from adminuser.views.category import AddCategory,DeleteCategory,ListCategory,FetchCategory,UpdateCategory
from adminuser.views.ingredient import AddIngredient,DeleteIngredient,ListIngredient,FetchIngredient,UpdateIngredient
from adminuser.views.recipe import AddRecipe ,ListRecipe,Description ,AddRecipeToDB ,DescriptionDB,DeleteRecipe

from adminuser.views.requests import RequestsList,RequestsUpdateStatus
from adminuser.views.approvals import ListApprovals,ApproveRecipe,RejectRecipe
from adminuser.views.reports import ReportsList,ReportsUpdateStatus,ReportsDescription

urlpatterns=[

    #############CATEGORY################

    path("add/category/",AddCategory.as_view()),
    path("delete/category/<int:id>",DeleteCategory.as_view()),
    path("category/",ListCategory.as_view()),
    path("fetch/category/",FetchCategory.as_view()),
    path("update/category/<int:id>",UpdateCategory.as_view()),

    #############INGREDIENT###############

    path("add/ingredient/",AddIngredient.as_view()),
    path("delete/ingredient/<int:id>",DeleteIngredient.as_view()),
    path("ingredient/",ListIngredient.as_view()),
    path("fetch/ingredient/",FetchIngredient.as_view()),
    path("update/ingredient/<int:id>",UpdateIngredient.as_view()),

    #############RECIPE################
    path("recipe/",ListRecipe.as_view()),
    path("add/recipe/",AddRecipe.as_view()),
    path("delete/recipe/",DeleteRecipe.as_view()),

    # path("delete/ingredient/<int:id>",DeleteIngredient.as_view()),
    # path("fetch/ingredient/",FetchIngredient.as_view()),
    # path("update/ingredient/<int:id>",UpdateIngredient.as_view()),


    #############RECIPE-DESCRIPTION################
    path("add/recipe/description/",Description.as_view()),
    path("recipe/description/",DescriptionDB.as_view()),

    path("add/recipe/toDB/",AddRecipeToDB.as_view()),


    #################### REQUESTS ######################

    path("requests/",RequestsList.as_view()),
    path("requests/updatestatus/",RequestsUpdateStatus.as_view()),



    #################### APPROVALS ######################

    path("approvals/",ListApprovals.as_view()),
    path("approve/recipe/",ApproveRecipe.as_view()),
    path("reject/recipe/",RejectRecipe.as_view()),



    #################### REPORTS ######################

    path("reports/",ReportsList.as_view()),
    path("reports/updatestatus/",ReportsUpdateStatus.as_view()),
    path("recipe/reports/",ReportsDescription.as_view()),






]