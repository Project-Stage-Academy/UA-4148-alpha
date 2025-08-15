#!/usr/bin/env python
"""
Standalone script to populate database with fake data using Faker.
This script can be run independently of Django management commands.
"""

import os
import sys
import django
import random
from faker import Faker

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.hashers import make_password
from users.models import UserRole, UserProfile


def populate_fake_data(num_users=10, num_roles=2, clear_existing=False):
    """
    Populate database with fake data using Faker.
    
    Args:
        num_users (int): Number of fake users to create
        num_roles (int): Number of fake roles to create
        clear_existing (bool): Whether to clear existing data first
    """
    fake = Faker()
    
    print(f'Starting to populate database with fake data...')
    
    # Clear existing data if requested
    if clear_existing:
        print('Clearing existing data...')
        UserProfile.objects.all().delete()
        UserRole.objects.all().delete()
        print('Existing data cleared.')
    
    # Create fake roles
    print(f'Creating {num_roles} fake roles...')
    roles = []
    role_names = [
        'investor',
        'startup'
    ]
    
    for i in range(num_roles):
        role_name = role_names[i] if i < len(role_names) else fake.job()
        role = UserRole.objects.create(role=role_name)
        roles.append(role)
        print(f'Created role: {role_name}')
    
    print(f'Created {len(roles)} roles successfully.')
    
    # Create fake users
    print(f'Creating {num_users} fake users...')
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
                print(f'Created {users_created} users...')
                
        except Exception as e:
            print(f'Error creating user {i+1}: {str(e)}')
    
    print(f'Successfully created {users_created} users and {len(roles)} roles!')
    
    # Summary
    total_users = UserProfile.objects.count()
    total_roles = UserRole.objects.count()
    
    print(f'\nDatabase population complete!')
    print(f'Total users in database: {total_users}')
    print(f'Total roles in database: {total_roles}')


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Populate database with fake data')
    parser.add_argument('--users', type=int, default=10, help='Number of fake users to create (default: 10)')
    parser.add_argument('--roles', type=int, default=2, help='Number of fake roles to create (default: 2)')
    parser.add_argument('--clear', action='store_true', help='Clear existing data before populating')
    
    args = parser.parse_args()
    
    populate_fake_data(
        num_users=args.users,
        num_roles=args.roles,
        clear_existing=args.clear
    )

