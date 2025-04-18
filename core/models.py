from django.conf import settings
from django.db import models
from django.shortcuts import reverse


# Create your models here.


LABEL_CHOICES = (
    ('S', 'sale'),
    ('N', 'new'),
    ('P', 'promotion')
)

ADDRESS_CHOICES = (
    ('B', 'Billing'),
    ('S', 'Shipping'),
)

class UserAddress(models.Model):
    province = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    save_info = models.BooleanField(default=False)



    def __str__(self):
        return f"Payment by {self.user.username} on {self.timestamp}"


class Slide(models.Model):
    caption1 = models.CharField(max_length=100)
    caption2 = models.CharField(max_length=100)
    link = models.CharField(max_length=100)
    image = models.ImageField(help_text="Size: 1920x570",blank=True,null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return "{} - {}".format(self.caption1, self.caption2)

class Category(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField()
    description = models.TextField()
    image = models.ImageField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("core:category", kwargs={
            'slug': self.slug
        })


class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    label = models.CharField(choices=LABEL_CHOICES, max_length=1)
    slug = models.SlugField()
    stock_no = models.CharField(max_length=10)
    description_short = models.CharField(max_length=50)
    description_long = models.TextField()
    image = models.ImageField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("core:product", kwargs={
            'slug': self.slug
        })

    def get_add_to_cart_url(self):
        return reverse("core:add-to-cart", kwargs={
            'slug': self.slug
        })

    def get_remove_from_cart_url(self):
        return reverse("core:remove-from-cart", kwargs={
            'slug': self.slug
        })


class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    
    def __str__(self):
        return f"{self.quantity} of {self.item.title}"

    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_total_discount_item_price(self):
        return self.quantity * self.item.discount_price

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ref_code = models.CharField(max_length=20)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    shipping_address = models.ForeignKey(
        'BillingAddress', related_name='shipping_address', on_delete=models.SET_NULL, blank=True, null=True)
    billing_address = models.ForeignKey(
        'BillingAddress', related_name='billing_address', on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey(
        'Payment', on_delete=models.SET_NULL, blank=True, null=True)
    coupon = models.ForeignKey(
        'Coupon', on_delete=models.SET_NULL, blank=True, null=True)
    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)

    '''
    1. Item added to cart
    2. Adding a BillingAddress
    (Failed Checkout)
    3. Payment
    4. Being delivered
    5. Received
    6. Refunds
    '''

    def __str__(self):
        return self.user.username

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        if self.coupon:
            total -= self.coupon.amount
        return total



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
DISTRICTS_BY_PROVINCE = (
    ('1', (
        ('Bhojpur', 'Bhojpur'),
        ('Dhankuta', 'Dhankuta'),
        ('Ilam', 'Ilam'),
        ('Jhapa', 'Jhapa'),
        ('Khotang', 'Khotang'),
        ('Morang', 'Morang'),
        ('Okhaldhunga', 'Okhaldhunga'),
        ('Panchthar', 'Panchthar'),
        ('Sankhuwasabha', 'Sankhuwasabha'),
        ('Solukhumbu', 'Solukhumbu'),
        ('Sunsari', 'Sunsari'),
        ('Taplejung', 'Taplejung'),
        ('Terhathum', 'Terhathum'),
        ('Udayapur', 'Udayapur'),
    )),
    ('2', (
        ('Parsa', 'Parsa'),
        ('Bara', 'Bara'),
        ('Rautahat', 'Rautahat'),
        ('Sarlahi', 'Sarlahi'),
        ('Dhanusha', 'Dhanusha'),
        ('Siraha', 'Siraha'),
        ('Mahottari', 'Mahottari'),
        ('Saptari', 'Saptari'),
    )),
    ('3', (
        ('Bhaktapur', 'Bhaktapur'),
        ('Chitwan', 'Chitwan'),
        ('Dhading', 'Dhading'),
        ('Dolakha', 'Dolakha'),
        ('Kathmandu', 'Kathmandu'),
        ('Kavrepalanchok', 'Kavrepalanchok'),
        ('Lalitpur', 'Lalitpur'),
        ('Nuwakot', 'Nuwakot'),
        ('Ramechhap', 'Ramechhap'),
        ('Rasuwa', 'Rasuwa'),
        ('Sindhuli', 'Sindhuli'),
        ('Sindhupalchok', 'Sindhupalchok'),
    )),
    ('4', (
        ('Baglung', 'Baglung'),
        ('Gorkha', 'Gorkha'),
        ('Kaski', 'Kaski'),
        ('Lamjung', 'Lamjung'),
        ('Manang', 'Manang'),
        ('Mustang', 'Mustang'),
        ('Myagdi', 'Myagdi'),
        ('Nawalpur', 'Nawalpur'),
        ('Parbat', 'Parbat'),
        ('Syangja', 'Syangja'),
        ('Tanahun', 'Tanahun'),
    )),
    ('5', (
        ('Arghakhanchi', 'Arghakhanchi'),
        ('Banke', 'Banke'),
        ('Bardiya', 'Bardiya'),
        ('Dang', 'Dang'),
        ('Gulmi', 'Gulmi'),
        ('Kapilvastu', 'Kapilvastu'),
        ('Palpa', 'Palpa'),
        ('Pyuthan', 'Pyuthan'),
        ('Rolpa', 'Rolpa'),
        ('Rukum', 'Rukum'),
        ('Rupandehi', 'Rupandehi'),
    )),
    ('6', (
        ('Dailekh', 'Dailekh'),
        ('Dolpa', 'Dolpa'),
        ('Humla', 'Humla'),
        ('Jajarkot', 'Jajarkot'),
        ('Jumla', 'Jumla'),
        ('Kalikot', 'Kalikot'),
        ('Mugu', 'Mugu'),
        ('Salyan', 'Salyan'),
        ('Surkhet', 'Surkhet'),
        ('Western Rukum', 'Western Rukum'),
    )),
    ('7', (
        ('Achham', 'Achham'),
        ('Baitadi', 'Baitadi'),
        ('Bajhang', 'Bajhang'),
        ('Bajura', 'Bajura'),
        ('Dadeldhura', 'Dadeldhura'),
        ('Darchula', 'Darchula'),
        ('Doti', 'Doti'),
        ('Kailali', 'Kailali'),
        ('Kanchanpur', 'Kanchanpur'),
    )),
)


class BillingAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    street_address = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    province = models.CharField(max_length=100, choices=PROVINCES_OF_NEPAL)
    district = models.CharField(max_length=100, choices=DISTRICTS_BY_PROVINCE)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    default = models.BooleanField(default=False)

    def __str__(self):
        return  f" {self.street_address}, {self.city}, {self.district}, {self.province}"

    class Meta:
        verbose_name_plural = 'BillingAddresses'

class PaymentDetails(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    billing_address = models.CharField(max_length=255, default="")
    payment_image = models.ImageField(upload_to='payment_proofs/')
    payment_method = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)        
        
class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class Coupon(models.Model):
    code = models.CharField(max_length=15)
    amount = models.FloatField()

    def __str__(self):
        return self.code


class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()

    def __str__(self):
        return f"{self.pk}"
