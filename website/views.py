import datetime
import hashlib
import io
import json
import random
import os

from PIL import Image

from django.shortcuts import render, redirect
import check_permission
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.core.files.storage import FileSystemStorage
from django.forms.models import model_to_dict
from bson import ObjectId
from django.core import serializers
from .forms import *
from .models import *
import json
import urllib.request
import urllib
import uuid
import requests
import hmac
import hashlib

from mtnmomo.collection import Collection


# Create your views here.
def register_form(request):
    form = SignupForm
    return render(request, 'website/sigup_form.html', {'form': form})

def registration(request):
    form = SignupForm
    message = ''
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        usr = request.POST.get('account')
        pwd = request.POST.get('password')
        pwd = hashlib.sha1(bytes(pwd, 'utf-8'))
        pwd = pwd.hexdigest()
        auth_pwd = request.POST.get('auth_password')
        auth_pwd = hashlib.sha1(bytes(auth_pwd, 'utf-8'))
        auth_pwd = auth_pwd.hexdigest()
        email = request.POST.get('email')
        # address = request.POST.get('address')
        # city = request.POST.get('city')
        # district = request.POST.get('district')

        if pwd == auth_pwd:
            user = models.account.objects.filter(account=usr).first()
            if not user:
                # user = models.account(account=usr, password=pwd, email=email, address=address, city=city,
                #                       district=district,
                #                       role='user')
                # user.save()
                form = SignupForm(request.POST)
                if form.is_valid():
                    acc = form.save(commit=False)
                    acc.password = pwd
                    acc.role = 'user'
                    acc.save()
                    domain_name = get_current_site(request).domain
                    token = str(random.random()).split('.')[1]
                    models.account.objects(account=usr).update(__raw__={'$set': {'token': token}})

                    link = f'http://{domain_name}/verify/{token}'
                    mail = EmailMessage(
                        'Email Verification',
                        f'Please click {link} to verify your email.',
                        '',
                        ['django.projects.test@gmail.com'],
                        cc=[email],
                    )
                    mail.send(fail_silently=False)
                    return render(request, 'website/verification.html', {'user': usr, 'email': email})
            else:
                message = 'Thao tác thất bại!'

        else:
            message = 'Mật khẩu xác nhận không chính xác!'
        return render(request, 'website/sigup_form.html', {'form': form, 'message': message})
    else:
        return render(request, 'website/sigup_form.html', {'form': form})

def verify(request, token):
    try:
        user = models.account.objects.filter(token=token).first()
        print('hhhhhh')
        if user:
            user.update(__raw__={'$set': {'is_verify': True}})
            return render(request, 'website/is_verify.html')
        else:
            return render(request, '404.html')
    except Exception as e:
        return HttpResponse(e)

@csrf_exempt
def login(request):
    form = AccountForm
    try:
        acc = models.account.objects(pk=request.session['auction_account'].get('username'),
                                     password=request.session['auction_account'].get('password'),
                                     role='user').first()
        if check_permission.permission(request, acc, 'user') == 'user':
            return redirect("/usr/0/information")
    except:
        request.session['auction_account'] = ''

        if request.is_ajax and request.method == "POST":
            # get the form data
            form = AccountForm(request.POST)
            if form.is_valid():
                Account = form.cleaned_data['account']
                password = form.cleaned_data['password']
                password = hashlib.sha1(bytes(password, 'utf-8'))
                password = password.hexdigest()
                print('TTTTTT')
                acc = account.objects(pk=Account, password=password, role='user').first()
                if acc:
                    if acc.is_verify == True:
                        # my_image = open(r'C:\Users\ADMIN\Pictures\Screenshots\agg.png', 'rb')
                        # acc.image.replace(my_image, filename="conny.jpg")
                        # acc.save()
                        # print(acc.image.url)
                        kq = 1
                        request.session['auction_account'] = {'username': acc.account, 'password': acc.password,
                                                              'role': 'user'}
                        print(request.session['auction_account'])
                    else:
                        kq = 'redirect'

                else:
                    kq = '0'
                return JsonResponse({"kq": kq}, status=200)
            else:
                # some form errors occured.
                return JsonResponse({"error": form.errors}, status=400)
        return render(request, 'website/login_form.html', {'form': form})



