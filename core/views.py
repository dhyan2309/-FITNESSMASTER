from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login  
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from functools import wraps
from .models import *
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

# Create your views here.
def index(request):
    return render(request,'index.html')


from django.utils.translation import activate

def set_language(request):
    """Set user selected language (en/hi) and redirect back."""
    lang = (request.GET.get('lang') or '').strip().lower()
    if lang not in {'en', 'hi'}:
        lang = 'en'

    # Set in session
    request.session['django_language'] = lang
    # Activate for current request
    activate(lang)
    
    next_url = request.GET.get('next') or request.META.get('HTTP_REFERER') or '/' 
    response = redirect(next_url)
    # Set cookie as well (Django standard)
    response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang)
    return response


def set_currency(request):
    """Set user selected currency (INR/USD) and redirect back."""
    curr = (request.GET.get('currency') or 'INR').strip().upper()
    if curr not in {'INR', 'USD'}:
        curr = 'INR'
    request.session['currency'] = curr
    next_url = request.GET.get('next') or request.META.get('HTTP_REFERER') or '/'
    return redirect(next_url)


def register(request):
    next_url = (request.POST.get('next') or request.GET.get('next') or '').strip()
    context = {'next_url': next_url}

    if request.method == 'POST':
        full_name = (request.POST.get('fullname') or '').strip()
        email     = (request.POST.get('email') or '').strip()
        username  = (request.POST.get('username') or request.POST.get('fuuserllname') or '').strip()
        password  = request.POST.get('password') or request.POST.get('password1') or ''
        password2 = request.POST.get('password2') or request.POST.get('confirm_password') or ''

        role      = (request.POST.get('role') or 'customer').strip()
        phone_number = (request.POST.get('phone_number') or request.POST.get('mobileno') or request.POST.get('phone') or '').strip()
        trainer_category = (request.POST.get('trainer_category') or request.POST.get('training_category') or '').strip()
        specialization = (request.POST.get('specialization') or '').strip()

        allowed_roles = {'admin', 'trainer', 'customer'}
        if role not in allowed_roles:
            messages.error(request, 'Invalid role selected.')
            return render(request, 'register.html', context)

        
        if not username:
            messages.error(request, 'Username is required.')
            return render(request, 'register.html', context)
        if not password:
            messages.error(request, 'Password is required.')
            return render(request, 'register.html', context)
        if not full_name or not email:
            messages.error(request, 'Please fill in name and email.')
            return render(request, 'register.html', context)
        if not phone_number:
            messages.error(request, 'Phone number is required.')
            return render(request, 'register.html', context)

        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken. Choose another.')
            return render(request, 'register.html', context)

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered. Try logging in.')
            return render(request, 'register.html', context)

        user = User.objects.create_user(
            username   = username,
            password   = password,
            email      = email,
            first_name = full_name,
        )

        UserProfile.objects.create(
            user      = user,
            full_name = full_name,
            email     = email,
            phone_number = phone_number,
            role      = role,
        )

        if role == 'trainer':
            category_map = {'gym': 'Gym', 'yoga': 'Yoga', 'zumba': 'Zumba'}
            training_category = category_map.get(trainer_category.lower(), 'Gym') if trainer_category else 'Gym'
            Trainer.objects.create(
                user              = user,
                full_name         = full_name,
                training_category = training_category,
                specialization    = specialization or '',
            )

        if role == 'customer':
            Customer.objects.create(
                user      = user,
                full_name = full_name,
            )

        messages.success(request, 'Account created! Please log in.')
        if next_url and next_url.startswith('/'):
            return redirect(f"{reverse('login')}?next={next_url}")
        return redirect('login')

    return render(request, 'register.html', context)

def about(request):
    return render(request,'about.html')

def package(request):
    packages = Package.objects.all().order_by('duration')
    return render(request, 'package.html', {'packages': packages})


def package_payment_choice(request, pk):
    package = get_object_or_404(Package, pk=pk)
    customer = None

    if request.user.is_authenticated:
        customer = Customer.objects.filter(user=request.user).select_related('assigned_package').first()

    if request.method == 'POST':
        payment_method = (request.POST.get('payment_method') or '').strip().lower()

        if not request.user.is_authenticated:
            messages.info(request, 'Please log in to continue with payment.')
            return redirect(f"{reverse('login')}?next={request.path}")

        if customer is None:
            messages.error(request, 'Only customer accounts can purchase packages.')
            return redirect_by_role(request.user)

        if payment_method not in {'cash', 'online'}:
            messages.error(request, 'Please choose a payment method.')
            return redirect('package_payment_choice', pk=package.pk)

        customer.assigned_package = package
        customer.save()

        if payment_method == 'cash':
            Payment.objects.create(
                customer=customer,
                amount=package.price,
                payment_method='Cash',
            )
            messages.success(request, f'Cash payment recorded for {package.package_name}.')
            return redirect('customer_dashboard')

        messages.success(request, f'{package.package_name} selected. Continue with online payment.')
        return redirect('customer_payment')

    return render(request, 'customer/package_payment_choice.html', {
        'package': package,
        'customer': customer,
    })

def user_login(request):
    next_url = (request.POST.get('next') or request.GET.get('next') or '').strip()
    context = {'next_url': next_url}

    if request.user.is_authenticated:
        if next_url and next_url.startswith('/'):
            return redirect(next_url)
        return redirect_by_role(request.user)

    if request.method == 'POST':
        identifier = (request.POST.get('username') or '').strip()
        password = request.POST.get('password') or ''

        user = None
        if identifier and password:
            matched_user = (
                User.objects.filter(username=identifier).first()
                or User.objects.filter(email=identifier).first()
            )
            if matched_user is not None:
                user = authenticate(
                    request,
                    username=matched_user.username,
                    password=password,
                )

        if user is not None:

            
            if user.is_superuser:
                auth_login(request, user)
                if next_url and next_url.startswith('/'):
                    return redirect(next_url)
                return redirect('admin_dashboard')

            
            try:
                profile = UserProfile.objects.get(user=user)

                auth_login(request, user)

                if next_url and next_url.startswith('/'):
                    return redirect(next_url)

                if profile.role == 'admin':
                    return redirect('admin_dashboard')
                elif profile.role == 'trainer':
                    return redirect('trainer_dashboard')  
                elif profile.role == 'customer':
                    return redirect('customer_dashboard')  
                else:
                    messages.error(request, 'Unknown role. Contact admin.')

            except UserProfile.DoesNotExist:
                messages.error(request, 'Profile not found. Contact admin.')
        else:
            messages.error(request, 'Wrong username/email or password.')

    return render(request, 'login.html', context)


