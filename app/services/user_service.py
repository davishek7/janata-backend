from fastapi import status
import re
from beanie import PydanticObjectId
from beanie.operators import Or
from pymongo.asynchronous.client_session import AsyncClientSession
from app.models import User, UserRole
from app.exceptions.custom_exception import AppException
from app.schemas.user_schema import (
    UserCreate,
    UserListResponse,
    UserDetailsResponse,
    UserQueryParams,
)
from app.security.password import hash_password
from app.utils.responses import success_response
from app.schemas.common.pagination_schema import PaginatedResponse, Pagination
from app.utils.pagination import paginate


class UserService:
    async def create_user(self, user_create: UserCreate):
        user_role = await UserRole.find_one(
            UserRole.id == user_create.role_id, UserRole.is_active == True
        )
        if not user_role:
            raise AppException("User role not found.", status.HTTP_404_NOT_FOUND)
        hashed_password = hash_password(user_create.password)
        user = User(
            full_name=user_create.full_name,
            email=user_create.email,
            phone=user_create.phone,
            hashed_password=hashed_password,
            role=user_role,
            monthly_salary=user_create.monthly_salary,
        )
        await user.insert()
        return success_response("User created successfully.", status.HTTP_201_CREATED)

    async def get_users(self, params: UserQueryParams):
        conditions = []

        if params.search:
            search = re.escape(params.search.strip())

            conditions.append(
                Or(
                    {"full_name": {"$regex": search, "$options": "i"}},
                    {"email": {"$regex": search, "$options": "i"}},
                    {"phone": {"$regex": search, "$options": "i"}},
                )
            )

        if params.role:
            conditions.append(User.role.name == params.role)

        query = User.find(*conditions, User.is_active == True, fetch_links=True)
        users, total = await paginate(query, params.page, params.size)
        return PaginatedResponse[UserListResponse](
            items=[UserListResponse.from_document(user) for user in users],
            pagination=Pagination.from_total(
                page=params.page, size=params.size, total=total
            ),
        )

    async def _get_user(self, user_id: PydanticObjectId):
        user = await User.find_one(
            User.id == user_id, User.is_active == True, fetch_links=True
        )
        if not user:
            raise AppException("User not found.", status.HTTP_404_NOT_FOUND)
        return user

    async def get_user(self, user_id: PydanticObjectId):
        user = await self._get_user(user_id)
        return UserDetailsResponse.from_document(user)

    async def update_user(
        self,
    ): ...

    async def deactivate_user(self, user_id: PydanticObjectId):
        user = await self._get_user(user_id)
        if not user:
            raise AppException("User not found.", status.HTTP_404_NOT_FOUND)
        user.is_active = False
        await user.save()
        return success_response("User deactivated successfully.", status.HTTP_200_OK)

    async def get_admin(self):
        admin_role = await UserRole.find_one(
            UserRole.name == "ADMIN",
            UserRole.is_superuser == True,
            UserRole.is_active == True,
        )
        admin = await User.find_one(
            User.role.id == admin_role.id, User.is_active == True
        )
        return admin

    async def get_staff(self):
        staff_role = await UserRole.find_one(
            UserRole.name == "COUNTER_STAFF", UserRole.is_active == True
        )
        staff = await User.find_one(
            User.role.id == staff_role.id, User.is_active == True
        )
        if not staff:
            raise AppException("Staff is not added yet.", status.HTTP_404_NOT_FOUND)
        return staff