def information(request):
    try:
        acc = models.account.objects.filter(pk=request.session['auction_account']['username'],
                                            password=request.session['auction_account']['password'],
                                            role='user').first()
        if check_permission.permission(request, acc, 'user') == 'user':
            img_url = None
            form = SignupForm
            # u = user.to_mongo()
            u = acc.to_json()
            if acc.img_url != "":
                img_url = acc.img_url

            # with open(r'C:\Users\ADMIN\Pictures\Screenshots\agg.png', 'rb') as fd:
            #     a.image.put(fd, content_type='image/png')
            # a.save()
            # photo = a.image.read()
            # content_type = a.image.content_type
            return render(request, 'website/information.html', {'form': form,
                                                                'user': u, 'img_url': img_url,
                                                                "username": request.session['auction_account'][
                                                                    'username']})
        else:
            return redirect("/login")
    except KeyError:
        return redirect("/login")


@csrf_exempt
def logout(request):
    usr = request.session['auction_account']['username']
    pwd = request.session['auction_account']['password']
    rl = request.session['auction_account']['role']
    if usr != None and pwd != None and rl != None:
        del request.session['auction_account']
        request.session['auction_account'] = {'username': None, 'password': None, 'role': None}
    else:
        return redirect('/admin/index')
    return JsonResponse({"error": ''}, status=200)


@csrf_exempt
def update(request):
    if request.is_ajax and request.method == "POST":
        form = SignupForm(request.POST, request.FILES)
        if form.is_valid():
            acc = form.save(commit=False)
            img = request.FILES.get('image')
            fs = FileSystemStorage()
            if img is not None:
                name = fs.save(img.name, img)
                url = fs.url(name)
            acc.password = request.session['auction_account']['password']
            acc.is_verify = True
            acc.role = 'user'
            acc.img_url = url
            acc.save()

            # with open(r'C:\Users\ADMIN\Pictures\Screenshots\hhh.png', 'rb') as fd:
            #     a = models.account()
            #     i = a.image.put(fd, content_type='image/png')
            #     acc.image = i
            # acc.save()
            return JsonResponse({"error": ''}, status=200)
    return redirect("/usr/0/information")

def home(request):
    cate = models.category.objects()
    t = models.category.objects.filter(category_parent=3).first()
    rm = models.room.objects()
    for r in rm:
        print(r.status)
    return render(request, 'website/room.html', {'cate': cate, 'room': rm})

def product(request):
    l = 3
    form = ProductForm(l)
    prd_att = ProductAttributesForm
    c = models.category.objects()
    cate = c.to_json()
    print(cate)
    if request.method == "POST":
        if request.is_ajax:
            try:
                acc = models.account.objects.filter(pk=request.session['auction_account']['username'],
                                                    password=request.session['auction_account']['password'],
                                                    role='user').first()
                u = acc.to_json()
                form = ProductForm(l, request.POST)
                if form.is_valid():
                    category_id = form.cleaned_data['category']
                    print(category_id)
                    return JsonResponse({"message": category_id}, status=200)
            except:
                return redirect('/login')
        return render(request, 'website/detail_product.html', {'form': form, 'user': u, 'prd_att': prd_att, 'cate': cate, 'c': c})
    else:
        return render(request, 'website/category_select.html', {'form': form})


# def detail_product(request):
#     if request.is_ajax and request.method == "POST":
#         form = ProductForm(request.POST)
#         if form.is_valid():
#             category_id = form.cleaned_data['category']
#             print(category_id)
#             return JsonResponse({"message": ''}, status=200)
#     return redirect('/home')


def detail_product_form(request):
    if request.method == "POST":
        form = ProductForm
        return render(request, 'website/detail_product.html', {'form': form})
    return redirect("/seller/category")


def get_category(request):
    message = 'Lỗi!'
    if request.is_ajax and request.method == "POST":
        id = request.POST['id']
        category_list = models.category.objects.filter(id=id).first()
        d = category_list.attributes_id
        ls = []
        for item in d:
            item = model_to_dict(item)
            item['attribute_groups_id'] = model_to_dict(item['attribute_groups_id'])
            ls.append(item)
        print(ls)
        return JsonResponse({"message": ls}, status=200)
    return JsonResponse({"message": message}, status=400)


