from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.lifespan import lifespan
from app.core.settings import settings
from app.exceptions.handlers import register_exception_handlers
from app.routes.auth import router as auth_router
from app.routes.product import router as product_router
from app.routes.vendor import router as vendor_router
from app.routes.purchase import router as purchase_router
from app.routes.sale import router as sale_router
from app.routes.scrap_product import router as scrap_product_router
from app.routes.invoice import router as invoice_router
from app.routes.user import router as user_router
from app.routes.staff_ledger import router as staff_ledger_router
from app.routes.mechanic import router as mechanic_router
from app.routes.mechanic_ledger import router as mechanic_ledger_router
from app.routes.scrap_purchase import router as scrap_purchase_router
from app.routes.warranty_claim import router as warranty_claim_router
from app.routes.quick_sale import router as quick_sale_router
from app.routes.daily_ledger import router as daily_ledger_router
from app.routes.warranty import router as warranty_router
from app.routes.payment import router as payment_router
from app.routes.mechanic_invoice import router as mechanic_invoice_router
from app.routes.scrap_sale import router as scrap_sale_router
from app.routes.dashboard import router as dashboard_router

app = FastAPI(
    title=settings.APP_NAME,
    description=".",
    version="1.0.0",
    contact={
        "name": "Avishek Das",
        "email": "davishek7@gmail.com",
    },
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app=app)

URL_PREFIX = "/api"

app.include_router(auth_router, prefix=f"{URL_PREFIX}/auth", tags=["Auth"])
app.include_router(dashboard_router, prefix=f"{URL_PREFIX}/dashboard", tags=["Dashboard"])
app.include_router(product_router, prefix=f"{URL_PREFIX}/product", tags=["Product"])
app.include_router(
    scrap_product_router, prefix=f"{URL_PREFIX}/scrap-product", tags=["Scrap Product"]
)
app.include_router(vendor_router, prefix=f"{URL_PREFIX}/vendor", tags=["Vendor"])
app.include_router(purchase_router, prefix=f"{URL_PREFIX}", tags=["Purchase"])
app.include_router(sale_router, prefix=f"{URL_PREFIX}/sale", tags=["Sale"])
app.include_router(invoice_router, prefix=f"{URL_PREFIX}/invoice", tags=["Invoice"])
app.include_router(user_router, prefix=f"{URL_PREFIX}/user", tags=["User"])
app.include_router(
    staff_ledger_router, prefix=f"{URL_PREFIX}/staff-ledger", tags=["Staff Ledger"]
)
app.include_router(mechanic_router, prefix=f"{URL_PREFIX}/mechanic", tags=["Mechanic"])
app.include_router(
    mechanic_ledger_router,
    prefix=f"{URL_PREFIX}",
    tags=["Mechanic Ledger"],
)
app.include_router(
    scrap_purchase_router,
    prefix=f"{URL_PREFIX}/scrap-purchase",
    tags=["Scrap Purchase"],
)
app.include_router(
    scrap_sale_router, prefix=f"{URL_PREFIX}/scrap-sale", tags=["Scrap Sale"]
)
app.include_router(
    warranty_claim_router,
    prefix=f"{URL_PREFIX}/warranty-claim",
    tags=["Warranty Claim"],
)
app.include_router(
    quick_sale_router, prefix=f"{URL_PREFIX}/quick-sale", tags=["Quick Sale"]
)
app.include_router(
    daily_ledger_router, prefix=f"{URL_PREFIX}/daily-ledger", tags=["Daily Ledger"]
)
app.include_router(warranty_router, prefix=f"{URL_PREFIX}/warranty", tags=["Warranty"])
app.include_router(payment_router, prefix=f"{URL_PREFIX}/payment", tags=["Payment"])
app.include_router(
    mechanic_invoice_router, prefix=f"{URL_PREFIX}", tags=["Mechanic Invoice"]
)