def redirect_by_role(user):
    if user.is_superuser:
        return redirect('admin_dashboard')
    try:
        profile = UserProfile.objects.get(user=user)
        if profile.role == 'admin':
            return redirect('admin_dashboard')
        elif profile.role == 'trainer':
            return redirect('trainer_dashboard')
        elif profile.role == 'customer':
            return redirect('customer_dashboard')
    except:
        pass
    return redirect('index')


# ── admin pages ────────────────────────────────────────

def dashboard(request):
    if request.user.is_authenticated:
        return redirect_by_role(request.user)
    return redirect('login')


def is_admin_user(user):
    if user.is_superuser:
        return True
    try:
        profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        return False
    return profile.role == 'admin'


def admin_required(view_func):
    @wraps(view_func)
    @login_required(login_url='/login/')
    def _wrapped(request, *args, **kwargs):
        if not is_admin_user(request.user):
            messages.error(request, 'Access denied. Admins only.')
            return redirect_by_role(request.user)
        return view_func(request, *args, **kwargs)

    return _wrapped


@login_required(login_url='login')
def admin_dashboard(request):
    try:
        profile = UserProfile.objects.get(user=request.user)
        if profile.role != 'admin' and not request.user.is_superuser:
            return redirect('login')
    except UserProfile.DoesNotExist:
        if not request.user.is_superuser:
            return redirect('login')

    from django.utils import timezone
    from datetime import timedelta
    from django.db import models as db_models

    today    = timezone.now().date()
    one_week = today + timedelta(days=7)

    context = {
        'total_packages'  : Package.objects.count(),
        'total_customers' : Customer.objects.count(),
        'total_trainers'  : Trainer.objects.count(),
        'total_payments'  : Payment.objects.count(),
        'total_feedbacks' : Feedback.objects.count(),
        'total_products'  : Product.objects.count(),
        'total_notices'   : Notice.objects.count(),
        'total_invoices'  : Invoice.objects.count(),
        'total_enquiries' : Enquiry.objects.count(),
        'total_revenue'   : Payment.objects.aggregate(
                                total=db_models.Sum('amount')
                            )['total'] or 0,
        'expiring_count'  : Customer.objects.filter(
                                end_date__lte=one_week,
                                end_date__gte=today
                            ).count(),
        'recent_payments' : Payment.objects.order_by('-payment_date')[:5],
        'recent_feedbacks': Feedback.objects.select_related(
                                'customer',
                                'customer__assigned_package',
                            ).order_by('-id')[:5],
        'expiring_soon'   : Customer.objects.filter(
                                end_date__lte=one_week,
                                end_date__gte=today
                            ),
        'total_equipment'           : Equipment.objects.count(),
        'equipment_maintenance'     : Equipment.objects.filter(status='Under Maintenance').count(),
        'new_enquiries'             : Enquiry.objects.filter(status='New').count(),
    }

    return render(request, 'admin/admin_dashboard.html', context)


def user_logout(request):
    auth_logout(request)
    return redirect('login')

@login_required(login_url='login')
def package_list(request):
    packages = Package.objects.all().order_by('duration')
    return render(request, 'admin/package_list.html', {'packages': packages})


@login_required(login_url='login')
def package_add(request):
    if request.method == 'POST':
        Package.objects.create(
            package_name = request.POST['package_name'],
            duration     = request.POST['duration'],
            description  = request.POST['description'],
            price        = request.POST['price'],
        )
        messages.success(request, 'Package created successfully!')
        return redirect('package_list')
    return render(request, 'admin/package_form.html', {'action': 'Add'})


@login_required(login_url='login')
def package_edit(request, pk):
    package = get_object_or_404(Package, pk=pk)
    if request.method == 'POST':
        package.package_name = request.POST['package_name']
        package.duration     = request.POST['duration']
        package.description  = request.POST['description']
        package.price        = request.POST['price']
        package.save()
        messages.success(request, 'Package updated successfully!')
        return redirect('package_list')
    return render(request, 'admin/package_form.html', {
        'action'  : 'Edit',
        'package' : package
    })


@login_required(login_url='login')
def package_delete(request, pk):
    package = get_object_or_404(Package, pk=pk)
    package.delete()
    messages.success(request, 'Package deleted!')
    return redirect('package_list')


@login_required(login_url='/login/')
def trainer_list(request):
    trainers = Trainer.objects.select_related('user').all()
    return render(request, 'admin/trainer_list.html', {'trainers': trainers})


@login_required(login_url='/login/')
def trainer_add(request):
    if request.method == 'POST':

        
        if User.objects.filter(username=request.POST['username']).exists():
            messages.error(request, 'Username already taken. Choose another.')
            return render(request, 'admin/trainer_form.html', {'action': 'Add'})

        
        user = User.objects.create_user(
            username   = request.POST['username'],
            password   = request.POST['password'],
            email      = request.POST['email'],
            first_name = request.POST['full_name'],
        )

        
        UserProfile.objects.create(
            user         = user,
            full_name    = request.POST['full_name'],
            phone_number = request.POST['phone_number'],
            email        = request.POST['email'],
            role         = 'trainer',
        )

        
        Trainer.objects.create(
            user              = user,
            full_name         = request.POST['full_name'],
            training_category = request.POST['training_category'],
            specialization    = request.POST['specialization'],
        )

        messages.success(request, 'Trainer added successfully!')
        return redirect('trainer_list')

    return render(request, 'admin/trainer_form.html', {'action': 'Add'})