def save_product(request):
    if request.is_ajax and request.method == "POST":
        form = ProductForm(3, request.POST, request.FILES)
        print(request.POST)
        if form.is_valid():
            category_id = form.cleaned_data['category']
            c = models.category.objects(id=category_id).first()
            f = form.save(commit=False)
            f.category = c
            f.startingbid = float(request.POST['startingbid']) * 1000
            f.seller = models.account.objects(pk=request.session['auction_account']['username']).first()
            p_id = f.save()

            for i in range(0, len(request.POST.getlist("content"))):
                form_attr = ProductAttributesForm(request.POST)
                form_attr = form_attr.save(commit=False)
                form_attr.product_id = models.product.objects(id=ObjectId(p_id.id)).first()
                form_attr.attributes = models.attributes.objects(id=request.POST.getlist('attributes')[i]).first()
                form_attr.content = request.POST.getlist("content")[i]
                form_attr.save()

            p = models.product.objects(id=ObjectId(p_id.id)).first()
            days = p.duration.split(" day")
            timestamp = str(datetime.datetime.now())
            timestamp = timestamp[:len(timestamp) - 7]
            print(timestamp)

            end = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S") + datetime.timedelta(days=int(days[0]))

            room = models.room(product_id=models.product.objects(id=ObjectId(p_id.id)).first(), total=0,
                               start=datetime.datetime.now(), end=end, seller_id=models.account.objects(pk=request.session['auction_account']['username']).first(),
                               quantity_of_bidder=0, bidders=[], highestbidder='', current_bid=request.POST['startingbid'], status='opening',
                               winner=[], highestbidder_bid=0.0)
            room.save()
            return JsonResponse({"message": ''}, status=200)
    return redirect('/home')



