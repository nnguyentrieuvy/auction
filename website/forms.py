from django import forms
from .models import *
from  . import models
from django_mongoengine.forms import DocumentForm


class SignupForm(DocumentForm):
   account = forms.CharField(label='Tên đăng nhập', max_length=100)
   password = forms.CharField(label='Mật khẩu',
                                 widget=forms.PasswordInput(attrs={'placeholder': '****',
                                                                   'title': "Vui lòng nhập mật khẩu"}))
   auth_password = forms.CharField(label='Xác nhận mật khẩu',
                                 widget=forms.PasswordInput(attrs={'placeholder': '****',
                                                                   'title': "Vui xác nhận mật khẩu"}))
   address = forms.CharField(label='Địa chỉ', max_length=100)
   city = forms.ChoiceField(label='Tỉnh/ Thành phố')
   district = forms.ChoiceField(label='Quận/ Huyện')
   email = forms.CharField(max_length=100)

   def __init__(self, *args, **kwargs):
      super(SignupForm, self).__init__(*args, **kwargs)
      self.fields['city'].widget.attrs.update({'name': 'calc_shipping_provinces'})
      self.fields['district'].widget.attrs.update({'name': 'calc_shipping_district'})
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