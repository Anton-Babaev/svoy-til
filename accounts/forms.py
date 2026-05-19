from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from members.models import Member

class MemberRegistrationForm(forms.ModelForm):
    """Форма регистрации нового члена ассоциации"""
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label='Пароль', min_length=8)
    password_confirm = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label='Подтверждение пароля')
    
    class Meta:
        model = Member
        fields = [
            'company_name',
            'email',
            'inn',
            'ogrn',
            'legal_address',
            'actual_address',
            'director_fullname',
            'phone',
            'membership_category',
            'agreement_signed',
            'charter_document',
            'ogrn_document',
            'inn_document',
        ]
        labels = {
            'company_name': 'Название организации',
            'email': 'Email (будет использован для входа)',
            'inn': 'ИНН',
            'ogrn': 'ОГРН',
            'legal_address': 'Юридический адрес',
            'actual_address': 'Фактический адрес',
            'director_fullname': 'ФИО руководителя',
            'phone': 'Телефон',
            'membership_category': 'Категория членства',
            'agreement_signed': 'Согласие на обработку персональных данных',
            'charter_document': 'Устав организации (PDF, JPG, PNG)',
            'ogrn_document': 'Свидетельство ОГРН (PDF, JPG, PNG)',
            'inn_document': 'Свидетельство ИНН (PDF, JPG, PNG)',
        }
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ООО "Ромашка"'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'info@example.com'}),
            'inn': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '123456789012'}),
            'ogrn': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '123456789012345'}),
            'legal_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'г. Москва, ул. Ленина, д. 10'}),
            'actual_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Если совпадает с юридическим, оставьте пустым'}),
            'director_fullname': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Иванов Иван Иванович'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+7 (495) 123-45-67'}),
            'membership_category': forms.Select(attrs={'class': 'form-select'}),
            'agreement_signed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'charter_document': forms.FileInput(attrs={'class': 'form-control'}),
            'ogrn_document': forms.FileInput(attrs={'class': 'form-control'}),
            'inn_document': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def clean_email(self):
        """Проверяем, что email не занят"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(username=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже зарегистрирован')
        if Member.objects.filter(email=email).exists():
            raise forms.ValidationError('Член с таким email уже существует')
        return email
    
    def clean_inn(self):
        """Проверка ИНН (10 или 12 цифр)"""
        inn = self.cleaned_data.get('inn')
        if not inn.isdigit():
            raise forms.ValidationError('ИНН должен содержать только цифры')
        if len(inn) not in [10, 12]:
            raise forms.ValidationError('ИНН должен содержать 10 или 12 цифр')
        return inn
    
    def clean_ogrn(self):
        """Проверка ОГРН (13 или 15 цифр)"""
        ogrn = self.cleaned_data.get('ogrn')
        if not ogrn.isdigit():
            raise forms.ValidationError('ОГРН должен содержать только цифры')
        if len(ogrn) not in [13, 15]:
            raise forms.ValidationError('ОГРН должен содержать 13 или 15 цифр')
        return ogrn
    
    def clean_phone(self):
        """Очистка телефона"""
        phone = self.cleaned_data.get('phone')
        # Удаляем все пробелы и знаки
        phone = ''.join(c for c in phone if c.isdigit() or c == '+')
        return phone
    
    def clean_charter_document(self):
        """Валидация устава"""
        document = self.cleaned_data.get('charter_document')
        if document:
            # Проверяем размер файла (макс 5 МБ)
            if document.size > 5 * 1024 * 1024:
                raise forms.ValidationError('Размер файла не должен превышать 5 МБ')
            # Проверяем расширение
            ext = document.name.split('.')[-1].lower()
            if ext not in ['pdf', 'jpg', 'jpeg', 'png']:
                raise forms.ValidationError('Поддерживаются только PDF, JPG и PNG файлы')
        return document
    
    def clean_ogrn_document(self):
        """Валидация свидетельства ОГРН"""
        document = self.cleaned_data.get('ogrn_document')
        if document:
            if document.size > 5 * 1024 * 1024:
                raise forms.ValidationError('Размер файла не должен превышать 5 МБ')
            ext = document.name.split('.')[-1].lower()
            if ext not in ['pdf', 'jpg', 'jpeg', 'png']:
                raise forms.ValidationError('Поддерживаются только PDF, JPG и PNG файлы')
        return document
    
    def clean_inn_document(self):
        """Валидация свидетельства ИНН"""
        document = self.cleaned_data.get('inn_document')
        if document:
            if document.size > 5 * 1024 * 1024:
                raise forms.ValidationError('Размер файла не должен превышать 5 МБ')
            ext = document.name.split('.')[-1].lower()
            if ext not in ['pdf', 'jpg', 'jpeg', 'png']:
                raise forms.ValidationError('Поддерживаются только PDF, JPG и PNG файлы')
        return document
    
    def clean(self):
        """Проверка совпадения паролей"""
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError('Пароли не совпадают')
        
        return cleaned_data
