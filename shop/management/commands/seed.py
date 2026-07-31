from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.contrib.sessions.models import Session
from django.contrib.auth.hashers import make_password
from shop.models import CustomerProfile, Order, OrderItem, Product, User
from shop.encryption import encrypt_card

class Command(BaseCommand):

    def handle(self, *args, **kwargs):

        # Comment this line if you don't want 'python manage.py flush' to be run every time the seed file is invoked.
        call_command("flush", interactive=False) 

        """(OWASP A02:2021) - Cryptographic Failures (CWE-311)
            The flaw is that payment card data is not encrypted. Change ENCRYPT_PAYMENT_CARDS to True to fix.
            (OWASP A07:2021) - Identification and Authentication Failures (CWE-256)
            The flaw is that passwords are stored in plaintext and not hashed. Change USE_HASHED_PASSWORDS to True to fix.
        """
        USE_HASHED_PASSWORDS = False  # Change to True to hash passwords. See above.
        ENCRYPT_PAYMENT_CARDS = False  # Change to True to encrypt payment cards. See above.

        def card(value):
            return encrypt_card(value) if ENCRYPT_PAYMENT_CARDS else value
        
        def password(value):
            return make_password(value) if USE_HASHED_PASSWORDS else value

        admin = User.objects.create(username="admin", password=password("admin"), is_admin=True)
        guest = User.objects.create(username="employee", password=password("employee"))
        alice = User.objects.create(username="Alice", password=password("1"))
        bob = User.objects.create(username="Bob", password=password("2"))
        CustomerProfile.objects.get_or_create(user=alice, defaults={"email": "alice@example.com", "saved_card_number": card("1111222233334444")})
        CustomerProfile.objects.get_or_create(user=bob, defaults={"email": "bob@example.com", "saved_card_number": card("5555666677778888")})
        products = [
            {"name": "Death Wish Coffee", "description": "Strong, high-caffeine", "price": 19.99, "stock": 50},
            {"name": "Paulig Juhla Mokka", "description": "Smooth, traditional", "price": 9.99, "stock": 50},
            {"name": "Presidentti", "description": "Aromatic, refined", "price": 10.99, "stock": 50},
            {"name": "Secret Holiday Blend", "description": "Limited edition", "price": 24.99, "stock": 0},
            {"name": "Starbucks Pike Place Roast", "description": "Smooth, balanced", "price": 12.99, "stock": 50},
        ]
        for product in products:
            Product.objects.get_or_create(name=product["name"], defaults=product)
        coffee_1 = Product.objects.get(name="Death Wish Coffee")
        coffee_2 = Product.objects.get(name="Paulig Juhla Mokka")
        coffee_3 = Product.objects.get(name="Presidentti")
        alice_order = Order.objects.create(user=alice)
        OrderItem.objects.create(order=alice_order, product=coffee_1, quantity=1)
        OrderItem.objects.create(order=alice_order, product=coffee_2, quantity=2)
        bob_order = Order.objects.create(user=bob)
        OrderItem.objects.create(order=bob_order, product=coffee_3, quantity=3)
        self.stdout.write(self.style.SUCCESS("Database seeded successfully."))