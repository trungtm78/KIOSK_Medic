from __future__ import annotations

import re
from typing import Any, Dict, Tuple

from .triage_symptoms_data import TRIAGE_SYMPTOM_RULES

# Trigger keywords grouped by intent category for the NLU service.
DIRECTION_TRIGGERS = [
    "chi duong", "duong di", "huong dan duong",
    "di den", "di toi", "di ra", "di vao", "di qua", "di ve",
    "o dau", "nam o dau", "vi tri", "cho nao", "o cho nao",
    "toi khoa", "toi phong", "toi quay",
    "direction", "navigate", "how to get to", "where is", "way to", "go to",
]

PROCEDURE_TRIGGERS = [
    "thu tuc", "huong dan thu tuc", "quy trinh", "dang ky", "dat lich",
    "giay to", "ho so", "giay to can", "can gi", "can nhung gi", "can gi de",
    "procedure", "how to register", "register", "appointment",
    "document", "paperwork",
]

ISSUE_TICKET_TRIGGERS = [
    "boc so", "boc so kham", "lay so", "lay stt", "phat so", "so thu tu",
    "dang ky kham", "vao kham", "xep hang", "queue", "ticket", "lay phieu",
    "bốc số", "lấy số", "số thứ tự", "đăng ký khám", "xếp hàng",
]

INFO_LOOKUP_TRIGGERS = [
    "bao hiem", "bao hiem y te", "bhyt", "chi tra", "bao nhieu phan tram",
    "bao nhieu %", "muc huong", "duoc huong", "duoc bao nhieu",
    "gia", "chi phi", "bao nhieu tien", "gia dich vu", "phi kham",
    "insurance", "coverage", "co-pay", "co pay", "copay", "payment",
    "fee schedule", "price list",
    "tra cuu", "tra cuu thong tin", "tra cuu thong tin y te", "tra cuu thong tin bhyt",
    "tra cuu thong tin bao hiem", "tra cuu bhyt", "tra cuu bao hiem",
    "tra cứu", "tra cứu thông tin", "tra cứu thông tin y tế", "tra cứu bảo hiểm",
    "quy trinh", "quy trình", "thu tuc", "thủ tục", "ho so", "hồ sơ",
    "quy trinh benh vien", "quy trinh kham chua benh", "cac buoc kham benh",
    "workflow", "process", "business process", "luong xu ly", "phac do quy trinh",
]

TRIAGE_TRIGGERS = [
    "tu van", "tu van khoa", "trieu chung", "chon khoa", "khoa nao", "kham o dau",
    # "dau nhuc", "sot", "ho", "kho tho", "chong mat", "choang vang",
    "tư vấn", "triệu chứng", "chọn khoa", "khoa nào", "khó thở", "chóng mặt",
]

SMALLTALK_TRIGGERS = [
    "xin chao", "chao", "hello", "hi", "hey", "alo",
    "cam on", "cảm ơn", "thank", "thanks", "thank you",
    "tam biet", "tạm biệt", "bye", "goodbye",
]


PLACE_HINTS = [
    "khoa", "phong", "quay", "sanh", "cong", "giu xe", "thu ngan",
    "xet nghiem", "noi soi", "sieu am", "nhi", "san", "cap cuu",
    "cashier", "reception", "entrance", "parking", "information desk", "lobby",
]

RE_TAIL_AFTER_VERB = re.compile(
    r"(?:chi duong|duong di|huong dan|chi toi|di|di toi|di den|di qua)\s+(?:duong di|duong|di)?\s+(?:toi|den)?\s*(.+)$"
)
RE_BEFORE_ODAU = re.compile(r"^(.*?)(?:\s+(?:o dau|nam o dau|o cho nao|cho nao))\s*\??$")
RE_SIMPLE_TO = re.compile(r"(?:den|toi)\s+(.+)$")
RE_EN = re.compile(r"(?:where is|how to get to|go to|way to)\s+(.+)$")