@login_required(login_url='/login/')
def trainer_edit(request, pk):
    trainer = get_object_or_404(Trainer, pk=pk)

    if request.method == 'POST':
        
        trainer.full_name         = request.POST['full_name']
        trainer.training_category = request.POST['training_category']
        trainer.specialization    = request.POST['specialization']
        trainer.save()

        
        try:
            profile              = UserProfile.objects.get(user=trainer.user)
            profile.full_name    = request.POST['full_name']
            profile.phone_number = request.POST['phone_number']
            profile.save()
        except:
            pass

        
        trainer.user.email      = request.POST['email']
        trainer.user.first_name = request.POST['full_name']
        trainer.user.save()

        messages.success(request, 'Trainer updated successfully!')
        return redirect('trainer_list')

    return render(request, 'admin/trainer_form.html', {
        'action'  : 'Edit',
        'trainer' : trainer,
    })


@login_required(login_url='/login/')
def trainer_delete(request, pk):
    trainer = get_object_or_404(Trainer, pk=pk)
    trainer.user.delete()  
    messages.success(request, 'Trainer deleted successfully!')
    return redirect('trainer_list')


@login_required(login_url='/login/')
def customer_list(request):
    customers = Customer.objects.select_related(
        'user', 'assigned_package', 'assigned_trainer'
    ).all()
    return render(request, 'admin/customer_list.html', {'customers': customers})

@login_required(login_url='/login/')
def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)

    if request.method == 'POST':

       
        customer.full_name = request.POST['full_name']
        customer.gender    = request.POST['gender']
        customer.address   = request.POST['address']

        if request.POST.get('package'):
            customer.assigned_package = Package.objects.get(pk=request.POST['package'])
        else:
            customer.assigned_package = None

        if request.POST.get('trainer'):
            customer.assigned_trainer = Trainer.objects.get(pk=request.POST['trainer'])
        else:
            customer.assigned_trainer = None

        customer.start_date = request.POST['start_date'] or None
        customer.end_date   = request.POST['end_date'] or None
        customer.save()

        
        try:
            profile              = UserProfile.objects.get(user=customer.user)
            profile.full_name    = request.POST['full_name']
            profile.phone_number = request.POST['phone_number']
            profile.save()
        except:
            pass

        
        customer.user.email      = request.POST['email']
        customer.user.first_name = request.POST['full_name']
        customer.user.save()

        messages.success(request, 'Customer updated successfully!')
        return redirect('customer_list')

    context = {
        'action'   : 'Edit',
        'customer' : customer,
        'packages' : Package.objects.all(),
        'trainers' : Trainer.objects.all(),
    }
    return render(request, 'admin/customer_form.html', context)


@login_required(login_url='/login/')
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    customer.user.delete() 
    messages.success(request, 'Customer deleted successfully!')
    return redirect('customer_list')


@login_required(login_url='/login/')
def customer_setdates(request, pk):
    customer = get_object_or_404(Customer, pk=pk)

    if request.method == 'POST':

        if request.POST.get('package'):
            customer.assigned_package = Package.objects.get(pk=request.POST['package'])
        else:
            customer.assigned_package = None

        if request.POST.get('trainer'):
            customer.assigned_trainer = Trainer.objects.get(pk=request.POST['trainer'])
        else:
            customer.assigned_trainer = None

        customer.start_date = request.POST['start_date'] or None
        customer.end_date   = request.POST['end_date'] or None
        customer.save()

        messages.success(request, 'Dates updated successfully!')
        return redirect('customer_list')

    context = {
        'customer' : customer,
        'packages' : Package.objects.all(),
        'trainers' : Trainer.objects.all(),
    }
    return render(request, 'admin/customer_setdates.html', context)


@login_required(login_url='/login/')
def admin_notice_list(request):
    notices = Notice.objects.all().order_by('-id')
    return render(request, 'admin/notice_list.html', {'notices': notices})


@login_required(login_url='/login/')
def admin_notice_add(request):
    if request.method == 'POST':
        title   = request.POST['title']
        message = request.POST['message']
        sent_to = request.POST['sent_to']

        
        Notice.objects.create(
            title   = title,
            message = message,
            sent_to = sent_to,
        )

        
        recipient_emails = []

        if sent_to in ['all', 'customer']:
            customer_emails = UserProfile.objects.filter(
                role='customer'
            ).values_list('email', flat=True)
            recipient_emails += list(customer_emails)

        if sent_to in ['all', 'trainer']:
            trainer_emails = UserProfile.objects.filter(
                role='trainer'
            ).values_list('email', flat=True)
            recipient_emails += list(trainer_emails)

        
        recipient_emails = list(set(e for e in recipient_emails if e))

        
        if recipient_emails:
            from django.core.mail import send_mail
            from django.conf import settings

            email_body = f"""
Hello,

You have a new notice from FitnessMaster:

📢 {title}

{message}

—
FitnessMaster Team
"""
            try:
                send_mail(
                    subject      = f'[FitnessMaster] {title}',
                    message      = email_body,
                    from_email   = settings.DEFAULT_FROM_EMAIL,
                    recipient_list = recipient_emails,
                    fail_silently = False,
                )
                messages.success(request, f'Notice sent and email delivered to {len(recipient_emails)} recipient(s)!')
            except Exception as e:
                messages.warning(request, f'Notice saved but email failed: {str(e)}')
        else:
            messages.success(request, 'Notice saved. No email recipients found.')

        return redirect('admin_notice_list')

    return render(request, 'admin/notice_form.html')


@login_required(login_url='/login/')
def admin_notice_delete(request, pk):
    notice = get_object_or_404(Notice, pk=pk)
    notice.delete()
    messages.success(request, 'Notice deleted.')
    return redirect('admin_notice_list')


def admin_feedback_list(request):
    feedbacks = Feedback.objects.select_related(
        'customer',
        'customer__assigned_package',
    ).order_by('-id')
    return render(request, 'admin/feedback_list.html', {'feedbacks': feedbacks})


def admin_feedback_delete(request, pk):
    feedback = get_object_or_404(Feedback, pk=pk)
    feedback.delete()
    messages.success(request, 'Feedback deleted.')
    return redirect('admin_feedback_list')

#-----------trainer side--------------------------

