import math
from functools import lru_cache

from sqlalchemy import (Column, Engine, and_, distinct, func, literal_column,
                        select)
from sqlalchemy.orm import Session

from models import Organization, User
from schemas.users import FilterParam


class UserService:
    # Build columns to select (support Column objects or strings)
    def col_attr(self, c):
        if isinstance(c, Column):
            return getattr(User, c.name)
        return getattr(User, c)  # assume string name

    def get_user_list(self, query_params: FilterParam, engine: Engine):
        field_list = list(User.__table__.columns)
        with Session(engine) as session:
            if query_params.org_id:
                statement = select(Organization).filter_by(id=query_params.org_id)
                result = session.execute(statement=statement).scalar_one_or_none()
                if result and result.org_config:
                    field_list = [
                        key for key, value in result.org_config.items() if value is True
                    ]

            count_statement = select(func.count()).select_from(User)
            cols = [self.col_attr(col) for col in field_list]
            statement = select(*cols).select_from(User)

            if query_params.org_id:
                count_statement = count_statement.filter_by(org_id=query_params.org_id)
                statement = statement.filter_by(org_id=query_params.org_id)

            if query_params.location and "location" in field_list:
                count_statement = count_statement.filter_by(
                    location=query_params.location
                )
                statement = statement.filter_by(location=query_params.location)

            if query_params.department and "department" in field_list:
                count_statement = count_statement.filter_by(
                    department=query_params.department
                )
                statement = statement.filter_by(department=query_params.department)

            if query_params.position and "position" in field_list:
                count_statement = count_statement.filter_by(
                    position=query_params.position
                )
                statement = statement.filter_by(position=query_params.position)

            if query_params.status and "status" in field_list:
                count

            statement = statement.limit(query_params.limit).offset(query_params.offset)

            data = session.execute(statement=statement).mappings().all()
            count = session.execute(statement=count_statement).scalar()
            total_page = (count / query_params.limit) + (
                1 if (count % query_params.limit > 0) else 0
            )
            page = (
                ((query_params.offset / query_params.limit) + 1)
                if query_params.offset > 0
                else 1
            )

            return {
                "total_page": total_page,
                "page": page,
                "count": count,
                "data": data,
            }

    @lru_cache
    def get_filter_values(self, engine: Engine):
        response = {}
        with Session(engine) as session:
            statement = select(distinct(User.location))
            results = session.execute(statement=statement).scalars().all()
            response["locations"] = results

            statement = select(distinct(User.department))
            results = session.execute(statement=statement).scalars().all()
            response["departments"] = results

            statement = select(distinct(User.position))
            results = session.execute(statement=statement).scalars().all()
            response["positions"] = results

            statement = select(Organization)
            results = session.execute(statement=statement).scalars().all()
            response["organizations"] = results

        return response


user_services = UserService()
