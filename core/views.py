from itertools import product
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from core.models import Product,UserItem,sold,Order,mrentry,mrentryrecord,returnn,Customer,dailyreport,paybillcatogory,temppaybill,paybill,bill,mrentryrecord,supplier,Customerbalacesheet,corportepay,supplierbalancesheet,plreport
from .filters import OrderFilter,soldfilter,dailyreportfilter,expensefilter,paybillfilter,mrfilter,returnfilter,billfilter,Customerbalacesheetfilter,corportepayfilter,supplierbalanecesheetfilter,plreportfilter
from django.db.models import Count, F, Value
from django.db import connection
from core.form import soldformm, useritem,GeeksForm,mrr,returnnform,billfrom,dailyreportt,tempbilformm,mreditformm,CorportepayForm
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import (get_object_or_404,
                              render,
                              HttpResponseRedirect)
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q                              
from django.db.models import Sum
from num2words import num2words
import datetime
from twilio.rest import Client 
from django.shortcuts import render
from django.views import View

from django.core.paginator import Paginator
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import  ListView
from django.urls import reverse
from dal import autocomplete
from django.db.models import F

from django.http import JsonResponse

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import TaskSerializer
from rest_framework import status
import datetime
import pytz
from datetime import datetime as dt_datetime
from django.core.management.base import BaseCommand



@login_required
def cart(request):
    
    a =UserItem.objects.filter(user=request.user).last()
    form = useritem(request.POST or None, request.FILES or None)
    form2 = GeeksForm(request.POST or None, request.FILES or None,instance = a)
    shopcart =UserItem.objects.filter(user=request.user)
    user_products = UserItem.objects.filter(user=request.user,groupproduct =False)
   
    total=0
    total1=0
    for gs in user_products:
        total+=gs.price1 * gs.quantity
    for gs in user_products:
        total1+=gs.price1 * gs.quantity    
      
    
    if request.method=='POST' and 'btnform1' in request.POST: 
      if form2.is_valid() :
        fs = form2.save(commit=False)
        fs.user= request.user 
    
        fs.groupproduct=False
        fs.save()
        obj = get_object_or_404(Product, id = fs.product_id)
        products = Product.objects.all().filter(groupname=obj.groupname).exclude(groupname='')
       
        for rs in products: 
          item, created = UserItem.objects.get_or_create(
            user_id=request.user.id,
            product_id=rs.id,
            groupproduct = True,
            quantity=rs.subpartquantity * fs.quantity

          )

        return HttpResponseRedirect("/")
     

    # for rs in shopcart:
    #     product = Product.objects.get(id=rs.product_id)
    #     if product.quantity < rs.quantity and rs.credit =='noncredit':
    #                 outstock=0   


    dhaka_timezone = pytz.timezone('Asia/Dhaka')

# Get the current time in the Asia/Dhaka timezone
    current_time_dhaka = datetime.datetime.now(dhaka_timezone)

# Define the desired format
    date_time_format = "%d%m%y-%I%M"

# Format and print the current date and time in Asia/Dhaka timezone
    formatted_date_time = current_time_dhaka.strftime(date_time_format)


    if request.method=='POST' and 'btnform2' in request.POST and shopcart.exists(): 
     if form.is_valid() :
        fs= form.save(commit=False)
        fs.user= request.user
        fs.totalprice=total-fs.discount
        fs.totalprice1=total1-fs.discount
        fs.due=total-(fs.paid+fs.discount)
     
        fs.invoicenumber = formatted_date_time 

        
        fs.save()
        if fs.customer !=None:
          cus =Customer.objects.filter(id=fs.customer_id).first()
          cus.balance +=fs.due
        
          cus.save()        
          item, created =Customerbalacesheet.objects.get_or_create(
            order_id=fs.id,
            customer=cus,
            balance=cus.balance,
            duebalanceadd =fs.due
        )
          

        
        obj = dailyreport.objects.all().last()
        item, created =dailyreport.objects.get_or_create(
            order_id=fs.id,
            ammount=obj.ammount+fs.paid,
            petteyCash=obj.petteyCash,
            reporttype='INVOICE'
            
        )
        for rs in shopcart: 
           product = Product.objects.get(id=rs.product_id)
           if int(rs.quantity) > int(product.quantity) :
              messages.error(request, 'Do not have group product quanitity that quantity')
              return redirect('cart') 

        for rs in shopcart:
                detail = sold()
                detail.customer    = fs.customer
                 # Order Id
                 
                detail.product_id  = rs.product_id
                detail.order_id     = fs.id 
                detail.user  = request.user
                detail.quantity  = rs.quantity
                detail.added  = rs.added
                detail.discount = fs.discount
                detail.price1 = rs.price1
                detail.price2 = rs.price2
                detail.engine_no=rs.engine_no
                detail.Phone=fs.Phone
                detail.name=fs.name
                detail.remarks =rs.remarks
                detail.sparename =rs.sparename 
                detail.groupproduct = rs.groupproduct
                
                
                shopcart.delete()    
                user_products.delete()
                product = Product.objects.get(id=rs.product_id)
                product.quantity -= rs.quantity
                detail.exchange_ammount=rs.exchange_ammount
                detail.costprice=product.price
                detail.save()
                product.save()
                

                
        
          
            
        return HttpResponseRedirect("/soldlist")

      
    category = request.GET.get('category', '')
    search = request.GET.get('search', '')
    mother = request.GET.get('mother', '')

    if category and search and mother:
        products = Product.objects.filter(
            Q(name__icontains=search) & Q(productcatagory__icontains=category) & Q(mother=mother)
        )
    elif category and search:
        products = Product.objects.filter(
            Q(name__icontains=search) & Q(productcatagory__icontains=category)
        )
    elif category and mother:
        products = Product.objects.filter(
            Q(productcatagory__icontains=category) & Q(mother=mother)
        )
    elif search and mother:
        products = Product.objects.filter(
            Q(name__icontains=search) & Q(mother=mother)
        )
    elif category:
        products = Product.objects.filter(Q(productcatagory__icontains=category))
    elif search:
        products = Product.objects.filter(Q(name__icontains=search))
    elif mother:
        products = Product.objects.filter(Q(mother=mother))
    else:
        products = Product.objects.all()

  
    #products = Product.objects.filter(Q(productcatagory__icontains=category))
  

    
    
    # myFilter = OrderFilter(request.GET, queryset=products)
    # products = myFilter.qs 

    # p = Paginator(products, 5)  # creating a paginator object
    # # getting the desired page number from url
    # page_number = request.GET.get('page')
    # try:
    #     page_obj = p.get_page(page_number)  # returns the desired page object
    # except PageNotAnInteger:
    #     # if page_number is not an integer then assign the first page
    #     page_obj = p.page(1)
    # except EmptyPage:
    #     # if page is empty then return last page
    #     page_obj = p.page(p.num_pages)

    
    
    # products=page_obj  
    
    paginator = Paginator(products, 10) # Show 25 contacts per page.

    page_number = request.GET.get('page')
    pro = paginator.get_page(page_number)

    category=  Product.objects.values('productcatagory').distinct()
    
    context = {'category':category,'products': products,'form':form,'user_products':user_products,'pro':pro,'total':total,'form2':form2}
    return render(request, 'core/cart.html', context)






@login_required
def soldlist(request):
      #cursor = connection['db.sqlite3'].cursor()
      #user_products = Product.objects.raw("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM core_useritem WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_useritem WHERE product_id = core_product.id)")
      #cursor.execute("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM core_useritem WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_useritem WHERE product_id = core_product.id)")
     
      #with connection.cursor() as cursor:
       # cursor.execute("INSERT INTO core_sold SELECT * FROM core_useritem ")
        #cursor.execute("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM  core_sold WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_sold WHERE product_id = core_product.id) ")
        #cursor.execute("UPDATE  core_sold  SET quantityupdate=1")
        
        #row = cursor.fetchone()

        orders = Order.objects.all().order_by('-id')

        # Apply filtering using the custom filter (soldfilter)
        myFilter = soldfilter(request.GET, queryset=orders)
        filtered_orders = myFilter.qs
        
        # Pagination
        paginator = Paginator(filtered_orders, 16)  # Show 5 orders per page
        page_number = request.GET.get('page')
        page_orders = paginator.get_page(page_number)

        context = {
            'orders': page_orders,
            'myFilter': myFilter,  # Pass the filter for the template
        }

        
       


        return render(request, 'core/soldlist.html',context)







@login_required
def plreportlist(request):
      #cursor = connection['db.sqlite3'].cursor()
      #user_products = Product.objects.raw("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM core_useritem WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_useritem WHERE product_id = core_product.id)")
      #cursor.execute("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM core_useritem WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_useritem WHERE product_id = core_product.id)")
     
      #with connection.cursor() as cursor:
       # cursor.execute("INSERT INTO core_sold SELECT * FROM core_useritem ")
        #cursor.execute("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM  core_sold WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_sold WHERE product_id = core_product.id) ")
        #cursor.execute("UPDATE  core_sold  SET quantityupdate=1")
        
        #row = cursor.fetchone()

        orders = plreport.objects.all().order_by('-id')

        # Apply filtering using the custom filter (soldfilter)
        myFilter = plreportfilter(request.GET, queryset=orders)
        filtered_orders = myFilter.qs
        
        # Pagination
        paginator = Paginator(filtered_orders, 16)  # Show 5 orders per page
        page_number = request.GET.get('page')
        page_orders = paginator.get_page(page_number)

        context = {
            'orders': page_orders,
            'myFilter': myFilter,  # Pass the filter for the template
        }

        
       


        return render(request, 'core/plreport.html',context)





@login_required
def customerbalancesheetlist(request):
      #cursor = connection['db.sqlite3'].cursor()
      #user_products = Product.objects.raw("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM core_useritem WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_useritem WHERE product_id = core_product.id)")
      #cursor.execute("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM core_useritem WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_useritem WHERE product_id = core_product.id)")
     
      #with connection.cursor() as cursor:
       # cursor.execute("INSERT INTO core_sold SELECT * FROM core_useritem ")
        #cursor.execute("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM  core_sold WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_sold WHERE product_id = core_product.id) ")
        #cursor.execute("UPDATE  core_sold  SET quantityupdate=1")
        
        #row = cursor.fetchone()

        orders = Customerbalacesheet.objects.all().order_by('-id')

        # Apply filtering using the custom filter (soldfilter)
        myFilter = Customerbalacesheetfilter(request.GET, queryset=orders)
        filtered_orders = myFilter.qs
        
        # Pagination
        paginator = Paginator(filtered_orders, 16)  # Show 5 orders per page
        page_number = request.GET.get('page')
        page_orders = paginator.get_page(page_number)

        context = {
            'orders': page_orders,
            'myFilter': myFilter,  # Pass the filter for the template
        }

        
       


        return render(request, 'core/cusblsheet.html',context)







