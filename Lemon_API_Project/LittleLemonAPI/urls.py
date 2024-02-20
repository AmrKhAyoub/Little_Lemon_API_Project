from django.urls import path
from . import views
urlpatterns = [
    path('menu-items', views.menu_items),
    path('menu-items/<int:menuItem>', views.menu_items_single),

    path('groups/manager/users' , views.managers),
    path('groups/manager/users/<str:username>' , views.manager_single),
    path('groups/delivery-crew/users' , views.delivery_crew),
    path('groups/delivery-crew/users/<str:username>' , views.delivery_crew_single),
    
    path('cart/menu-items', views.cart),
    path('orders', views.orders),
    path('orders/<int:orderId>', views.orders_single),
]

