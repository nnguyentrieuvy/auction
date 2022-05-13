import hashlib
import io
import random

from PIL import Image

from django.shortcuts import render, redirect
import check_permission
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.core.files.storage import FileSystemStorage
from .forms import *
from .models import *

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
    acc = models.account.objects.filter(pk=request.session['auction_account'].get('username'),
                                        password=request.session['auction_account'].get('password'),
                                        role='user').first()
    if check_permission.permission(request, acc, 'user') == 'user':
        return redirect("/usr/0/information")

    else:
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
                                                            "username": request.session['auction_account']['username']})
    else:
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
            # fs.save(img.name, img)
            if img is not None:
                name = fs.save(img.name, img)
                url = fs.url(name)
            acc.password = request.session['auction_account']['password']
            acc.is_verify = True
            acc.role = 'user'
            acc.img_url = url
            print(request.FILES)
            # print(img.name)

            # destination = open('/images/' + str(img.name), 'wb+')
            acc.save()
            # for c in img.chunks():
            #     destination.write(c)
            return JsonResponse({"error": ''}, status=200)
    return redirect("/usr/0/information")

def home(request):
    cate = models.category.objects()
    t = models.category.objects.filter(catagory_parent=3).first()
    print(t.pk)
    return render(request, 'website/room.html', {'cate': cate})

def category_select(request):
    form = ProductForm
    return render(request, 'website/category_select.html', {'form': form})


def detail_product(request):
    if request.is_ajax and request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            category_id = form.cleaned_data['category']
            print(category_id)
            return JsonResponse({"message": ''}, status=200)
    return redirect('/home')

def detail_product_form(request):
    form = ProductForm
    return render(request, 'website/detail_product.html', {'form': form})

def save_product(request):
    if request.is_ajax and request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        print(form.errors)
        print(request.POST)
        print(request.FILES)
        if form.is_valid():
            category_id = form.cleaned_data['category']
            c = models.category.objects(id=category_id).first()
            f = form.save(commit=False)
            f.category = c
            # list = []
            # f.image = []
            #
            # for i in range(0, 3):
            #     l = request.FILES['image_'+ str(i)]
            #     db_image = OneImage(image=l)
            #     f.image.append(db_image)

            # f.imageURL = ['jjjj','qq']
            f.save()
            return JsonResponse({"message": ''}, status=200)
    return redirect('/home')



