"""
Generate synthetic provider data for demonstration
"""
import json
import random
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()

SPECIALTIES = [
    "Cardiology", "Dermatology", "Endocrinology", "Family Medicine",
    "Gastroenterology", "Internal Medicine", "Neurology", "Obstetrics/Gynecology",
    "Oncology", "Ophthalmology", "Orthopedic Surgery", "Pediatrics",
    "Psychiatry", "Radiology", "Surgery", "Urology"
]

STATES = ["CA", "NY", "TX", "FL", "IL", "PA", "OH", "GA", "NC", "MI"]

def generate_npi():
    """Generate realistic looking NPI number"""
    return f"1{random.randint(100000000, 999999999)}"

def generate_provider(provider_id):
    """Generate a single provider profile with intentional data quality issues"""

    # Introduce data quality issues (40% of providers have issues)
    has_phone_issue = random.random() < 0.4
    has_address_issue = random.random() < 0.3
    has_credential_issue = random.random() < 0.2

    state = random.choice(STATES)
    city = fake.city()
    street = fake.street_address()

    # Intentionally corrupt some data
    phone = fake.phone_number() if not has_phone_issue else "(000) 000-0000"
    address = street if not has_address_issue else "123 Old Address St"
    license_status = "Active" if not has_credential_issue else "Unknown"

    provider = {
        "provider_id": f"PRV{provider_id:05d}",
        "npi": generate_npi(),
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "specialty": random.choice(SPECIALTIES),
        "sub_specialty": random.choice(["General", "Specialized", "Interventional"]),
        "phone": phone,
        "email": fake.email(),
        "address": address,
        "city": city,
        "state": state,
        "zip_code": fake.zipcode(),
        "license_number": f"{state}{random.randint(100000, 999999)}",
        "license_status": license_status,
        "license_expiry": (datetime.now() + timedelta(days=random.randint(30, 730))).strftime("%Y-%m-%d"),
        "board_certified": random.choice([True, True, True, False]),
        "years_experience": random.randint(3, 40),
        "medical_school": fake.company() + " Medical School",
        "accepting_new_patients": random.choice([True, True, False]),
        "languages": random.sample(["English", "Spanish", "Mandarin", "French", "German"], k=random.randint(1, 3)),
        "hospital_affiliations": [fake.company() + " Hospital" for _ in range(random.randint(1, 3))],
        "insurance_accepted": random.sample(["Medicare", "Medicaid", "Blue Cross", "Aetna", "Cigna", "UnitedHealthcare"], k=random.randint(2, 5)),
        "data_quality_score": 0,  # To be calculated
        "last_verified": (datetime.now() - timedelta(days=random.randint(30, 365))).strftime("%Y-%m-%d"),
        "validation_status": "Pending",
        "confidence_score": 0.0,
        "needs_manual_review": False,
        "issues_found": []
    }

    return provider

def generate_dataset(num_providers=200):
    """Generate complete provider dataset"""
    providers = [generate_provider(i+1) for i in range(num_providers)]

    # Save to JSON
    with open('data/providers.json', 'w') as f:
        json.dump(providers, f, indent=2)

    print(f"Generated {num_providers} provider records")
    print(f"Data saved to: data/providers.json")

    # Generate summary statistics
    phone_issues = sum(1 for p in providers if p['phone'] == "(000) 000-0000")
    address_issues = sum(1 for p in providers if "Old Address" in p['address'])
    credential_issues = sum(1 for p in providers if p['license_status'] == "Unknown")

    print(f"\nData Quality Issues Introduced:")
    print(f"  - Phone Issues: {phone_issues} ({phone_issues/len(providers)*100:.1f}%)")
    print(f"  - Address Issues: {address_issues} ({address_issues/len(providers)*100:.1f}%)")
    print(f"  - Credential Issues: {credential_issues} ({credential_issues/len(providers)*100:.1f}%)")

    return providers

if __name__ == "__main__":
    import os
    os.makedirs('data', exist_ok=True)
    generate_dataset(200)