STOP_TAIL = [
    "giup", "giup voi", "voi", "voi voi", "voi nhe", "voi a", "voi nhe a",
    "voi ban", "voi minh",
]
LEADING_FILLERS = ["toi", "den", "di", "ra", "vao", "qua", "ve", "the", "to", "a", "an", "the"]

CONFIRM_NO_PHRASES = [
    "khong", "khong nhe", "khong a", "khong em",
    "khum", "hong", "khoong",
    "khong dong y", "khong duoc", "khong phai",
    "khong xac nhan", "chua xac nhan",
    "no", "nope", "nah",
    "sai", "de sau", "tu choi",
    "khong co", "toi khong co", "toi khong co dau",
    "chua co", "toi chua co", "toi chua co dau",
    "hong co", "hong co dau",
    "khong co nhe", "khong co a", "khong co em",
]

CONFIRM_YES_PHRASES = [
    "co", "co nhe", "co a", "co em", "co chi", "co anh",
    "dong y", "dong y nhe", "dong y a",
    "ok", "oke", "okela", "okie",
    "yes", "y", "yep", "yeah",
    "chinh xac", "dung roi", "dung",
    "xac nhan", "xac nhan nhe", "xac nhan a",
    "co roi", "toi co", "toi co roi", "roi",
]

EMERGENCY_KEYWORDS = (
    "dau nguc",
    "tuc nguc",
    "that nguc",
    "nang nguc",
    "kho tho",
    "tho gap",
    "tho kho",
    "tho khong du",
    "kho tho qua",
    "khong tho duoc",
    "suy ho hap",
    "thieu oxi",
    "tim dap nhanh",
    "tim dap bat thuong",
    "co giat",
    "giat",
    "dong kinh",
    "len con",
    "ngat",
    "ngat xiu",
    "bat tinh",
    "mat y thuc",
    "hon me",
    "khong tinh tao",
    "mat tri giac",
    "choang vang",
    "choang",
    "tai nan",
    "tai nan giao thong",
    "tai nan xe may",
    "nga",
    "nga xe",
    "nga xuong",
    "nga tu cao",
    "chan thuong",
    "chan thuong nang",
    "bi thuong",
    "thuong tich",
    "rach",
    "dut",
    "gay xuong",
    "gay tay",
    "gay chan",
    "gay co",
    "xuong gay",
    "chay mau",
    "ra mau",
    "mat mau",
    "mau chay",
    "bleed",
    "bleeding",
    "injury",
    "wound",
    "trauma",
    "accident",
    "broken bone",
    "fracture",
    "burn",
    "bong",
    "heart attack",
    "chest pain",
    "short of breath",
    "shortness of breath",
    "difficulty breathing",
    "hard to breathe",
    "cannot breathe",
    "unconscious",
    "faint",
    "fainting",
    "seizure",
    "black out",
    "stroke",
)

EMERGENCY_SELECTION_TOKENS = {
    "1", "2", "3",
    "mot", "hai", "ba",
    "one", "two", "three",
    "first", "second", "third",
    "nhat", "nhi", "ba",
}

__all__ = [
    "DIRECTION_TRIGGERS",
    "PROCEDURE_TRIGGERS",
    "ISSUE_TICKET_TRIGGERS",
    "INFO_LOOKUP_TRIGGERS",
    "TRIAGE_TRIGGERS",
    "SMALLTALK_TRIGGERS",
    "TRIAGE_SYMPTOM_RULES",
    "PLACE_HINTS",
    "RE_TAIL_AFTER_VERB",
    "RE_BEFORE_ODAU",
    "RE_SIMPLE_TO",
    "RE_EN",
    "STOP_TAIL",
    "LEADING_FILLERS",
    "CONFIRM_NO_PHRASES",
    "CONFIRM_YES_PHRASES",
    "EMERGENCY_KEYWORDS",
    "EMERGENCY_SELECTION_TOKENS",
]
