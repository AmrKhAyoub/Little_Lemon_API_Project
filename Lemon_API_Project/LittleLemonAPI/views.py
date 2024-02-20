from decimal import Decimal
from datetime import datetime
#------------------------------------------------------#
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator , EmptyPage
from rest_framework.response import Response
from rest_framework.decorators import api_view , permission_classes , throttle_classes
from rest_framework.permissions import IsAuthenticated , IsAdminUser
from rest_framework.throttling import UserRateThrottle
#------------------------------------------------------#
from django.contrib.auth.models import User , Group
from .models import MenuItem , Cart , Order , OrderItem
from .serializers import MenuItemSerializer , UserSerializer , CartSerializer , OrderSerializer , OrderItemSerializer
#------------------------------------------------------#

# Create your views here.
@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def menu_items(request):
    if request.method == 'GET':
        items = MenuItem.objects.select_related('category').all()
        category = request.query_params.get('category')
        to_price = request.query_params.get('to_price')
        search = request.query_params.get('search')
        ordering = request.query_params.get('ordering')
        perpage = request.query_params.get('perpage',default=3)
        page = request.query_params.get('page',default=1)
        if category:
            items = items.filter(category__slug=category)
        if to_price:
            items = items.filter(price__lte=to_price)
        if search:
            items = items.filter(title__icontains=search)
        if ordering:
            ordering_fields = ordering.split(",")
            items = items.order_by(*ordering_fields) 
              
        paginator = Paginator(items,per_page=perpage)
        try:
            items = paginator.page(number=page)
        except EmptyPage:
            items = []      
            
        serialized_items = MenuItemSerializer(items,many=True)
        return Response(serialized_items.data,200)
        
    if request.method == 'POST':
        if request.user.groups.filter(name='Manager').exists() or IsAdminUser:
            serialized_item = MenuItemSerializer(data=request.data)
            serialized_item.is_valid(raise_exception=True)
            serialized_item.save()
            return Response(serialized_item.data, 201)
        else:
            return Response({'message': 'you do not have a permission to perform this action !'} , 403)
            
