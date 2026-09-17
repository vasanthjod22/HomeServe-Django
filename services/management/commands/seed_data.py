from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import CustomerProfile, ProviderProfile
from services.models import ServiceCategory, Service

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds database with initial categories, services, and demo accounts'

    def handle(self, *args, **options):
        self.stdout.write("Starting database seeding...")

        # 1. Create Categories
        categories_data = [
            {
                'name': 'Plumber',
                'slug': 'plumber',
                'icon': 'fa-faucet-drip',
                'description': 'Pipe repair, leakage fixing, tap & sink installation, and drainage clearing.'
            },
            {
                'name': 'Electrician',
                'slug': 'electrician',
                'icon': 'fa-bolt',
                'description': 'Wiring, circuit breaker repair, lighting, switchboard & appliance setup.'
            },
            {
                'name': 'AC Service',
                'slug': 'ac-service',
                'icon': 'fa-snowflake',
                'description': 'Air conditioner deep cleaning, gas refill, cooling diagnostics & compressor repairs.'
            },
            {
                'name': 'Cleaning',
                'slug': 'cleaning',
                'icon': 'fa-broom',
                'description': 'Full home deep cleaning, sofa & carpet shampooing, kitchen & bathroom sanitation.'
            },
            {
                'name': 'Painting',
                'slug': 'painting',
                'icon': 'fa-paint-roller',
                'description': 'Interior & exterior wall painting, waterproof coating, and decorative touchups.'
            },
        ]

        cat_objs = {}
        for cdata in categories_data:
            cat, created = ServiceCategory.objects.get_or_create(
                slug=cdata['slug'],
                defaults=cdata
            )
            cat_objs[cdata['slug']] = cat
            if created:
                self.stdout.write(f"Created category: {cat.name}")

        # 2. Create Services
        services_data = [
            # Plumber
            ('plumber', 'Pipe Leak Repair', 'Detection and emergency sealing of leaking water pipes.', 75.00, 1.5),
            ('plumber', 'Tap & Sink Installation', 'Installation or replacement of bathroom and kitchen taps/sinks.', 50.00, 1.0),
            ('plumber', 'Drainage Unclogging', 'High-pressure jet cleaning for blocked drain lines.', 90.00, 2.0),
            # Electrician
            ('electrician', 'Wiring Inspection & Repair', 'Comprehensive electrical safety check and short-circuit repair.', 85.00, 2.0),
            ('electrician', 'Switchboard & Socket Repair', 'Fix loose wiring, burnt sockets, and faulty switches.', 45.00, 1.0),
            ('electrician', 'Ceiling Fan & Light Fitting', 'Installation of ceiling fans, chandeliers, and LED fixtures.', 60.00, 1.5),
            # AC Service
            ('ac-service', 'Deep AC Service & Filter Cleaning', 'Foam jet wash for indoor and outdoor AC units.', 110.00, 2.5),
            ('ac-service', 'Refrigerant Gas Refilling', 'Cooling gas top-up and pressure leak inspection.', 130.00, 2.0),
            ('ac-service', 'Compressor Repair & Diagnostics', 'Comprehensive PCB board and compressor troubleshooting.', 180.00, 3.0),
            # Cleaning
            ('cleaning', 'Full Home Deep Cleaning', 'Complete floor scrub, window polishing, and deep sanitation.', 150.00, 4.0),
            ('cleaning', 'Sofa & Carpet Shampooing', 'Fabric steam vacuuming and stain removal.', 80.00, 2.0),
            ('cleaning', 'Kitchen & Bathroom Sanitation', 'Degreasing stove areas and descaling tile surfaces.', 95.00, 2.5),
            # Painting
            ('painting', 'Interior Wall Accent Painting', 'Single room premium color coat application.', 220.00, 5.0),
            ('painting', 'Full Room Repainting', 'Two coats of premium washable emulsion paint.', 350.00, 8.0),
            ('painting', 'Exterior Waterproofing Touchup', 'Weather-shield sealant application for outer walls.', 180.00, 4.0),
        ]

        for cat_slug, name, desc, price, est_hrs in services_data:
            cat = cat_objs.get(cat_slug)
            srv, created = Service.objects.get_or_create(
                name=name,
                category=cat,
                defaults={
                    'description': desc,
                    'price': price,
                    'estimated_hours': est_hrs,
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(f"Created service: {srv.name}")

        # 3. Create Demo Accounts
        # Admin Account
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser('admin', 'admin@homeservices.com', 'password123', role=User.Role.ADMIN)
            self.stdout.write("Created Superuser Admin (username: admin, password: password123)")

        # Demo Customers
        customers_data = [
            ('customer1', 'Alice', 'Smith', 'alice@example.com', '1234567890', '123 Maple Street', 'New York'),
            ('customer2', 'Bob', 'Johnson', 'bob@example.com', '9876543210', '456 Oak Avenue', 'Los Angeles'),
        ]
        for uname, fname, lname, email, phone, addr, city in customers_data:
            if not User.objects.filter(username=uname).exists():
                u = User.objects.create_user(uname, email, 'password123', first_name=fname, last_name=lname, role=User.Role.CUSTOMER, phone=phone)
                CustomerProfile.objects.create(user=u, address=addr, city=city)
                self.stdout.write(f"Created Customer: {uname} (password: password123)")

        # Demo Service Providers
        providers_data = [
            ('plumber_jack', 'Jack', 'Miller', 'jack@example.com', '555-0101', 'plumber', 5, 55.00, 'Master Plumber with 5+ years experience.'),
            ('electrician_sam', 'Sam', 'Wilson', 'sam@example.com', '555-0102', 'electrician', 7, 65.00, 'Certified Master Electrician.'),
            ('ac_tech_mike', 'Mike', 'Davis', 'mike@example.com', '555-0103', 'ac-service', 4, 60.00, 'HVAC Specialist & AC Technician.'),
            ('cleaner_lisa', 'Lisa', 'Taylor', 'lisa@example.com', '555-0104', 'cleaning', 3, 40.00, 'Residential & Commercial Hygiene Expert.'),
            ('painter_david', 'David', 'White', 'david@example.com', '555-0105', 'painting', 6, 50.00, 'Custom Interior & Wall Painter.'),
        ]
        for uname, fname, lname, email, phone, cat_slug, exp, rate, bio in providers_data:
            if not User.objects.filter(username=uname).exists():
                u = User.objects.create_user(uname, email, 'password123', first_name=fname, last_name=lname, role=User.Role.PROVIDER, phone=phone)
                ProviderProfile.objects.create(
                    user=u,
                    service_category=cat_objs.get(cat_slug),
                    experience_years=exp,
                    hourly_rate=rate,
                    bio=bio,
                    is_available=True
                )
                self.stdout.write(f"Created Provider: {uname} (password: password123)")

        self.stdout.write(self.style.SUCCESS("Database seeding completed successfully!"))
