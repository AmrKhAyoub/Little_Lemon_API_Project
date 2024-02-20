from rest_framework import serializers
from .models import MenuItem , Category , Cart , Order , OrderItem
from django.contrib.auth.models import User , Group

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','slug','title']
    
class MenuItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    class Meta:
        model = MenuItem
        fields = ['id','title','price','featured','category','category_id']
        partial = True
        
class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id','name']

class UserSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True , read_only=True)
    groups_id = serializers.IntegerField(write_only=True)
    
    #groups = serializers.SerializerMethodField(method_name='get_groups')
    def get_groups(self, obj):
        return [{'id': group.id, 'name': group.name} for group in obj.groups.all()]
    
    class Meta:
        model = User
        fields = ['id','username','email','first_name','last_name','groups','groups_id']

class CartSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    menuitem = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Cart
        fields = ['id','user','user_id','menuitem','menuitem_id','quantity','unit_price','price']
        requierd_fileds = ['menuitem_id','quantity']
        partial = True

class OrderItemSerializer(serializers.ModelSerializer):
    menuitem = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = OrderItem
        fields = ['id','order_id','menuitem','menuitem_id','quantity','unit_price','price']
    
class OrderSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    delivery_crew = serializers.StringRelatedField(read_only=True)
    delivery_crew_id = serializers.IntegerField() 
    order_items = serializers.SerializerMethodField(method_name='get_order_items')
    
    #a function to fetch the items of each order
    def get_order_items(self,order_obj:Order):
        order_items = OrderItem.objects.filter(order_id=order_obj.pk)
        serialized_order_items = OrderItemSerializer(order_items,many=True)
        return serialized_order_items.data
    
    class Meta:
        model = Order
        fields = ['id','user','user_id','delivery_crew','delivery_crew_id','status','date','total','order_items']
        partial = True

