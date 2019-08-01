from django import forms

from django_apps.remind import models


# class RemindModelForm(forms.ModelForm):
#     class Meta:
#         model = models.Fruiter
#         fields = ['name', 'pwd']
#         # labels = {
#         #     'name': '用户名',
#         #     'pwd': '密码',
#         # }
#         widgets = {
#             # 'name': forms.CharField(attrs={'class': 'form-control'}),
#             'pwd': forms.PasswordInput(attrs={'class': 'form-control'})
#         }
#         error_messages = {
#             # '__all__': {
#             #
#             # },
#             'pwd': {
#                 'required': '用户名不能为空',
#                 'invalid': '用户名格式错误',
#             }
#         }


class FruiterModelForm(forms.ModelForm):
    age = forms.IntegerField(
        label='年龄',
        max_value=50,
        # widget=forms.widgets.TextInput(attrs={'class': 'form-control'}),
        initial=22
    )

    def clean_age(self):
        age = self.cleaned_data['age']
        print('123',type(age))
        if age < 40:
            raise forms.ValidationError('我是丁怡的rr')
        return age

    class Meta:
        model = models.Fruiter
        fields = '__all__'
        help_texts = {
            'name': '哈哈哈哈哈哈哈'
        }
        error_messages = {
            # '__all__': {
            #     'required': '此处不能为空'
            # },
            'age': {
                'invalid': '请输入一个有效的年龄'
            }
        }
