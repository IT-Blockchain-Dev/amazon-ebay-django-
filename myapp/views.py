from django.views.decorators.csrf import csrf_exempt
# from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ebaysdk import response
from ebaysdk.trading import Connection as Trading
from ebaysdk.exception import ConnectionError
from ebaysdk.policies import Connection as Policies
from django.db import connection
import json

@api_view(['GET', 'POST'])
def getPolicy(request):
  
    if request.method == 'POST':
        token1 = request.POST.get('user_token')
        # token1 = 'AgAAAA**AQAAAA**aAAAAA**KlviYQ**nY+sHZ2PrBmdj6wVnY+sEZ2PrA2dj6MHlYapDpOEqAydj6x9nY+seQ**d8oGAA**AAMAAA**zSMLmj+enSYAP9QMNZTqiPqso2+OtzbE7iPpz1p82DWfR0Og+7kXbyiEoGG6x0RkMYQcZ9ZXPkqfDHnRCVu4zKQry7gFq2ean5Kxu4g8B6Hj76Eu3Li6mTu/d1+jJwbGSl8IVjE2Ieo7MZRDUQwjnuYOSElFw5gTfLSY5Wa1ZdEGnaqltPY0yGtvtUYmkVvNCCy/5vdA/wqce0ixfiM4QnCj3vdWQzFasm33RhNiaisTxz9Cr6KkkD8IM2fR4JhUHhB/c2xS9hhxDMA6E4lnsxh82LMKh+O8xro3A+++j9iJUna6mCnc82DuhQGLM5sTCSaZeJlhr+RgjWKekbFz0pqXLq4Se/Y2GcR040ipKCbMy72vyfeQzMcfY0gsXGXOsBrHt9wHpAhWNU1wZnZjjyb8ycDn//ggxK5QkfmrOiJb3yHLXS/Fhrh1ZZ9bIrjR4i8s0h+DMegLFU7VOsXjVnkATJdb0R2qP7Uakm1Tg0Wb9Lk+pTLev5fgdyrIrkoFLVF35E+TfL8Ye1RQBArDYV9iDd3Ct4c35h97wqOYmGwG8Kv23NpGFwFSHiqmbY5uWnK9YI44ny6vECQPabrynYC5T5f4KyEb6GJHbKi0IC2uhTthSVmbGEnrbQ1lHGo2u65ZirBfZZJpc/88VD4EZ7vd/8ke8ypzwKGIwMpf4+NrjC8Pt1y4b/Gshkm+cE8TpDJnEP8jCLPWdvS2XHhGTS92ius3ebA/BfVyXAqIPveJeyWaV/7CZefs7cq/kZwX'
        api = Policies(domain='svcs.ebay.com',appid='arsensah-myapp-PRD-41d9f5f51-f3aac787',
        certid='PRD-1d9f5f511ac9-005d-4560-8eee-672f',devid='96d594f7-cbdf-434d-b1ed-42d5b1a26adc',
        token=token1, config_file=None)
    res = api.execute('getSellerProfiles')
    result = res.dict()
    paymentProfiles = result['paymentProfileList']['PaymentProfile']
    returnProfiles = result['returnPolicyProfileList']['ReturnPolicyProfile']
    shippingProfiles = result['shippingPolicyProfile']['ShippingPolicyProfile']
    paymentlist = []
    returnlist = []
    shippinglist = []
    businessPolicyObject = {}
    for payment in paymentProfiles:

        businessPolicyObject = {'policyName':payment['profileName'],'policyID':payment['profileId']}
        paymentlist.append(businessPolicyObject)
    for returnPolicy in returnProfiles:

        businessPolicyObject = {'policyName':returnPolicy['profileName'],'policyID':returnPolicy['profileId']}
        returnlist.append(businessPolicyObject)
    for shipping in shippingProfiles:
        
        businessPolicyObject = {'policyName':shipping['profileName'],'policyID':shipping['profileId']}
        shippinglist.append(businessPolicyObject)
    # data = request.POST.get('user_id')
    data = {'paymentlist':paymentlist,'returnlist':returnlist,'shippinglist':shippinglist}
    return Response(data, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def getProduct (request):
    with connection.cursor() as cursor:
        cursor.execute("select * from product_information where user_id=%s and importname_id=%s",
        [request.POST.get('user_id'),request.POST.get('importname_id')])
        row = cursor.fetchall()
        row_headers=[x[0] for x in cursor.description] #this will extract row headers
    
        productlist=[]
        for result in row:
           productlist.append(dict(zip(row_headers,result)))
        
    
    return Response(productlist,status=status.HTTP_201_CREATED)  

@api_view(['POST'])
def listProduct(request):
    with connection.cursor() as cursor:
        cursor.execute("select * from business_policy")
        row = cursor.fetchall()
        row_headers=[x[0] for x in cursor.description] #this will extract row headers
    
        businessPolicy=[]
        for result in row:
           businessPolicy.append(dict(zip(row_headers,result)))
    
    token1 = businessPolicy[0]['user_token']
    
    ebay_categoryID = request.POST.get('ebay_category')
    currency_rating = businessPolicy[0]['currency_rating']
    asin = request.POST.get('asin')
    with connection.cursor() as cursor:
        cursor.execute("select image_url from product_image where asin=%s",[asin])
        row = cursor.fetchall()
        row_headers=[x[0] for x in cursor.description] #this will extract row headers
    
        product_image_list=[]
        image_url_array = []
        for result in row:
           product_image_list.append(dict(zip(row_headers,result)))
        for product_image in product_image_list:
           image_url_array.append(product_image['image_url'])

    print(image_url_array)       
    api = Trading(domain='api.ebay.com',appid='arsensah-myapp-PRD-41d9f5f51-f3aac787',
        certid='PRD-1d9f5f511ac9-005d-4560-8eee-672f',devid='96d594f7-cbdf-434d-b1ed-42d5b1a26adc',
        token=token1, config_file=None,siteid=0)
    request1 = {
            "CategorySpecific":{
                "CategoryID":"{}".format(ebay_categoryID)
            }

        }
    try:         
        response1=api.execute("GetCategorySpecifics", request1)
        # print(response.dict())
    except:
    
        pass
    result = response1.dict()
  
    requiredItem = {}
    requiredList = []
    for item in result['Recommendations']['NameRecommendation']:
        if item['ValidationRules']['UsageConstraint'] == 'Required':
            
            if(len(item['ValueRecommendation'])==2):
                requiredItem = {"name":item['Name'],"value":item['ValueRecommendation']['Value']}
                requiredList.append(requiredItem)
            else:
                requiredItem = {"name":item['Name'],"value":item['ValueRecommendation'][0]['Value']}
                requiredList.append(requiredItem)
            
    print("requiredlist",requiredList)

    item_price = int(request.POST.get('price'))/int(currency_rating)
    item_title = request.POST.get('title')
    item_title = (item_title[:70] +'...') if len(item_title) > 70 else item_title
    print("item title=>",item_title)
    # list new product
    try:    
                    api = Trading(domain='api.ebay.com',appid='arsensah-myapp-PRD-41d9f5f51-f3aac787',
                    certid='PRD-1d9f5f511ac9-005d-4560-8eee-672f',devid='96d594f7-cbdf-434d-b1ed-42d5b1a26adc',
                    token=token1, config_file=None,siteid=0)
                    request1 = {
                        "Item":{
                                        "Title":"{}".format(item_title),
                                         "BestOfferDetails":{
                                            "BestOfferEnabled":"true"
                                        },
                                        "Description":"{}".format(request.POST.get('description')),
                                        "ListingDuration":"GTC",
                                        "ListingType":"FixedPriceItem",
                                        "Location":"Beverly Hills",
                                        "StartPrice":"{}".format(item_price),
                                        "Country":"JP",
                                        "Currency":"USD",
                                        "Quantity":"{}".format(request.POST.get('quantity')),
                                        "ConditionID":"1000",
                                        "ProductListingDetails":{
                                            "ItemSpecifics":{
                                               "Brand":"CONTINENTAL",
                                               "IncludeeBayProductDetails":"true",
                                               "Mount":"Canon EF",
                                               "Type":"standard"
                                            }
                                                     
                                        },
                                        "ItemSpecifics":{
                                            "NameValueList":{}
                                        },
                                        "PaymentMethods":"PayPal",
                                        "PayPalEmailAddress":"kevinzoo.lancer@gmail.com",
                                        "DispatchTimeMax":"1",
                                        "ShipToLocations":"None",
                                        "ReturnPolicy":{
                                            "ReturnsAcceptedOption":"ReturnsNotAccepted"
                                        },
                                        "PrimaryCategory":{
                                            "CategoryID":"{}".format(request.POST.get('ebay_category'))
                                        },
                                        "PictureDetails":{
                                            "PictureURL":image_url_array,
                                        },
                                        "ItemCompatibilityList":{
                                                "Compatibility":{
                                                    "NameValueList":[
                                                        {"Name":"Year","Value":"2010"},
                                                        {"Name":"Make","Value":"Hummer"},
                                                        {"Name":"Model","Value":"H3"}
                                                    ],
                                                    "CompatibilityNotes":"An example compatibility"
                                                }
                                        },
                                      
                                        "SellerProfiles":{

                                                "SellerPaymentProfile":{
                                                   
                                                        "PaymentProfileName":"{}".format(businessPolicy[0]['payment_name']),  
                                                        "PaymentProfileID":"{}".format(businessPolicy[0]['payment_id'])
                                                        },
                                                        "SellerReturnProfile":{
                                                  
                                                        "ReturnProfileName":"{}".format(businessPolicy[0]['return_name']),  
                                                        "ReturnProfileID":"{}".format(businessPolicy[0]['return_id'])
                                                        },
                                                        "SellerShippingProfile":{
                                                      
                                                        "ShippingProfileName": "{}".format(businessPolicy[0]['shipping_name']),
                                                        "ShippingProfileID":"{}".format(businessPolicy[0]['shipping_id']) 
                                                        },
                                        } ,
        
    
                                        
                                        "Site":"US"

                                }
                                        
                
                    }

                    i=0
                    request1['Item']['ItemSpecifics']['NameValueList']={}
                    itemList=[]
                    for item in requiredList:
                        itemList.append({"Name":item['name'],"Value":item['value']})
                        i=i+1
                    print(itemList)    
                    request1['Item']['ItemSpecifics']['NameValueList']=itemList    
                    response=api.execute("AddItem", request1)
                    print(response.dict())
                    print(response.reply)
    except ConnectionError as e:
                    print(e)
                    print(e.response.dict())
                    pass
    response = {"result":"true"}

    return Response(response,status.HTTP_200_OK)