def get_balance(request):
    # # parameters send to MoMo get get payUrl
    # endpoint = "https://test-payment.momo.vn/v2/gateway/api/create"
    # partnerCode = "MOMO"
    # accessKey = "F8BBA842ECF85"
    # secretKey = "K951B6PE1waDMi640xX08PD3vg6EkVlz"
    # orderInfo = "pay with MoMo"
    # redirectUrl = "http://127.0.0.1:8000/vd"
    # ipnUrl = "http://127.0.0.1:8000/vd"
    # amount = "50000"
    # orderId = str(uuid.uuid4())
    # requestId = str(uuid.uuid4())
    # requestType = "captureWallet"
    # extraData = ""  # pass empty value or Encode base64 JsonString
    #
    # # before sign HMAC SHA256 with format: accessKey=$accessKey&amount=$amount&extraData=$extraData&ipnUrl=$ipnUrl
    # # &orderId=$orderId&orderInfo=$orderInfo&partnerCode=$partnerCode&redirectUrl=$redirectUrl&requestId=$requestId
    # # &requestType=$requestType
    # rawSignature = "accessKey=" + accessKey + "&amount=" + amount + "&extraData=" + extraData + "&ipnUrl=" + ipnUrl + "&orderId=" + orderId + "&orderInfo=" + orderInfo + "&partnerCode=" + partnerCode + "&redirectUrl=" + redirectUrl + "&requestId=" + requestId + "&requestType=" + requestType
    #
    # # puts raw signature
    # print("--------------------RAW SIGNATURE----------------")
    # print(rawSignature)
    # # signature
    # h = hmac.new(bytes(secretKey, 'ascii'), bytes(rawSignature, 'ascii'), hashlib.sha256)
    # signature = h.hexdigest()
    # print("--------------------SIGNATURE----------------")
    # print(signature)
    #
    # # json object send to MoMo endpoint
    #
    # data = {
    #     'partnerCode': partnerCode,
    #     'partnerName': "Test",
    #     'storeId': "MomoTestStore",
    #     'requestId': requestId,
    #     'amount': amount,
    #     'orderId': orderId,
    #     'orderInfo': orderInfo,
    #     'redirectUrl': redirectUrl,
    #     'ipnUrl': ipnUrl,
    #     'lang': "vi",
    #     'extraData': extraData,
    #     'requestType': requestType,
    #     'signature': signature
    # }
    # print("--------------------JSON REQUEST----------------\n")
    # data = json.dumps(data)
    # print(data)
    #
    # clen = len(data)
    # response = requests.post(endpoint, data=data,
    #                          headers={'Content-Type': 'application/json', 'Content-Length': str(clen)})
    #
    # # f.close()
    # print("--------------------JSON response----------------\n")
    # print(response.json())
    #
    # print(response.json()['payUrl'])

    config = {
        "ENVIRONMENT": 'sandbox',
        "BASE_URL": 'https://sandbox.momodeveloper.mtn.com',
        "CALLBACK_HOST": "https://webhook.site/6a073522-a7f0-475a-8c1c-cdbf4c527804",  # Mandatory.
        "COLLECTION_PRIMARY_KEY": '7d88edbf173f4f2a9d28a7fa7d5d09a5',
        "COLLECTION_USER_ID": 'cffad568-c3c0-4194-ad23-67fb1fb6a15b',
        "COLLECTION_API_SECRET": 'e197ad12de104901bf531fdbc8503759',
    }

    client = Collection({
        "ENVIRONMENT": 'sandbox',
        "BASE_URL": 'https://sandbox.momodeveloper.mtn.com',
        "CALLBACK_HOST": "https://webhook.site/6a073522-a7f0-475a-8c1c-cdbf4c527804",  # Mandatory.
        "COLLECTION_PRIMARY_KEY": '7d88edbf173f4f2a9d28a7fa7d5d09a5',
        "COLLECTION_USER_ID": '8ccc8c75-6508-41df-acba-310390d39dd0',
        "COLLECTION_API_SECRET": '7cb763e6f46a4025904e5da8ccf0f38b',
    })
    y = client.requestToPay(
       mobile="256782181656", amount="600", external_id="111", payee_note="dd", payer_message="dd", currency="EUR")
    t = client.getBalance()
    print(t)

    # import http.client, urllib.request, urllib.parse, urllib.error, base64
    # #
    # headers = {
    #     # Request headers
    #     'Authorization': '',
    #     'X-Target-Environment': 'sandbox',
    #     'Ocp-Apim-Subscription-Key': '7d88edbf173f4f2a9d28a7fa7d5d09a5',
    # }
    #
    # params = urllib.parse.urlencode({
    # })
    #
    # try:
    #     conn = http.client.HTTPSConnection('sandbox.momodeveloper.mtn.com')
    #     conn.request("GET", "/collection/v1_0/account/balance?%s" % params, "{body}", headers)
    #     response = conn.getresponse()
    #     data = response.read()
    #     print('sjkskjskjs')
    #     print(data)
    #     conn.close()
    # except Exception as e:
    #     print("[Errno {0}] {1}".format(e.errno, e.strerror))

    return HttpResponse('hello')

