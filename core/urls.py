from django.urls import path
from .views import *
urlpatterns = [
   
    #==============comman urls========================
    path('',index,name='index'),  
    path('set-language/', set_language, name='set_language'),
    path('set-currency/', set_currency, name='set_currency'),
    path('login/',user_login,name='login'),

    path('logout/',   user_logout, name='logout'),
    path('register/',register,name='register'), 
    path('about/',about,name='about'),
    path('package/',package,name='package'),
    path('package/<int:pk>/payment/', package_payment_choice, name='package_payment_choice'),
    path('dashboard/', dashboard, name='dashboard'),

     #==============admin urls=========================
    path('admin/', admin_required(admin_dashboard), name='admin_dashboard'),
    path('admin_dashboard', admin_required(admin_dashboard), name='admin_dashboard_legacy'),

    # Admin Package 
    path('admin/packages/',                admin_required(package_list),   name='package_list'),
    path('admin/packages/add/',            admin_required(package_add),    name='package_add'),
    path('admin/packages/edit/<int:pk>/',  admin_required(package_edit),   name='package_edit'),
    path('admin/packages/delete/<int:pk>/',admin_required(package_delete), name='package_delete'),

    #Admin Trainers
    path('admin/trainers/',                admin_required(trainer_list),   name='trainer_list'),
    path('admin/trainers/add/',            admin_required(trainer_add),    name='trainer_add'),
    path('admin/trainers/edit/<int:pk>/',  admin_required(trainer_edit),   name='trainer_edit'),
    path('admin/trainers/delete/<int:pk>/',admin_required(trainer_delete), name='trainer_delete'),

    # Admin Customer 
    path('admin/customers/',admin_required(customer_list),name='customer_list'),
    path('admin/customers/edit/<int:pk>/',admin_required(customer_edit),name='customer_edit'),
    path('admin/customers/delete/<int:pk>/',admin_required(customer_delete),  name='customer_delete'),
    path('admin/customers/setdates/<int:pk>/',admin_required(customer_setdates),name='customer_setdates'),

    path('admin/notices/',admin_required(admin_notice_list),name='admin_notice_list'),
    path('admin/notices/add/',admin_required(admin_notice_add),name='admin_notice_add'),
    path('admin/notices/delete/<int:pk>/',admin_required(admin_notice_delete), name='admin_notice_delete'),
    path('admin/feedback/', admin_required(admin_feedback_list), name='admin_feedback_list'),
    path('admin/feedback/delete/<int:pk>/', admin_required(admin_feedback_delete), name='admin_feedback_delete'),
    # Admin Payments
    path('admin/payments/', admin_required(admin_payment_list), name='admin_payment_list'),

    # Admin Equipment
    path('admin/equipment/',                admin_required(equipment_list),   name='equipment_list'),
    path('admin/equipment/add/',            admin_required(equipment_add),    name='equipment_add'),
    path('admin/equipment/edit/<int:pk>/',  admin_required(equipment_edit),   name='equipment_edit'),
    path('admin/equipment/delete/<int:pk>/',admin_required(equipment_delete), name='equipment_delete'),

    # Admin Enquiries
    path('admin/enquiries/',                     admin_required(admin_enquiry_list),          name='admin_enquiry_list'),
    path('admin/enquiries/detail/<int:pk>/',      admin_required(admin_enquiry_detail),        name='admin_enquiry_detail'),
    path('admin/enquiries/status/<int:pk>/',      admin_required(admin_enquiry_status_update), name='admin_enquiry_status_update'),
    path('admin/enquiries/delete/<int:pk>/',      admin_required(admin_enquiry_delete),        name='admin_enquiry_delete'),

    # Public Enquiry
    path('enquiry/', enquiry_form, name='enquiry_form'),

    # Trainer pages
    path('trainer/trainer_dashboard',  trainer_dashboard,  name='trainer_dashboard'),
    path('trainer/trainer_customer',  trainer_customer,  name='trainer_customer'),
    # Trainer — Diet Plans
    path('trainer/diet-plans/',trainer_diet_plans,name='trainer_diet_plans'),
    path('trainer/diet-plans/add/',trainer_diet_add,name='trainer_diet_add'),
    path('trainer/diet-plans/add/<int:customer_pk>/',trainer_diet_add,    name='trainer_diet_add_for'),
    path('trainer/diet-plans/edit/<int:pk>/',trainer_diet_edit,   name='trainer_diet_edit'),
    path('trainer/diet-plans/delete/<int:pk>/',trainer_diet_delete,name='trainer_diet_delete'),
    # Trainer — Exercise Plans
    path('trainer/exercise-plans/',trainer_exercise_plans,name='trainer_exercise_plans'),
    path('trainer/exercise-plans/add/',trainer_exercise_add,name='trainer_exercise_add'),
    path('trainer/exercise-plans/add/<int:customer_pk>/',trainer_exercise_add,    name='trainer_exercise_add_for'),
    path('trainer/exercise-plans/edit/<int:pk>/',trainer_exercise_edit,   name='trainer_exercise_edit'),
    path('trainer/exercise-plans/delete/<int:pk>/',trainer_exercise_delete, name='trainer_exercise_delete'),
    path('trainer/profile/', trainer_profile, name='trainer_profile'),

    #==============customer urls=========================
    path('customer/dashboard/', customer_dashboard, name='customer_dashboard'),
    path('customer/diet-plan/',customer_diet_plan,name='customer_diet_plan'),
    path('customer/exercise-plan/', customer_exercise_plan, name='customer_exercise_plan'),
    path('customer/profile/', customer_profile, name='customer_profile'),
    path('customer/payment/', customer_payment, name='customer_payment'),
    path('razorpay/callback/', razorpay_callback, name='razorpay_callback'),
    path('razorpay/order-callback/', razorpay_order_callback, name='razorpay_order_callback'),
    path('customer/feedback/', customer_feedback, name='customer_feedback'),
    path('customer/notices/', customer_notices, name='customer_notices'),
    path('customer/tracker/',customer_tracker,name='customer_tracker'),
    path('customer/tracker/delete/<int:pk>/',customer_tracker_delete, name='customer_tracker_delete'),

    # Customer Store
    path('customer/store/',customer_store,name='customer_store'),
    path('customer/store/order/<int:product_pk>/',customer_order,   name='customer_order'),
    path('customer/my-orders/',customer_my_orders,name='customer_my_orders'),

    # Admin Products
    path('admin/products/',admin_required(admin_product_list),name='admin_product_list'),
    path('admin/products/add/',admin_required(admin_product_add),name='admin_product_add'),
    path('admin/products/edit/<int:pk>/',admin_required(admin_product_edit),   name='admin_product_edit'),
    path('admin/products/delete/<int:pk>/',admin_required(admin_product_delete), name='admin_product_delete'),

    # Admin Invoices
    path('admin/invoices/',admin_required(admin_invoice_list),name='admin_invoice_list'),
    path('admin/invoices/generate/<int:customer_pk>/', admin_required(admin_invoice_generate), name='admin_invoice_generate'),
    path('admin/invoices/view/<int:pk>/',admin_required(admin_invoice_view),     name='admin_invoice_view'),
    path('admin/invoices/delete/<int:pk>/',admin_required(admin_invoice_delete),   name='admin_invoice_delete'),

    # Customer Invoices
    path('customer/invoices/',customer_invoices,name='customer_invoices'),
    path('customer/invoices/view/<int:pk>/',customer_invoice_view,  name='customer_invoice_view'),
]

