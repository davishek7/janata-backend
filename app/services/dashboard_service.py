from fastapi import Depends, status
from app.models import Sale, QuickSale, ScrapSale
from app.schemas.dashboard_schema import RecentSaleResponse
from app.enums.SaleType import SaleType


class DashboardService:
    async def get_dashboard(self):
        sale_limit = 10
        results = []

        sales = await Sale.find(fetch_links=True).sort(-Sale.sale_date).limit(sale_limit).to_list()
        quick_sales = await QuickSale.find(fetch_links=True).sort(-QuickSale.sale_date).limit(sale_limit).to_list()
        scrap_sales = await ScrapSale.find(fetch_links=True).sort(-ScrapSale.transaction_date).limit(sale_limit).to_list()

        for sale in sales:
            results.append(
                RecentSaleResponse(
                    id=sale.id,
                    sale_type=SaleType.SALE,
                    reference_number=sale.sale_number if sale.sale_number else sale.id,
                    sale_date=sale.sale_date,
                    description="Customer Sale",
                    payment_status=sale.invoice.payment_status,
                    amount=sale.total_amount
                )
        )

        for sale in quick_sales:
            results.append(
                RecentSaleResponse(
                    id=sale.id,
                    sale_type=SaleType.QUICK_SALE,
                    reference_number=sale.sale_number,
                    sale_date=sale.sale_date,
                    description="Quick Sale",
                    payment_status=sale.payment_status,
                    amount=sale.total_amount
                )
        )

        for sale in scrap_sales:
            results.append(
                RecentSaleResponse(
                    id=sale.id,
                    sale_type=SaleType.SCRAP_SALE,
                    reference_number=sale.sale_number,
                    sale_date=sale.transaction_date,
                    description="Scrap Sale",
                    payment_status=sale.payment_status,
                    amount=sale.total_amount
                )
        )
            
        results.sort(key=lambda x: x.sale_date, reverse=True)
        return results[:sale_limit]
