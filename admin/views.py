import hashlib
import json

from django.shortcuts import render, redirect
import check_permission
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .forms import *
from .models import *
# Create your views here.



def login_form(request):
    acc = account.objects(role='admin').first()
    if check_permission.permission(request, acc, 'admin') == 'admin':
        return redirect('../../admin/index')
    else:
        form = AccountForm()
        return render(request, 'admin/login_form.html', {'form': form})



def category(request):
    list = []
    acc = account.objects(role='admin').first()
    if check_permission.permission(request, acc, 'admin') == 'admin':
        user = acc.id
        user = user.split().pop(0)

        for cate in models.category.objects:
            list1 = [cate.name]
            pr = cate.category_parent

            while pr != 0:
                if pr != 0:
                    c = models.category.objects.get(id=pr)
                    pr = c.category_parent
                    list1.append(c.name)
            list1.reverse()
            s = ' > '.join([str(item) for item in list1])
            list.append({'id': cate.id, 'name': s})

        return render(request, 'admin/category.html', {'username': user, 'category_list': list})
    else:
        print(request.session.get('auction_account'))
        return redirect('/admin')


@csrf_exempt
def category_edit(request):
    acc = account.objects(role='admin').first()
    if check_permission.permission(request, acc, 'admin') == 'admin':
        user = acc.id
        user = user.split().pop(0)

        message = 'Lỗi!'
        form = CategoryForm
        form_attribute = AttributesForm
        list_attrs_id = []
        if request.is_ajax and request.method == "POST":
            form = CategoryForm(request.POST)
            name = request.POST.get('name')
            category_parent = request.POST.get('category_parent')
            attrs_id = request.POST.getlist('attrs_id[]')
            if not models.category.objects(name=name):
                if form.is_valid():
                    message = ''
                    cate = form.save(commit=False)
                    print(request.POST)
                    if not models.category.objects.latest('id'):
                        cate.id = 1
                    else:
                        last_doc = models.category.objects.latest('id')
                        cate.id = int(last_doc.id) + 1
                    if request.POST['check_add_attr'] == 'True':
                       for l in attrs_id:
                          doc = models.attributes.objects(id=int(l)).first()
                          list_attrs_id.append(doc)
                    cate.attributes_id = list_attrs_id
                    cate.save()
            else:
                message = 'Thuộc tính đã tồn tại!'
            return JsonResponse({"message": message}, status=200)
        return render(request, 'admin/category_edit.html', {'username': user, 'form': form, 'form_attribute': form_attribute})
    else:
        print(request.session.get('auction_account'))
        return redirect('/admin')


@csrf_exempt
def category_update(request, id):
    form = CategoryForm
    print('snkshskhs')
    form_attribute = AttributesForm
    cate = models.category.objects(id=id).first()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "POST":
        message = 'Lỗi!'
        ls_attr = request.POST.getlist('attributes[]')
        name = request.POST['name']
        cate_attr = []
        cate_attr_int = []
        if request.POST['check_add_attr'] == 'True':
           for x in ls_attr:
              cate_attr_int.append(models.attributes.objects(id=int(x)).first())
        if (name == cate.name) and (cate_attr == ls_attr):
            message = 'Các thông tin không có sự thay đổi!'
        else:
            form = CategoryForm(request.POST)
            f = form.save(commit=False)
            f.id = id
            f.name = name
            f.attributes_id = cate_attr_int
            f.save()
            message = 'Cập nhật thành công!'
        return JsonResponse({"message": message}, status=200)
    else:
        return render(request, 'admin/category_update.html', {'form': form, 'form_attribute': form_attribute, 'cate': cate})

def index(request):
    acc = account.objects(role='admin').first()
    if check_permission.permission(request, acc, 'admin') == 'admin':
        s = acc.id
        s = s.split().pop(0)

        return render(request, 'admin/index.html', {'username': s})
    else:
        print(request.session.get('auction_account'))
        return redirect('/admin')

def change_password_form(request):
    form = ChangePaswordForm
    return render(request, 'admin/change_password_form.html', {'form': form})


@csrf_exempt
def login(request):
    # request should be ajax and method should be POST.
    acc = account.objects(role='admin').first()
    if check_permission.permission(request, acc, 'admin') == 'admin':
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
                if Account == acc.id and password == acc.password:
                    kq = 1
                    request.session['auction_account'] = {'username': acc.id, 'password': acc.password, 'role': 'admin'}
                    vd = request.session['auction_account']
                    print(vd['username'])
                else:
                    kq = 0
                return JsonResponse({"kq": kq}, status=200)
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
            # get the form data
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
                        account.objects(id='admin').update(__raw__={'$set': {'password': NewPwd}})
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
    acc = account.objects(role='admin').first()
    if check_permission.permission(request, acc, 'admin') == 'admin':
        user = acc.id
        user = user.split().pop(0)

        message = 'Lỗi!'
        list = models.attribute_groups.objects
        form = AttributeGroupsForm
        if request.is_ajax and request.method == "POST":
            form = AttributeGroupsForm(request.POST)
            name = request.POST.get('name')
            if not models.attribute_groups.objects(name=name):
                if form.is_valid():
                    message = ''
                    attr = form.save(commit=False)
                    if not models.attribute_groups.objects.latest('id'):
                        attr.id = 1
                    else:
                        last_doc = models.attribute_groups.objects.latest('id')
                        attr.id = int(last_doc.id) + 1
                    attr.save()
            else:
                message = 'Thuộc tính đã tồn tại!'
            return JsonResponse({"message": message}, status=200)
        return render(request, 'admin/attribute_groups.html', {'attribute_groups': list, 'form': form, 'username': user})
    else:
        print(request.session.get('auction_account'))
        return redirect('/admin')



@csrf_exempt
def attributes(request):
    acc = account.objects(role='admin').first()
    if check_permission.permission(request, acc, 'admin') == 'admin':
        user = acc.id
        user = user.split().pop(0)

        message = 'Lỗi!'
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
                    # atrg is refe..field in model so it just saves _id of corresponding attribute_groups documenent.
                    atrg = models.attribute_groups(id=attribute_groups_id)
                    attg = form.save(commit=False)
                    attg.attribute_groups_id = atrg
                    if not last_doc:
                        attg.id = 1
                    else:
                        attg.id = int(last_doc.id) + 1
                    attg.save()
            else:
                message = 'Thuộc tính đã tồn tại!'
            return JsonResponse({"message": message}, status=200)
        return render(request, 'admin/attributes.html', {'attributes': list, 'form': form, 'username': user})
    else:
        print(request.session.get('auction_account'))
        return redirect('/admin')



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
def delete_category(request, id):
    print(id)
    form = CategoryForm
    form_attribute = AttributesForm
    if request.is_ajax and request.method == "POST":
        attr = models.category.objects(id=id).first()
        doc = models.category.objects(category_parent=id).first()
        if doc:
           doc.delete()

        attr.delete()
        return JsonResponse({"message": 'delete_category'}, status=200)
    return render(request, 'admin/category_edit.html', {'form': form, 'form_attribute': form_attribute})


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
    message = "Lỗi!"
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

@csrf_exempt
def attributes_attrgroups(request):
    if request.is_ajax and request.method == "POST":
        id_attr = request.POST.get('id_attr')
        print(id_attr)
        doc = models.attributes.objects(id=int(id_attr)).first()
        return JsonResponse({"message": doc.attribute_groups_id.id}, status=200)
    return JsonResponse({"message": 'Lỗi!'}, status=400)