@login_required
def supplierbalancesheetlist(request):
      

        orders = supplierbalancesheet.objects.all().order_by('-id')

        # Apply filtering using the custom filter (soldfilter)
        myFilter = supplierbalanecesheetfilter(request.GET, queryset=orders)
        filtered_orders = myFilter.qs
        
        # Pagination
        paginator = Paginator(filtered_orders, 16)  # Show 5 orders per page
        page_number = request.GET.get('page')
        page_orders = paginator.get_page(page_number)

        context = {
            'orders': page_orders,
            'myFilter': myFilter,  # Pass the filter for the template
        }

        
       


        return render(request, 'core/supblsheet.html',context)





@login_required
def returnlist(request):
      #cursor = connection['db.sqlite3'].cursor()
      #user_products = Product.objects.raw("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM core_useritem WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_useritem WHERE product_id = core_product.id)")
      #cursor.execute("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM core_useritem WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_useritem WHERE product_id = core_product.id)")
     
      #with connection.cursor() as cursor:
       # cursor.execute("INSERT INTO core_sold SELECT * FROM core_useritem ")
        #cursor.execute("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM  core_sold WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_sold WHERE product_id = core_product.id) ")
        #cursor.execute("UPDATE  core_sold  SET quantityupdate=1")
        
        #row = cursor.fetchone()

         returns=returnn.objects.all().order_by('-id')
         myFilter =returnfilter(request.GET, queryset=returns)
         returns = myFilter.qs 


         paginator = Paginator(returns, 15) # Show 25 contacts per page.

         page_number = request.GET.get('page')
         returns= paginator.get_page(page_number)
        
         context = {#'category': category,
               'returns': returns,
               'myFilter':myFilter
               }


         return render(request, 'core/returnlist.html',context)




@login_required
def bill_list(request):
      #cursor = connection['db.sqlite3'].cursor()
      #user_products = Product.objects.raw("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM core_useritem WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_useritem WHERE product_id = core_product.id)")
      #cursor.execute("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM core_useritem WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_useritem WHERE product_id = core_product.id)")
     
      #with connection.cursor() as cursor:
       # cursor.execute("INSERT INTO core_sold SELECT * FROM core_useritem ")
        #cursor.execute("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM  core_sold WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_sold WHERE product_id = core_product.id) ")
        #cursor.execute("UPDATE  core_sold  SET quantityupdate=1")
        
        #row = cursor.fetchone()

         returns=bill.objects.all().order_by('-id')
         myFilter =billfilter(request.GET, queryset=returns)
         returns = myFilter.qs 


         paginator = Paginator(returns, 15) # Show 25 contacts per page.

         page_number = request.GET.get('page')
         returns= paginator.get_page(page_number)
        
         context = {#'category': category,
               'returns': returns,
               'myFilter':myFilter
               }


         return render(request, 'core/bill_list.html',context)






@login_required
def supplierbill_list(request):
    #   cursor = connection['db.sqlite3'].cursor()
    #   user_products = Product.objects.raw("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM core_useritem WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_useritem WHERE product_id = core_product.id)")
    #   cursor.execute("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM core_useritem WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_useritem WHERE product_id = core_product.id)")
     
    #   with connection.cursor() as cursor:
    #    cursor.execute("INSERT INTO core_sold SELECT * FROM core_useritem ")
    #     cursor.execute("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM  core_sold WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_sold WHERE product_id = core_product.id) ")
    #     cursor.execute("UPDATE  core_sold  SET quantityupdate=1")
        
    #     row = cursor.fetchone()

         returns=corportepay.objects.all().order_by('-id')
         myFilter =corportepayfilter(request.GET, queryset=returns)
         returns = myFilter.qs 


         paginator = Paginator(returns, 15) # Show 25 contacts per page.

         page_number = request.GET.get('page')
         returns= paginator.get_page(page_number)
        
         context = {#'category': category,
               'returns': returns,
               'myFilter':myFilter
               }


         return render(request, 'core/bill_list.html',context)


def mrlist(request):
      #cursor = connection['db.sqlite3'].cursor()
      #user_products = Product.objects.raw("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM core_useritem WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_useritem WHERE product_id = core_product.id)")
      #cursor.execute("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM core_useritem WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_useritem WHERE product_id = core_product.id)")
     
      #with connection.cursor() as cursor:
       # cursor.execute("INSERT INTO core_sold SELECT * FROM core_useritem ")
        #cursor.execute("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM  core_sold WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_sold WHERE product_id = core_product.id) ")
        #cursor.execute("UPDATE  core_sold  SET quantityupdate=1")
        
        #row = cursor.fetchone()

         orders=mrentry.objects.all().order_by('-id')
         #myFilter =soldfilter(request.GET, queryset=orders)
         #orders = myFilter.qs 
        
         context = {#'category': category,
               'orders': orders,
               #'myFilter':myFilter
               }


         return render(request, 'core/mrlist.html',context)
				  
def update_view(request,id):
    # dictionary for initial data with
    # field names as keys
    context ={}
 
    # fetch the object related to passed id
    #obj = get_object_or_404(Product, id = id)
    
    item, created = UserItem.objects.get_or_create(
            user_id=request.user.id,
            product_id=id,
            groupproduct = False
        )
    shopcart =UserItem.objects.filter(user=request.user,product_id=id).first()
    obj = get_object_or_404(Product, id = id)
    products = Product.objects.all().filter(groupname=obj.groupname,mother=True).first()
   
    
    

    
    # pass the object as instance in form
    form = GeeksForm(request.POST or None, instance = shopcart)
 
    # save the data from the form and
    # redirect to detail_view
    if form.is_valid():
        fs= form.save(commit=False)
        fs.save()
        if fs.enginecomplete =="complete":
            products.quantity = products.quantity-1
            products.save()
        return HttpResponseRedirect("/")
 
    # add form dictionary to context
    context["form"] = form
 
    return render(request, "core/update_view.html", context)



def addproduct(request,id):
    # dictionary for initial data with
    # field names as keys
    context ={}
 
    # fetch the object related to passed id
    #obj = get_object_or_404(Product, id = id)
    
    item, created = UserItem.objects.get_or_create(
            user_id=request.user.id,
            product_id=id,
            groupproduct = False
        )

    #obj = get_object_or_404(Product, id = id,mother=True)
   

      
    
   
    
    return HttpResponseRedirect("/") 

  

def addproductgroup(request,id):
    # dictionary for initial data with
    # field names as keys
    

    #obj = get_object_or_404(Product, id = id,mother=True)
    obj = get_object_or_404(Product, id = id)
    products = Product.objects.all().filter(groupname=obj.groupname)
    for rs in products: 
        item, created = UserItem.objects.get_or_create(
            user_id=request.user.id,
            product_id=rs.id,
            groupproduct = True,
            quantity=rs.quantity

        )

      
    
   
    
    return HttpResponseRedirect("/") 



def expenseform(request,id):
    # dictionary for initial data with
    # field names as keys
    context ={}
 
    # fetch the object related to passed id
    #obj = get_object_or_404(Product, id = id)
    
    item, created = temppaybill.objects.get_or_create(
            user_id=request.user.id,
            paybillcatogory_id=id,
           
        )
    shopcart =temppaybill.objects.filter(user=request.user,paybillcatogory_id=id).first()
    obj = get_object_or_404(Product, id = id)
   
   
    
    

    
    # pass the object as instance in form
    form = tempbilformm(request.POST or None, instance = shopcart)
 
    # save the data from the form and
    # redirect to detail_view
    if form.is_valid():
        fs= form.save(commit=False)
        fs.save()
        
        return HttpResponseRedirect("/expense")
 
    # add form dictionary to context
    context["form"] = form
 
    return render(request, "core/update_view.html", context)





def groupupdate_view(request,id):
    # dictionary for initial data with
    # field names as keys
    context ={}
 
    # fetch the object related to passed id
    #obj = get_object_or_404(Product, id = id)
    
    item, created = UserItem.objects.get_or_create(
            user_id=request.user.id,
            product_id=id,
            groupproduct=True
        )
    shopcart =UserItem.objects.filter(user=request.user,product_id=id).first()

    obj = get_object_or_404(Product, id = id)
    products = Product.objects.all().filter(groupname=obj.groupname,mother=True).first()
    
    mother =UserItem.objects.filter(user=request.user,product_id=products.id).first()


   
   

    
    
    # pass the object as instance in form
    form = GeeksForm(request.POST or None, instance = shopcart)
 
    # save the data from the form and
    # redirect to detail_view
    if form.is_valid():
        fs= form.save(commit=False)
       
        
        
        fs.save()
        
        if fs.enginecomplete =="complete":
            products.quantity = products.quantity-1
        products.save()


        product = Product.objects.get(pk=id)
    
    # Get the group name of the selected product
        group_name = product.groupname
    
    # Filter products from the same group where mother is equal to 1
        mother_products = Product.objects.filter(groupname=group_name, mother=True)
    
    # Assuming there's only one mother product, you can get its ID
        if mother_products.exists():
            mother_product_id = mother_products.first().id
            # Redirect to the 'group' URL with mother product ID in the URL
            return HttpResponseRedirect(f"/{mother_product_id}/group")
        else:
        # If there's no mother product, simply redirect to the 'group' URL without including the ID parameter.
           return HttpResponseRedirect(f"/{id}/group")
    # add form dictionary to context
    context["form"] = form
 
    return render(request, "core/update_view.html", context)    



def mrupdate_view(request,id):
    # dictionary for initial data with
    # field names as keys
    context ={}
 
    # fetch the object related to passed id
    #obj = get_object_or_404(Product, id = id)
    
    item, created = UserItem.objects.get_or_create(
            user_id=request.user.id,
            product_id=id,
        )
    shopcart =UserItem.objects.filter(user=request.user,product_id=id).first()
    
    # pass the object as instance in form
    form = GeeksForm(request.POST or None, instance = shopcart)
 
    # save the data from the form and
    # redirect to detail_view
    if form.is_valid():
        form.save()
        return HttpResponseRedirect("/mr")
 
    # add form dictionary to context
    context["form"] = form
 
    return render(request, "core/update_view.html", context)


