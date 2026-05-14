from .db import maps_col
from .models import MapData, MapUpdate
from fastapi import HTTPException

class MapRepository:

    async def create_map(self, data: MapData):
        exist = await maps_col.find_one({"name": data.name})
        if exist:
            raise HTTPException(409, "Tên bản đồ đã tồn tại")

        r = await maps_col.insert_one(data.model_dump())
        return str(r.inserted_id)

    async def get_map(self, name: str):
        doc = await maps_col.find_one({"name": name})
        if not doc:
            raise HTTPException(404, "Không tìm thấy bản đồ")
        doc["id"] = str(doc["_id"])
        del doc["_id"]
        return doc

    async def update_map(self, name: str, body: MapUpdate):
        update_doc = body.model_dump(exclude_unset=True)
        if not update_doc:
            raise HTTPException(400, "Không có gì để cập nhật")

        r = await maps_col.update_one({"name": name}, {"$set": update_doc})
        if r.matched_count == 0:
            raise HTTPException(404, "Không tìm thấy bản đồ")

        return await self.get_map(name)

    async def delete_map(self, name: str):
        r = await maps_col.delete_one({"name": name})
        if r.deleted_count == 0:
            raise HTTPException(404, "Không tìm thấy bản đồ")
        return True

    async def search(self, q: str):
        cursor = maps_col.find({"name": {"$regex": q, "$options": "i"}})
        results = []
        async for doc in cursor:
            results.append(doc["name"])
        return results


repo = MapRepository()
