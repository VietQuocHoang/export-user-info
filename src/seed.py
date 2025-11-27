from faker import Faker
from faker.providers import DynamicProvider
from sqlalchemy import Engine, insert, select
from sqlalchemy.orm import Session

from models import Organization, User

fake = Faker()
company_department_provider = DynamicProvider(
    provider_name="company_department",
    elements=["Human Resource", "Engineering", "Accounting", "Admin"]
)
fake.add_provider(company_department_provider)

def generate_organization(engine: Engine):
    with Session(engine) as session:
        for i in range(10):
            org = Organization(
                name=fake.company(),
                org_config={
                    "id": True, 
                    "org_id": True,
                    # Always return id and FK
                    "first_name": fake.boolean(),
                    "last_name": fake.boolean(),
                    "email": fake.boolean(),
                    "phone_number": fake.boolean(),
                    "position": fake.boolean(),
                    "location": fake.boolean(),
                    "status": fake.boolean(),
                },
            )
            session.add(org)
        session.commit()


def generate_user(engine: Engine):
    with Session(engine) as session:
        statement = select(Organization.id)
        orgs = session.execute(statement=statement).scalars().all()

        data = []
        for i in range(len(orgs) * 500):
            data.append(
                {
                    "first_name": fake.first_name(),
                    "last_name": fake.last_name(),
                    "email": fake.unique.email(),
                    "phone_number": fake.basic_phone_number(),
                    "position": fake.job(),
                    "location": fake.country(),
                    "department": fake.company_department(),
                    "org_id": fake.random_element(elements=orgs),
                }
            )

        statement = insert(User).values(data)
        session.execute(statement=statement)
        session.commit()


def seed(engine: Engine):
    generate_organization(engine)
    generate_user(engine)