def thanhtoan_momo(request):
    # parameters send to MoMo get get payUrl
    # endpoint = "https://test-payment.momo.vn/v2/gateway/api/create"
    # partnerCode = "MOMO"
    # accessKey = "F8BBA842ECF85"
    # secretKey = "K951B6PE1waDMi640xX08PD3vg6EkVlz"
    # orderInfo = "pay with MoMo"
    # redirectUrl = "https://webhook.site/b3088a6a-2d17-4f8d-a383-71389a6c600b"
    # ipnUrl = "https://webhook.site/b3088a6a-2d17-4f8d-a383-71389a6c600b"
    # amount = "50000"
    # orderId = str(uuid.uuid4())
    # requestId = str(uuid.uuid4())
    # requestType = "captureWallet"
    # extraData = ""  # pass empty value or Encode base64 JsonString

    endpoint = "https://test-payment.momo.vn/v2/gateway/api/create"
    endpoint = 'https://test-payment.momo.vn/v2/gateway/api/query'

    # accessKey = "F8BBA842ECF85"
    # secretKey = "K951B6PE1waDMi640xX08PD3vg6EkVlz"
    # partnerCode = "MOMO"
    partnerCode = 'MOMOBKUN20180529'
    accessKey = 'klm05TvNBzhg7h7j'
    secretKey = 'at67qH6mk8w5Y1nAyMoYKMWACiEi2bsa'
    orderInfo = "Thanh toán qua MoMo"
    amount = "10000"
    orderId = str(uuid.uuid4())
    redirectUrl = "http://127.0.0.1:8000/vd"
    ipnUrl = 'http://127.0.0.1:8000/vd'
    extraData = ""
    requestId = str(uuid.uuid4())
    requestType = 'payWithATM'

    # before sign HMAC SHA256 with format: accessKey=$accessKey&amount=$amount&extraData=$extraData&ipnUrl=$ipnUrl
    # &orderId=$orderId&orderInfo=$orderInfo&partnerCode=$partnerCode&redirectUrl=$redirectUrl&requestId=$requestId
    # &requestType=$requestType

    rawSignature = "accessKey=" + accessKey + "&amount=" + amount + "&extraData=" + extraData + "&ipnUrl=" + ipnUrl + "&orderId=" + orderId + "&orderInfo=" + orderInfo + "&partnerCode=" + partnerCode + "&redirectUrl=" + redirectUrl + "&requestId=" + requestId + "&requestType=" + requestType
    # puts raw signature
    print("--------------------RAW SIGNATURE----------------")
    print(rawSignature)
    # signature
    h = hmac.new(bytes(secretKey, 'utf-8'), bytes(rawSignature, 'utf-8'), hashlib.sha256)
    signature = h.hexdigest()
    print("--------------------SIGNATURE----------------")
    print(signature)

    # json object send to MoMo endpoint

    data = {
        'partnerCode': partnerCode,
        'partnerName': "Test",
        'storeId': 'MomoTestStore',
        'requestId': requestId,
        'amount': amount,
        'orderId': orderId,
        'orderInfo': orderInfo,
        'redirectUrl': redirectUrl,
        'ipnUrl': ipnUrl,
        'lang': 'vi',
        # 'autoCapture': autoCapture,
        'extraData': extraData,
        # 'paymentCode': paymentCode,
        # 'orderGroupId': orderGroupId,
        'requestType': requestType,
        'signature': signature
    }

    print("--------------------JSON REQUEST----------------\n")
    data = {
    "partnerCode": "123456",
    "requestId": "1527246504579",
    "orderId": "1527246478428",
    "signature": "13be80957a5ee32107198920fa26aa85a4ca238a29f46e292e8c33dd9186142a",
    "lang": "en"
}
    data = json.dumps(data)
    print(data)

    clen = len(data)
    response = requests.post(endpoint, data=data,
                             headers={'Content-Type': 'application/json', 'Content-Length': str(clen)})

    # f.close()
    print("--------------------JSON response----------------\n")
    print(response.json())


    # print(response.json()['payUrl'])
    return HttpResponse('hello')

