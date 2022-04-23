import hashlib
import json

from django.shortcuts import render, redirect
import check_permission
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from . import models
# from sms import send_sms
from .forms import *
from .models import *
# Create your views here.


def register(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = SignupForm(request.POST)
        # print(form.errors)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            form.save()
            # redirect to a new URL:
            return HttpResponseRedirect('/admin/index')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = SignupForm(instance=SignupForm(account= '', password= ''))

    return render(request, 'admin/index.html', {'form': form})

def login_form(request):
    acc = account.objects(role='admin').first()
    if check_permission.permission(request, acc, 'admin') == 'admin':
        return redirect('../../admin/index')
    else:
        form = AccountForm()
        # request.session['auction_account'] = {'username': 'admin', 'password': 'd033e22ae348aeb5660fc2140aec35850c4da997', 'role': 'admin'}
        return render(request, 'admin/login_form.html', {'form': form})

def register_form(request):
    form = SignupForm
    return render(request, 'admin/sigup_form.html', {'form': form})

def category(request):
    list = []
    acc = account.objects(role='admin').first()
    if check_permission.permission(request, acc, 'admin') == 'admin':
        user = acc.account
        user = user.split().pop(0)

        for cate in models.category.objects:
            list1 = [cate.name]
            pr = cate.catagory_parent

            while pr != 0:
                if pr != 0:
                    cate = models.category.objects.get(id=pr)
                    pr = cate.catagory_parent
                    list1.append(cate.name)
            list1.reverse()
            s = ' > '.join([str(item) for item in list1])
            list.append(s)
            # else:
            #     list.append(cate.name)

        return render(request, 'admin/category.html', {'username': user, 'category_list': list})
    else:
        print(request.session.get('auction_account'))
        return redirect('/admin')

def index(request):
    acc = account.objects(role='admin').first()
    if check_permission.permission(request, acc, 'admin') == 'admin':
        s = acc.account
        s = s.split().pop(0)

        return render(request, 'admin/index.html', {'username': s})
    else:
        print(request.session.get('auction_account'))
        return redirect('/admin')

def change_password_form(request):
    form = ChangePaswordForm
    return render(request, 'admin/change_password_form.html', {'form': form})

# @csrf_exempt
# def login(request):
#     if request.method == "POST":
#         # if this is a POST request we need to process the form data
#         acc = request.POST.get('account')
#         pwd = request.POST.get('password')
#         response_data = {}
#
#         post = account(account=acc, password=pwd, auth_password= '', email= '', auth_email= '')
#         # post.save()
#         print(acc)
#         response_data['result'] = 'Mat khau sai!'
#
#         # return HttpResponse(
#         #     json.dumps(response_data),
#         #     content_type="application/json"
#         # )
#         print('highghghg')
#         return JsonResponse({'kq': 'Tai khoan hoac mat khau khong chinhs xac!'}, status=200)
#         # return HttpResponseRedirect('/admin/index')
#         # return render(request, 'admin/index.html')
#
#     else:
#         return HttpResponse(
#             json.dumps({"nothing to see": "this isn't happening"}),
#             content_type="application/json"
#         )
#
#     # return render(request, 'admin/lg.html', {'form': AccountForm()})
#     # return JsonResponse({'kq': 'Tai khoan hoac mat khau khong chinhs xac!'}, status=200)
#     # return render(request, 'admin/login_message.html')

@csrf_exempt
def login(request):
    # request should be ajax and method should be POST.
    acc = account.objects(role='admin').first()
    if check_permission.permission(request, acc, 'admin') == 'admin':
        print('1')
        # some error occured
        return JsonResponse({"kq": 3}, status=200)
    else:
        if request.is_ajax and request.method == "POST":
            # get the form data
            form = AccountForm(request.POST)
            if form.is_valid():
                Account = form.cleaned_data['account']
                password = form.cleaned_data['password']
                password = hashlib.sha1(bytes(password, 'utf-8'))
                password = password.hexdigest()
                if Account == acc.account and password == acc.password:
                    kq = 1
                    request.session['auction_account'] = {'username': acc.account, 'password': acc.password, 'role': 'admin'}
                    vd = request.session['auction_account']
                    print(vd['username'])
                else:
                    kq = 0
                return JsonResponse({"kq": kq}, status=200)
                # return HttpResponseRedirect('/admin/index',status=200)
                # return render(request, 'admin/index.html', {'form': form})
            else:
                # some form errors occured.
                return JsonResponse({"error": form.errors}, status=400)
        else:
            return redirect('/admin')
        return JsonResponse({"kq": 'redirect'}, status=200)

@csrf_exempt
def logout(request):
    usr = request.session['auction_account']['username']
    pwd = request.session['auction_account']['password']
    rl = request.session['auction_account']['role']
    if usr != None and pwd != None and rl != None:
        # request.session.modified = True
        del request.session['auction_account']
        request.session['auction_account'] = {'username': None, 'password': None, 'role': None}
    else:
        return redirect('/admin/index')
    return redirect('/admin/index')

@csrf_exempt
def changepwd(request):
    # request should be ajax and method should be POST.
    acc = account.objects(role='admin').first()
    if check_permission.permission(request, acc, 'admin') == 'admin':
        if request.is_ajax and request.method == "POST":
        #     # get the form data
            form = ChangePaswordForm(request.POST)
            if form.is_valid():
                OldPwd = form.cleaned_data['OldPassword']
                OldPwd = hashlib.sha1(bytes(OldPwd, 'utf-8'))
                OldPwd = OldPwd.hexdigest()
                NewPwd = form.cleaned_data['NewPassword']
                NewPwd = hashlib.sha1(bytes(NewPwd, 'utf-8'))
                NewPwd = NewPwd.hexdigest()
                AuthPwd = form.cleaned_data['AuthPassword']
                AuthPwd = hashlib.sha1(bytes(AuthPwd, 'utf-8'))
                AuthPwd = AuthPwd.hexdigest()
                if OldPwd == acc.password:
                    if NewPwd == AuthPwd:
                        # d033e22ae348aeb5660fc2140aec35850c4da997
                        account.objects(account='admin').update(__raw__={'$set': {'password': NewPwd}})
                        acc.save()
                        message = 'Thao tác thành công!'
                    else:
                        message = 'Mật khẩu xác nhận không chính xác!'
                else:
                    message = 'Mật khẩu hiện tại không chính xác!'
                # print(message)
                return JsonResponse({"message": message}, status=200)
        else:
            return JsonResponse({"error": ''}, status=400)
    return redirect('/admin')



@csrf_exempt
def attribute_groups(request):
    message = 'attribute_groups'
    list = models.attribute_groups.objects
    form = AttributeGroupsForm
    if request.is_ajax and request.method == "POST":
        form = AttributeGroupsForm(request.POST)
        name = request.POST.get('name')
        if not models.attribute_groups.objects(name=name):
            if form.is_valid():
                message = ''
                last_doc = models.attribute_groups.objects.latest('id')
                attr = form.save(commit=False)
                attr.id = int(last_doc.id) + 1
                attr.save()
                # form.save()

        else:
            message = 'Thuộc tính đã tồn tại!'
        return JsonResponse({"message": message}, status=200)
    return render(request, 'admin/attribute_groups.html', {'attribute_groups': list, 'form': form})


@csrf_exempt
def attributes(request):
    message = 'attributes'
    list = models.attributes.objects
    form = AttributesForm
    if request.is_ajax and request.method == "POST":
        name = request.POST.get('name')
        attribute_groups_id = request.POST.get('attribute_groups_id')
        form = AttributesForm(request.POST)
        print(request.POST)
        if not models.attributes.objects(name=name):
            if form.is_valid():
                message = ''
                last_doc = models.attributes.objects.latest('id')
                #atrg is refe..field in model so it just saves _id of corresponding attribute_groups documenent.
                atrg = models.attribute_groups(id=attribute_groups_id)
                attg = form.save(commit=False)
                attg.id = int(last_doc.id) + 1
                attg.attribute_groups_id = atrg
                attg.save()
        else:
            message = 'Thuộc tính đã tồn tại!'
        return JsonResponse({"message": message}, status=200)
    return render(request, 'admin/attributes.html', {'attributes': list, 'form': form})


@csrf_exempt
def delete_attribute_groups(request, id):
    list = models.attribute_groups.objects
    form = AttributeGroupsForm
    if request.is_ajax and request.method == "POST":
        attr_grp = models.attribute_groups.objects(id=id)
        attr_grp.delete()
        return JsonResponse({"message": 'delete_atr_g'}, status=200)
    return render(request, 'admin/attribute_groups.html', {'attribute_groups': list, 'form': form})

@csrf_exempt
def delete_attributes(request, id):
    print(id)
    list = models.attributes.objects
    form = AttributesForm
    if request.is_ajax and request.method == "POST":
        attr = models.attributes.objects(id=id)
        attr.delete()
        return JsonResponse({"message": 'delete_attributes'}, status=200)
    return render(request, 'admin/attributes.html', {'attributes': list, 'form': form})

@csrf_exempt
def update_attribute_groups(request, id):
    list = models.attribute_groups.objects
    form = AttributeGroupsForm
    if request.is_ajax and request.method == "POST":
        form = AttributeGroupsForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({"name": "update_attribute_groups"}, status=200)
    return render(request, 'admin/attribute_groups.html', {'attribute_groups': list, 'form': form})

@csrf_exempt
def update_attributes(request, id):
    message = "update_attributes"
    list = models.attributes.objects
    form = AttributesForm
    if request.is_ajax and request.method == "POST":
        form = AttributesForm(request.POST)
        if not models.attributes.objects(name=request.POST['name']):
            if form.is_valid():
                message = ''
                atrg = models.attribute_groups(id=request.POST['attribute_groups_id'])
                attg = form.save(commit=False)
                attg.attribute_groups_id = atrg
                attg.save()
        else:
            message = 'Thuộc tính này đã tồn tại!'

        return JsonResponse({"message": message}, status=200)
    return render(request, 'admin/attributes.html', {'attributes': list, 'form': form})

