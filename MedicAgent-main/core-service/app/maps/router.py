from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.directory.db import get_db as get_directory_db
from app.directory.repository import repo as directory_repo

from .repository import repo
from .models import MapData, MapUpdate, ShortestPathByMapRequest
from .service import convert_weight_keys, dijkstra, build_direction_text, build_direction_text_original

import httpx

router = APIRouter()


# ---------------------------------------------------------
#                     CRUD MAPS
# ---------------------------------------------------------

@router.post("/")
async def create_map(data: MapData):
    id = await repo.create_map(data)
    return {"ok": True, "id": id, "name": data.name}


@router.get("/search")
async def search_maps(q: str = ""):
    return {"ok": True, "results": await repo.search(q)}


@router.get("/{name}")
async def get_map(name: str):
    return await repo.get_map(name)


@router.put("/{name}")
async def update_map(name: str, body: MapUpdate):
    return await repo.update_map(name, body)


@router.delete("/{name}")
async def delete_map(name: str):
    await repo.delete_map(name)
    return {"ok": True, "deleted_name": name}


# ---------------------------------------------------------
#           SHORTES PATH VỚI ZONE / KHOA / PHÒNG
# ---------------------------------------------------------

@router.post("/shortest-path")
async def shortest_path(
    req: ShortestPathByMapRequest,
    db_directory: Session = Depends(get_directory_db),
):
    # ==== CHUẨN HOÁ INPUT NGƯỜI DÙNG ====
    start_input = req.start.strip()
    end_input   = req.end.strip()

    start_l = start_input.lower()
    end_l   = end_input.lower()

    # ==== LOAD MAP ====
    doc = await repo.get_map(req.map_name)

    graph_orig = doc["graph"]
    nodes_orig = doc["nodes"]
    weights_orig = doc["weights"]

    # ==== Tạo bản lowercase để search ====
    lower_to_original = {key.lower(): key for key in nodes_orig.keys()}

    graph_l = {k.lower(): [n.lower() for n in v] for k, v in graph_orig.items()}
    nodes_l = {k.lower(): v for k, v in nodes_orig.items()}

    weights_l = {}
    for k, v in weights_orig.items():
        if "-" in k:
            a, b = k.split("-")
            weights_l[(a.lower(), b.lower())] = v

    # ==== Resolve end (zone/department/room) ====
    resolved_end_l = end_l
    end_type = "zone"
    zone_name_original: Optional[str] = None
    room_desc: Optional[str] = None

    # TH1 – End là node zone trực tiếp (đã có trong graph)
    if end_l in graph_l:
        zone_name_original = lower_to_original[end_l]

    else:
        # TH2 – End là tên khoa (department)
        zones_by_dept = directory_repo.get_zones_by_department_name(
            db=db_directory,
            department_name=end_input,
            hospital_id=req.hospital_id,
        )

        if zones_by_dept:
            end_type = "department"
            zone = zones_by_dept[0]
            # Giữ nguyên chữ hoa/thường như trong DB
            zone_name_original = zone.name
            resolved_end_l = zone_name_original.lower()

        else:
            # TH3 – End là phòng (room)
            rooms = directory_repo.get_room_location_by_name(
                db=db_directory,
                room_number=end_input,
                hospital_id=req.hospital_id,
            )
            zones_by_room = directory_repo.get_zones_by_room_number(
                db=db_directory,
                room_number=end_input,
                hospital_id=req.hospital_id,
            )

            if rooms and zones_by_room:
                end_type = "room"
                room = rooms[0]
                zone = zones_by_room[0]

                zone_name_original = zone.name
                room_desc = room.location_description
                resolved_end_l = zone_name_original.lower()
            else:
                raise HTTPException(
                    status_code=404,
                    detail="Không tìm thấy khu / khoa / phòng để dẫn đường",
                )

    # ==== VALIDATE (lowercase bản copy) ====
    if start_l not in graph_l:
        raise HTTPException(400, f"Start '{start_input}' không tồn tại trong bản đồ")

    if resolved_end_l not in graph_l:
        raise HTTPException(400, f"Đích '{end_input}' không tồn tại trong bản đồ")

    # ==== DIJKSTRA ====
    cost, path_l = dijkstra(graph_l, weights_l, start_l, resolved_end_l)

    if not path_l:
        raise HTTPException(400, "Không tìm thấy đường đi")

    # ==== CONVERT PATH TRỞ LẠI ĐÚNG KEY GỐC ====
    path_original = [lower_to_original[x] for x in path_l]

    # ==== TEXT HƯỚNG ĐI ====
    direction_text = build_direction_text_original(
        path_l,
        weights_l,
        nodes_l,
        lower_to_original,
    )

    # ==== Append câu mô tả cuối ====
    if end_type == "zone":
        direction_text += f"\n{zone_name_original} là đích đến của bạn."

    elif end_type == "department":
        direction_text += f"\n{end_input} nằm trong {zone_name_original}, đó là đích đến của bạn."

    elif end_type == "room":
        direction_text += (
            f"\nPhòng {end_input} nằm ở {zone_name_original}, {room_desc}, đó là đích đến của bạn."
        )

    # ==== RETURN OUTPUT ĐÚNG CHỮ HOA/THƯỜNG GỐC ====
    return {
        "ok": True,
        "path": path_original,
        "total_cost": cost,
        "direction_text": direction_text,
        "zone": zone_name_original,
        "type": end_type,
        "map": {
            "id": doc.get("id"),
            "name": doc.get("name"),
            "nodes": doc.get("nodes"),
            "edges": doc.get("edges"),
            "graph": doc.get("graph"),
            "weights": doc.get("weights"),
            "image_url": doc.get("image_url"),
        },
    }


