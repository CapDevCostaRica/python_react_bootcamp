from app.models import People, Family, FavoriteFood, Hobbies, Studies, Base
from sqlalchemy.orm import aliased
from sqlalchemy import func, select, and_
from app.database import get_session

class PeopleService:
    def getFieldTable(self, field):
        if field == "family":
            return "kinship", Family
        
        tables = [People, Family, FavoriteFood, Hobbies, Studies]
        for table in tables:
            if hasattr(table, field):
                return field, table

        print(f"Field {field} not found in any table.")
        return None, None
    
    def get_query(self, query):
        filters = query.get("filters", [{}])

        if isinstance(filters, dict):
            filters = [filters]

        query_fields_names = query.get("select_fields", ['full_name'])
        if isinstance(query_fields_names, str):
            query_fields_names = [query_fields_names]

        query_fields = []
        for field_name in query_fields_names:
            field, table = self.getFieldTable(field_name)
            if table:
                query_fields.append(getattr(table, field))
            else:
                print(f"Field {field_name} not found, using People.full_name as fallback")
                query_fields.append(People.full_name)

        joins = []
        conditions = []
        alias_map = {}

        try:
            for idx, filter_group in enumerate(filters):  
                for field_name, value in filter_group.items():
                    field, table = self.getFieldTable(field_name)
                    if not table:
                        continue

                    key = (table, idx)
                    if table is People:
                        alias = People
                    else:
                        key = (table, idx)
                        if key not in alias_map:
                            alias_map[key] = aliased(table)
                            joins.append(alias_map[key])
                        alias = alias_map[key]
                    
                    if not isinstance(value, dict):
                        conditions.append(getattr(alias, field) == value)
                    else:
                        for op, val in value.items():
                            if op == "eq":
                                conditions.append(getattr(alias, field) == val)
                            elif op == "gt":
                                conditions.append(getattr(alias, field) > val)
                            elif op == "lt":
                                conditions.append(getattr(alias, field) < val)
                            elif op == "gte":
                                conditions.append(getattr(alias, field) >= val)
                            elif op == "lte":
                                conditions.append(getattr(alias, field) <= val)
                            elif op == "neq":
                                conditions.append(getattr(alias, field) != val)
                            elif op == "like":
                                conditions.append(getattr(alias, field).like(f"%{val}%"))
                            else:
                                print(f"Unsupported operation: {op}")
            
                sql_query = select(*query_fields)
                for j in joins:
                    sql_query = sql_query.join(j, j.person_id == People.id)

                if conditions:
                    sql_query = sql_query.where(and_(*conditions))
                sql_query = sql_query.distinct()
            return sql_query
    
        except Exception as e:
            print(f"Error building query: {e}")
            return None
            
    def okResponse(self, data):
        return {
            "success": True,
            "data": data,
            "code": 200
        }
    
    def errorResponse(self, message, code=400):
        return {
            "success": False,
            "message": message,
            "code": code
        }

    def find(self, query):
        try:
            db = get_session()
        except Exception as e:
            return {"error": str(e), "code": 500}
        
        sql_query = self.get_query(query)

        if sql_query is None:
            return {"success": False, "message": "Invalid query", "code": 400}

        try:
            results = db.execute(sql_query).scalars().all()
        except Exception as e:
            db.close()
            return {"success": False, "message": str(e), "code": 500}
        
        db.close()

        response = {
            "success": True,
            "data": {
                "total": len(results),
                "results": results
            },
            "code": 200
        }

        return response
    
    def sushi_ramen(self, filters):
        results = self.find(filters)
        response = {
            "success": True,
            "data": results["data"]["total"],
            "code": 200
        }

        return response


    def round_number(self, number):
         return float("{:.2f}".format(number))

    def avg_weight_above_hair(self, weight):
        try:
            with get_session() as db:
                query = select(People.hair_color, func.avg(People.weight_kg).label("weight_avg")).group_by(People.hair_color).where(People.weight_kg > weight)
                results = db.execute(query).all()
                data = {}
                for row in results:
                    data[row.hair_color] = self.round_number(row.weight_avg) if row.weight_avg else 0.0

            return self.okResponse(data)
        except Exception as e:
            return self.errorResponse(str(e), 500)
           
    def extra1(self):
        try:
            with get_session() as db:
                stmt = (
                    select(
                        FavoriteFood.food,
                        func.count(FavoriteFood.food).label("n")
                    )
                    .group_by(FavoriteFood.food)
                    .order_by(func.count(FavoriteFood.food).desc())
                    .limit(1)
                )
                result = db.execute(stmt).first()

            return self.okResponse(result.food if result else "")

        except Exception as e:
            return self.errorResponse(str(e), 500)

    def extra2(self):
        try:
            with get_session() as db:
                query = select(
                    People.nationality,
                    People.hair_color,
                    func.avg(People.weight_kg).label("weight")).group_by(
                        People.nationality,
                        People.hair_color
                    )
                results = db.execute(query).all()
            data = {f"{row.nationality}-{row.hair_color}".lower(): self.round_number(row.weight) for row in results}
            return self.okResponse(data)

        except Exception as e:
            return self.errorResponse(str(e), 500)
        
    def extra3(self):
        try:
            with get_session() as db:
                subq = (
                    select(
                        People.full_name, People.nationality,
                        func.row_number()
                        .over(
                            partition_by=People.nationality,
                            order_by=People.age.desc()
                        )
                        .label("age_rank")
                    )
                    .subquery()
                )
                query = (
                    select(subq.c.full_name, subq.c.nationality, subq.c.age_rank)
                    .where(subq.c.age_rank <= 4).order_by(subq.c.nationality.asc(), subq.c.age_rank.asc())
                )

                results = db.execute(query).all()
                rows = {}
                for row in results:
                    rows.setdefault(row.nationality, []).append(row.full_name)
            
            return self.okResponse(rows)            
        except Exception as e:
            return self.errorResponse(str(e), 500)

    def extra4(self):
        try:
            with get_session() as db:
                query = select(
                    People.full_name,
                    func.count(Hobbies.hobby).label("hobbies")).group_by(
                        People.id
                    ).limit(3).order_by(func.count(Hobbies.hobby).desc()).order_by(People.full_name)

                results = db.execute(query).all()

            rows = [row.full_name for row in results]
            
            return self.okResponse(rows)

        except Exception as e:
            return self.errorResponse(str(e), 500)
        
    def extra5(self):
        try:
            with get_session() as db:
                avg_general_subquery = select(func.avg(People.height_cm)).scalar_subquery()
                query = select(
                        People.nationality,
                        func.avg(People.height_cm).label("avg_height"),
                        avg_general_subquery.label("avg_general_height")
                    ).group_by(
                        People.nationality
                    )

                results = db.execute(query).all()

            data = {
                "general": self.round_number(results[0].avg_general_height) if results else 0,
                "nationalities": {row.nationality.lower(): self.round_number(row.avg_height) for row in results}
            }
            
            return self.okResponse(data)

        except Exception as e:
            return self.errorResponse(str(e), 500)