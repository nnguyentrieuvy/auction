from django import forms
from .models import *
from  . import models
from django_mongoengine.forms import DocumentForm


class SignupForm(DocumentForm):
   account = forms.CharField(label='Tên đăng nhập', max_length=100)
   password = forms.CharField(label='Mật khẩu',
                                 widget=forms.PasswordInput(attrs={'placeholder': '****',
                                                                   'title': "Vui lòng nhập mật khẩu"}), required=False)
   auth_password = forms.CharField(label='Xác nhận mật khẩu',
                                 widget=forms.PasswordInput(attrs={'placeholder': '****',
                                                                   'title': "Vui xác nhận mật khẩu"}),required=False)
   address = forms.CharField(label='Địa chỉ', max_length=100)
   city = forms.CharField(label='Tỉnh/ Thành phố', required=False, widget=forms.Select(choices=[]))
   district = forms.CharField(label='Quận/ Huyện', required=False, widget=forms.Select(choices=[]))
   email = forms.CharField(max_length=100)
   phonenb = forms.CharField(max_length=100, required=False)
   phonenb.widget.attrs.update({'placeholder': 'Số điện thoại'})
   image = forms.ImageField(required=False)

   def __init__(self, *args, **kwargs):
      super(SignupForm, self).__init__(*args, **kwargs)
      for visible in self.visible_fields():
         visible.field.widget.attrs['class'] = 'form-control'


   class Meta:
      document = account
      fields = ('__all__')

class AccountForm(forms.Form):
   account  = forms.CharField(label='Tài khoản', max_length=100)
   password = forms.CharField(label='Mật khẩu',
                              widget=forms.PasswordInput(attrs={'id':'password',
                              'placeholder': '****', 'title':"Vui lòng nhập mật khẩu"}))

   account.widget.attrs.update({'id':'username', 'placeholder': 'abc123','title':"Vui lòng nhập tên đăng nhập"})

   def __init__(self, *args, **kwargs):
      super(AccountForm, self).__init__(*args, **kwargs)
      for visible in self.visible_fields():
         visible.field.widget.attrs['class'] = 'form-control'


def get_values():
    list = []
    category_list = []

    for cate in models.category.objects:
        if cate.attributes_id == [] or cate.attributes_id[0].id == 0:
            list1 = [cate.name]
            pr = cate.catagory_parent

            while pr != 0:
                if pr != 0:
                    c = models.category.objects.get(id=pr)
                    pr = c.catagory_parent
                    list1.append(c.name)
            list1.reverse()
            s = ' > '.join([str(item) for item in list1])
            try:
                field = cate.attributes_id[0]
                if field != 0:
                   list.append({'id': cate.id, 'name': s})
            except IndexError:
                g = 2


    for l in list:
        item = (l['id'], l['name'])
        category_list.append(item)

    return category_list

class RoomForm(DocumentForm):
    def __init__(self, *args, **kwargs):
      super(RoomForm, self).__init__(*args, **kwargs)
      for visible in self.visible_fields():
         visible.field.widget.attrs['class'] = 'form-control'

    class Meta:
      document = models.room
      fields = ('__all__')

class ProductForm(DocumentForm):
    CHOICES = [('1', '1 ngày'),
               ('3', '3 ngày'),
               ('5', '5 ngày'),
               ('7', '7 ngày'),
               ('10', '10 ngày')]

    duration = forms.ChoiceField(label='Diễn ra', choices=CHOICES, widget=forms.RadioSelect, initial='1')
    startingbid = forms.CharField(label='Giá khởi điểm (.000)',widget=forms.TextInput(attrs={'data-mask': "VND 999999",'title':"Đơn giá 1000VND"}))
    category = forms.ChoiceField(label='Danh mục', choices=get_values)
    name = forms.CharField(label='Tiêu đề')
    image = forms.ImageField(label='Hình ảnh')
    decription = forms.CharField(label='Mô tả sản phẩm', widget=forms.Textarea())
    shipping = forms.ChoiceField(label='Phí vận chuyển', choices=[('---Chọn---', '---Chọn---'),
        ('Giá sản phẩm đã bao gồm phí vận chuyển' ,'Giá sản phẩm đã bao gồm phí vận chuyển'),
        ('Người mua tự thanh toán phí vận chuyển', 'Người mua tự thanh toán phí vận chuyển')])


    def __init__(self, *args, **kwargs):
      super(ProductForm, self).__init__(*args, **kwargs)
      for visible in self.visible_fields():
         visible.field.widget.attrs['class'] = 'form-control'

      self.fields['category'].widget.attrs['class'] = 'form-control chosen-select'
      self.fields['duration'].widget.attrs['class'] = 'i - checks pull - left'

    class Meta:
      document = models.product
      fields = ['category', 'name', 'decription', 'quantity', 'shipping', 'image']