def ggroup(request, id):
    # dictionary for initial data with
    # field names as keys
    context ={}
 
    # fetch the object related to passed id
    obj = get_object_or_404(Product, id = id)
 
    # pass the object as instance in form
    form = GeeksForm(request.POST or None, instance = obj)
   
    # save the data from the form and
    # redirect to detail_view
    if form.is_valid():
        form.save()
        
        return HttpResponseRedirect("/")
 
    # add form dictionary to context
    context["form"] = form
 
    return render(request, "core/update_view.html", context)	




@login_required
def group(request,id):
    form = useritem(request.POST or None, request.FILES or None)
    #shopcart =UserItem.objects.filter(user=request.user)
    obj = get_object_or_404(Product, id = id)
    user_products = UserItem.objects.filter(user=request.user, product__groupname=obj.groupname)
    user_products = user_products.exclude(product_id=obj.id)
    if form.is_valid():
        fs= form.save(commit=False)
        fs.user= request.user
        fs.save()
        

        # for rs in shopcart:
        #         detail = sold()
        #         detail.customer    = fs.customer # Order Id
        #         detail.product_id  = rs.product_id
        #         detail.user  = request.user
        #         detail.quantity  = rs.quantity
        #         detail.added  = rs.added
        #         detail.left = fs.left
        #         detail.discount = fs.discount
        #         detail.save()
        #         product = Product.objects.get(id=rs.product_id)
        #         if rs.credit =='noncredit':    
        #              product.quantity -= rs.quantity
        #              product.save()

     
    total=0
    for rs in user_products:
            total+=rs.product.price * rs.quantity
        
    
    #shopcart =UserItem.objects.filter(user=request.user,product=obj.product)
    products = Product.objects.all().filter(groupname=obj.groupname)
    
    
    
	  
    context = {'products': products, 'user_products': user_products, 'total': total}
    return render(request, 'core/group.html', context)



@login_required
def cashmemo(request,id):
      #cursor = connection['db.sqlite3'].cursor()
      #user_products = Product.objects.raw("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM core_useritem WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_useritem WHERE product_id = core_product.id)")
      #cursor.execute("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM core_useritem WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_useritem WHERE product_id = core_product.id)")
     
      #with connection.cursor() as cursor:
       # cursor.execute("INSERT INTO core_sold SELECT * FROM core_useritem ")
        #cursor.execute("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM  core_sold WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_sold WHERE product_id = core_product.id) ")
        #cursor.execute("UPDATE  core_sold  SET quantityupdate=1")
        
        #row = cursor.fetchone()

         orders=sold.objects.all().filter(order_id=id,groupproduct =False).exclude(quantity=0)
         ordere_de=Order.objects.all().filter(id=id)
         date=Order.objects.all().filter(id=id).last()
         total=0
         for rs in orders:
            total+=rs.price1 * rs.quantity

         total1=total-date.discount
         text=num2words(total1)   
         text= text.replace(',', '')
         #total = sum(product.total_price for product in self.user_products)
         context = {#'category': category,
               'orders': orders,
               'total': total,
               'text': text,
               'date': date,
               'ordere_de':ordere_de,
               'total':total,
               'total1':total1,
               }


         return render(request, 'core/cashmemo1.html',context)








@login_required
def cashmemo1(request,id):
      #cursor = connection['db.sqlite3'].cursor()
      #user_products = Product.objects.raw("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM core_useritem WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_useritem WHERE product_id = core_product.id)")
      #cursor.execute("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM core_useritem WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_useritem WHERE product_id = core_product.id)")
     
      #with connection.cursor() as cursor:
       # cursor.execute("INSERT INTO core_sold SELECT * FROM core_useritem ")
        #cursor.execute("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM  core_sold WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_sold WHERE product_id = core_product.id) ")
        #cursor.execute("UPDATE  core_sold  SET quantityupdate=1")
        
        #row = cursor.fetchone()

         orders=sold.objects.all().filter(order_id=id,groupproduct =False).exclude(quantity=0)
         ordere_de=Order.objects.all().filter(id=id)
         date=Order.objects.all().filter(id=id).last()
         total=0
         for rs in orders:
            total+=rs.price2 * rs.quantity

         total1=total-date.discount
         text=num2words(total1) 
         text= text.replace(',', '')
         due=total- date.paid

         if date.paid - date.totalprice ==0 :
             due = 0
             date.paid= total1
           
         #total = sum(product.total_price for product in self.user_products)
         context = {#'category': category,
               'orders': orders,
               'total': total,
               'text': text,
               'date': date,
               'ordere_de':ordere_de,
               'total':total,
               'total1':total1,
                'due' :due
               }


         return render(request, 'core/cashmemo2.html',context)


@login_required
def chalan(request,id):
      #cursor = connection['db.sqlite3'].cursor()
      #user_products = Product.objects.raw("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM core_useritem WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_useritem WHERE product_id = core_product.id)")
      #cursor.execute("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM core_useritem WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_useritem WHERE product_id = core_product.id)")
     
      #with connection.cursor() as cursor:
       # cursor.execute("INSERT INTO core_sold SELECT * FROM core_useritem ")
        #cursor.execute("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM  core_sold WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_sold WHERE product_id = core_product.id) ")
        #cursor.execute("UPDATE  core_sold  SET quantityupdate=1")
        
        #row = cursor.fetchone()

         orders=sold.objects.all().filter(order_id=id,groupproduct =False)
         ordere_de=Order.objects.all().filter(id=id)
         date=Order.objects.all().filter(id=id).last()
         total=0
         for rs in orders:
            total+=rs.price2 * rs.quantity

         total1=total-date.discount
         text=num2words(total1)   
         #total = sum(product.total_price for product in self.user_products)
         context = {#'category': category,
               'orders': orders,
               'total': total,
               'text': text,
               'date': date,
               'ordere_de':ordere_de,
               'total':total,
               'total1':total1,
               }


         return render(request, 'core/chalan.html',context)    

@login_required
def mrcashmemo(request,id):
      #cursor = connection['db.sqlite3'].cursor()
      #user_products = Product.objects.raw("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM core_useritem WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_useritem WHERE product_id = core_product.id)")
      #cursor.execute("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM core_useritem WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_useritem WHERE product_id = core_product.id)")
     
      #with connection.cursor() as cursor:
       # cursor.execute("INSERT INTO core_sold SELECT * FROM core_useritem ")
        #cursor.execute("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM  core_sold WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_sold WHERE product_id = core_product.id) ")
        #cursor.execute("UPDATE  core_sold  SET quantityupdate=1")
        
        #row = cursor.fetchone()

         orders=mrentryrecord.objects.all().filter(mrentry_id=id,groupproduct =False)
         ordere_de=mrentry.objects.all().filter(id=id)
         date=mrentry.objects.all().filter(id=id).last()
         total=0
         for rs in orders:
            total+=rs.price1 * rs.quantity

         total1=total-date.discount
         text=num2words(total1)   
         #total = sum(product.total_price for product in self.user_products)
         context = {#'category': category,
               'orders': orders,
               'total': total,
               'text': text,
               'date': date,
               'ordere_de':ordere_de,
               'total':total,
               'total1':total1,
               }


         return render(request, 'core/mrcashmemo.html',context)


@login_required
def mreditcashmemo(request,id):
      #cursor = connection['db.sqlite3'].cursor()
      #user_products = Product.objects.raw("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM core_useritem WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_useritem WHERE product_id = core_product.id)")
      #cursor.execute("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM core_useritem WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_useritem WHERE product_id = core_product.id)")
     
      #with connection.cursor() as cursor:
       # cursor.execute("INSERT INTO core_sold SELECT * FROM core_useritem ")
        #cursor.execute("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM  core_sold WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_sold WHERE product_id = core_product.id) ")
        #cursor.execute("UPDATE  core_sold  SET quantityupdate=1")
        
        #row = cursor.fetchone()

        #  orders=sold.objects.all().filter(order_id=id)
        #  ordere_de=Order.objects.all().filter(id=id)
        #  date=sold.objects.all().filter(order_id=id).last()

         orders=mrentryrecord.objects.all().filter(mrentry_id=id,groupproduct =False)
         ordere_de=mrentry.objects.all().filter(id=id)
         date=mrentry.objects.all().filter(id=id).last()

         total=0
         for rs in orders:
            total+=rs.price1 * rs.quantity

         total1=total-date.discount
         text=num2words(total1) 
         products = Product.objects.all()
   
    
         myFilter = OrderFilter(request.GET, queryset=products)
         products = myFilter.qs 
         orderr =mrentry.objects.get(id=id)

         form = mrr(request.POST or None, request.FILES or None, instance = orderr)
         shopcart =UserItem.objects.filter(user=request.user)
         user_products = UserItem.objects.filter(user=request.user)
         total=0
         for gs in user_products:
           total+=gs.price1 * gs.quantity


         total1=0
         
         for gs in user_products:
           total1+=gs.price1 * gs.quantity   


         paginator = Paginator(products, 20) # Show 25 contacts per page.

         page_number = request.GET.get('page')
         pro = paginator.get_page(page_number) 

         if form.is_valid():
           fs= form.save(commit=False)
           fs.user= request.user
           
           fs.invoice_id=fs.added
           fs.totalprice=total-fs.discount
           fs.totalprice1=total1-fs.discount
           fs.due=total-(fs.paid+fs.discount)
           fs.invoice_id=fs.added
        
           fs.save()  
           for rs in shopcart:
                detail = sold()
                detail.customer    = fs.customer
                 # Order Id
                 
                detail.product_id  = rs.product_id
                detail.order_id     =id 
                detail.user  = request.user
                detail.quantity  = rs.quantity
                detail.added  = rs.added
                detail.left = fs.left
                detail.discount = fs.discount
                detail.price1 = rs.price1
                detail.price2 = rs.price2
                detail.engine_no=rs.engine_no
                detail.Phone=fs.Phone
                detail.name=fs.name
                detail.sparename =rs.sparename 
                detail.groupproduct = rs.groupproduct

                detail.save()
                
                shopcart.delete()    
                product = Product.objects.get(id=rs.product_id)
                if rs.credit =='noncredit':    
                     product.quantity -= rs.quantity
                     product.save()

         #total = sum(product.total_price for product in self.user_products)
         context = {#'category': category,
               'orders': orders,
               'total': total,
               'text': text,
               'date': date,
               'ordere_de':ordere_de,
               'total':total,
               'total1':total1,
               'products': products,
               'myFilter':myFilter,
               'form':form,
               'user_products':user_products,
               'pro':pro

               }


         return render(request, 'core/mreditcashmemo.html',context)   






