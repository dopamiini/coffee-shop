from .constants import *
from .encryption import decrypt_card, encrypt_card
from .models import CustomerProfile, LoginAttempt, Order, OrderItem, Product, User
from decimal import Decimal
from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import make_password
from django.db.models import Q
from django.shortcuts import get_object_or_404, render, redirect

def add_to_cart(request, product_id):
    cart = request.session.get("cart", {})
    product_id = str(product_id)
    if product_id in cart:
        cart[product_id] += 1
    else:
        cart[product_id] = 1
    request.session["cart"] = cart
    return redirect("index")

def admin_view(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("/login/")
    try:
        user = User.objects.get(id=user_id)
        if not user.is_admin:
            return redirect("/")
    except User.DoesNotExist:
        return redirect("/login/")
    if request.method == "POST":
        LoginAttempt.objects.all().delete()
    users = User.objects.all()
    profiles = CustomerProfile.objects.all()
    failed_attempts = LoginAttempt.objects.filter(successful=False).order_by("-timestamp")
    return render(request, "shop/admin.html", {"users": users, "profiles": profiles, "failed_attempts": failed_attempts})

def cart(request):
    cart = request.session.get("cart", {})
    cart_items = []
    total = Decimal("0.00")
    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            continue
        subtotal = product.price * quantity
        total += subtotal
        cart_items.append({"product": product, "quantity": quantity, "subtotal": subtotal})
    return render(request, "shop/cart.html", {"cart_items": cart_items, "total": total, "username": request.session.get("username")})

def checkout(request):
    if request.method != "POST":
        return redirect("cart")
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")
    cart = request.session.get("cart", {})
    if not cart:
        return redirect("cart")
    user = User.objects.get(id=user_id)
    for product_id, quantity in cart.items():
        product = Product.objects.get(id=product_id)
        if product.stock < quantity:
            return redirect("cart")
    order = Order.objects.create(user=user)
    for product_id, quantity in cart.items():
        product = Product.objects.get(id=product_id)
        OrderItem.objects.create(order=order, product=product, quantity=quantity)
        product.stock -= quantity
        product.save()
    request.session["cart"] = {}
    return redirect("orders")

"""
    (OWASP A03:2021) - Injection (CWE-89)
    The flaw is that the input is concatenated directly into the SQL query instead of being parameterized. The user can enter 
    "' OR 1=1 --" without the outer quotes to modify the search results. This results in the "Secret Holiday Blend" coffee
    that has no stock to be listed on the page against the filtering rule that restricts products with no stock to be shown.
    
    The SQL query becomes:

    SELECT * FROM shop_product
    WHERE name LIKE '%'
    OR 1=1 -- %'
    AND quantity > 0;

    The single quotation mark closes LIKE '%'. Everything after the double dashes become a comment. The query matches every 
    table row as 1=1 is True and the query effectively becomes WHERE True. The fix is to pass the input as plaintext 
    separately from the SQL query.
"""
def index(request):
    query = request.GET.get("query", "").strip()

    #####################################################################################################################
    # (OWASP A03:2021)(CWE-89) Comment out the first if-else block below and uncomment the second if-else block to fix. #
    #####################################################################################################################
    if query:
        sql = f'''
            SELECT *
            FROM shop_product
            WHERE stock > 0 AND name LIKE '%{query}%'
        '''
        print("Generated SQL:")
        print(sql)
        products = Product.objects.raw(sql)
    else:
        products = Product.objects.filter(stock__gt=0)
    #####################################################################################################################
    #if query:
    #    products = Product.objects.filter(Q(name__icontains=query) | Q(description__icontains=query), stock__gt=0)
    #else:
    #    products = Product.objects.filter(stock__gt=0)
    #####################################################################################################################

    orders = []
    if request.session.get("user_id"):
        orders = Order.objects.filter(user_id=request.session["user_id"])
    return render(request, "shop/index.html", {"orders": orders, "products": products, "query": query, "username": request.session.get("username")})

"""
    (OWASP A07:2021) - Identification and Authentication Failures (CWE-256)
    The flaw is that passwords are stored in plaintext and not hashed. This is fixed by hashing the passwords.
    (OWASP A07:2021) - Identification and Authentication Failures (CWE-307)
    The flaw is that failed login attempts are not limited. The fix is to have a counter that keeps track of failed login
    attempts from a given IP and block any further tries after N attemps (see constants.py). Currently set to 3 attemps.
    (OWASP A09:2021) - Security Logging and Monitoring Failures (CWE-778)
    The flaw is that failed login attempts are not logged. The fix is to keep a record of failed login attempts (username, IP, time/date, ...).
"""
def login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        ################################################################################################################################################################################
        # (OWASP A07:2021)(CWE-256, CWE-307) (OWASP A09:2021)(CWE-778) Comment the first try-except block below and uncomment the second try-except block                              #
        # with the three lines above it to fix all three flaws.                                                                                                                        #
        ################################################################################################################################################################################
        try:
            user = User.objects.get(username=username, password=password)
            request.session["user_id"] = user.id
            request.session["username"] = user.username
            if user.is_admin:
                return redirect("/dashboard/")
            return redirect("/")
        except User.DoesNotExist:
            return render(request, "shop/login.html", {"error": "Invalid username or password"})
        ################################################################################################################################################################################
        #attempts = request.session.get("login_attempts", 0)
        #if attempts >= MAX_ATTEMPTS:
        #    return render(request, "shop/login.html", {"error": "Too many failed login attempts. Try again later.", "attempts": attempts, "max_attempts": MAX_ATTEMPTS})
        #try:
        #    user = User.objects.get(username=username)
        #    if check_password(password, user.password):
        #        request.session["login_attempts"] = 0
        #        request.session["user_id"] = user.id
        #        request.session["username"] = user.username
        #        if user.is_admin:
        #            return redirect("/dashboard/")
        #        return redirect("/")
        #    else:
        #        request.session["login_attempts"] = attempts + 1
        #        LoginAttempt.objects.create(username=username, ip_address=request.META.get("REMOTE_ADDR"), user_agent=request.META.get("HTTP_USER_AGENT", "Unknown"), successful=False)
        #        return render(request, "shop/login.html", {"error": "Invalid username or password", "attempts": attempts + 1, "max_attempts": MAX_ATTEMPTS})
        #except User.DoesNotExist:
        #    request.session["login_attempts"] = attempts + 1
        #    LoginAttempt.objects.create(username=username, ip_address=request.META.get("REMOTE_ADDR"), user_agent=request.META.get("HTTP_USER_AGENT", "Unknown"), successful=False)
        #    return render(request, "shop/login.html", {"error": "Invalid username or password", "attempts": attempts + 1, "max_attempts": MAX_ATTEMPTS})
        ################################################################################################################################################################################

    return render(request, "shop/login.html")

def logout(request):
    request.session.flush()
    return redirect("/")

def orders(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")
    user = User.objects.get(id=user_id)
    orders = Order.objects.filter(user=user)
    return render(request, "shop/orders.html", {"orders": orders, "username": user.username})

"""
    (OWASP A02:2021) - Cryptographic Failures (CWE-311)
    The flaw is that payment card data is not encrypted. If the database is hacked then the attacker can get access
    to sensitive information. The fix is to simply encrypt the data. Then even if the database is compromised the
    attacker will still need an encryption key.
    (OWASP A07:2021) - Identification and Authentication Failures (CWE-521) - Weak Password Requirements
    The flaw is that password strength is not enforced. The fix is to simply add rules for valid password generation. 
    This is a very simple demo with minimal rules (see constants.py).
"""
def register(request):
    error = None
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")
        saved_card_number = request.POST.get("saved_card_number", "").strip()
        if not username or not email or not password or not saved_card_number:
            error = "All fields are required."
        elif password != confirm_password:
            error = "Passwords do not match."

        #################################################################################
        # (OWASP A07:2021)(CWE-521) Comment out the lines below fix.                    #
        #################################################################################
        #elif len(password) < MIN_PASSWORD_LENGTH:
        #    error = f"Password must contain at least {MIN_PASSWORD_LENGTH} characters."
        #elif password.lower() in COMMON_PASSWORDS:
        #    error = "Choose a less common password."
        #elif username.lower() in password.lower():
        #    error = "Password must not contain your username."
        #################################################################################

        elif User.objects.filter(username=username).exists():
            error = "Username already exists."
        elif CustomerProfile.objects.filter(email=email).exists():
            error = "Email is already registered."
        else:

            ############################################################################################################
            # (OWASP A07:2021)(CWE-256) Comment out the first line below and uncomment the second to fix.              #
            ############################################################################################################
            user = User.objects.create(username=username, password=password)                                          
            ############################################################################################################
            #user = User.objects.create(username=username, password=make_password(password))                            
            ############################################################################################################

            ############################################################################################################
            # (OWASP A02:2021)(CWE-311) Comment out the first line below and uncomment the second line below to fix.   #
            ############################################################################################################
            CustomerProfile.objects.create(user=user, email=email, saved_card_number=saved_card_number)
            ############################################################################################################
            #CustomerProfile.objects.create(user=user, email=email, saved_card_number=encrypt_card(saved_card_number)) 
            ############################################################################################################

            return redirect("login")
    return render(request, "shop/register.html", {"error": error})

"""
    (OWASP A02:2021) - Cryptographic Failures (CWE-311)
    The flaw is that payment card data is not encrypted. This method simply decrypts the data and displays the 
    last four digits of the payment card.
"""
def user_profile(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")
    user = User.objects.get(id=user_id)
    profile = CustomerProfile.objects.get(user=user)
    orders = Order.objects.filter(user=user)

    ##########################################################################################################
    # (OWASP A02:2021)(CWE-311) Comment out the first line below and uncomment the second line below to fix. #
    ##########################################################################################################
    card_number = profile.saved_card_number                                                                 
    ##########################################################################################################
    #card_number = decrypt_card(profile.saved_card_number)                                                   
    ##########################################################################################################

    if len(card_number) >= 4:
        masked_card = "**** **** **** " + card_number[-4:]
    else:
        masked_card = "****"
    return render(request, "shop/profile.html", {"user": user, "profile": profile, "orders": orders, "masked_card": masked_card})

""" 
    (OWASP A01:2021) - Broken Access Control (CWE-639) - Authorization Bypass Through User-Controlled Key
    The flaw is that there is no authorization check to verify the user has permission to access the order. The fix is to 
    verify the order belongs to them.
"""
def view_order(request, order_id):
   
    ##############################################################################################################
    # (OWASP A01:2021)(CWE-639) Comment out the line below and uncomment the next three lines below that to fix. #
    ##############################################################################################################
    order = Order.objects.get(id=order_id)                                                                      
    ##############################################################################################################
    #if not request.session.get("user_id"):                                                                       
    #    return redirect("/login/")
    #order = get_object_or_404(Order, id=order_id, user_id=request.session["user_id"])
    ##############################################################################################################

    items = OrderItem.objects.filter(order=order)
    return render(request, "shop/order.html", {"order": order, "items": items, "username": request.session.get("username")})