@login_required(login_url='/login/')
def trainer_dashboard(request):
    
    try:
        trainer = Trainer.objects.get(user=request.user)
    except Trainer.DoesNotExist:
        messages.error(request, 'You are not a trainer.')
        return redirect('login')

    from django.utils import timezone
    from datetime import timedelta

    today    = timezone.now().date()
    one_week = today + timedelta(days=7)

    
    my_clients = Customer.objects.filter(assigned_trainer=trainer)

    context = {
        'trainer'             : trainer,
        'total_clients'       : my_clients.count(),
        'total_diet_plans'    : Dietplan.objects.filter(trainer=trainer).count(),
        'total_exercise_plans': Exerciseplan.objects.filter(trainer=trainer).count(),
        'my_clients'          : my_clients[:5],
        'recent_diet_plans'   : Dietplan.objects.filter(
                                    trainer=trainer
                                ).order_by('-id')[:4],
    }
    return render(request, 'trainer/trainer_dashboard.html', context)


@login_required(login_url='/login/')
def trainer_customer(request):
    
    try:
        trainer = Trainer.objects.get(user=request.user)
    except Trainer.DoesNotExist:
        return redirect('login')

    
    my_clients = Customer.objects.filter(
        assigned_trainer=trainer
    ).select_related('user', 'assigned_package')

    context = {
        'trainer'    : trainer,
        'my_clients' : my_clients,
    }
    return render(request, 'trainer/trainer_customer.html', context)

@login_required(login_url='/login/')
def trainer_diet_plans(request):
    try:
        trainer = Trainer.objects.get(user=request.user)
    except Trainer.DoesNotExist:
        return redirect('login')

    diet_plans = Dietplan.objects.filter(trainer=trainer).select_related('customer')
    context = {
        'trainer'    : trainer,
        'diet_plans' : diet_plans,
    }
    return render(request, 'trainer/diet_plan_list.html', context)


@login_required(login_url='/login/')
def trainer_diet_add(request, customer_pk=None):
    try:
        trainer = Trainer.objects.get(user=request.user)
    except Trainer.DoesNotExist:
        return redirect('login')

    my_clients = Customer.objects.filter(assigned_trainer=trainer)

    if request.method == 'POST':
        customer_id = request.POST.get('customer')
        customer    = get_object_or_404(Customer, pk=customer_id, assigned_trainer=trainer)
        Dietplan.objects.create(
            trainer     = trainer,
            customer    = customer,
            description = request.POST['description'],
            calories    = request.POST['calories'],
        )
        messages.success(request, 'Diet plan added successfully!')
        return redirect('trainer_diet_plans')

    selected_customer = None
    if customer_pk:
        selected_customer = get_object_or_404(Customer, pk=customer_pk, assigned_trainer=trainer)

    context = {
        'trainer'          : trainer,
        'my_clients'       : my_clients,
        'selected_customer': selected_customer,
        'action'           : 'Add',
    }
    return render(request, 'trainer/diet_plan_form.html', context)


@login_required(login_url='/login/')
def trainer_diet_edit(request, pk):
    try:
        trainer = Trainer.objects.get(user=request.user)
    except Trainer.DoesNotExist:
        return redirect('login')

    plan       = get_object_or_404(Dietplan, pk=pk, trainer=trainer)
    my_clients = Customer.objects.filter(assigned_trainer=trainer)

    if request.method == 'POST':
        plan.customer    = get_object_or_404(Customer, pk=request.POST['customer'], assigned_trainer=trainer)
        plan.description = request.POST['description']
        plan.calories    = request.POST['calories']
        plan.save()
        messages.success(request, 'Diet plan updated!')
        return redirect('trainer_diet_plans')

    context = {
        'trainer'    : trainer,
        'plan'       : plan,
        'my_clients' : my_clients,
        'action'     : 'Edit',
    }
    return render(request, 'trainer/diet_plan_form.html', context)


@login_required(login_url='/login/')
def trainer_diet_delete(request, pk):
    try:
        trainer = Trainer.objects.get(user=request.user)
    except Trainer.DoesNotExist:
        return redirect('login')

    plan = get_object_or_404(Dietplan, pk=pk, trainer=trainer)
    plan.delete()
    messages.success(request, 'Diet plan deleted.')
    return redirect('trainer_diet_plans')


@login_required(login_url='/login/')
def trainer_exercise_plans(request):
    try:
        trainer = Trainer.objects.get(user=request.user)
    except Trainer.DoesNotExist:
        return redirect('login')

    exercise_plans = Exerciseplan.objects.filter(trainer=trainer).select_related('customer')
    context = {
        'trainer'        : trainer,
        'exercise_plans' : exercise_plans,
    }
    return render(request, 'trainer/exercise_plan_list.html', context)


@login_required(login_url='/login/')
def trainer_exercise_add(request, customer_pk=None):
    try:
        trainer = Trainer.objects.get(user=request.user)
    except Trainer.DoesNotExist:
        return redirect('login')

    my_clients = Customer.objects.filter(assigned_trainer=trainer)

    if request.method == 'POST':
        customer = get_object_or_404(Customer, pk=request.POST['customer'], assigned_trainer=trainer)
        Exerciseplan.objects.create(
            trainer   = trainer,
            customer  = customer,
            title     = request.POST['title'],
            exercises = request.POST['exercises'],
            category  = request.POST.get('category', ''),
        )
        messages.success(request, 'Exercise plan added successfully!')
        return redirect('trainer_exercise_plans')

    selected_customer = None
    if customer_pk:
        selected_customer = get_object_or_404(Customer, pk=customer_pk, assigned_trainer=trainer)

    context = {
        'trainer'          : trainer,
        'my_clients'       : my_clients,
        'selected_customer': selected_customer,
        'action'           : 'Add',
    }
    return render(request, 'trainer/exercise_plan_form.html', context)


@login_required(login_url='/login/')
def trainer_exercise_edit(request, pk):
    try:
        trainer = Trainer.objects.get(user=request.user)
    except Trainer.DoesNotExist:
        return redirect('login')

    plan       = get_object_or_404(Exerciseplan, pk=pk, trainer=trainer)
    my_clients = Customer.objects.filter(assigned_trainer=trainer)

    if request.method == 'POST':
        plan.customer  = get_object_or_404(Customer, pk=request.POST['customer'], assigned_trainer=trainer)
        plan.title     = request.POST['title']
        plan.exercises = request.POST['exercises']
        plan.category  = request.POST.get('category', '')
        plan.save()
        messages.success(request, 'Exercise plan updated!')
        return redirect('trainer_exercise_plans')

    context = {
        'trainer'    : trainer,
        'plan'       : plan,
        'my_clients' : my_clients,
        'action'     : 'Edit',
    }
    return render(request, 'trainer/exercise_plan_form.html', context)


