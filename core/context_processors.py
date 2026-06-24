ADMIN_SIDEBAR_SECTIONS = [
    {
        'title': 'Overview',
        'links': [
            {
                'label': 'Dashboard',
                'url_name': 'admin_dashboard',
                'icon': 'DB',
                'active_names': ['admin_dashboard', 'admin_dashboard_legacy', 'dashboard'],
            },
        ],
    },
    {
        'title': 'Management',
        'links': [
            {
                'label': 'Packages',
                'url_name': 'package_list',
                'icon': 'PK',
                'active_names': ['package_list', 'package_add', 'package_edit', 'package_delete'],
            },
            {
                'label': 'Trainers',
                'url_name': 'trainer_list',
                'icon': 'TR',
                'active_names': ['trainer_list', 'trainer_add', 'trainer_edit', 'trainer_delete'],
            },
            {
                'label': 'Members',
                'url_name': 'customer_list',
                'icon': 'MB',
                'active_names': ['customer_list', 'customer_edit', 'customer_delete', 'customer_setdates'],
            },
        ],
    },
    {
        'title': 'Business',
        'links': [
            {
                'label': 'Payments',
                'url_name': 'admin_payment_list',
                'icon': 'PM',
                'active_names': ['admin_payment_list'],
            },
            {
                'label': 'Products',
                'url_name': 'admin_product_list',
                'icon': 'PR',
                'active_names': ['admin_product_list', 'admin_product_add', 'admin_product_edit', 'admin_product_delete'],
            },
            {
                'label': 'Invoices',
                'url_name': 'admin_invoice_list',
                'icon': 'IV',
                'active_names': ['admin_invoice_list', 'admin_invoice_generate', 'admin_invoice_view', 'admin_invoice_delete'],
            },
        ],
    },
    {
        'title': 'Operations',
        'links': [
            {
                'label': 'Notices',
                'url_name': 'admin_notice_list',
                'icon': 'NO',
                'active_names': ['admin_notice_list', 'admin_notice_add', 'admin_notice_delete'],
            },
            {
                'label': 'Feedback',
                'url_name': 'admin_feedback_list',
                'icon': 'FB',
                'active_names': ['admin_feedback_list', 'admin_feedback_delete'],
            },
            {
                'label': 'Equipment',
                'url_name': 'equipment_list',
                'icon': 'EQ',
                'active_names': ['equipment_list', 'equipment_add', 'equipment_edit', 'equipment_delete'],
            },
            {
                'label': 'Enquiries',
                'url_name': 'admin_enquiry_list',
                'icon': 'EN',
                'active_names': ['admin_enquiry_list', 'admin_enquiry_detail', 'admin_enquiry_status_update', 'admin_enquiry_delete'],
            },
        ],
    },
    {
        'title': 'Quick Create',
        'links': [
            {
                'label': 'Package',
                'url_name': 'package_add',
                'icon': '+P',
                'active_names': ['package_add'],
            },
            {
                'label': 'Trainer',
                'url_name': 'trainer_add',
                'icon': '+T',
                'active_names': ['trainer_add'],
            },
            {
                'label': 'Notice',
                'url_name': 'admin_notice_add',
                'icon': '+N',
                'active_names': ['admin_notice_add'],
            },
            {
                'label': 'Product',
                'url_name': 'admin_product_add',
                'icon': '+R',
                'active_names': ['admin_product_add'],
            },
            {
                'label': 'Equipment',
                'url_name': 'equipment_add',
                'icon': '+E',
                'active_names': ['equipment_add'],
            },
        ],
    },
]


def admin_shell(request):
    path = (request.path or '').lower()
    show_admin_shell = (
        path == '/admin/'
        or path.startswith('/admin/')
        or path.startswith('/admin_dashboard')
    )

    return {
        'show_admin_shell': show_admin_shell,
        'admin_sidebar_sections': ADMIN_SIDEBAR_SECTIONS,
    }


def currency(request):
    """Expose currency preference (INR / USD) to all templates."""
    curr = request.session.get('currency', 'INR').upper()
    if curr not in {'INR', 'USD'}:
        curr = 'INR'
    symbol   = '₹' if curr == 'INR' else '$'
    usd_rate = 83.5   # approximate INR per 1 USD
    return {
        'currency'        : curr,
        'currency_symbol' : symbol,
        'usd_rate'        : usd_rate,
    }


def language(request):
    """Provide mock translations for common strings when gettext is not available."""
    lang = request.session.get('django_language', 'en').lower()
    
    translations = {
        'en': {
            'Home': 'Home',
            'Features': 'Features',
            'Packages': 'Packages',
            'Login': 'Login',
            'Register': 'Register',
            'Dashboard': 'Dashboard',
            'Join_Now': 'Join Now',
            'Get_Started_Free': 'Get Started Free',
            'Enquiry': 'Enquiry',
            'Feedback': 'Feedback',
            'Logout': 'Logout',
            'Sign_in': 'Sign in',
            'Create_Account': 'Create Account',
        },
        'hi': {
            'Home': 'होम',
            'Features': 'विशेषताएं',
            'Packages': 'पैकेज',
            'Login': 'लॉगिन',
            'Register': 'रजिस्टर',
            'Dashboard': 'डैशबोर्ड',
            'Join_Now': 'अभी जुड़ें',
            'Get_Started_Free': 'मुफ्त में शुरू करें',
            'Enquiry': 'पूछताछ',
            'Feedback': 'प्रतिक्रिया',
            'Logout': 'लॉगआउट',
            'Sign_in': 'साइन इन करें',
            'Create_Account': 'खाता बनाएं',
        }
    }
    
    return {
        't': translations.get(lang, translations['en'])
    }