@login_required
def mrfianaleditcashmemo(request,id):
    context ={}
    shopcart =mrentryrecord.objects.get(id=id)
    

    # pass the object as instance in form
    form = mreditformm(request.POST or None, instance = shopcart)
    productnew = Product.objects.get(id=shopcart.product_id)
    qua=productnew.quantity - shopcart.quantity
    # save the data from the form and
    # redirect to detail_view
    if form.is_valid():
        fs= form.save(commit=False)
        form.save()
        #productnew.quantity  += shopcart.quantity
        
        
        productnew.quantity  = qua + fs.quantity
        productnew.save()
       
   

        
        
 
    # add form dictionary to context
    
    context["form"] = form
 
    return render(request, "core/update_view.html", context)







@login_required
def returnno(request,id):
      #cursor = connection['db.sqlite3'].cursor()
      #user_products = Product.objects.raw("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM core_useritem WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_useritem WHERE product_id = core_product.id)")
      #cursor.execute("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM core_useritem WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_useritem WHERE product_id = core_product.id)")
     
      #with connection.cursor() as cursor:
       # cursor.execute("INSERT INTO core_sold SELECT * FROM core_useritem ")
        #cursor.execute("UPDATE core_product SET quantity =core_product.quantity-(SELECT quantity FROM  core_sold WHERE product_id = core_product.id) where EXISTS (SELECT quantity FROM core_sold WHERE product_id = core_product.id) ")
        #cursor.execute("UPDATE  core_sold  SET quantityupdate=1")
        
        #row = cursor.fetchone()

         orders=sold.objects.all().filter(order_id=id)
         ordere_de=Order.objects.all().filter(id=id)
         date=sold.objects.all().filter(order_id=id).last()
         total=0
         for rs in orders:
            total+=rs.price1 * rs.quantity

         total1=total-date.discount
         text=num2words(total1)   
         #total = sum(product.total_price for product in self.user_products)
         context = {#'category': category,
               'orders': orders,
               'total': total,
               'text': text,
               'date': date,
               'ordere_de':ordere_de,
               'total':total,
               'total1':total1,
               }


         return render(request, 'core/return.html',context)




def get_total(self):
        self.total = sum(product.total_price for product in self.user_products)

                                  
def productlist(request):
    return render(request, 'core/productlist.html', {
        'products': Product.objects.all(),
    })

def mrinvoicelist(request):
         orders=mrentry.objects.all().order_by('-id')
         myFilter = mrfilter(request.GET, queryset=orders)
         filtered_orders = myFilter.qs
        
        # Pagination
         paginator = Paginator(filtered_orders, 10)  # Show 5 orders per page
         page_number = request.GET.get('page')
         page_orders = paginator.get_page(page_number)

         context = {
            'orders': page_orders,
            'myFilter': myFilter,  # Pass the filter for the template
        }


         return render(request, 'core/mrinvoicelist.html',context)

# @login_required
# def cart(request):
    
#     a =UserItem.objects.filter(user=request.user).last()
#     form = useritem(request.POST or None, request.FILES or None)
#     form2 = GeeksForm(request.POST or None, request.FILES or None,instance = a)
#     shopcart =UserItem.objects.filter(user=request.user)
#     user_products = UserItem.objects.filter(user=request.user,groupproduct =False)
   
#     total=0
#     total1=0
#     for gs in user_products:
#         total+=gs.price1 * gs.quantity
#     for gs in user_products:
#         total1+=gs.price1 * gs.quantity    
#     outstock=1    
    
#     if request.method=='POST' and 'btnform1' in request.POST: 
#       if form2.is_valid() :
#         fs = form2.save(commit=False)
#         fs.user= request.user 
    
#         fs.groupproduct=False
#         fs.save()
#         obj = get_object_or_404(Product, id = fs.product_id)
#         products = Product.objects.all().filter(groupname=obj.groupname).exclude(groupname='')
       
#         for rs in products: 
#           item, created = UserItem.objects.get_or_create(
#             user_id=request.user.id,
#             product_id=rs.id,
#             groupproduct = True,
#             quantity=rs.subpartquantity * fs.quantity

#           )

#         return HttpResponseRedirect("/")
     

#     # for rs in shopcart:
#     #     product = Product.objects.get(id=rs.product_id)
#     #     if product.quantity < rs.quantity and rs.credit =='noncredit':
#     #                 outstock=0   
#     if request.method=='POST' and 'btnform2' in request.POST: 
#      if form.is_valid() and outstock==1:
#         fs= form.save(commit=False)
#         fs.user= request.user
#         fs.totalprice=total-fs.discount
#         fs.totalprice1=total1-fs.discount
#         fs.due=total-(fs.paid+fs.discount)
#         fs.invoice_id=fs.added

        
#         fs.save()
#         if fs.customer !=None:
#           cus =Customer.objects.filter(id=fs.customer_id).first()
#           cus.balance +=fs.due
#           cus.save()
        
#         obj = dailyreport.objects.all().last()
#         item, created =dailyreport.objects.get_or_create(
#             order_id=fs.id,
#             ammount=obj.ammount+fs.paid,
#             petteyCash=obj.petteyCash,
#             reporttype='INVOICE'
            
#         )
           
        

#         for rs in shopcart:
#                 detail = sold()
#                 detail.customer    = fs.customer
#                  # Order Id
                 
#                 detail.product_id  = rs.product_id
#                 detail.order_id     = fs.id 
#                 detail.user  = request.user
#                 detail.quantity  = rs.quantity
#                 detail.added  = rs.added
#                 detail.left = fs.left
#                 detail.discount = fs.discount
#                 detail.price1 = rs.price1
#                 detail.price2 = rs.price2
#                 detail.engine_no=rs.engine_no
#                 detail.Phone=fs.Phone
#                 detail.name=fs.name
#                 detail.remarks =rs.remarks
#                 detail.sparename =rs.sparename 
#                 detail.groupproduct = rs.groupproduct
                
                
#                 shopcart.delete()    
#                 user_products.delete()
#                 product = Product.objects.get(id=rs.product_id)
#                 product.quantity -= rs.quantity
#                 detail.exchange_ammount=rs.exchange_ammount
#                 detail.costprice=product.price
#                 detail.save()
#                 product.save()
                

                
        
          
            
#         return HttpResponseRedirect("/soldlist")

def mr(request):
    form = mrr(request.POST or None, request.FILES or None)
    shopcart =UserItem.objects.filter(user=request.user)
    user_products = UserItem.objects.filter(user=request.user,groupproduct =False)


    total=0
    for gs in user_products:
        total+=gs.price1 * gs.quantity



    if form.is_valid():
        fs= form.save(commit=False)
        fs.user= request.user
        fs.totalprice=total-fs.discount
        #fs.totalprice1=total1-fs.discount
        fs.due=total-(fs.paid+fs.discount)
        fs.invoice_id=fs.added

        
        fs.save()
        if fs.supplier !=None:
            sup =supplier.objects.filter(id=fs.supplier_id).first()
            sup.balance +=fs.due
            sup.save()


            item, created =supplierbalancesheet.objects.get_or_create(
            mrentry_id=fs.id,
            supplier=sup,
            balance=sup.balance,
            duebalanceadd =fs.due
        )
        
        

        for rs in shopcart:
                detail =mrentryrecord()
                detail.supplier= fs.supplier
                 # Order Id
                 
                detail.product_id  = rs.product_id
                detail.mrentry_id    = fs.id 
                detail.user  = request.user
                detail.quantity  = rs.quantity
                detail.added  = rs.added
                detail.left = fs.left
                detail.price1=rs.price1
                detail.discount = fs.discount
                detail.groupproduct = rs.groupproduct
                detail.save()
                
                shopcart.delete()    
                product = Product.objects.get(id=rs.product_id)
                 
                product.quantity += rs.quantity
                product.price = rs.price1
                product.save()


        obj = dailyreport.objects.all().last()
        item, created =dailyreport.objects.get_or_create(
            mrentry_id=fs.id,
            ammount=obj.ammount+fs.paid,
            petteyCash=obj.petteyCash,
            reporttype='MR ENTRY'
            
        )        
        return HttpResponseRedirect("/mrinvoicelist")



        
    
    category = request.GET.get('category', '')
    search = request.GET.get('search', '')
    mother = request.GET.get('mother', '')

    if category and search and mother:
        products = Product.objects.filter(
            Q(name__icontains=search) & Q(productcatagory__icontains=category) & Q(mother=mother)
        )
    elif category and search:
        products = Product.objects.filter(
            Q(name__icontains=search) & Q(productcatagory__icontains=category)
        )
    elif category and mother:
        products = Product.objects.filter(
            Q(productcatagory__icontains=category) & Q(mother=mother)
        )
    elif search and mother:
        products = Product.objects.filter(
            Q(name__icontains=search) & Q(mother=mother)
        )
    elif category:
        products = Product.objects.filter(Q(productcatagory__icontains=category))
    elif search:
        products = Product.objects.filter(Q(name__icontains=search))
    elif mother:
        products = Product.objects.filter(Q(mother=mother))
    else:
        products = Product.objects.all()
  
    #products = Product.objects.filter(Q(productcatagory__icontains=category))
    totalbalnce=0
    for p in products:
        totalbalnce +=p.price * p.quantity

    mo = Product.objects.filter(mother=True)

  
    # myFilter = OrderFilter(request.GET, queryset=products)
    # products = myFilter.qs 

    # p = Paginator(products, 5)  # creating a paginator object
    # # getting the desired page number from url
    # page_number = request.GET.get('page')
    # try:
    #     page_obj = p.get_page(page_number)  # returns the desired page object
    # except PageNotAnInteger:
    #     # if page_number is not an integer then assign the first page
    #     page_obj = p.page(1)
    # except EmptyPage:
    #     # if page is empty then return last page
    #     page_obj = p.page(p.num_pages)

    
    
    # products=page_obj  
    
    paginator = Paginator(products, 10) # Show 25 contacts per page.

    page_number = request.GET.get('page')
    pro = paginator.get_page(page_number)

    category=  Product.objects.values('productcatagory').distinct()
    
    context = {'category':category,'products': products,'form':form,'user_products':user_products,'pro':pro,'total':total}
    return render(request, 'core/mr.html', context)
   
    
   

 