@login_required(login_url='/login/')
def trainer_exercise_delete(request, pk):
    try:
        trainer = Trainer.objects.get(user=request.user)
    except Trainer.DoesNotExist:
        return redirect('login')

    plan = get_object_or_404(Exerciseplan, pk=pk, trainer=trainer)
    plan.delete()
    messages.success(request, 'Exercise plan deleted.')
    return redirect('trainer_exercise_plans')


@login_required(login_url='/login/')
def trainer_profile(request):
    try:
        trainer = Trainer.objects.get(user=request.user)
    except Trainer.DoesNotExist:
        return redirect('login')

    profile = UserProfile.objects.get(user=request.user)

    if request.method == 'POST':
        trainer.full_name         = request.POST['full_name']
        trainer.training_category = request.POST['training_category']
        trainer.specialization    = request.POST.get('specialization', '')
        trainer.save()

        profile.full_name    = request.POST['full_name']
        profile.phone_number = request.POST.get('phone_number', profile.phone_number)
        profile.save()

        request.user.email      = request.POST.get('email', request.user.email)
        request.user.first_name = request.POST['full_name']
        request.user.save()

        messages.success(request, 'Profile updated successfully!')
        return redirect('trainer_profile')

    context = {
        'trainer' : trainer,
        'profile' : profile,
    }
    return render(request, 'trainer/trainer_profile.html', context)

#-----------customer side--------------------------

from django.utils import timezone

def customer_required(view_func):
    """Decorator: ensures logged-in user is a customer."""
    @login_required(login_url='/login/')
    def _wrapped(request, *args, **kwargs):
        try:
            customer = Customer.objects.get(user=request.user)
        except Customer.DoesNotExist:
            messages.error(request, 'Access denied. Customer account not found.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return _wrapped


@customer_required
def customer_dashboard(request):
    customer = Customer.objects.select_related(
        'assigned_package', 'assigned_trainer'
    ).get(user=request.user)

    today = timezone.now().date()

    
    days_remaining = None
    days_total = None
    progress_percent = 0

    if customer.end_date:
        days_remaining = (customer.end_date - today).days
        days_remaining = max(days_remaining, 0)  

    if customer.start_date and customer.end_date:
        days_total = (customer.end_date - customer.start_date).days
        days_elapsed = (today - customer.start_date).days
        if days_total > 0:
            progress_percent = min(int((days_elapsed / days_total) * 100), 100)

    
    diet_count     = Dietplan.objects.filter(customer=customer).count()
    exercise_count = Exerciseplan.objects.filter(customer=customer).count()

    
    latest_diet     = Dietplan.objects.filter(customer=customer).order_by('-id').first()
    latest_exercise = Exerciseplan.objects.filter(customer=customer).order_by('-id').first()

    
    recent_payments = Payment.objects.filter(customer=customer).order_by('-payment_date')[:3]

    context = {
        'customer'         : customer,
        'today'            : today,
        'days_remaining'   : days_remaining,
        'days_total'       : days_total,
        'progress_percent' : progress_percent,
        'diet_count'       : diet_count,
        'exercise_count'   : exercise_count,
        'latest_diet'      : latest_diet,
        'latest_exercise'  : latest_exercise,
        'recent_payments'  : recent_payments,
    }
    return render(request, 'customer/customer_dashboard.html', context)


@customer_required
def customer_diet_plan(request):
    customer   = Customer.objects.get(user=request.user)
    diet_plans = Dietplan.objects.filter(customer=customer).select_related('trainer').order_by('-id')

    context = {
        'customer'   : customer,
        'diet_plans' : diet_plans,
    }
    return render(request, 'customer/customer_diet_plan.html', context)

@customer_required
def customer_exercise_plan(request):
    customer       = Customer.objects.get(user=request.user)
    exercise_plans = Exerciseplan.objects.filter(customer=customer).select_related('trainer').order_by('-id')

    context = {
        'customer'       : customer,
        'exercise_plans' : exercise_plans,
    }
    return render(request, 'customer/customer_exercise_plan.html', context)

@customer_required
def customer_profile(request):
    customer = Customer.objects.select_related(
        'assigned_package', 'assigned_trainer'
    ).get(user=request.user)
    profile  = UserProfile.objects.get(user=request.user)

    if request.method == 'POST':
        
        full_name    = request.POST.get('full_name', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        gender       = request.POST.get('gender', '').strip()
        address      = request.POST.get('address', '').strip()
        dob          = request.POST.get('date_of_birth', '').strip()

        if not full_name:
            messages.error(request, 'Full name cannot be empty.')
            return redirect('customer_profile')

        
        customer.full_name     = full_name
        customer.gender        = gender
        customer.address       = address
        customer.date_of_birth = dob if dob else None
        customer.save()

        
        profile.full_name    = full_name
        profile.phone_number = phone_number
        profile.save()

        
        request.user.first_name = full_name
        request.user.save()

        messages.success(request, 'Profile updated successfully!')
        return redirect('customer_profile')

    context = {
        'customer' : customer,
        'profile'  : profile,
    }
    return render(request, 'customer/customer_profile.html', context)


import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

@customer_required
def customer_payment(request):
    customer = Customer.objects.select_related('assigned_package').get(user=request.user)
    payments = Payment.objects.filter(customer=customer).order_by('-payment_date')

    from django.db.models import Sum
    total_paid_inr = payments.aggregate(total=Sum('amount'))['total'] or 0

    amount_due_inr = 0
    if customer.assigned_package:
        amount_due_inr = max(float(customer.assigned_package.price) - float(total_paid_inr), 0)

    # Currency support
    USD_RATE = 83.5
    curr = request.session.get('currency', 'INR').upper()
    if curr == 'USD':
        total_paid_display = round(float(total_paid_inr) / USD_RATE, 2)
        amount_due_display = round(amount_due_inr / USD_RATE, 2)
    else:
        total_paid_display = total_paid_inr
        amount_due_display = amount_due_inr

    # Razorpay always charges in INR
    razorpay_order_id = None
    if amount_due_inr > 0:
        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )
        rz_order = client.order.create({
            'amount'         : int(amount_due_inr * 100),
            'currency'       : 'INR',
            'payment_capture': 1,
        })
        razorpay_order_id = rz_order['id']

    context = {
        'customer'             : customer,
        'payments'             : payments,
        'total_paid'           : total_paid_display,
        'total_paid_inr'       : total_paid_inr,
        'amount_due'           : amount_due_display,
        'amount_due_inr'       : amount_due_inr,
        'razorpay_order_id'    : razorpay_order_id,
        'razorpay_key_id'      : settings.RAZORPAY_KEY_ID,
        'usd_rate'             : USD_RATE,
    }
    return render(request, 'customer/customer_payment.html', context)


@csrf_exempt
def razorpay_callback(request):
    """Razorpay calls this after payment is done."""
    if request.method == 'POST':
        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )

        payment_id    = request.POST.get('razorpay_payment_id', '')
        order_id      = request.POST.get('razorpay_order_id', '')
        signature     = request.POST.get('razorpay_signature', '')
        amount        = request.POST.get('amount', '0')

        
        try:
            client.utility.verify_payment_signature({
                'razorpay_order_id'   : order_id,
                'razorpay_payment_id' : payment_id,
                'razorpay_signature'  : signature,
            })
            
            payment_verified = True
        except Exception:
            payment_verified = False

        if payment_verified and request.user.is_authenticated:
            try:
                customer   = Customer.objects.get(user=request.user)
                amount_inr = float(amount) / 100   # Razorpay always in INR paise
                Payment.objects.create(
                    customer       = customer,
                    amount         = amount_inr,
                    payment_method = 'Razorpay',
                )
                # Show success in user's chosen currency
                curr     = request.session.get('currency', 'INR').upper()
                USD_RATE = 83.5
                if curr == 'USD':
                    display_amount = f'${amount_inr / USD_RATE:.2f}'
                else:
                    display_amount = f'₹{amount_inr:.2f}'
                messages.success(request, f'Payment of {display_amount} successful! 🎉')
            except Exception:
                messages.error(request, 'Payment done but could not save. Contact admin.')
        else:
            messages.error(request, 'Payment verification failed. Please try again.')

    return redirect('customer_payment')