# def thanhtoan_momo(request):
#     # parameters send to MoMo get get payUrt
#     endpoint = "https://test-payment.momo.vn/v2/gateway/api/pos"
#     accessKey = "F8BBA842ECF85"
#     secretKey = "K951B6PE1waDMi640xX08PD3vg6EkVlz"
#     orderInfo = "pay with MoMo"
#     partnerCode = "MOMO"
#     redirectUrl = "https://webhook.site/b3088a6a-2d17-4f8d-a383-71389a6c600b"
#     ipnUrl = "https://webhook.site/b3088a6a-2d17-4f8d-a383-71389a6c600b"
#     amount = "50000"
#     orderId = str(uuid.uuid4())
#     requestId = str(uuid.uuid4())
#     extraData = ""  # pass empty value or Encode base64 JsonString
#     partnerName = "MoMo Payment"
#     storeId = "Test Store"
#     paymentCode = "L/U2a6KeeeBBU/pQAa+g8LilOVzWfvLf/P4XOnAQFmnkrKHICj51qrOTUQ+YrX8/Xs1YD4IOdyiGSkCfV6Je9PeRzl3sO+mDzXNG4enhigU3VGPFh67a37dSwItMJXRDuK64DCqv35YPQtiAOVVZV35/1XBw1rWopmRP03YMNgQWedGLHwmPSkRGoT6XtDSeypJtgbLZ5KIOJsdcynBdFEnHAuIjvo4stADmRL8GqdgsZ0jJCx/oq5JGr8wY+a4g9KolEOSTLBTih48RrGZq3LDBbT4QGBjtW+0W+/95n8W0Aot6kzdG4rWg1NB7EltY6/A8RWAHJav4kWQoFcxgfA=="
#     orderGroupId = ""
#     autoCapture = True
#     lang = "vi"
#
#     # before sign HMAC SHA256 with format: accessKey=$accessKey&amount=$amount&extraData=$extraData&ipnUrl=$ipnUrl
#     # &orderId=$orderId&orderInfo=$orderInfo&partnerCode=$partnerCode&redirectUrl=$redirectUrl&requestId=$requestId
#     # &requestType=$requestType
#
#     rawSignature = "accessKey="+accessKey+"&amount="+amount+"&extraData="+extraData+"&orderId="+orderId+"&orderInfo="+orderInfo+"&partnerCode="+partnerCode+"&paymentCode="+paymentCode+"&requestId="+requestId
#     # puts raw signature
#     print("--------------------RAW SIGNATURE----------------")
#     print(rawSignature)
#     # signature
#     h = hmac.new(bytes(secretKey, 'ascii'), bytes(rawSignature, 'utf-8'), hashlib.sha256)
#     signature = h.hexdigest()
#     print("--------------------SIGNATURE----------------")
#     print(signature)
#
#     # json object send to MoMo endpoint
#
#     data = {
#         'partnerCode': partnerCode,
#         'partnerName': partnerName,
#         'storeId': storeId,
#         'requestId': requestId,
#         'amount': amount,
#         'orderId': orderId,
#         'orderInfo': orderInfo,
#         # 'redirectUrl': redirectUrl,
#         'ipnUrl': ipnUrl,
#         'lang': lang,
#         'autoCapture': autoCapture,
#         'extraData': extraData,
#         'paymentCode': paymentCode,
#         'orderGroupId': orderGroupId,
#         'signature': signature
#     }
#     print("--------------------JSON REQUEST----------------\n")
#     data = json.dumps(data)
#     print(data)
#
#     clen = len(data)
#     response = requests.post(endpoint, data=data,
#                              headers={'Content-Type': 'application/json', 'Content-Length': str(clen)})
#
#     # f.close()
#     print("--------------------JSON response----------------\n")
#     print(response.json())
#
#
#     print(response.json()['payUrl'])
#     return HttpResponse('hello')

def vd(request):
    return render(request, 'vd.html')

def room_detail(request, id):
    room = models.room.objects(id=ObjectId(id)).first()
    pr_att = models.product_attributes.objects(product_id=ObjectId(room.product_id.id))
    history_bidding = models.history_bidding.objects(room_id=ObjectId(id), bidder_id=request.session['auction_account']['username'])
    count = history_bidding.count()
    try:
       history_bidding = history_bidding[count-1]
    except IndexError:
       history_bidding = ''
    return render(request, 'website/room_detail.html', {'room': room, 'pr_att': pr_att, 'hs_bidding': history_bidding})


def get_auction_bid(current_price, currency):
    bid_increment = 0
    currency = float(currency)
    if (0.01 * currency) <= current_price or current_price <= (0.99 * currency):
        bid_increment = 0.05 * currency
    elif (0.1 * currency) <= current_price or current_price <= (4.99 * currency):
        bid_increment = 0.025 * currency
    elif (5.0 * currency) <= current_price or current_price <= (24.99 * currency):
        bid_increment = 0.5 * currency
    elif (25.00 * currency) <= current_price or current_price <= (99.99 * currency):
        bid_increment = 1.0 * currency
    elif (100.00 * currency) <= current_price or current_price <= (249.99 * currency):
        bid_increment = 2.50 * currency
    elif (250.00 * currency) <= current_price or current_price <= (499.99 * currency):
        bid_increment = 5.00 * currency
    elif (500.00 * currency) <= current_price or current_price <= (999.99 * currency):
        bid_increment = 10.00 * currency
    elif (1000.00 * currency) <= current_price or current_price <= (2499.99 * currency):
        bid_increment = 25.00 * currency
    elif (2500.00 * currency) <= current_price or current_price <= (4999.99 * currency):
        bid_increment = 50.00 * currency
    elif (5000.00 * currency) <= current_price:
        bid_increment = 100.00 * currency
    return bid_increment


