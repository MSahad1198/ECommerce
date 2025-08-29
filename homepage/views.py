# homepage/views.py

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from .models import Customer, Product
from .forms import CustomerRegisterForm, CustomerLoginForm


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
    categories = ['All', 'Meat', 'Fish', 'Veggies', 'Grocery']

    featured_products = Product.objects.filter(available=True, stock__gt=0)[:8]

    cart = request.session.get('cart', {})
    cart_count = sum(cart.values())

    return render(
        request,
        'homepage/home.html',
        {
            'categories': categories,
            'featured_products': featured_products,
            'cart_count': cart_count,
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
        'categories': ['All', 'Meat', 'Fish', 'Veggies', 'Grocery'],
    })


# -----------------------
# Cart functions
# -----------------------
def add_to_cart(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        if not product.available or product.stock <= 0:
            return redirect('product_list')

        product.stock -= 1
        if product.stock == 0:
            product.available = False
        product.save()

        cart = request.session.get('cart', {})
        cart[str(product_id)] = cart.get(str(product_id), 0) + 1
        request.session['cart'] = cart

    except Product.DoesNotExist:
        pass
    return redirect('product_list')


def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        try:
            product = Product.objects.get(id=product_id)
            quantity = cart[str(product_id)]
            product.stock += quantity
            product.available = True
            product.save()
        except Product.DoesNotExist:
            pass
        del cart[str(product_id)]
        request.session['cart'] = cart
    return redirect('view_cart')


def decrease_quantity(request, product_id):
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        try:
            product = Product.objects.get(id=product_id)
            product.stock += 1
            product.available = True
            product.save()
        except Product.DoesNotExist:
            pass

        if cart[str(product_id)] > 1:
            cart[str(product_id)] -= 1
        else:
            del cart[str(product_id)]
        request.session['cart'] = cart
    return redirect('view_cart')


def view_cart(request):
    cart = request.session.get('cart', {})
    items = []
    total = 0
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
            if customer:
                login(request, customer, backend='django.contrib.auth.backends.ModelBackend')
                request.session['is_customer'] = True
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