@customer_required
def customer_feedback(request):
    customer  = Customer.objects.get(user=request.user)
    feedbacks = Feedback.objects.filter(customer=customer).order_by('-id')

    if request.method == 'POST':
        message = request.POST.get('message', '').strip()
        rating  = request.POST.get('rating', '').strip()

        if not message:
            messages.error(request, 'Please write a feedback message.')
            return redirect('customer_feedback')

        if not rating or not rating.isdigit() or not (1 <= int(rating) <= 5):
            messages.error(request, 'Please select a rating between 1 and 5.')
            return redirect('customer_feedback')

        Feedback.objects.create(
            customer = customer,
            message  = message,
            rating   = int(rating),
        )

        messages.success(request, 'Thank you! Your feedback has been submitted.')
        return redirect('customer_feedback')

    context = {
        'customer'  : customer,
        'feedbacks' : feedbacks,
    }
    return render(request, 'customer/customer_feedback.html', context)


@customer_required
def customer_notices(request):
    customer = Customer.objects.get(user=request.user)

    
    notices = Notice.objects.filter(
        sent_to__in=['all', 'customer']
    ).order_by('-id')

    context = {
        'customer' : customer,
        'notices'  : notices,
    }
    return render(request, 'customer/customer_notice.html', context)

@customer_required
def customer_tracker(request):
    customer = Customer.objects.get(user=request.user)
    records  = BodyRecord.objects.filter(customer=customer).order_by('-recorded_on')

    if request.method == 'POST':
        weight = request.POST.get('weight_kg', '').strip()
        height = request.POST.get('height_cm', '').strip()
        note   = request.POST.get('note', '').strip()

        if not weight or not height:
            messages.error(request, 'Please enter both weight and height.')
            return redirect('customer_tracker')

        try:
            weight = float(weight)
            height = float(height)
            if weight <= 0 or height <= 0:
                raise ValueError
        except ValueError:
            messages.error(request, 'Please enter valid weight and height values.')
            return redirect('customer_tracker')

        BodyRecord.objects.create(
            customer  = customer,
            weight_kg = weight,
            height_cm = height,
            note      = note,
        )
        messages.success(request, 'Your record has been saved successfully!')
        return redirect('customer_tracker')

    
    latest = records.first()

    context = {
        'customer' : customer,
        'records'  : records,
        'latest'   : latest,
    }
    return render(request, 'customer/customer_tracker.html', context)


@customer_required
def customer_tracker_delete(request, pk):
    customer = Customer.objects.get(user=request.user)
    record   = get_object_or_404(BodyRecord, pk=pk, customer=customer)
    record.delete()
    messages.success(request, 'Record deleted.')
    return redirect('customer_tracker')

@customer_required
def customer_store(request):
    customer = Customer.objects.get(user=request.user)
    products = Product.objects.filter(stock__gt=0).order_by('product_name')

    context = {
        'customer' : customer,
        'products' : products,
    }
    return render(request, 'customer/customer_store.html', context)


@customer_required
def customer_order(request, product_pk):
    customer = Customer.objects.get(user=request.user)
    product  = get_object_or_404(Product, pk=product_pk)

    if request.method == 'POST':
        quantity = request.POST.get('quantity', '1').strip()

        try:
            quantity = int(quantity)
            if quantity <= 0:
                raise ValueError
        except ValueError:
            messages.error(request, 'Please enter a valid quantity.')
            return redirect('customer_store')

        if quantity > product.stock:
            messages.error(request, f'Only {product.stock} item(s) in stock.')
            return redirect('customer_store')

        total_price_inr = product.price * quantity

        # Currency conversion for display
        USD_RATE = 83.5
        curr = request.session.get('currency', 'INR').upper()
        if curr == 'USD':
            display_total = round(float(total_price_inr) / USD_RATE, 2)
        else:
            display_total = total_price_inr

        # Razorpay always in INR
        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )
        rz_order = client.order.create({
            'amount'          : int(total_price_inr * 100),  
            'currency'        : 'INR',
            'payment_capture' : 1,
        })

       
        context = {
            'customer'          : customer,
            'product'           : product,
            'quantity'          : quantity,
            'total_price'       : display_total,
            'total_price_inr'   : total_price_inr,
            'razorpay_order_id' : rz_order['id'],
            'razorpay_key_id'   : settings.RAZORPAY_KEY_ID,
            'currency'          : curr,
            'currency_symbol'   : '$' if curr == 'USD' else '₹',
        }
        return render(request, 'customer/customer_checkout.html', context)

    return redirect('customer_store')