def returnreasonn(request,id):
    # dictionary for initial data with
    # field names as keys
    context ={}
 
    # fetch the object related to passed id
    #obj = get_object_or_404(Product, id = id)
    
    item, created = returnn.objects.get_or_create(
           sold_id=id,
        )
    shopcart =returnn.objects.filter(sold_id=id).first()
    
    # pass the object as instance in form
    form = returnnform(request.POST or None, instance =None)
 
    # save the data from the form and
    # redirect to detail_view
    #sold = sold.objects.get(id=id)
    solds = get_object_or_404(sold, id = id)
    product = Product.objects.get(id=solds.product_id)
    if form.is_valid():
        fs= form.save(commit=False)
        if solds.returnquantity >= solds.quantity:
            # Add an error to the form
           
            
            messages.error(request, 'Do not have that quantity')
            return redirect('returnreasonn', id=id) 
        
        else:
            fs.customer=solds.customer
            fs.returnprice=fs.cashreturnprice + fs.duereturnprice 
            
            product.quantity += fs.quantity
            product.save()
            
            fs.save()  
            solds.returnquantity = solds.returnquantity + fs.quantity
            solds.save()
            obj = dailyreport.objects.all().last()
            if fs.status == "CASH RETURN":
                item, created =dailyreport.objects.get_or_create(
                    returnn_id=fs.id,
                    ammount=obj.ammount-fs.returnprice,
                    returnprice=fs.cashreturnprice ,
                    returncostprice = solds.costprice
                )
                messages.success(request, 'Return successfully processed!')
                return redirect('returnreasonn', id=id) 


            elif fs.status == "DUE RUTURN": 
                item, created =dailyreport.objects.get_or_create(
                    returnn_id=fs.id,
                    ammount=obj.ammount,
                    returnprice=fs.duereturnprice


                ) 

                solds.order.due -= fs.duereturnprice 
                solds.order.save()

                
                if solds.order.customer !=None:
                    solds.customer.balance -= fs.duereturnprice 
                    solds.customer.save()
                


                    item, created =Customerbalacesheet.objects.get_or_create(
                    order_id=solds.order.id,
                    customer=solds.order.customer,
                    balance=solds.customer.balance,
                    returnn_id=fs.id
                
                )  
                messages.success(request, 'Return successfully processed!')
                return redirect('returnreasonn', id=id)      


                

            else :  
                    item, created =dailyreport.objects.get_or_create(
                        returnn_id=fs.id,
                        ammount=obj.ammount,
                        returnprice=fs.cashreturnprice + fs.duereturnprice
                    )  

                    if solds.order.customer !=None:
                        solds.customer.balance -= fs.duereturnprice 
                        solds.customer.save()
                    


                        item, created =Customerbalacesheet.objects.get_or_create(
                        order_id=solds.order.id,
                        customer=solds.order.customer,
                        balance=solds.customer.balance,
                        returnn_id=fs.id
                
                )  

            
                    messages.success(request, 'Return successfully processed!')
                    return redirect('returnreasonn', id=id) 
            
    # add form dictionary to context
    context["form"] = form
    
    return render(request, "core/update_view.html", context)


@login_required
def editcashmemo(request,id):
    
         orders=sold.objects.all().filter(order_id=id)
         ordere_de=Order.objects.all().filter(id=id)
         date=sold.objects.all().filter(order_id=id).last()
         total=0
         for rs in orders:
            total+=rs.price1 * rs.quantity

         total1=total-date.discount
         text=num2words(total1) 
         products = Product.objects.all()
   
    
         myFilter = OrderFilter(request.GET, queryset=products)
         products = myFilter.qs 
         orderr =Order.objects.get(id=id)



         daily =dailyreport.objects.get(order_id=id)


         form = useritem(request.POST or None, request.FILES or None, instance = orderr)

         shopcart =UserItem.objects.filter(user=request.user)
         user_products = UserItem.objects.filter(user=request.user)
         total=0
         a=sold.objects.all().filter(order_id=id,groupproduct =False)
         for gs in  a  :
           total+=gs.price1 * gs.quantity

         for i in user_products:  
            total+=i.price1 * i.quantity

         total1=0

         for gs in  a  :
           total1+=gs.price2 * gs.quantity

         for i in user_products:  
            total1+=i.price2 * i.quantity

         
        

         paginator = Paginator(products, 20) # Show 25 contacts per page.

         page_number = request.GET.get('page')
         pro = paginator.get_page(page_number) 
         if orderr.customer:
           oldid= orderr.customer.id
         if form.is_valid():
            fs = form.save(commit=False)
            
            fs.user= request.user
           
            fs.invoice_id=fs.added
            fs.totalprice=total-fs.discount
            fs.totalprice1=total1-fs.discount
            fs.due=total-(fs.paid+fs.discount)
            fs.invoice_id=fs.added
            #current daily report paid
            daily.ammount = (daily.ammount-daily.order.paid) + fs.paid
            daily.save()
            fs.save()  
            
            daily_reports_after_id = dailyreport.objects.filter(order_id__gt=id)
                # daily report ammount update
            for i in  daily_reports_after_id:
                i.ammount = i.ammount - daily.order.paid
                i.save()
            for i in  daily_reports_after_id:
                i.ammount = i.ammount + fs.paid  
                i.save()
            

            for rs in shopcart:
                detail = sold()
                detail.customer    = fs.customer
                 # Order Id
                
                detail.product_id = rs.product_id
                detail.order_id     =id 
                detail.user  = request.user
                detail.quantity  = rs.quantity
                detail.added  = rs.added
               
                detail.discount = fs.discount
                detail.price1 = rs.price1
                detail.price2 = rs.price2
                detail.engine_no=rs.engine_no
                detail.Phone=fs.Phone
                detail.name=fs.name
                detail.sparename =rs.sparename 
                detail.groupproduct = rs.groupproduct

                detail.save()
                
                shopcart.delete()    
                product = Product.objects.get(id=rs.product_id)
                   
                product.quantity -= rs.quantity
                product.save()


            if orderr.customer:
              if fs.customer.id != oldid:
                print("Updating customer balance...")  # Informative print statement

        # Update customer balance if customer changed for the order
                orderr.customer.balance -= orderr.due
                orderr.customer.save()

                order_creation_date = orderr.added

        # Efficiently update related CustomerBalanceSheet objects
                Customerbalacesheet.objects.filter(
                    added__gt=order_creation_date, customer=orderr.customer
                ).update(balance=F('balance') - orderr.due)  # F() expression for in-place update

        # Delete existing CustomerBalanceSheet objects associated with the previous order
                Customerbalacesheet.objects.filter(order=orderr).delete()


                cus =Customer.objects.filter(id=fs.customer_id).first()
                cus.balance +=fs.due
        
                cus.save()        
                item, created =Customerbalacesheet.objects.get_or_create(
                    order_id=fs.id,
                    customer=cus,
                    balance=cus.balance,
                    duebalanceadd =fs.due
                )

                

            else:
        # Handle the case where the customer remains the same (optional logic)
                print("Customer did not change for the order.")

    # Complete form saving after all checks and updates
 # Save the form data to create the model instance
                if orderr.customer:
                    cus =Customer.objects.filter(id=daily.order.customer_id).first()

                    olddue=total - daily.order.paid
                    newdue=total - fs.paid
                

    # Update the customer's balance
                
                    cus.balance = (cus.balance - olddue) +newdue

        # Save the updated customer object
                    cus.save()

                    order_creation_date = orderr.added
                    balance_sheets = Customerbalacesheet.objects.filter(added__gte=order_creation_date, customer=fs.customer) 
                    
                    for i in balance_sheets:
                        
                        if(newdue-olddue)>0 :
                            i.balance = i.balance - (newdue-olddue)
                            i.save()
                        else :
                            
                            i.balance = i.balance + (newdue-olddue)
                            i.save()


             
             


           
               
                
               
               
            messages.success(request, 'Form submitted successfully') 

         #total = sum(product.total_price for product in self.user_products)
         context = {#'category': category,
               'orders': orders,
               'total': total,
               'text': text,
               'date': date,
               'ordere_de':ordere_de,
               'total':total,
               'total1':total1,
               'products': products,
               'myFilter':myFilter,
               'form':form,
               'user_products':user_products,
               'pro':pro

               }


         return render(request, 'core/editcashmemo.html',context)    


from django.contrib import messages
from django.shortcuts import render, redirect

@login_required
def fianaleditcashmemo(request, id):
    context = {}
    shopcart = sold.objects.get(id=id)

    # pass the object as an instance in form
    form = soldformm(request.POST or None, instance=shopcart)
    productnew = Product.objects.get(id=shopcart.product_id)
    qua = productnew.quantity + shopcart.quantity
    orders = Order.objects.get(id=shopcart.order_id)
    omitprice1=orders.totalprice - (shopcart.price1 * shopcart.quantity)
    omitprice2=orders.totalprice1 - (shopcart.price2 *  shopcart.quantity)
    if form.is_valid():
        fs = form.save(commit=False)

        # Check if the resulting quantity is negative
        if qua - fs.quantity < 0:
            messages.error(request, 'Do not have that quantity')
            return redirect('fianaleditcashmemo', id=id)  # Replace 'update_view' with your actual URL name

        form.save()

        # Update product quantity
        productnew.quantity = qua - fs.quantity
        productnew.save()

        orders.totalprice = omitprice1 +(fs.quantity *fs.price1)
        orders.totalprice1 = omitprice2 +(fs.quantity *fs.price2)
        orders.due = orders.totalprice -  orders.paid
        orders.save()

        messages.success(request, 'Form submitted successfully')

        # Redirect to the updated URL
        return redirect('editcashmemo', id=shopcart.order.id)

    # add form dictionary to context
    context["form"] = form

    return render(request, "core/update_view.html", context)





@login_required
def billt(request,id):
  context ={}
  form = billfrom(request.POST or None, request.FILES or None)

  if form.is_valid():
           fs= form.save(commit=False)
           fs.order_id= id
           fs.save() 
           obj = dailyreport.objects.all().last()

           messages.success(request, 'Form submission successful')

           order = Order.objects.get(id=id)
           order.due=order.due-fs.ammount
           order.save()
           item, created =dailyreport.objects.get_or_create(
            bill_id=fs.id,
            ammount=obj.ammount+fs.ammount
            
            )

  context["form"] = form
  return render(request, "core/update_view.html", context)



