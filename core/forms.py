from django import forms
from .models import UserAddress, PaymentDetails, BillingAddress
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, HTML
from django.core.validators import FileExtensionValidator

# List of provinces in Nepal
PROVINCES_OF_NEPAL = (
    ('', 'Select Province'),
    ('1', 'Province 1'),
    ('2', 'Province 2'),
    ('3', 'Bagmati Province'),
    ('4', 'Gandaki Province'),
    ('5', 'Lumbini Province'),
    ('6', 'Karnali Province'),
    ('7', 'Sudurpashchim Province'),
)

# List of districts in Nepal (grouped by province)
DISTRICTS_BY_PROVINCE = {
    '1': [('Bhojpur', 'Bhojpur'), ('Dhankuta', 'Dhankuta'), ('Ilam', 'Ilam'), ('Jhapa', 'Jhapa'), ('Khotang', 'Khotang'), ('Morang', 'Morang'), ('Okhaldhunga', 'Okhaldhunga'), ('Panchthar', 'Panchthar'), ('Sankhuwasabha', 'Sankhuwasabha'), ('Solukhumbu', 'Solukhumbu'), ('Sunsari', 'Sunsari'), ('Taplejung', 'Taplejung'), ('Terhathum', 'Terhathum'), ('Udayapur', 'Udayapur')],
    '2': [('Parsa', 'Parsa'), ('Bara', 'Bara'), ('Rautahat', 'Rautahat'), ('Sarlahi', 'Sarlahi'), ('Dhanusha', 'Dhanusha'), ('Siraha', 'Siraha'), ('Mahottari', 'Mahottari'), ('Saptari', 'Saptari')],
    '3': [('Bhaktapur', 'Bhaktapur'), ('Chitwan', 'Chitwan'), ('Dhading', 'Dhading'), ('Dolakha', 'Dolakha'), ('Kathmandu', 'Kathmandu'), ('Kavrepalanchok', 'Kavrepalanchok'), ('Lalitpur', 'Lalitpur'), ('Nuwakot', 'Nuwakot'), ('Ramechhap', 'Ramechhap'), ('Rasuwa', 'Rasuwa'), ('Sindhuli', 'Sindhuli'), ('Sindhupalchok', 'Sindhupalchok')],
    '4': [('Baglung', 'Baglung'), ('Gorkha', 'Gorkha'), ('Kaski', 'Kaski'), ('Lamjung', 'Lamjung'), ('Manang', 'Manang'), ('Mustang', 'Mustang'), ('Myagdi', 'Myagdi'), ('Nawalpur', 'Nawalpur'), ('Parbat', 'Parbat'), ('Syangja', 'Syangja'), ('Tanahun', 'Tanahun')],
    '5': [('Arghakhanchi', 'Arghakhanchi'), ('Banke', 'Banke'), ('Bardiya', 'Bardiya'), ('Dang', 'Dang'), ('Gulmi', 'Gulmi'), ('Kapilvastu', 'Kapilvastu'), ('Palpa', 'Palpa'), ('Pyuthan', 'Pyuthan'), ('Rolpa', 'Rolpa'), ('Rukum', 'Rukum'), ('Rupandehi', 'Rupandehi')],
    '6': [('Dailekh', 'Dailekh'), ('Dolpa', 'Dolpa'), ('Humla', 'Humla'), ('Jajarkot', 'Jajarkot'), ('Jumla', 'Jumla'), ('Kalikot', 'Kalikot'), ('Mugu', 'Mugu'), ('Salyan', 'Salyan'), ('Surkhet', 'Surkhet'), ('Western Rukum', 'Western Rukum')],
    '7': [('Achham', 'Achham'), ('Baitadi', 'Baitadi'), ('Bajhang', 'Bajhang'), ('Bajura', 'Bajura'), ('Dadeldhura', 'Dadeldhura'), ('Darchula', 'Darchula'), ('Doti', 'Doti'), ('Kailali', 'Kailali'), ('Kanchanpur', 'Kanchanpur')],
}

class CheckoutForm(forms.Form):
    full_name = forms.CharField(max_length=100, required=True, label="Full Name")
    email = forms.EmailField(required=True, label="Email Address")
    phone = forms.CharField(max_length=15, required=True, label="Phone Number")
    
    # Province field
    province = forms.ChoiceField(
        choices=PROVINCES_OF_NEPAL,
        widget=forms.Select(attrs={'class': 'form-control', 'onchange': 'loadDistricts(this)'}),
        label="Province"
    )

    # District field (initially empty, populated dynamically)
    district = forms.ChoiceField(
        choices=[('', 'Select District')],
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="District"
    )
    city = forms.CharField(max_length=100, required=True, label="City")
    street_address = forms.CharField(max_length=200, required=True, label="Street Address")
   

    payment_image = forms.ImageField(
        required=True,
        label="Upload Payment Proof",
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])],
        widget=forms.ClearableFileInput(attrs={'class': 'form-control-file'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'full_name',
            'email',
            'phone',
            'street_address',
            'city',
            'province',
            'district',
            'payment_option',
            HTML("""
                <div id="qr-code-container" style="display: none;">
                    <p>Scan the QR code to complete your payment:</p>
                    <img id="qr-code-image" src="Esewa.QR.jpg" alt="QR Code" style="width: 200px; height: 200px;">
                </div>
            """),
            'payment_image',
            Submit('submit', 'Place Order', css_class='btn btn-primary btn-block')
        )

    def clean_payment_image(self):
        payment_image = self.cleaned_data.get('payment_image')
        if self.cleaned_data['payment_option'] != 'select payment method' and not payment_image:
            raise forms.ValidationError("Please upload a payment proof image.")
        return payment_image


class UserAddressForm(forms.ModelForm):
    class Meta:
        model = UserAddress
        fields = ['province', 'district', 'save_info']


class PaymentDetailsForm(forms.ModelForm):
    class Meta:
        model = PaymentDetails
        fields = ['payment_image']