@csrf_exempt
def bid(request):
    message = 'Lỗi!'
    if request.is_ajax and request.method == "POST":
        bidder = request.session['auction_account']['username']
        if bidder is None:
            return JsonResponse({"message": 'Lỗi!'}, status=200)
        bids = float(request.POST['bids'])
        print(bids)
        id = request.POST['id']
        room = models.room.objects(id=ObjectId(id)).first()
        if bids >= (room.current_bid + get_auction_bid(room.current_bid, 23000)):
            if bidder == room.highestbidder.id:
                if bids >= (room.highestbidder_bid + get_auction_bid(room.highestbidder_bid, 23000)):
                   models.room.objects(id=ObjectId(id)).update(highestbidder_bid=bids)
                   history = models.history_bidding(bidder_id=bidder, room_id=room, bids=bids)
                   history.save()
                   message = 'Bạn đang là highest bid. Bạn đã tăng giá tối đa thành công!'
                else:
                    message = 'Highest bid không thể hạ giá bid tối đa đã đặt hoặc giá tiền không hợp lệ!'
            else:
                if bids > room.highestbidder_bid:
                    # change hb and hb_bid
                    # new bidder becomes hb
                    models.room.objects(id=ObjectId(id)).update(
                        current_bid=float(room.highestbidder_bid + get_auction_bid(room.highestbidder_bid, 23000)),
                        highestbidder=models.account.objects(pk=bidder).first(),
                        highestbidder_bid=bids)
                    history = models.history_bidding(bidder_id=bidder, room_id=room, bids=bids)
                    history.save()
                    message = 'Cập nhật highest bidder thành công!'
                elif bids == room.highestbidder_bid:
                    # new bidder don't becomes hb, current_bid = new bid and hb, but new bidder outbid and hb not
                    models.room.objects(id=ObjectId(id)).update(
                        current_bid=float(room.highestbidder_bid))
                    history = models.history_bidding(bidder_id=bidder, room_id=room, bids=bids)
                    history.save()
                    if bidder == room.highestbidder.id:
                        message = 'Bạn vẫn đang là highest bidder!'
                    else:
                        message = 'Bạn đang bị outbid'
                else:
                    # new bidder not hb
                    message = 'Ban dang bi outbid!'
                    # auto bid for hb
                    auto_bidding(id, bids, bidder)

        else:
            message = 'Giá tiền phải từ ' + str(int(room.current_bid + get_auction_bid(room.current_bid, 23000))) + 'đ trở lên!'
        return JsonResponse({"message": message}, status=200)
    return JsonResponse({"error": ''}, status=400)



def auto_bidding(id_room, bid, bidder):
    new_current_bid = bid + get_auction_bid(bid, 23000)
    models.room.objects(id=ObjectId(id_room)).update(current_bid=new_current_bid)
    history = models.history_bidding(bidder_id=bidder, room_id = models.room.objects(id=ObjectId(id_room)).first(), bids=bid)
    history.save()


@csrf_exempt
def get_next_bids(request):
    if request.is_ajax and request.method == "POST":
        print(request.POST)
        bidder = request.session['auction_account']['username']
        id_room = request.POST['id_room']
        room = models.room.objects(id=ObjectId(id_room)).first()
        if bidder == room.highestbidder.id:
            hb = 'Bạn đang là người đặt giá cao nhất!'
            color = 'green'
            result = room.highestbidder_bid + get_auction_bid(room.highestbidder_bid, 23000)
        else:
            hb = 'Bạn đang bị trả giá cao hơn!'
            color = 'red'
            current_price = room.current_bid
            result = current_price + get_auction_bid(current_price, 23000)
        return JsonResponse({"message": result, 'hb': hb, 'hb_color': color}, status=200)
    return JsonResponse({"error": ''}, status=400)

@csrf_exempt
def set_status_room(request):
    if request.is_ajax and request.method == "POST":
        print(request.POST)
        id_room = request.POST['id_room']
        print('dnkdldkdldkd')
        print(id_room)
        models.room.objects(id=ObjectId(id_room)).update(status='closed')
        return JsonResponse({"message": 'Cập nhật status thành công!'}, status=200)
    return JsonResponse({"error": ''}, status=400)