@login_required
def customerlist(request):
    user_list = Customer.objects.all()
    page = request.GET.get('page', 1)

    paginator = Paginator(user_list, 20)
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)

    return render(request, 'core/customerlist.html', { 'users': users })
        
      
  

def search(request):

    results = []

    if request.method == "GET":

        query = request.GET.get('search')

        if query == '':

            query = 'None'

        results = Customer.objects.filter(Q(name__icontains=query)  )

    return render(request, 'core/search_results.html', {'query': query, 'users': results})
        
      

@login_required
def customersolddeatails(request):
    user_list = Customer.objects.all()
    page = request.GET.get('page', 1)

    paginator = Paginator(user_list, 3)
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)

    return render(request, 'core/customerlist.html', { 'users': users })   






@login_required
def suplierlist(request):
    user_list = supplier.objects.all().order_by('-id')
    page = request.GET.get('page', 1)

    paginator = Paginator(user_list, 20)
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)

    return render(request, 'core/supplierlist.html', { 'users': users })




@login_required
def billcustomer(request,id):
  context ={}
  form = billfrom(request.POST or None, request.FILES or None)
  cus = Customer.objects.get(id=id)

  if form.is_valid():
           fs= form.save(commit=False)
           fs.customer_id=id
           fs.save() 
           cus.balance  -= fs.ammount
           cus.save()
           obj = dailyreport.objects.all().last()
           item, created =dailyreport.objects.get_or_create(
            bill_id=fs.id,
            ammount=obj.ammount+fs.ammount
            
            )
           
           item, created =Customerbalacesheet.objects.get_or_create(
            bill_id=fs.id,
            customer=cus,
            balance=cus.balance,
          
        )
           
           messages.success(request, 'Form submission successful')

  context["form"] = form
  return render(request, "core/update_view.html", context)


def dalyreport(request):

         orders=dailyreport.objects.all().order_by('id')
         myFilter =dailyreportfilter(request.GET, queryset=orders)
         orders = myFilter.qs 

         
        #  paginator = Paginator(orders, 15) # Show 25 contacts per page.

        #  page_number = request.GET.get('page')
        #  orders = paginator.get_page(page_number)
         cashsale=0
         duesale=0
         netsale=0
         salesreturn=0
         collection=0
         expense=0
         returnprice=0
        
         orderlist=Order.objects.all()
         mrlist=mrentry.objects.all()
         mrsale=0


         for rs in orders:
           for invoice in orderlist:
                if invoice.id == rs.order_id:
                    cashsale += invoice.paid
                    duesale += invoice.due

           for mrentri in mrlist:  
                 if mrentri.id == rs.mrentry_id:      
                    mrsale += mrentri.totalprice
           returnprice += rs.returnprice
    
           if rs.bill and rs.bill.ammount is not None:
                collection += rs.bill.ammount
           else:
                collection += 0  # Adding 0 when rs.bill.amount is None
           expense  =  expense +  rs.billexpense
        
             



          



        
         context = {#'category': category,
               'orders': orders,
               'myFilter':myFilter,
                'cashsale':cashsale,
                'duesale':duesale,
                'netsale':cashsale + duesale ,
                'mrsale' : mrsale,
                'returnprice':returnprice,
                'collection':collection,
                'expense' :expense,
               }


         return render(request, 'core/daily-report.html',context)



def dalyreportsearch(request):
    
    return render(request, "core/a.html")    

def expense(request):

         orders=dailyreport.objects.all().last()
         lastpaybill=paybill.objects.all().last()
         #myFilter =dailyreportfilter(request.GET,queryset=orders)
         user_products = temppaybill.objects.filter(user=request.user)
         form = dailyreportt(request.POST or None, request.FILES or None)
         total=0
        
         for gs in user_products:
           total+=gs.ammount 
         if request.method=='POST' and 'btnform1' in request.POST:
           
           if form.is_valid() :
           
             fs = form.save(commit=False)
             item, created =paybill.objects.get_or_create(

             pettycashbalance=orders.petteyCash +fs.petteyCash,
             reloadpetteycash=fs.petteyCash,
             typecat="receive"
             )
             fs.billexpense = fs.petteyCash
             fs.ammount =orders.ammount -fs.petteyCash
             
             fs.petteyCash =fs.petteyCash +orders.petteyCash
             fs.reporttype='FUND TRANSFER'
             
              
             fs.save()
             return HttpResponseRedirect("/expense")
         
         form2 = CorportepayForm(request.POST or None, request.FILES or None)

         if request.method=='POST' and 'btnform2' in request.POST:
           if form2.is_valid() :
           
             fs1 = form2.save(commit=False)
            #  fs1.billexpense = fs1.petteyCash
            #  fs1.ammount =orders.ammount -fs1.petteyCash
            #  fs1.petteyCash =orders.petteyCash
            #  fs1.reporttype='CORPORATE'
             fs1.save()
             item, created = dailyreport.objects.get_or_create(
            billexpense=fs1.ammount,
            ammount=orders.ammount - fs1.ammount,
            petteyCash=orders.petteyCash,
            reporttype = 'CORPORATE' " " + (str(fs1.supplier) if fs1.supplier else '') + (str(fs1.corpocatagory) if fs1.corpocatagory else '')
             )
             if fs1.supplier : 
                supplier_id = fs1.supplier.id  #

    # Query the supplier from the Supplier model
                #supplier = supplier.objects.get(pk=supplier_id)

                supp=supplier.objects.filter(id=supplier_id).first()
                
    # Assuming there is a balance field in the Supplier model, deduct the balance
                
                supp.balance = supp.balance -fs1.ammount
                supp.save()



                item, created =supplierbalancesheet.objects.get_or_create(
           
            supplier=supp,
            balance=supp.balance,
            corportepay=fs1
        )



                
             messages.success(request, 'Form submitted successfully')
             return HttpResponseRedirect("/expense")

         form3 = dailyreportt(request.POST or None, request.FILES or None)

         if request.method=='POST' and 'btnform3' in request.POST:
            if form3.is_valid() :
           
             fs1 = form2.save(commit=False)
             fs1.billexpense = fs1.petteyCash
             fs1.ammount =orders.ammount -fs1.petteyCash
             fs1.petteyCash =orders.petteyCash
             fs1.reporttype='COMMISSION'
             fs1.save()
            
             return HttpResponseRedirect("/expense")   
            
         if request.method=='POST' and 'btnform4' in request.POST:
            if form3.is_valid() :
           
             fs1 = form2.save(commit=False)
             fs1.billexpense = fs1.petteyCash
             fs1.ammount =orders.ammount -fs1.petteyCash
             fs1.petteyCash =orders.petteyCash
             fs1.reporttype='Discount'
             fs1.save()
            
             return HttpResponseRedirect("/expense")    

              

               
         products =  paybillcatogory.objects.all()







   
    
         myFilter = expensefilter(request.GET, queryset=products)
         products = myFilter.qs    
        
         context = {#'category': category,
               'orders': orders,
               'form':form,
               'myFilter':myFilter,
               'pro':products,
               'user_products':user_products,
               'total':total,
               'form2':form2,
               'form3':form3
               }


         return render(request, 'core/expense.html',context)

def expensestore(request):

         orders=dailyreport.objects.all().last()
         #myFilter =dailyreportfilter(request.GET,queryset=orders)
         user_products = temppaybill.objects.filter(user=request.user)
         
         total=0
         total1=0
         for gs in user_products:
           total+=gs.ammount 

         

         for rs in  user_products:
                detail = paybill()
                detail.paybillcatogory =rs.paybillcatogory
                paybilllast=paybill.objects.all().last()
                 # Order Id
                detail.pettycashbalance=paybilllast.pettycashbalance-rs.ammount
                detail.ammount  = rs.ammount 
                detail.remarks    = rs.remarks
                detail.user  = request.user
                detail.typecat="payment"
                detail.save()
                
                user_products.delete()

         item, created =dailyreport.objects.get_or_create(
            
            petteyCash=orders.petteyCash-total,
            billexpense=total,
            ammount=orders.ammount,
            reporttype="office expense"
            )      
                 

         return HttpResponseRedirect("/expense")



def delete_item(request,id):
        item = UserItem.objects.get(id=id)
        #item1 = sold.objects.get(pk=product_pk)
        item.delete()         
        return HttpResponseRedirect(reverse('cart'))

def delete_itemgroup(request, id):
    # Assuming UserItem has a field called 'product_id' which stores the ID of the product
    items = UserItem.objects.filter(product_id=id)
    
    # Delete the items associated with the given product ID
    items.delete()

    product = Product.objects.get(pk=id)
    
    # Get the group name of the selected product
    group_name = product.groupname
    
    # Filter products from the same group where mother is equal to 1
    mother_products = Product.objects.filter(groupname=group_name, mother=True)
    
    # Assuming there's only one mother product, you can get its ID
    if mother_products.exists():
        mother_product_id = mother_products.first().id
        # Redirect to the 'group' URL with mother product ID in the URL
        return HttpResponseRedirect(f"/{mother_product_id}/group")
    else:
        # If there's no mother product, simply redirect to the 'group' URL without including the ID parameter.
        return HttpResponseRedirect(f"/{id}/group")

def deleteinvoice(request, id):
    item = sold.objects.filter(order_id=id)
    updates = {}

    for a in item:
        # Use F() expression to update the quantity directly in the database
        Product.objects.filter(id=a.product.id).update(quantity=F('quantity') + a.quantity)
    
    item.delete()      

    item1 = get_object_or_404(Order, id=id)
    
    daily_reports_after_id = dailyreport.objects.filter(order_id__gt=id)
    
    # Daily report amount update
    for i in daily_reports_after_id:
        i.ammount -= item1.paid
        i.save()

    if item1.customer != None:
        item1.customer.balance -= item1.due
        item1.customer.save()
        order = Order.objects.get(id=id)
        order_creation_date = order.added
        
        # Query all balance sheet entries created after the order's creation date
        balance_sheets = Customerbalacesheet.objects.filter(added__gt=order_creation_date, customer=order.customer) 
            
        for i in balance_sheets:
            i.balance -= order.due
            i.save()
    
    item1.delete() 
    messages.success(request, 'invoice deleted  successfully')
    return HttpResponseRedirect("/soldlist")


class CountryAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return Product.objects.none()

        qs = Product.objects.all()

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs        

