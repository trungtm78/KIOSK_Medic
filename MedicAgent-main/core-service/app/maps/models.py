from pydantic import BaseModel
from typing import Dict, List, Optional

class Node(BaseModel):
    x: float
    y: float

class MapData(BaseModel):
    name: str
    nodes: Dict[str, Node]
    edges: List[List]
    graph: Dict[str, List[str]]
    weights: Dict[str, float]
    image_url: Optional[str] = None

class MapUpdate(BaseModel):
    nodes: Optional[Dict[str, Node]] = None
    edges: Optional[List[List]] = None
    graph: Optional[Dict[str, List[str]]] = None
    weights: Optional[Dict[str, float]] = None
    image_url: Optional[str] = None

class ShortestPathByMapRequest(BaseModel):
    map_name: str
    start: str
    end: str
    hospital_id: int
