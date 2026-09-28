from app.models import User, UserRole
from app.core.settings import settings
from app.enums.Permission import Permission
from app.security.password import hash_password


async def seed_user_roles():
    admin_role = await UserRole.find_one(UserRole.name == "ADMIN")

    if not admin_role:
        await UserRole(
            name="ADMIN", is_superuser=True, permissions=list(Permission)
        ).insert()

    counter_staff = await UserRole.find_one(UserRole.name == "COUNTER_STAFF")

    if not counter_staff:
        await UserRole(
            name="COUNTER_STAFF",
            permissions=[
                Permission.QUICK_SALE,
                Permission.WARRANTY_VIEW,
                Permission.DAILY_LEDGER_VIEW,
                Permission.MECHANIC_LEDGER_VIEW,
                Permission.MECHANIC_TRANSACTION_CREATE,
                Permission.SCRAP_PURCHASE,
                Permission.SCRAP_SALE,
            ],
        ).insert()


async def seed_admin():
    if await User.find().count() > 0:
        return

    admin_role = await UserRole.find_one(UserRole.name == "ADMIN")

    hashed_password = hash_password(settings.ADMIN_PASSWORD)

    admin = User(
        full_name=settings.ADMIN_NAME,
        email=settings.ADMIN_EMAIL,
        phone=settings.ADMIN_PHONE,
        hashed_password=hashed_password,
        role=admin_role,
    )
    await admin.insert()
