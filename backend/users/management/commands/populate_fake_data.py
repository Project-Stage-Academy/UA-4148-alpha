from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from faker import Faker
from users.models import UserRole, UserProfile
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
            '--roles',
            type=int,
            default=2,
            help='Number of fake roles to create (default: 2)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before populating'
        )

    def handle(self, *args, **options):
        fake = Faker()
        
        num_users = options['users']
        num_roles = options['roles']
        clear_existing = options['clear']
        
        self.stdout.write(
            self.style.SUCCESS(f'Starting to populate database with fake data...')
        )
        
        # Clear existing data if requested
        if clear_existing:
            self.stdout.write('Clearing existing data...')
            UserProfile.objects.all().delete()
            UserRole.objects.all().delete()
            self.stdout.write(
                self.style.SUCCESS('Existing data cleared.')
            )
        
        # Create fake roles
        self.stdout.write(f'Creating {num_roles} fake roles...')
        roles = []
        role_names = [
            'investor',
            'startup'
        ]
        
        for i in range(num_roles):
            role_name = role_names[i] if i < len(role_names) else fake.job()
            role = UserRole.objects.create(role=role_name)
            roles.append(role)
            self.stdout.write(f'Created role: {role_name}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Created {len(roles)} roles successfully.')
        )
        
        # Create fake users
        self.stdout.write(f'Creating {num_users} fake users...')
        users_created = 0
        
        for i in range(num_users):
            try:
                # Generate fake user data
                first_name = fake.first_name()
                last_name = fake.last_name()
                email = fake.unique.email()
                username = fake.unique.user_name()
                
                # Create user with hashed password
                user = UserProfile.objects.create(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password=make_password('password123'),  # Default password
                    role=random.choice(roles),
                    is_active=True,
                    is_staff=random.choice([True, False]),
                    is_superuser=False
                )
                
                users_created += 1
                
                if users_created % 10 == 0:  # Progress indicator every 10 users
                    self.stdout.write(f'Created {users_created} users...')
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error creating user {i+1}: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {users_created} users and {len(roles)} roles!'
            )
        )
        
        # Summary
        total_users = UserProfile.objects.count()
        total_roles = UserRole.objects.count()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nDatabase population complete!\n'
                f'Total users in database: {total_users}\n'
                f'Total roles in database: {total_roles}'
            )
        )

