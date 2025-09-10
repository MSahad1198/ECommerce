# homepage/views.py

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from .models import Customer, Product
from .forms import CustomerRegisterForm, CustomerLoginForm
from .models import Cart, CartItem
from .models import Order, OrderItem
from django.utils import timezone
from django.shortcuts import get_object_or_404



# -----------------------
# Homepage view 
# -----------------------
def homepage(request):
    """
    Displays the homepage with:
    - Categories
    - Featured products (in stock, available, limit 8)
    - Cart count from session
    """
    categories = ['All', 'Meat', 'Fish', 'Veggies', 'Grocery', 'Fruit']

    featured_products = Product.objects.filter(available=True, stock__gt=0)[:8]

    cart = request.session.get('cart', {})
    cart_count = sum(cart.values())

    return render(
        request,
        'homepage/home.html',
        {
            'categories': categories,
            'featured_products': featured_products,
           # 'cart_count': cart_count,
        }
    )


# -----------------------
# Product list / search
# -----------------------
def product_list(request):
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')

    products = Product.objects.all()

    if category and category.lower() != 'all':
        products = products.filter(category__iexact=category)

    if query:
        products = products.filter(name__icontains=query)

    return render(request, 'homepage/products.html', {
        'products': products,
        'query': query,
        'selected_category': category,
        'categories': ['All', 'Meat', 'Fish', 'Veggies', 'Grocery', 'Fruit'],
    })


# -----------------------
# Cart functions (DB for logged-in, session for guests)
# -----------------------

def add_to_cart(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        if not product.available:
            return redirect('product_list')

        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
            item, created = CartItem.objects.get_or_create(cart=cart, product=product)
            item.quantity += 1
            item.save()
        else:
            cart = request.session.get('cart', {})
            cart[str(product_id)] = cart.get(str(product_id), 0) + 1
            request.session['cart'] = cart

    except Product.DoesNotExist:
        pass
    return redirect('product_list')


def remove_from_cart(request, product_id):
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            CartItem.objects.get(cart=cart, product_id=product_id).delete()
        except (Cart.DoesNotExist, CartItem.DoesNotExist):
            pass
    else:
        cart = request.session.get('cart', {})
        if str(product_id) in cart:
            del cart[str(product_id)]
            request.session['cart'] = cart
    return redirect('view_cart')


def decrease_quantity(request, product_id):
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            item = CartItem.objects.get(cart=cart, product_id=product_id)
            if item.quantity > 1:
                item.quantity -= 1
                item.save()
            else:
                item.delete()
        except (Cart.DoesNotExist, CartItem.DoesNotExist):
            pass
    else:
        cart = request.session.get('cart', {})
        if str(product_id) in cart:
            if cart[str(product_id)] > 1:
                cart[str(product_id)] -= 1
            else:
                del cart[str(product_id)]
            request.session['cart'] = cart
    return redirect('view_cart')


def view_cart(request):
    items = []
    total = 0

    if request.user.is_authenticated:
        # Logged-in users → get items from DB cart
        cart, created = Cart.objects.get_or_create(user=request.user)
        for item in cart.items.select_related('product'):
            subtotal = item.product.price * item.quantity
            items.append({
                'product': item.product,
                'quantity': item.quantity,
                'subtotal': subtotal
            })
            total += subtotal
    else:
        # Guests → get items from session
        cart = request.session.get('cart', {})
        for product_id, quantity in cart.items():
            try:
                product = Product.objects.get(id=product_id)
                subtotal = product.price * quantity
                items.append({
                    'product': product,
                    'quantity': quantity,
                    'subtotal': subtotal
                })
                total += subtotal
            except Product.DoesNotExist:
                continue

    return render(request, 'homepage/cart.html', {'items': items, 'total': total})


# -----------------------
# Context processor for cart count
# -----------------------
def cart_count(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        return {'cart_count': sum(item.quantity for item in cart.items.all())}
    else:
        cart = request.session.get('cart', {})
        return {'cart_count': sum(cart.values())}


# -----------------------
# Customer registration
# -----------------------
def register_view(request):
    if request.method == 'POST':
        form = CustomerRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created! You can now log in.")
            return redirect('login')
    else:
        form = CustomerRegisterForm()
    return render(request, 'homepage/register.html', {'form': form})



# -----------------------
# Customer login
# -----------------------
def login_view(request):
    if request.method == 'POST':
        form = CustomerLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            customer = authenticate(request, email=email, password=password)
            if customer is not None:
                login(request, customer)

                # Sync session cart with DB cart
                session_cart = request.session.get('cart', {})
                cart, created = Cart.objects.get_or_create(user=customer)
                for product_id, qty in session_cart.items():
                    product = Product.objects.get(id=product_id)
                    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
                    item.quantity += qty
                    item.save()
                request.session['cart'] = {}  # clear session cart

                return redirect('homepage')
            else:
                messages.error(request, "Invalid credentials")
    else:
        form = CustomerLoginForm()
    return render(request, 'homepage/login.html', {'form': form})



# -----------------------
# Customer logout
# -----------------------
def site_logout(request):
    logout(request)
    return redirect('homepage')


# -----------------------
# Customer profile
# -----------------------
@login_required
def profile(request):
    return render(request, 'homepage/profile.html')

@login_required
def checkout(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    if not cart.items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect('view_cart')

    # ✅ Create the order first
    order = Order.objects.create(
        user=request.user,
        total_price=0
    )

    total = 0
    for item in cart.items.select_related('product'):
        product = item.product
        if product.stock >= item.quantity:
            product.stock -= item.quantity
            if product.stock == 0:
                product.available = False
            product.save()

            # ✅ Add each product as OrderItem
            OrderItem.objects.create(
                order=order,
                product=product,
                price=product.price,
                quantity=item.quantity
            )

            total += product.price * item.quantity
        else:
            messages.error(request, f"Not enough stock for {product.name}")
            return redirect('view_cart')

    # ✅ Update total after loop
    order.total_price = total
    order.save()

    # ✅ Empty the cart
    cart.items.all().delete()

    messages.success(request, f"Order #{order.id} placed successfully!")
    return redirect('homepage')

# -----------------------
# Purchase history 
# -----------------------
@login_required
def order_history(request):
    """Show all past orders for the logged-in user"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'homepage/order_history.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    """Show details of one specific order"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'homepage/order_detail.html', {'order': order})