def sms(request):
    # Data to pass in the context

    current_date = dt_datetime.now().strftime("%Y-%m-%d")
    orders=dailyreport.objects.all().last()
    orders_not_sent = Order.objects.filter(smssend=False)

# Calculate the sum of totalprice, due, and paid
    total_sale = orders_not_sent.aggregate(total_totalprice=Sum('totalprice'))['total_totalprice'] or 0
    cash_sale = orders_not_sent.aggregate(total_paid=Sum('paid'))['total_paid'] or 0
    bill_receive = bill.objects.filter(smssend=False).aggregate(total_amount=Sum('ammount'))['total_amount'] or 0
    closing_balance = orders.ammount

# Construct the message including the current date
    message = f"On {current_date}, Total sale: {total_sale}, Cash sale: {cash_sale}, Bill received: {bill_receive}, Closing balance: {closing_balance}"

     #message = f"On {current_date}, Total sale: {total_sale}, Cash sale: {cash_sale}, Bill received: {bill_receive}, Closing balance: {closing_balance}"

    context = {
    'message': message,
    # Include other context variables here if needed
}
    # Render the template with context data
    return render(request, "core/sms_template.html", context)    



import requests
def smssend(request):
    # Data to pass in the context

    current_date = dt_datetime.now().strftime("%Y-%m-%d")
    orders=dailyreport.objects.all().last()
    orders_not_sent = Order.objects.filter(smssend=False)

# Calculate the sum of totalprice, due, and paid
    total_sale = orders_not_sent.aggregate(total_totalprice=Sum('totalprice'))['total_totalprice'] or 0
    cash_sale = orders_not_sent.aggregate(total_paid=Sum('paid'))['total_paid'] or 0
    bill_receive = bill.objects.filter(smssend=False).aggregate(total_amount=Sum('ammount'))['total_amount'] or 0
    closing_balance = orders.ammount

# Construct the message including the current date
    message = f"On {current_date}, Total sale: {total_sale}, Cash sale: {cash_sale}, Bill received: {bill_receive}, Closing balance: {closing_balance}"

     #message = f"On {current_date}, Total sale: {total_sale}, Cash sale: {cash_sale}, Bill received: {bill_receive}, Closing balance: {closing_balance}"
    




    

    url = 'https://login.esms.com.bd/api/v3/sms/send'
    headers = {
    'Authorization': 'Bearer 297|fOiAZt4BLS5eL1MTjmk4UZvWlHPaOnsIhpW7ivqq',
    'Content-Type': 'application/json'
}
    recipients = ["8801814392710","8801922542456"]
    sender_id = "8809601001296"
    #

    for recipient in recipients:
        data = {
            "recipient": recipient,
            "sender_id": sender_id,
            "type": "plain",
            "message": message
        }

        response = requests.post(url, headers=headers, json=data)

        print(f"Recipient: {recipient}")
        print(f"Status code: {response.status_code}")
        print(f"Response text: {response.text}")
        print()

#recipients = ['8801311848771', '8801814392710']
        data = {
            "recipient": "8801814392710",
            "sender_id": "8809601001296",
            "type": "plain",
            "message": "Rohan is fucking madarchud!"
        }

        response = requests.post(url, headers=headers, json=data)

        if response.status_code != 200:
            # If there's an error, redirect with an error message
            return HttpResponseRedirect("/sms?error=Error occurred while sending SMS. Please try again later.")
        
        orders_not_sent.update(smssend=True)
        all_bills = bill.objects.all()

# Loop through each bill object and set smssend to True
        for bill_obj in all_bills:
            bill_obj.smssend = True
            bill_obj.save()

    # If all SMS sent successfully, redirect with a success message
    return HttpResponseRedirect("/sms?success=SMS sent successfully.")  




def salesreport(request):
         start_date = request.GET.get('start_date')
         end_date = request.GET.get('end_date')
         if not end_date:
           
           end_date =dt_datetime.now().strftime('%Y-%m-%d')

         
   
         orders=dailyreport.objects.all().order_by('id')
         myFilter =dailyreportfilter(request.GET, queryset=orders)
         orders = myFilter.qs
         s=0
         c=0
         e=0
         profit=0
         l=0
         open=0
        
         cash=0
         dew=0
         open2=0
         corporrateex=0
         discount=0
         billa=bill.objects.all()
         closeblance=0
         comm=0
         returnprice=0
         returncostprice=0
         soldlist=sold.objects.all().filter(groupproduct =False)
         orderlist=Order.objects.all()
         officeexpense=0
         pettycashtransfer = 0
         for rs in orders :
            
            # if l==0:
            #   open=rs.ammount
            #   l=l+1
            
            if rs.reporttype == 'office expense':
               officeexpense=rs.billexpense+officeexpense
            returnprice=returnprice+rs.returnprice
            returncostprice=returncostprice+rs.returncostprice
            corporrateex=rs.billexpense+ corporrateex
            if rs.reporttype == "COMMISSION":
               comm=comm+rs.billexpense  
            if rs.reporttype == "Discount":     
               discount=rs.billexpense +discount     

            if rs.reporttype == "FUND TRANSFER":     
               pettycashtransfer=rs.billexpense +pettycashtransfer     

            for b in soldlist: 
              if b.order_id == rs.order_id and rs.order_id  is not None:
                 s=b.total_price+s
                 c=b.total_costprice+c
                 e=b.exchange_ammount+e
                 profit=profit+b.totalprofit

            for  t in orderlist:      
               if t.id == rs.order_id and rs.order_id  is not None:
                  cash=t.paid+cash
                  
            for  ac in billa:      
               if ac.order_id == rs.order_id and rs.order_id  is not None:
                  dew=ac.ammount+dew    

         
         #soldlist=sold.objects.filter(order_id__in=s)
         
         
         paginator = Paginator(orders, 15) # Show 25 contacts per page.

         page_number = request.GET.get('page')
         orders = paginator.get_page(page_number)
         

         for x in list(reversed(list(orders)))[0:1]:
            closeblance=x.ammount
        
         if open is not None and  cash is not None and  dew is not None:
           open2= open +dew+cash
         withoutex=s-e
         aftercommmision=closeblance+corporrateex
         totalcost=comm+discount+c+ returnprice
         netsale =s-returnprice
         grossprofit=s-totalcost
         netprofit=grossprofit- officeexpense
         if c == 0 :
             percentageprofit=0
         if c != 0 :   
            percentageprofit=(grossprofit/c ) *100
         duesales=withoutex-cash
         pettycashreportbalnce=closeblance+corporrateex
         commisiondisreportbalnce=pettycashreportbalnce+pettycashtransfer
         cashreturnbalance=commisiondisreportbalnce+comm+discount
         collentionbalance= cashreturnbalance+returnprice
         openbalance=collentionbalance-(cash+dew)
         #newreturncost =returnprice - returncostprice



        #for calculating previous time duration  order 
         

         orders_within_time_range = dailyreport.objects.filter(
    added__range=(start_date, end_date)
)

# Retrieve returnn instances within the same time range
         returnn_within_time_range = returnn.objects.filter(
    sold__order__added__range=(start_date, end_date)
)

# Exclude dailyreport instances where associated returnn objects fall within the time range
         orders_not_in_range = orders_within_time_range.exclude(
    id__in=returnn_within_time_range.values_list('sold__order__id', flat=True)
)           
         oldreturnpricet=0
         oldreturncostt=0
         for rs in orders_not_in_range :
              
             oldreturnpricet=rs.returnprice+oldreturnpricet
                
         netsale2 =s - (returnprice-oldreturnpricet)

         context = {#'category': category,
               'pettycashreportbalnce':pettycashreportbalnce,
               'commisiondisreportbalnce':commisiondisreportbalnce,
               'cashreturnbalance':cashreturnbalance,
               'collentionbalance':collentionbalance,
               'openbalance':openbalance,
               'orders': orders,
               'myFilter':myFilter,
               'a':soldlist,
               'duesales':duesales,
                'c':c,
                's':s,
                'e':e,
                'pettycashtransfer':pettycashtransfer,
                'percentageprofit':percentageprofit,
                'grossprofit': grossprofit,
                'netprofit':netprofit,
                'totalcost':totalcost,
                'withoutex':withoutex,
                'profit':profit,
                'open':open,
                'cash':cash,
                'dew' :dew,
                'open2':open2,
                'comm' :comm,
                'discount':discount , 
                'closeblance':closeblance,
                'corporrateex':corporrateex,
                'aftercommmision':aftercommmision,
                'returnprice':returnprice,
                 'returncostprice': returncostprice,
                'officeexpense':officeexpense,
                'start_date': start_date,
                 'end_date': end_date,
                 'netsale' :netsale,
                 'netsale2' :netsale2,
                 'oldreturnpricet':oldreturnpricet,
               }  
    
         return render(request, "core/salesreport.html",context )           


def expensereport(request):
         credit1 =0
         debit1= 0
          

         orders=paybill.objects.all().order_by('id')
         myFilter =paybillfilter(request.GET, queryset=orders)
         orders = myFilter.qs 
         
         
         for rs in orders :
             credit1 = credit1 + (rs.reloadpetteycash if rs.reloadpetteycash is not None else 0)
             debit1 = debit1 + (rs.ammount if rs.ammount is not None else 0)
        
         context = {#'category': category,
               'orders': orders,
               'myFilter':myFilter,
               'credittotal'  :credit1,
               'debit1total'   :debit1
               }


         return render(request, 'core/expensereport.html',context)



def corporatepayment(request):
    suppliers = supplier.objects.all()
    if request.method == 'POST':
        selected_supplier_id = request.POST.get('supplier')
        amount = request.POST.get('amount')
        des = request.POST.get('description')
        selected_supplier = supplier.objects.get(id=selected_supplier_id)
        selected_supplier.balance = selected_supplier.balance - int(amount)
        selected_supplier.save()

        orders=dailyreport.objects.all().last()
        item, created =paybill.objects.get_or_create(

             pettycashbalance=orders.petteyCash - int(amount),
             ammount =int(amount),
             typecat="corporate payment " + selected_supplier.name,
             remarks = des
             )
        item, created =dailyreport.objects.get_or_create(
            
             ammount =orders.ammount ,
             billexpense= int(amount) ,
             reporttype="corporate payment " + selected_supplier.name,
             petteyCash = orders.petteyCash - int(amount)
             
             )
        
        
        return redirect('cart')

    context = {#'category': category,
               'suppliers': suppliers ,
              
               }
    
    return render(request, "core/corporatepayment.html",context)  


