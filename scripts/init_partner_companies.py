# -*- coding: utf-8 -*-
"""
Initialize Partner Company Configuration - SemiMOS/WISEWORLD/IOTOR/RY-IMP
Quick setup script for adding 4 partner companies' basic configuration

Author: KR + Claude Code
Date: 2026-03-23
"""

import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from database import init_database, PartnerCompanyManager


def init_partner_companies():
    """Initialize 4 partner companies configuration"""

    # Ensure database is initialized
    init_database()

    # 4 partner companies configuration
    companies = [
        {
            'company_name': 'IOTOR',
            'company_code': 'YOUTO',
            'contact_person': 'Kongson Ren',
            'contact_phone': '',
            'contact_email': '',
            'api_endpoint': '',
            'api_key': '',
            'api_secret': '',
            'data_sync_enabled': True,
            'sync_frequency': 'hourly',
            'notes': 'Founded by KR - Lighting products, launched 2026'
        },
        {
            'company_name': 'WISEWORLD',
            'company_code': 'SMARTWORLD',
            'contact_person': '',
            'contact_phone': '',
            'contact_email': '',
            'api_endpoint': '',
            'api_key': '',
            'api_secret': '',
            'data_sync_enabled': False,
            'sync_frequency': 'daily',
            'notes': 'Smart lighting solutions partnership'
        },
        {
            'company_name': 'SemiMOS',
            'company_code': 'XIMAO',
            'contact_person': '',
            'contact_phone': '',
            'contact_email': '',
            'api_endpoint': '',
            'api_key': '',
            'api_secret': '',
            'data_sync_enabled': False,
            'sync_frequency': 'daily',
            'notes': 'Chip product line partnership'
        },
        {
            'company_name': 'RY-IMP',
            'company_code': 'SILVER',
            'contact_person': '',
            'contact_phone': '',
            'contact_email': '',
            'api_endpoint': '',
            'api_key': '',
            'api_secret': '',
            'data_sync_enabled': False,
            'sync_frequency': 'daily',
            'notes': 'Chip product line partnership'
        }
    ]

    print("=" * 60)
    print("Partner Company Configuration Initialization")
    print("=" * 60)

    for company in companies:
        # Check if already exists
        existing = PartnerCompanyManager.get_company_by_code(company['company_code'])

        if existing:
            print(f"  {company['company_code']} already exists, skipping")
        else:
            company_id = PartnerCompanyManager.add_company(company)
            print(f"  Added: {company['company_code']} - {company['company_name']} (ID: {company_id})")

    print("=" * 60)
    print("Partner company configuration initialized successfully!")
    print("=" * 60)

    # Display all companies
    print("\nConfigured Companies:")
    all_companies = PartnerCompanyManager.get_all_companies()
    for c in all_companies:
        status = "Active" if c['data_sync_enabled'] else "Inactive"
        print(f"  [{status}] {c['company_code']} - {c['company_name']}")


if __name__ == "__main__":
    init_partner_companies()