@api_view(['GET','PUT','PATCH','DELETE'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def menu_items_single(request,menuItem):
    if request.method == 'GET':
        item = get_object_or_404(MenuItem,pk=menuItem)
        serialized_item = MenuItemSerializer(item)
        return Response(serialized_item.data,200)
    
    if request.method == 'PUT' or request.method == 'PATCH' :
        if request.user.groups.filter(name='Manager').exists() or IsAdminUser:
            item = get_object_or_404(MenuItem,pk=menuItem)
            serialized_item = MenuItemSerializer(item,data=request.data,partial=True)
            serialized_item.is_valid(raise_exception=True)
            serialized_item.save()
            return Response(serialized_item.data, 200)
        else:
            return Response({'message': 'you do not have a permission to perform this action !'} , 403)
        
    if request.method == 'DELETE' :
        if request.user.groups.filter(name='Manager').exists() or IsAdminUser:
            item = get_object_or_404(MenuItem,pk=menuItem)
            item.delete()
            return Response({'message': f'an item with id={menuItem} deleted'} , 200)
        else:
            return Response({'message': 'you do not have a permission to perform this action !'} , 403)


#------------------------------------------------------#
@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def managers(request):
    # cheking if the user is manager or admin, if not then 403 message returned
    if not (request.user.groups.filter(name='Manager').exists() or IsAdminUser):
        return Response({'message': 'you do not have a permission to perform this action !'} , 403)
    
    if request.method == 'GET' :
        users = User.objects.all()  
        managers = users.filter(groups=2)
        serialized_managers = UserSerializer(managers,many=True)
        return Response(serialized_managers.data , 200)
    
    if request.method == 'POST' : 
        username = request.data.get('username')   
        if username:
            user = get_object_or_404(User,username=username) 
            managers = Group.objects.get(name='Manager')
            managers.user_set.add(user)
            return Response({'m':'user added to the managers group'},201)
        else:
            return Response({'m':'messing username !'},400)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def manager_single(request,username):
    # cheking if the user is a manager or an admin, if not then 403 message returned
    if request.user.groups.filter(name='Manager').exists() or IsAdminUser:
        user = get_object_or_404(User,username=username) 
        managers = Group.objects.get(name='Manager')
        managers.user_set.remove(user)
        return Response({'m':f'the user {username} removed from managers group'},201)
    
    return Response({'message': 'you do not have a permission to perform this action !'} , 403) 


@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def delivery_crew(request):
    # cheking if the user is manager, if not then 403 message returned
    if not (request.user.groups.filter(name='Manager').exists() or IsAdminUser):
        return Response({'message': 'you do not have a permission to perform this action !'} , 403)
    
    if request.method == 'GET' :    
        users = User.objects.all()  
        delivery_crew = users.filter(groups=3)
        serialized_delivery_crew = UserSerializer(delivery_crew,many=True)
        return Response(serialized_delivery_crew.data , 200)
    
    if request.method == 'POST' :    
        username = request.data.get('username')   
        if username:
            user = get_object_or_404(User,username=username) 
            delivery_crew = Group.objects.get(name='Delivery_Crew')
            delivery_crew.user_set.add(user)
            return Response({'m':'user added to the delivery crew'},201)        
        else:
            return Response({'m':'messing username !'},400)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def delivery_crew_single(request,username):
    # cheking if the user is manager, if not then 403 message returned
    if not request.user.groups.filter(name='Manager').exists():
        user = get_object_or_404(User,username=username) 
        delivery_crew = Group.objects.get(name='Delivery_Crew')
        delivery_crew.user_set.remove(user)
        return Response({'m':f'user {username} removed from delivery crew'},200)
    
    return Response({'message': 'you do not have a permission to perform this action !'} , 403) 

#------------------------------------------------------#
@api_view(['GET','POST','DELETE'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def cart(request):
    #checking if the user is not a customer
    if request.user.groups.filter(name='Manager').exists() or request.user.groups.filter(name='Delivery_Crew').exists():
        return Response({'m':'sorry you as a manger or delivery do not have a cart'},404)
    
    user_id = request.user.id
    if request.method == 'GET' :
        cart_items = Cart.objects.filter(user_id=user_id)
        serialized_cart_items = CartSerializer(cart_items,many=True)
        return Response(serialized_cart_items.data , 200)
    
    if request.method == 'POST' :
        menuitem_id = request.data.get('menuitem_id')
        quantity = request.data.get('quantity')
        if menuitem_id and quantity :
            menuitem = get_object_or_404(MenuItem,pk=menuitem_id)
            serialized_cart_item = CartSerializer(data=request.data,partial=True)
            serialized_cart_item.is_valid(raise_exception=True)
            serialized_cart_item.validated_data['user_id'] = user_id
            serialized_cart_item.validated_data['menuitem_id'] = menuitem_id
            serialized_cart_item.validated_data['unit_price'] = menuitem.price
            serialized_cart_item.validated_data['price'] = menuitem.price * Decimal(quantity)
            serialized_cart_item.is_valid(raise_exception=True)
            serialized_cart_item.save()
            return Response(serialized_cart_item.data,201)
        else:
            return Response({'m':'error some filds are missing'},400)
    
    if request.method == 'DELETE' :
        cart_items = Cart.objects.filter(user_id=user_id)
        if cart_items:
            cart_items.delete() 
            return Response({'m':'all the cart items have been deleted sucssefully'} , 200)
        
#------------------------------------------------------#
@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def orders(request):
    if request.method == 'GET' :
        if request.user.groups.filter(name='Manager').exists() or IsAdminUser:
            all_orders = Order.objects.all()
            serialized_orders = OrderSerializer(all_orders,many=True)
            return Response(serialized_orders.data,200)
        
        elif request.user.groups.filter(name='Delivery_Crew').exists():  
            delivery_crew_id = request.user.id
            orders = Order.objects.filter(delivery_crew_id=delivery_crew_id)    
            serialized_orders = OrderSerializer(orders,many=True)
            return Response(serialized_orders.data,200)
        else : #customer
            user_id = request.user.id
            orders = Order.objects.filter(user_id=user_id)    
            serialized_orders = OrderSerializer(orders,many=True)
            return Response(serialized_orders.data,200)
        
    if request.method == 'POST' :
        # cheking if user is a customer
        if request.user.groups.filter(name='Manager').exists() or request.user.groups.filter(name='Delivery_Crew').exists():
            return Response({'message': 'you do not have a permission to perform this action !'} , 403)
        user_id = request.user.id
        cart_items = Cart.objects.filter(user_id=user_id)
        if not cart_items:
            return Response({'m':'you do not have a cart to place an order !'},400)
        
        order = Order.objects.create(
            user_id=user_id,
            total=0,
            date=datetime.now().date()
        )
        
        total_price = Decimal()
        for cart_item in cart_items:
            order_item = OrderItem.objects.create(
                order_id=order.pk,
                menuitem_id=cart_item.menuitem.pk,
                quantity=cart_item.quantity,
                unit_price=cart_item.unit_price,
                price=cart_item.price
            )
            total_price += cart_item.price
            order_item.save()
            
        order.total = total_price
        order.save()
        cart_items.delete()
        serialized_order = OrderSerializer(order)
        return Response(serialized_order.data,201)         

@api_view(['GET','PUT','PATCH','DELETE'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def orders_single(request,orderId):
    if request.method == 'GET' :
         #checking if the user is not a customer
        if request.user.groups.filter(name='Manager').exists() or request.user.groups.filter(name='Delivery_Crew').exists():
            return Response({'m':'sorry you as a manger or delivery not allow for GET method'},403)
        
        user_id = request.user.id
        order = get_object_or_404(Order,pk=orderId)
        if order.user.pk != user_id:
            return Response({'m':'this is not your order !'},403)

        order_items = OrderItem.objects.filter(order_id=orderId)
        serialized_order_items = OrderItemSerializer(order_items,many=True)
        return Response(serialized_order_items.data , 200)
    
    if request.method == 'PUT':
        if request.user.groups.filter(name='Manager').exists():
            delivery_crew_id = request.data.get('delivery_crew_id')
            status = request.data.get('status')
            if delivery_crew_id and status:
                order = get_object_or_404(Order,pk=orderId)
                updated_data = {'delivery_crew_id':delivery_crew_id,'status':status} #to make sure that that only this fileds will be edited
                serialized_order = OrderSerializer(order,data=updated_data,partial=True)
                serialized_order.is_valid(raise_exception=True)
                serialized_order.save()
                return Response(serialized_order.data , 200) 
            return Response({'m':'you must enter a new delivery_crew_id and a new status'} , 400)
        else :
            return Response({'message': 'you do not have a permission to perform this action !'} , 403) 
        
    if request.method == 'PATCH' :
        if request.user.groups.filter(name='Manager').exists():
            delivery_crew_id = request.data.get('delivery_crew_id')
            status = request.data.get('status')
            if delivery_crew_id or status:
                order = get_object_or_404(Order,pk=orderId)
                serialized_order = OrderSerializer(order,data=request.data,partial=True)
                serialized_order.is_valid(raise_exception=True)
                serialized_order.save()
                return Response(serialized_order.data , 200) 
            return Response({'m':'enter a new delivery_crew_id or a new status'} , 400)
        
        elif request.user.groups.filter(name='Delivery_Crew').exists():
            status = request.data.get('status')
            if status:
                order = get_object_or_404(Order,pk=orderId)
                updated_data = {'status':status} #to make sure that that the delivery person will not change anything else
                serialized_order = OrderSerializer(order,data=updated_data,partial=True)
                serialized_order.is_valid(raise_exception=True)
                serialized_order.save()
                return Response(serialized_order.data , 200) 
            return Response({'m':'you as a delivery must enter a value for updating status'} , 400)
        else :
            return Response({'message': 'you do not have a permission to perform this action !'} , 403) 
        
    if request.method == 'DELETE':
        if request.user.groups.filter(name='Manager').exists():
            order = get_object_or_404(Order,pk=orderId)
            order.delete()
            order_items = OrderItem.objects.filter(order_id=orderId)
            order_items.delete()
            return Response({'m':'deleted successfuly'} , 200)
        else :
            return Response({'message': 'you do not have a permission to perform this action !'} , 403) 