class AutocompleteView(View):
    def get(self, request):
        query = request.GET.get('term', '')
        countries = Product.objects.filter(name__icontains=query)[:10]
       
        results = []
        for country in countries:
            country_json = {
                'id': country.id,
                'label': country.name,
                'value': country.productcatagory,
            }
            results.append(country_json)
        return JsonResponse(results, safe=False) 


#### apiproductlist

@api_view(['GET'])
def api_productlist(request):
    tasks = UserItem.objects.filter(groupproduct=False).order_by('-id')
    serializer = TaskSerializer(tasks, many=True)
    #total_sum = tasks.aggregate(total_sum=Sum('price1'))['total_sum']  
    total=0
   
    for gs in tasks :
        total+=gs.price1 * gs.quantity

    response_data = {
        'tasks': serializer.data,
        'total_sum': total  # Include the total sum in the response
    }

    return Response(response_data, status=status.HTTP_200_OK)


@csrf_exempt
def delete_user_item(request, item_id):
    if request.method == 'DELETE':
        try:
            with transaction.atomic():
                user_item = get_object_or_404(UserItem, id=item_id)
                product_id = user_item.product_id
                groupname = user_item.product.groupname
                
                # Delete related UserItems in the same group
                if  user_item.product.mother == 1:
                    products_to_delete = UserItem.objects.filter(
                        product__groupname=groupname,
                        product_id__isnull=False  # Ensure valid product_id
                    )
                    products_to_delete.delete()

                    




                
                # Delete the primary UserItem
                user_item.delete()
                
                # Debugging output
                print("UserItem and related records deleted successfully.")
                
                return JsonResponse({"message": "UserItem and related records deleted successfully."})
                
        except UserItem.DoesNotExist:
            return JsonResponse({"error": "UserItem with ID {} does not exist.".format(item_id)})
        except Product.DoesNotExist:
            return JsonResponse({"error": "Product with ID {} does not exist.".format(product_id)})
        except Exception as e:
            return JsonResponse({"error": "An error occurred: {}".format(e)})







    


@csrf_exempt
def apiaddproduct(request,id):
    # dictionary for initial data with
    # field names as keys
    context ={}
 
    # fetch the object related to passed id
    #obj = get_object_or_404(Product, id = id)
    
    item, created = UserItem.objects.get_or_create(
            user_id=request.user.id,
            product_id=id,
            groupproduct = False
        )

    #obj = get_object_or_404(Product, id = id,mother=True)
   

      
    return JsonResponse({'error': 'Method not allowed'}, status=405)





# product = models.ForeignKey(Product, on_delete=models.CASCADE,null=True,related_name='product')
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     quantity = models.PositiveIntegerField(default=0,null=True)
#     price1 = models.DecimalField(
#         default=0,
#         decimal_places=0,
#         max_digits=10,
#         validators=[MinValueValidator(0)],
#         null=True
#     )
#     price2 = models.DecimalField(
#         default=0,
#         decimal_places=0,
#         max_digits=10,
#         validators=[MinValueValidator(0)],
#         null=True
#     )
#     added = models.DateTimeField(auto_now_add=True)
#     customer = models.ForeignKey(Customer, on_delete=models.CASCADE,null=True,blank=True)
#     model_no = models.CharField(max_length=200,blank=True,null=True)
#     engine_no = models.CharField(max_length=200,null=True,default='',blank=True)
#     status=models.CharField(max_length=10,choices=PRODUCT,default='Direct',null=True)
#     credit=models.CharField(max_length=10,choices=credit,default='noncredit',null=True)
#     productype=models.CharField(max_length=100,choices=PRODUCT1,default='LocalContainer',null=True)
#     enginecomplete=models.CharField(max_length=10,choices=engine,default='incomplete',null=True)
#     remarks = models.CharField(max_length=500,blank=True,null=True)
#     exchange_ammount = models.PositiveIntegerField(default=0,null=True)
#     #exchange_engine = models.CharField(max_length=500,blank=True,default='')
#     sparename = models.CharField(max_length=200,null=True,blank=True)
#     groupproduct = models.BooleanField(null=True,blank=True)


def process_products(request, product_id, quantity):
    shopcart = UserItem.objects.filter(user=request.user, product_id=product_id).first()
    obj = get_object_or_404(Product, id=product_id)
    motherproduct = Product.objects.filter(groupname=obj.groupname, mother=True).first()
    products = Product.objects.filter(groupname=obj.groupname).exclude(groupname='')
   
    for rs in products:
        item, created = UserItem.objects.get_or_create(
            user_id=request.user.id,
            product_id=rs.id,
            groupproduct = True,
            quantity=rs.subpartquantity * quantity
        )
        print(rs.id)

    




@csrf_exempt
def userItemstore(request):
    if request.method == 'POST':
        # Retrieve the form data from the request
        
        json_data = json.loads(request.body)
            # Extract the required fields from the JSON data
        productId = json_data.get('productId')
        product = json_data.get('product')
        quantity = json_data.get('quantity')
        price1 = json_data.get('price1')
        price2 = json_data.get('price2')
        status = json_data.get('status')
        engine = json_data.get('engine')
        exchangeAmount = json_data.get('exchangeAmount')
        spareName = json_data.get('spareName')
        remarks = json_data.get('remarks')
        print(productId)
        obj = get_object_or_404(Product, id = productId)
        # Create an object using the form data


        if int(quantity) > int(obj.quantity) :
            messages.error(request, 'Do not have that quantity')
            return redirect('cart') 
        if int(quantity) <= int(obj.quantity) :
            obj = UserItem.objects.create(
                product_id=productId,
                user_id=request.user.id,
                quantity=quantity,
                price1=price1,
                price2=price2,
                groupproduct = False,
                status= status,
                remarks = remarks ,
                exchange_ammount =exchangeAmount ,
                sparename =spareName ,
                enginecomplete = engine

                
            )

        # if qua - fs.quantity < 0:
        #     messages.error(request, 'Do not have that quantity')
        #     return redirect('fianaleditcashmemo', id=id)  # Replace 'update_view' with your actual URL name

        # form.save()

        # # Update product quantity
        # productnew.quantity = qua - fs.quantity
        # productnew.save()

        # messages.success(request, 'Form submitted successfully')

        
        
       
        obj = get_object_or_404(Product, id = productId)
        motherproduct = Product.objects.all().filter(groupname=obj.groupname,mother=True).first()
        if  obj.mother ==1 :
            products = Product.objects.filter(groupname=obj.groupname).exclude(groupname='').exclude(id=obj.id)
            

            # allsubquantity=0
            # for product in products:
            #     if int(product.quantity) < int(product.subpartquantity)*int(quantity) :
            #         allsubquantity=1

            # print(str(allsubquantity) + "JJJJJ")        
            # if allsubquantity ==0:
            for product in products:
                print(product.id)
                
        # Create an object using the form data
                
                print(product.subpartquantity )
                totalquan=product.subpartquantity * int(quantity)
                obj = UserItem.objects.create(
                product_id=product.id,
            
            
                user_id=request.user.id,
                quantity =  totalquan ,
                price1=0,
                price2=0,
                groupproduct = True,
                status= status,
                remarks = remarks ,
                exchange_ammount =exchangeAmount ,
                sparename =spareName ,
                enginecomplete = engine

                
            )







       
    
    # pass the object as instance in form
    



        # You can perform additional operations with the created object if needed

        # Return a JSON response
        return JsonResponse({"message": "Form data received and object created successfully"})

    # Return an error response for other request methods
    return JsonResponse({"error": "Invalid request method"}, status=405)






@csrf_exempt
def mruserItemstore(request):
    if request.method == 'POST':
        # Retrieve the form data from the request
        
        json_data = json.loads(request.body)
            # Extract the required fields from the JSON data
        productId = json_data.get('productId')
        product = json_data.get('product')
        quantity = json_data.get('quantity')
        price1 = json_data.get('price1')
        price2 = json_data.get('price2')
        status = json_data.get('status')
        engine = json_data.get('engine')
        exchangeAmount = json_data.get('exchangeAmount')
        spareName = json_data.get('spareName')
        remarks = json_data.get('remarks')
        print(productId)
        obj = get_object_or_404(Product, id = productId)
        # Create an object using the form data


      
        
        obj = UserItem.objects.create(
                product_id=productId,
                user_id=request.user.id,
                quantity=quantity,
                price1=price1,
                price2=price2,
                groupproduct = False,
                status= status,
                remarks = remarks ,
                exchange_ammount =exchangeAmount ,
                sparename =spareName ,
                enginecomplete = engine

                
            )

        # if qua - fs.quantity < 0:
        #     messages.error(request, 'Do not have that quantity')
        #     return redirect('fianaleditcashmemo', id=id)  # Replace 'update_view' with your actual URL name

        # form.save()

        # # Update product quantity
        # productnew.quantity = qua - fs.quantity
        # productnew.save()

        # messages.success(request, 'Form submitted successfully')

        
        
       
        obj = get_object_or_404(Product, id = productId)
        motherproduct = Product.objects.all().filter(groupname=obj.groupname,mother=True).first()
        if  obj.mother ==1 :
            products = Product.objects.filter(groupname=obj.groupname).exclude(groupname='').exclude(id=obj.id)
            

            # allsubquantity=0
            # for product in products:
            #     if int(product.quantity) < int(product.subpartquantity)*int(quantity) :
            #         allsubquantity=1

            # print(str(allsubquantity) + "JJJJJ")        
            # if allsubquantity ==0:
            for product in products:
                print(product.id)
                
        # Create an object using the form data
                
                print(product.subpartquantity )
                totalquan=product.subpartquantity * int(quantity)
                obj = UserItem.objects.create(
                product_id=product.id,
            
            
                user_id=request.user.id,
                quantity =  totalquan ,
                price1=0,
                price2=0,
                groupproduct = True,
                status= status,
                remarks = remarks ,
                exchange_ammount =exchangeAmount ,
                sparename =spareName ,
                enginecomplete = engine

                
            )







       
    
    # pass the object as instance in form
    



        # You can perform additional operations with the created object if needed

        # Return a JSON response
        return JsonResponse({"message": "Form data received and object created successfully"})

    # Return an error response for other request methods
    return JsonResponse({"error": "Invalid request method"}, status=405)





from django.http import JsonResponse
from django.views.generic import View


class CustomerAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Customer.objects.all()

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs
    
    
         