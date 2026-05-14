import heapq, math
from typing import Dict, List, Tuple
import httpx

# ==== Convert weights "A-B" → ("A","B") ====
def convert_weight_keys(weight_dict: Dict[str, float]):
    out = {}
    for k, v in weight_dict.items():
        if "-" in k:
            a, b = k.split("-")
            out[(a, b)] = v
    return out


# ==== Dijkstra ====
def dijkstra(graph, weights, start, end):
    pq = [(0, start, [start])]
    visited = set()

    while pq:
        cost, node, path = heapq.heappop(pq)

        if node in visited:
            continue
        visited.add(node)

        if node == end:
            return cost, path

        for neighbor in graph.get(node, []):
            if neighbor in visited:
                continue

            w = weights.get((node, neighbor))
            if w is None:
                continue

            heapq.heappush(pq, (cost + w, neighbor, path + [neighbor]))

    return None, None


# ==== Hướng rẽ ====
def get_turn_direction(a, b, c, nodes):
    ax, ay = nodes[a]["x"], nodes[a]["y"]
    bx, by = nodes[b]["x"], nodes[b]["y"]
    cx, cy = nodes[c]["x"], nodes[c]["y"]

    v1 = (bx - ax, by - ay)
    v2 = (cx - bx, cy - by)

    len1 = math.hypot(*v1)
    len2 = math.hypot(*v2)
    if len1 == 0 or len2 == 0:
        return "đi tiếp"

    dot = v1[0] * v2[0] + v1[1] * v2[1]
    cos_angle = max(-1, min(1, dot / (len1 * len2)))
    angle = math.degrees(math.acos(cos_angle))
    cross = v1[0] * v2[1] - v1[1] * v2[0]

    if angle < 25:
        return "đi thẳng"
    if angle > 140:
        return "quay đầu"
    return "rẽ phải" if cross > 0 else "rẽ trái"


# ==== Build direction text ====
def build_direction_text(path, weights, nodes):
    if len(path) < 2:
        return ""

    total = 0
    lines = []

    for i in range(len(path) - 1):
        a, b = path[i], path[i + 1]
        w = int(weights.get((a, b), 0))
        total += w

        if i == 0:
            lines.append(f"Từ {a}, bắt đầu đi {w} mét tới {b}.")
        else:
            turn = get_turn_direction(path[i-1], a, b, nodes)
            if turn == "đi thẳng":
                lines.append(f"Từ {a}, đi thẳng {w} mét tới {b}.")
            elif turn in ["rẽ trái", "rẽ phải"]:
                lines.append(f"Từ {a}, {turn} và đi thêm {w} mét để tới {b}.")
            else:
                lines.append(f"Từ {a}, {turn} và đi {w} mét tới {b}.")

    return f"Tổng quãng đường khoảng {total} mét.\n" + "\n".join(lines)

def build_direction_text_original(path_l, weights_l, nodes_l, lower_to_original):
    """
    Build hướng dẫn nhưng dùng tên node đúng như trong DB.
    """
    # path original (đúng chữ hoa/thường)
    path = [lower_to_original[p] for p in path_l]

    total = 0
    lines = []

    for i in range(len(path_l) - 1):
        a_l = path_l[i]
        b_l = path_l[i + 1]

        a = lower_to_original[a_l]
        b = lower_to_original[b_l]

        w = int(weights_l.get((a_l, b_l), 0))
        total += w

        if i == 0:
            # Câu bắt đầu
            lines.append(f"Từ {a}, bắt đầu đi {w} mét tới {b}.")
        else:
            # Tính hướng rẽ dựa theo lowercase để ổn định
            turn = get_turn_direction(path_l[i - 1], a_l, b_l, nodes_l)

            if turn == "đi thẳng":
                lines.append(f"Từ {a}, đi thẳng {w} mét tới {b}.")
            elif turn in ["rẽ trái", "rẽ phải"]:
                lines.append(f"Từ {a}, {turn} và đi thêm {w} mét để tới {b}.")
            else:
                lines.append(f"Từ {a}, {turn} và đi {w} mét tới {b}.")

    return f"Tổng quãng đường khoảng {total} mét.\n" + "\n".join(lines)


