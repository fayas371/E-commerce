from django.urls import path
from base.views import product_views as views


urlpatterns = [

    path('', views.getProducts, name="products"),

    path('create/', views.createproduct, name="product-create"),
    path('<str:product_id>/upload/', views.uploadImage, name='image-upload'),
    path('top/',views.getTopProducts,name='top-products'),

    path('<str:pk>/reviews/', views.createProductReview, name="create-review"),
    path('<str:pk>/',views.getproduct,name='product'),  
    path('update/<str:pk>/',views.updateproduct,name='update-product'),
    path('delete/<str:pk>/',views.deleteProduct,name='delete-product'),
]
