from django.http import HttpResponseRedirect
from django.shortcuts import render,redirect
from shop.models import ShopItems,Customer,Order,OrderItem
from shop.forms import ShopForm
from django.views.generic import ListView
import random
from django.db.models import Q
from django.core.paginator import Paginator
from .processors import Process



"""
    Code written by RockaDev (www.github.com/rockadev - for more projects).

    E-Shop backend system - views.

    Sorry if the code is a bit unreadable or hard to read (understand), this is my very first e-shop (or big) project.

"""



def shop(request):
    """ Get device id cookies generated by javascript using uuid """

    if 'device' in request.COOKIES.keys():
            device = request.COOKIES['device']
    else:
        return HttpResponseRedirect('/loading/')

    customer,created = Customer.objects.get_or_create(device=device)
    _products = ShopItems.objects.all()

    order,created = Order.objects.get_or_create(customer=customer,complete=False)


    if request.method == 'POST':
        admin_product_add = ShopForm(request.POST,request.FILES)
        if admin_product_add.is_valid():
            admin_product_add.save()
            return HttpResponseRedirect(request.META['HTTP_REFERER'])
        else:
            admin_product_add = ShopForm()
    else:
        admin_product_add = ShopForm()

    if request.method == 'POST':

        Process.add_to_cart_function(request)

        

    page_obj_filter = ShopItems.objects.all().order_by('-created_date')

    paginator = Paginator(page_obj_filter,3)
    page_obj = paginator.get_page(request.GET.get('page',1))
    


    _data = {
        'products':page_obj.object_list,
        'admin_product_add':admin_product_add,
        'order':order,
        'paginator':paginator

    }
    return render(request,'shop/shop.html',_data)

class ProductList(ListView):
    model = ShopItems

def productdetail(request,pk):
    product = ShopItems.objects.get(pk = pk)
    _products = ShopItems.objects.filter(pk=pk)

    if 'device' in request.COOKIES.keys():
        device = request.COOKIES['device']
    else:
        return HttpResponseRedirect('/loading/')

    customer,created = Customer.objects.get_or_create(device=device)
    order,created = Order.objects.get_or_create(customer=customer,complete=False)

    if request.method == 'POST':
        product = ShopItems.objects.get(pk = pk)
        device = request.COOKIES['device']
        customer,created = Customer.objects.get_or_create(device=device)


    for product in _products:
        if request.method == 'POST':
            if request.POST.get(f"del-{product.id}"):
                current_product = ShopItems.objects.filter(product_item=product.product_item,id=product.id)

                current_product.delete()
                removeFromCartDb = OrderItem.objects.filter(product=None)

                if removeFromCartDb:
                    removeFromCartDb.delete()

                return HttpResponseRedirect('/shop/')

            if request.POST.get(f"add-to-cart-{product.id}"):
                ItemQuantity = request.POST.get('quantity')

                if not ItemQuantity or int(ItemQuantity) < 1:
                    return HttpResponseRedirect(request.META['HTTP_REFERER'])

                elif int(ItemQuantity) > int(product.on_stock):
                    return HttpResponseRedirect(request.META['HTTP_REFERER'])

                else:
                    product = ShopItems.objects.get(pk = product.id)
                    device = request.COOKIES['device']
                    customer,created = Customer.objects.get_or_create(device=device)

                    order, created = Order.objects.get_or_create(customer=customer, complete=False)
                    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)
                    orderItem.quantity=request.POST['quantity']
                    orderItem.save()

                    return HttpResponseRedirect(request.META['HTTP_REFERER'])
        

    return render(request, 'shop/info.html', {'product': product,'order':order,'products':_products})

def cart(request):
    if 'device' in request.COOKIES.keys():
        device = request.COOKIES['device']
    else:
        return HttpResponseRedirect('/loading/')

    customer,created = Customer.objects.get_or_create(device=device)
    order,created = Order.objects.get_or_create(customer=customer,complete=False)

    _products = ShopItems.objects.all()

    """ Edit quantity and remove items from cart function written in processors.py """
    if request.method == 'POST':
    
        Process.edit_quantity_and_remove_items_function(request)

        return HttpResponseRedirect(request.META['HTTP_REFERER'])

    _data = {'order':order,'products':_products}
    return render(request,"shop/cart.html",_data)



def search(request):
    if 'device' in request.COOKIES.keys():
        device = request.COOKIES['device']
    else:
        return HttpResponseRedirect('/loading/')
    customer,created = Customer.objects.get_or_create(device=device)
    order,created = Order.objects.get_or_create(customer=customer,complete=False)
    _products = ShopItems.objects.all()
    
    search = request.GET['q']

    """
        Search products with ascii and non-ascii characters. Ex. čokoláda or cokolada is the same.
    """

    search_filter = ShopItems.objects.filter(Q(product_item_ascii__icontains=search) | Q(product_item__icontains=search)).order_by('-id')
    

    """ Call add to cart function from processors.py """
    if request.method == 'POST':
    
        Process.add_to_cart_function(request)

        return HttpResponseRedirect(request.META['HTTP_REFERER'])

    data = {'results':search_filter,'order':order,'products':_products}
    return render(request,'shop/search.html',data)