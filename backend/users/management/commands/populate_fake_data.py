from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from faker import Faker
from users.models import UserRole, UserProfile
from profiles.models import (
    Industry,
    Location,
    StartupProfile,
    InvestorProfile,
)
from projects.models import (
    ProjectStatus,
    StartupProject,
    SavedStartup,
)
import random

class Command(BaseCommand):
    help = 'Populate database with fake data using Faker'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=10,
            help='Number of fake users to create (default: 10)'
        )
        parser.add_argument(
            '--investors',
            type=int,
            help='Number of investor profiles to create (default: half of users)'
        )
        parser.add_argument(
            '--startups',
            type=int,
            help='Number of startup profiles to create (default: half of users)'
        )
        parser.add_argument(
            '--projects',
            type=int,
            help='Number of startup projects to create (default: 1 per startup)'
        )
        parser.add_argument(
            '--saved-startups',
            type=int,
            help='Number of saved startup relationships to create (default: 1-3 per investor)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before populating'
        )

    def validate_parameters(self, options):
        """Validate that the provided parameters make logical sense."""
        num_users = options['users']
        num_investors = options.get('investors')
        num_startups = options.get('startups')
        num_projects = options.get('projects')
        num_saved = options.get('saved_startups')
        
        errors = []
        
        # Validate investor/startup counts
        if num_investors is not None and num_startups is not None:
            if num_investors + num_startups != num_users:
                errors.append(
                    f"Total users ({num_users}) must equal investors ({num_investors}) + startups ({num_startups})"
                )
        elif num_investors is not None:
            if num_investors > num_users:
                errors.append(f"Cannot create {num_investors} investors with only {num_users} users")
        elif num_startups is not None:
            if num_startups > num_users:
                errors.append(f"Cannot create {num_startups} startups with only {num_users} users")
        
        # Note: Projects can be more than startups since they're distributed among startups
        
        # Validate saved startups count
        if num_saved is not None:
            max_possible_saved = num_investors if num_investors is not None else num_users // 2
            max_saved_per_investor = 3  # Each investor can save up to 3 startups
            max_possible_saved_total = max_possible_saved * max_saved_per_investor
            if num_saved > max_possible_saved_total:
                errors.append(
                    f"Cannot create {num_saved} saved relationships with only {max_possible_saved} investors "
                    f"(max {max_possible_saved_total} possible)"
                )
        
        if errors:
            self.stdout.write(
                self.style.ERROR("Parameter validation errors:")
            )
            for error in errors:
                self.stdout.write(self.style.ERROR(f"  - {error}"))
            return False
        
        return True

    def handle(self, *args, **options):
        # Validate parameters first
        if not self.validate_parameters(options):
            return
        
        fake = Faker()
        
        num_users = options['users']
        num_investors = options.get('investors')
        num_startups = options.get('startups')
        num_projects = options.get('projects')
        num_saved = options.get('saved_startups')
        clear_existing = options['clear']
        
        # Set defaults if not specified
        if num_investors is None and num_startups is None:
            num_investors = num_users // 2
            num_startups = num_users - num_investors
        elif num_investors is None:
            num_investors = num_users - num_startups
        elif num_startups is None:
            num_startups = num_users - num_investors
        
        self.stdout.write(
            self.style.SUCCESS(f'Starting to populate database with fake data...')
        )
        self.stdout.write(f'Configuration: {num_users} users ({num_investors} investors, {num_startups} startups)')
        if num_projects:
            self.stdout.write(f'Projects: {num_projects}')
        if num_saved:
            self.stdout.write(f'Saved startups: {num_saved}')
        
        # Clear existing data if requested
        if clear_existing:
            self.stdout.write('Clearing existing data...')
            try:
                # Delete dependent data in safe order
                SavedStartup.objects.all().delete()
                StartupProject.objects.all().delete()
                StartupProfile.objects.all().delete()
                InvestorProfile.objects.all().delete()
                # Clear users and roles
                UserProfile.objects.all().delete()
                UserRole.objects.all().delete()
                # Base lookup tables
                Industry.objects.all().delete()
                Location.objects.all().delete()
                ProjectStatus.objects.all().delete()
                self.stdout.write(
                    self.style.SUCCESS('Existing data cleared.')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'Warning: Could not clear all existing data: {str(e)}')
                )
                self.stdout.write(
                    self.style.WARNING('Continuing with existing data...')
                )
        
        # Create roles (investor and startup)
        self.stdout.write('Creating roles (investor and startup)...')
        roles = []
        role_names = ['investor', 'startup']
        
        for role_name in role_names:
            role, created = UserRole.objects.get_or_create(role=role_name)
            roles.append(role)
            if created:
                self.stdout.write(f'Created role: {role_name}')
            else:
                self.stdout.write(f'Role already exists: {role_name}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Roles ready: {len(roles)} roles available.')
        )

        # Seed base lookup tables: ProjectStatus, Industry, Location
        self.stdout.write('Seeding base lookup tables...')
        status_values = [value for value, _ in ProjectStatus.STATUS_CHOICES]
        industry_values = [value for value, _ in Industry.INDUSTRY_CHOICES]
        location_values = [value for value, _ in Location.LOCATION_CHOICES]

        for status in status_values:
            ProjectStatus.objects.get_or_create(status=status)
        for name in industry_values:
            Industry.objects.get_or_create(name=name)
        for name in location_values:
            Location.objects.get_or_create(name=name)

        self.stdout.write(self.style.SUCCESS('Base lookup tables are ready.'))
        
        # Create fake users and related profiles
        self.stdout.write(f'Creating {num_users} fake users...')
        users_created = 0
        role_map = {r.role: r for r in roles}
        investor_users = []
        startup_users = []
        
        # Create investor users first
        for i in range(num_investors):
            try:
                first_name = fake.first_name()
                last_name = fake.last_name()
                email = fake.unique.email()
                username = fake.unique.user_name()
                assigned_role = role_map['investor']
                
                user = UserProfile.objects.create(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password=make_password('password123'),
                    role=assigned_role,
                    is_active=True,
                    is_staff=random.choice([True, False]),
                    is_superuser=False
                )
                
                investor_users.append(user)
                users_created += 1
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error creating investor user {i+1}: {str(e)}')
                )
        
        # Create startup users
        for i in range(num_startups):
            try:
                first_name = fake.first_name()
                last_name = fake.last_name()
                email = fake.unique.email()
                username = fake.unique.user_name()
                assigned_role = role_map['startup']
                
                user = UserProfile.objects.create(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password=make_password('password123'),
                    role=assigned_role,
                    is_active=True,
                    is_staff=random.choice([True, False]),
                    is_superuser=False
                )
                
                startup_users.append(user)
                users_created += 1
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error creating startup user {i+1}: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {users_created} users!'
            )
        )

        # Create investor profiles
        self.stdout.write(f'Creating {len(investor_users)} investor profiles...')
        investor_profiles = []
        for user in investor_users:
            try:
                profile = InvestorProfile.objects.create(
                    user=user,
                    company_name=fake.company(),
                    website=fake.url(),
                )
                investor_profiles.append(profile)
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error creating investor profile for {user.email}: {str(e)}')
                )

        # Create startup profiles
        self.stdout.write(f'Creating {len(startup_users)} startup profiles...')
        startup_profiles = []
        for user in startup_users:
            try:
                profile = StartupProfile.objects.create(
                    user=user,
                    company_name=fake.company(),
                    description=fake.paragraph(nb_sentences=3),
                    website=fake.url(),
                    views_count=random.randint(0, 5000),
                    industry=Industry.objects.order_by('?').first(),
                    location=Location.objects.order_by('?').first(),
                )
                startup_profiles.append(profile)
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error creating startup profile for {user.email}: {str(e)}')
                )

        # Create startup projects
        if num_projects:
            self.stdout.write(f'Creating {num_projects} startup projects...')
        else:
            self.stdout.write('Creating startup projects (1 per startup)...')
            num_projects = len(startup_profiles)
        
        statuses = list(ProjectStatus.objects.all())
        projects_created = 0
        
        # Distribute projects among startups
        projects_per_startup = num_projects // len(startup_profiles) if startup_profiles else 0
        extra_projects = num_projects % len(startup_profiles) if startup_profiles else 0
        
        for i, startup in enumerate(startup_profiles):
            projects_for_this_startup = projects_per_startup + (1 if i < extra_projects else 0)
            
            for _ in range(projects_for_this_startup):
                try:
                    project = StartupProject.objects.create(
                        subject=fake.catch_phrase(),
                        idea=fake.paragraph(nb_sentences=4),
                        description=fake.paragraph(nb_sentences=6),
                        website=fake.url(),
                        investment_needed=random.choice([True, False]),
                        views_count=random.randint(0, 10000),
                        status=random.choice(statuses) if statuses else None,
                        startup=startup,
                        investor=random.choice(investor_profiles) if investor_profiles and random.random() < 0.5 else None,
                    )
                    projects_created += 1
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'Could not create project for {startup.company_name}: {e}'))

        self.stdout.write(self.style.SUCCESS(f'Created {projects_created} projects.'))

        # Create saved startups
        if num_saved:
            self.stdout.write(f'Creating {num_saved} saved startup relationships...')
            saved_created = 0
            
            # Distribute saved relationships among investors
            saved_per_investor = num_saved // len(investor_profiles) if investor_profiles else 0
            extra_saved = num_saved % len(investor_profiles) if investor_profiles else 0
            
            for i, investor in enumerate(investor_profiles):
                saved_for_this_investor = saved_per_investor + (1 if i < extra_saved else 0)
                
                # Get random startups for this investor
                available_startups = list(startup_profiles)
                random.shuffle(available_startups)
                
                for startup in available_startups[:saved_for_this_investor]:
                    if not SavedStartup.objects.filter(investor=investor, startup=startup).exists():
                        SavedStartup.objects.create(investor=investor, startup=startup)
                        saved_created += 1
                        
                        if saved_created >= num_saved:
                            break
                
                if saved_created >= num_saved:
                    break
        else:
            self.stdout.write('Creating saved startups (1-3 per investor)...')
            saved_created = 0
            for investor in investor_profiles:
                # Each investor saves between 0 and 3 random startups
                for startup in random.sample(startup_profiles, k=min(len(startup_profiles), random.randint(0, 3))):
                    if not SavedStartup.objects.filter(investor=investor, startup=startup).exists():
                        SavedStartup.objects.create(investor=investor, startup=startup)
                        saved_created += 1
        
        self.stdout.write(self.style.SUCCESS(f'Created {saved_created} saved startups.'))
        
        # Summary
        total_users = UserProfile.objects.count()
        total_roles = UserRole.objects.count()
        total_investors = InvestorProfile.objects.count()
        total_startups = StartupProfile.objects.count()
        total_projects = StartupProject.objects.count()
        total_saved = SavedStartup.objects.count()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nDatabase population complete!\n'
                f'Total users: {total_users}\n'
                f'Total roles: {total_roles}\n'
                f'Investor profiles: {total_investors}\n'
                f'Startup profiles: {total_startups}\n'
                f'Projects: {total_projects}\n'
                f'Saved startups: {total_saved}'
            )
        )