@csrf_exempt
def razorpay_order_callback(request):
    """Called after product order payment is completed."""
    if request.method == 'POST':
        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )

        payment_id  = request.POST.get('razorpay_payment_id', '')
        order_id    = request.POST.get('razorpay_order_id', '')
        signature   = request.POST.get('razorpay_signature', '')
        product_pk  = request.POST.get('product_pk')
        quantity    = request.POST.get('quantity')
        total_price = request.POST.get('total_price')

        
        try:
            client.utility.verify_payment_signature({
                'razorpay_order_id'   : order_id,
                'razorpay_payment_id' : payment_id,
                'razorpay_signature'  : signature,
            })
            verified = True
        except Exception:
            verified = False

        if verified and request.user.is_authenticated:
            try:
                customer    = Customer.objects.get(user=request.user)
                product     = Product.objects.get(pk=product_pk)
                quantity    = int(quantity)
                total_inr   = float(total_price) # This is expected to be the INR amount from hidden field

                Order.objects.create(
                    customer    = customer,
                    product     = product,
                    quantity    = quantity,
                    total_price = total_inr,
                )

                product.stock -= quantity
                product.save()

                # Success message in chosen currency
                curr = request.session.get('currency', 'INR').upper()
                USD_RATE = 83.5
                if curr == 'USD':
                    display_amt = f'${total_inr / USD_RATE:.2f}'
                else:
                    display_amt = f'₹{total_inr:.2f}'

                messages.success(
                    request,
                    f'Payment successful! {quantity}x {product.product_name} ordered for {display_amt}. 🎉'
                )
            except Exception as e:
                messages.error(request, f'Payment done but order failed. Contact admin.')
        else:
            messages.error(request, 'Payment verification failed. Order not placed.')

    return redirect('customer_my_orders')


@customer_required
def customer_my_orders(request):
    customer = Customer.objects.get(user=request.user)
    orders   = Order.objects.filter(customer=customer).select_related('product').order_by('-id')

    context = {
        'customer' : customer,
        'orders'   : orders,
    }
    return render(request, 'customer/customer_my_orders.html', context)




@login_required(login_url='/login/')
def admin_product_list(request):
    products = Product.objects.all().order_by('product_name')
    return render(request, 'admin/product_list.html', {'products': products})


@login_required(login_url='/login/')
def admin_product_add(request):
    if request.method == 'POST':
        Product.objects.create(
            product_name = request.POST['product_name'],
            description  = request.POST['description'],
            price        = request.POST['price'],
            stock        = request.POST['stock'],
            image        = request.FILES.get('image'),
        )
        messages.success(request, 'Product added successfully!')
        return redirect('admin_product_list')
    return render(request, 'admin/product_form.html', {'action': 'Add'})


@login_required(login_url='/login/')
def admin_product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.product_name = request.POST['product_name']
        product.description  = request.POST['description']
        product.price        = request.POST['price']
        product.stock        = request.POST['stock']
        if request.FILES.get('image'):
            product.image = request.FILES['image']
        product.save()
        messages.success(request, 'Product updated successfully!')
        return redirect('admin_product_list')
    return render(request, 'admin/product_form.html', {'action': 'Edit', 'product': product})


@login_required(login_url='/login/')
def admin_product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    messages.success(request, 'Product deleted!')
    return redirect('admin_product_list')



import uuid

@login_required(login_url='/login/')
def admin_invoice_list(request):
    invoices = Invoice.objects.select_related(
        'customer', 'payment'
    ).order_by('-generated_on')
    return render(request, 'admin/invoice_list.html', {'invoices': invoices})


@login_required(login_url='/login/')
def admin_invoice_generate(request, customer_pk):
    customer = get_object_or_404(Customer, pk=customer_pk)

    
    payment = Payment.objects.filter(customer=customer).order_by('-payment_date').first()

    
    count      = Invoice.objects.count() + 1
    invoice_no = f"INV-{count:04d}"

    invoice = Invoice.objects.create(
        customer   = customer,
        payment    = payment,
        invoice_no = invoice_no,
        notes      = request.POST.get('notes', ''),
    )

    messages.success(request, f'Invoice {invoice_no} generated for {customer.full_name}!')
    return redirect('admin_invoice_view', pk=invoice.pk)


@login_required(login_url='/login/')
def admin_invoice_view(request, pk):
    invoice  = get_object_or_404(Invoice, pk=pk)
    customer = invoice.customer
    orders   = Order.objects.filter(customer=customer).select_related('product')

    context = {
        'invoice'  : invoice,
        'customer' : customer,
        'orders'   : orders,
    }
    return render(request, 'admin/invoice_view.html', context)


