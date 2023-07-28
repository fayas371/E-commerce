from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from django.db.models import Avg, Count
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from ..models import Product,Review
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from rest_framework.decorators import api_view
from rest_framework.response import Response


from ..serializers import ProductSerializer



@api_view(['GET'])
def getProducts(request):
    query = request.query_params.get('keyword')
    if query == None:
        query = ''

    products = Product.objects.filter(
        name__icontains=query).order_by('-createdAt')

    page = request.query_params.get('page')
    paginator = Paginator(products, 4)

    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    if page == None:
        page = 1

    page = int(page)
    print('Page:', page)
    serializer = ProductSerializer(products, many=True)
    return Response({'products': serializer.data, 'page': page, 'pages': paginator.num_pages})

@api_view(['GET'])
def getTopProducts(request):
    products = Product.objects.filter(rating__gte=4).order_by('-rating')[0:5]
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)






@api_view(['GET'])
def getproduct(request, pk):
    product = get_object_or_404(Product, _id=pk)
    serializer = ProductSerializer(product)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def createproduct(request):
    user=request.user
    product=Product.objects.create(
        user=user,
        name='Sample Name',
        price=0,
        brand='Sample Brand',
        countInStock=0,
        category='Sample Category',
        description=''

    )
    serializer = ProductSerializer(product,many=False)
    return Response(serializer.data)




@api_view(['PUT'])
@permission_classes([IsAdminUser])  
def updateproduct(request, pk):
    data=request.data

    product = get_object_or_404(Product, _id=pk)
    product.name=data['name']
    product.price=data['price']
    product.brand=data['brand']
    product.countInStock=data['countInStock']
    product.category=data['category']
    product.description=data['description']

    product.save()



    

    serializer = ProductSerializer(product)
    return Response(serializer.data)



@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def deleteProduct(request, pk):
    product = get_object_or_404(Product, _id=pk)
    product.delete()
    return Response('product Deleted')


@api_view(['POST'])
def uploadImage(request, product_id):
    product = Product.objects.get(_id=product_id)
    image = request.FILES['image']

    # Save the image file to a media directory
    filename = default_storage.save(f'images/{image.name}', image)

    # Update the product's image field with the file path
    product.image = filename
    product.save()

    return Response('Image uploaded successfully')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createProductReview(request, pk):
    user = request.user
    product = Product.objects.get(_id=pk)
    data = request.data

    # 1 - Review already exists
    already_exists = product.review_set.filter(user=user).exists()
    if already_exists:
        content = {'detail': 'Product already reviewed'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)

    # 2 - No Rating or 0
    elif data['rating'] == 0:
        content = {'detail': 'Please select a rating'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)

    # 3 - Create review
    else:
        review = Review.objects.create(
            user=user,
            product=product,
            name=user.first_name,
            rating=data['rating'],
            comment=data['comment'],
        )

        # Update product's numReviews and rating
        reviews = product.review_set.all()
        product.numReviews = reviews.count()
        product.rating = reviews.aggregate(Avg('rating'))['rating__avg']
        product.save()

        return Response('Review Added')