@login_required(login_url='/login/')
def admin_invoice_delete(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    invoice.delete()
    messages.success(request, 'Invoice deleted.')
    return redirect('admin_invoice_list')


@customer_required
def customer_invoices(request):
    customer = Customer.objects.get(user=request.user)
    invoices = Invoice.objects.filter(customer=customer).order_by('-generated_on')
    context  = {
        'customer' : customer,
        'invoices' : invoices,
    }
    return render(request, 'customer/customer_invoices.html', context)


@customer_required
def customer_invoice_view(request, pk):
    customer = Customer.objects.get(user=request.user)
    invoice  = get_object_or_404(Invoice, pk=pk, customer=customer)
    orders   = Order.objects.filter(customer=customer).select_related('product')
    context  = {
        'invoice'  : invoice,
        'customer' : customer,
        'orders'   : orders,
    }
    return render(request, 'customer/customer_invoice_view.html', context)



@login_required(login_url='/login/')
def admin_payment_list(request):
    try:
        profile = UserProfile.objects.get(user=request.user)
        if profile.role != 'admin' and not request.user.is_superuser:
            return redirect('login')
    except UserProfile.DoesNotExist:
        if not request.user.is_superuser:
            return redirect('login')

    from django.db.models import Sum
    payments     = Payment.objects.select_related('customer').order_by('-payment_date')
    total_revenue = payments.aggregate(total=Sum('amount'))['total'] or 0

    context = {
        'payments'      : payments,
        'total_revenue' : total_revenue,
    }
    return render(request, 'admin/payment_list.html', context)


# ── Equipment management ───────────────────────────────

@login_required(login_url='/login/')
def equipment_list(request):
    try:
        profile = UserProfile.objects.get(user=request.user)
        if profile.role != 'admin' and not request.user.is_superuser:
            return redirect('login')
    except UserProfile.DoesNotExist:
        if not request.user.is_superuser:
            return redirect('login')

    equipment = Equipment.objects.all().order_by('name')
    return render(request, 'admin/equipment_list.html', {'equipment': equipment})


@login_required(login_url='/login/')
def equipment_add(request):
    try:
        profile = UserProfile.objects.get(user=request.user)
        if profile.role != 'admin' and not request.user.is_superuser:
            return redirect('login')
    except UserProfile.DoesNotExist:
        if not request.user.is_superuser:
            return redirect('login')

    if request.method == 'POST':
        Equipment.objects.create(
            name             = request.POST['name'],
            category         = request.POST['category'],
            description      = request.POST.get('description', ''),
            quantity         = request.POST.get('quantity', 1),
            status           = request.POST.get('status', 'Working'),
            purchase_date    = request.POST.get('purchase_date') or None,
            last_maintenance = request.POST.get('last_maintenance') or None,
        )
        messages.success(request, 'Equipment added successfully!')
        return redirect('equipment_list')
    return render(request, 'admin/equipment_form.html', {'action': 'Add'})


@login_required(login_url='/login/')
def equipment_edit(request, pk):
    try:
        profile = UserProfile.objects.get(user=request.user)
        if profile.role != 'admin' and not request.user.is_superuser:
            return redirect('login')
    except UserProfile.DoesNotExist:
        if not request.user.is_superuser:
            return redirect('login')

    item = get_object_or_404(Equipment, pk=pk)
    if request.method == 'POST':
        item.name             = request.POST['name']
        item.category         = request.POST['category']
        item.description      = request.POST.get('description', '')
        item.quantity         = request.POST.get('quantity', 1)
        item.status           = request.POST.get('status', 'Working')
        item.purchase_date    = request.POST.get('purchase_date') or None
        item.last_maintenance = request.POST.get('last_maintenance') or None
        item.save()
        messages.success(request, 'Equipment updated successfully!')
        return redirect('equipment_list')
    return render(request, 'admin/equipment_form.html', {'action': 'Edit', 'item': item})


@login_required(login_url='/login/')
def equipment_delete(request, pk):
    try:
        profile = UserProfile.objects.get(user=request.user)
        if profile.role != 'admin' and not request.user.is_superuser:
            return redirect('login')
    except UserProfile.DoesNotExist:
        if not request.user.is_superuser:
            return redirect('login')

    item = get_object_or_404(Equipment, pk=pk)
    item.delete()
    messages.success(request, 'Equipment deleted!')
    return redirect('equipment_list')


# ── Enquiry management ─────────────────────────────────

def enquiry_form(request):
    """Public enquiry form — no login required."""
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        email     = request.POST.get('email', '').strip()
        phone     = request.POST.get('phone', '').strip()
        message   = request.POST.get('message', '').strip()

        if not full_name or not email or not phone or not message:
            messages.error(request, 'Please fill in all fields.')
            return render(request, 'enquiry.html')

        Enquiry.objects.create(
            full_name = full_name,
            email     = email,
            phone     = phone,
            message   = message,
        )
        messages.success(request, 'Thank you! Your enquiry has been submitted. We will contact you soon.')
        return redirect('enquiry_form')

    return render(request, 'enquiry.html')


@login_required(login_url='/login/')
def admin_enquiry_list(request):
    try:
        profile = UserProfile.objects.get(user=request.user)
        if profile.role != 'admin' and not request.user.is_superuser:
            return redirect('login')
    except UserProfile.DoesNotExist:
        if not request.user.is_superuser:
            return redirect('login')

    enquiries = Enquiry.objects.all().order_by('-created_at')
    return render(request, 'admin/enquiry_list.html', {'enquiries': enquiries})


@login_required(login_url='/login/')
def admin_enquiry_detail(request, pk):
    try:
        profile = UserProfile.objects.get(user=request.user)
        if profile.role != 'admin' and not request.user.is_superuser:
            return redirect('login')
    except UserProfile.DoesNotExist:
        if not request.user.is_superuser:
            return redirect('login')

    enquiry = get_object_or_404(Enquiry, pk=pk)
    return render(request, 'admin/enquiry_detail.html', {'enquiry': enquiry})


@login_required(login_url='/login/')
def admin_enquiry_status_update(request, pk):
    try:
        profile = UserProfile.objects.get(user=request.user)
        if profile.role != 'admin' and not request.user.is_superuser:
            return redirect('login')
    except UserProfile.DoesNotExist:
        if not request.user.is_superuser:
            return redirect('login')

    enquiry = get_object_or_404(Enquiry, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in ['New', 'In Progress', 'Resolved']:
            enquiry.status = new_status
            enquiry.save()
            messages.success(request, f'Enquiry status updated to {new_status}.')
        else:
            messages.error(request, 'Invalid status.')
    return redirect('admin_enquiry_detail', pk=pk)


@login_required(login_url='/login/')
def admin_enquiry_delete(request, pk):
    try:
        profile = UserProfile.objects.get(user=request.user)
        if profile.role != 'admin' and not request.user.is_superuser:
            return redirect('login')
    except UserProfile.DoesNotExist:
        if not request.user.is_superuser:
            return redirect('login')

    enquiry = get_object_or_404(Enquiry, pk=pk)
    enquiry.delete()
    messages.success(request, 'Enquiry deleted.')
    return redirect('admin_enquiry_list')
