from __future__ import annotations

from typing import Any, Dict, Tuple

MAX_SYNDROME_SUGGESTIONS = 1
MAX_UNIT_SUGGESTIONS = 1

# Default triage unit catalogue used when directory service does not override a mapping.
DEFAULT_TRIAGE_UNITS: Dict[str, Dict[str, str]] = {
    "general": {"triage_unit_id": "general", "department_id": "general", "name": "Khoa tổng quát"},
    "emergency": {"triage_unit_id": "emergency", "department_id": "emergency", "name": "Khoa cấp cứu"},
    "cardiology": {"triage_unit_id": "cardiology", "department_id": "cardiology", "name": "Khoa tim mạch"},
    "pulmonology": {"triage_unit_id": "pulmonology", "department_id": "pulmonology", "name": "Khoa hô hấp"},
    "gastroenterology": {"triage_unit_id": "gastroenterology", "department_id": "gastroenterology", "name": "Khoa tiêu hóa"},
    "general_surgery": {"triage_unit_id": "general_surgery", "department_id": "general_surgery", "name": "Ngoại tổng quát"},
    "neurology": {"triage_unit_id": "neurology", "department_id": "neurology", "name": "Khoa thần kinh"},
    "orthopedics": {"triage_unit_id": "orthopedics", "department_id": "orthopedics", "name": "Chấn thương chỉnh hình"},
    "dermatology": {"triage_unit_id": "dermatology", "department_id": "dermatology", "name": "Khoa da liễu"},
    "ent": {"triage_unit_id": "ent", "department_id": "ent", "name": "Khoa tai mũi họng"},
    "ophthalmology": {"triage_unit_id": "ophthalmology", "department_id": "ophthalmology", "name": "Khoa mắt"},
    "pediatrics": {"triage_unit_id": "pediatrics", "department_id": "pediatrics", "name": "Khoa nhi"},
    "nephrology": {"triage_unit_id": "nephrology", "department_id": "nephrology", "name": "Khoa thận - tiết niệu"},
    "urology": {"triage_unit_id": "urology", "department_id": "urology", "name": "Khoa tiết niệu"},
    "obstetrics_gynecology": {"triage_unit_id": "obstetrics_gynecology", "department_id": "obstetrics_gynecology", "name": "Sản phụ khoa",},
    "allergy_immunology": {"triage_unit_id": "allergy_immunology","department_id": "allergy_immunology", "name": "Khoa dị ứng miễn dịch",},
    "infectious_disease": {"triage_unit_id": "infectious_disease","department_id": "infectious_disease","name": "Khoa truyền nhiễm", },
    "burn_unit": {"triage_unit_id": "burn_unit", "department_id": "burn_unit", "name": "Đơn vị bỏng"},
    "toxicology": {"triage_unit_id": "toxicology", "department_id": "toxicology", "name": "Trung tâm chống độc"},
    "wound_care": {"triage_unit_id": "wound_care", "department_id": "wound_care", "name": "Chăm sóc vết thương"},
}

# Danh sách syndrome_id dùng để tham chiếu nhanh khi cần liệt kê/lọc hội chứng.
LIST_SYNDROME_KEYS = [
    "cardiac_chest_pain",  #  đau ngực nghi tim mạch
    "respiratory_chest_pain",  #  đau ngực nghi hô hấp
    "acute_dyspnea",  #  khó thở cấp
    "chronic_cough",  #  ho kéo dài
    "asthma_exacerbation",  #  hen phế quản
    "pneumonia",  #  viêm phổi
    "fever_with_rash",  #  sốt cao kèm phát ban
    "high_fever_chills",  #  sốt rét run
    "upper_respiratory_infection",  #  nhiễm trùng đường hô hấp trên
    "ruq_abdominal_pain",  #  đau bụng phải trên (nghi gan mật)
    "periumbilical_pain",  #  đau bụng quanh rốn
    "lower_abdominal_pain",  #  đau bụng dưới
    "acute_gastroenteritis",  #  rối loạn tiêu hóa cấp
    "gi_bleeding",  #  xuất huyết tiêu hóa
    "peptic_ulcer",  #  loét dạ dày tá tràng
    "dysuria",  #  đái buốt/đái dắt
    "acute_kidney_injury",  #  suy thận cấp
    "generalized_edema",  #  phù toàn thân
    "acute_stroke",  #  đột quỵ
    "thunderclap_headache",  #  đau đầu dữ dội cấp
    "vertigo",  #  chóng mặt mất thăng bằng
    "seizure",  #  động kinh/co giật
    "peripheral_paresthesia",  #  tê bì tay chân
    "neck_shoulder_pain",  #  đau cổ vai gáy
    "limb_trauma",  #  chấn thương chi thể
    "acute_low_back_pain",  #  đau lưng cấp
    "burn_injury",  #  bỏng
    "infected_wound",  #  vết thương hở nhiễm trùng
    "allergic_reaction",  #  dị ứng/quincke
    "anaphylaxis",  #  sốc phản vệ
    "acute_dermatitis",  #  bệnh ngoài da cấp
    "generalized_pruritus",  #  ngứa toàn thân
    "conjunctivitis",  #  đau mắt đỏ
    "acute_visual_loss",  #  giảm thị lực cấp
    "ear_infection",  #  tai đau/viêm tai
    "pharyngitis",  #  viêm họng/viêm amidan
    "poisoning_foreign_body",  #  tai nạn, ngộ độc/nuốt dị vật
]


# Baseline rule set: symptoms -> syndrome scoring.
TRIAGE_SYNDROME_RULES: Tuple[Dict[str, Any], ...] = (
    {
        "syndrome_id": "cardiac_chest_pain",
        "name": "Hội chứng đau ngực nghi tim mạch",
        "base_score": 0.32,
        "threshold": 0.55,
        "symptoms": (
            {"symptom_id": "chest_pain", "weight": 0.5},
            {"symptom_id": "shortness_of_breath", "weight": 0.25},
            {"symptom_id": "palpitations", "weight": 0.2},
            {"symptom_id": "cold_sweat", "weight": 0.15},
        ),
    },
    {
        "syndrome_id": "respiratory_chest_pain",
        "name": "Hội chứng đau ngực nghi hô hấp",
        "base_score": 0.27,
        "threshold": 0.5,
        "symptoms": (
            {"symptom_id": "chest_pain", "weight": 0.4},
            {"symptom_id": "acute_cough", "weight": 0.2},
            {"symptom_id": "chronic_cough", "weight": 0.2},
            {"symptom_id": "shortness_of_breath", "weight": 0.2},
            {"symptom_id": "fever", "weight": 0.1},
        ),
    },
    {
        "syndrome_id": "acute_dyspnea",
        "name": "Hội chứng khó thở cấp",
        "base_score": 0.27,
        "threshold": 0.5,
        "symptoms": (
            {"symptom_id": "shortness_of_breath", "weight": 0.5},
            {"symptom_id": "wheezing", "weight": 0.3},
            {"symptom_id": "chest_pain", "weight": 0.15},
            {"symptom_id": "dizziness", "weight": 0.15},
        ),
    },
    {
        "syndrome_id": "chronic_cough",
        "name": "Hội chứng ho kéo dài",
        "base_score": 0.27,
        "threshold": 0.5,
        "symptoms": (
            {"symptom_id": "chronic_cough", "weight": 0.5},
            {"symptom_id": "acute_cough", "weight": 0.3},
            {"symptom_id": "shortness_of_breath", "weight": 0.15},
            {"symptom_id": "fever", "weight": 0.15},
        ),
    },
    {
        "syndrome_id": "asthma_exacerbation",
        "name": "Hội chứng hen phế quản",
        "base_score": 0.27,
        "threshold": 0.5,
        "symptoms": (
            {"symptom_id": "wheezing", "weight": 0.5},
            {"symptom_id": "shortness_of_breath", "weight": 0.3},
            {"symptom_id": "acute_cough", "weight": 0.2},
            {"symptom_id": "chest_pain", "weight": 0.1},
        ),
    },
    {
        "syndrome_id": "pneumonia",
        "name": "Hội chứng viêm phổi",
        "base_score": 0.3,
        "threshold": 0.55,
        "symptoms": (
            {"symptom_id": "fever", "weight": 0.3},
            {"symptom_id": "high_fever", "weight": 0.2},
            {"symptom_id": "acute_cough", "weight": 0.2},
            {"symptom_id": "shortness_of_breath", "weight": 0.2},
            {"symptom_id": "chills", "weight": 0.2},
        ),
    },
    {
        "syndrome_id": "fever_with_rash",
        "name": "Hội chứng sốt cao kèm phát ban",
        "base_score": 0.27,
        "threshold": 0.5,
        "symptoms": (
            {"symptom_id": "high_fever", "weight": 0.4},
            {"symptom_id": "fever", "weight": 0.2},
            {"symptom_id": "skin_rash", "weight": 0.3},
            {"symptom_id": "skin_itching", "weight": 0.1},
            {"symptom_id": "chills", "weight": 0.1},
        ),
    },
    {
        "syndrome_id": "high_fever_chills",
        "name": "Hội chứng sốt rét run",
        "base_score": 0.27,
        "threshold": 0.5,
        "symptoms": (
            {"symptom_id": "high_fever", "weight": 0.45},
            {"symptom_id": "chills", "weight": 0.3},
            {"symptom_id": "fever", "weight": 0.2},
            {"symptom_id": "body_ache", "weight": 0.15},
        ),
    },
    {
        "syndrome_id": "upper_respiratory_infection",
        "name": "Hội chứng nhiễm trùng đường hô hấp trên",
        "base_score": 0.27,
        "threshold": 0.5,
        "symptoms": (
            {"symptom_id": "acute_cough", "weight": 0.4},
            {"symptom_id": "sore_throat", "weight": 0.3},
            {"symptom_id": "runny_nose", "weight": 0.2},
            {"symptom_id": "fever", "weight": 0.2},
        ),
    },
    {
        "syndrome_id": "ruq_abdominal_pain",
        "name": "Hội chứng đau bụng phải trên (nghi gan mật)",
        "base_score": 0.27,
        "threshold": 0.5,
        "symptoms": (
            {"symptom_id": "abdominal_pain_ruq", "weight": 0.5},
            {"symptom_id": "nausea", "weight": 0.2},
            {"symptom_id": "fever", "weight": 0.15},
            {"symptom_id": "digestive_disorder", "weight": 0.1},
            {"symptom_id": "body_ache", "weight": 0.1},
        ),
    },
    {
        "syndrome_id": "periumbilical_pain",
        "name": "Hội chứng đau bụng quanh rốn",
        "base_score": 0.27,
        "threshold": 0.5,
        "symptoms": (
            {"symptom_id": "abdominal_pain_mid", "weight": 0.5},
            {"symptom_id": "digestive_disorder", "weight": 0.2},
            {"symptom_id": "nausea", "weight": 0.2},
            {"symptom_id": "diarrhea", "weight": 0.2},
        ),
    },
    {
        "syndrome_id": "lower_abdominal_pain",
        "name": "Hội chứng đau bụng dưới",
        "base_score": 0.27,
        "threshold": 0.5,
        "symptoms": (
            {"symptom_id": "abdominal_pain_lower", "weight": 0.48},
            {"symptom_id": "painful_urination", "weight": 0.2},
            {"symptom_id": "frequent_urination", "weight": 0.2},
            {"symptom_id": "fever", "weight": 0.15},
            {"symptom_id": "digestive_disorder", "weight": 0.1},
        ),
    },
    {
        "syndrome_id": "acute_gastroenteritis",
        "name": "Hội chứng rối loạn tiêu hóa cấp",
        "base_score": 0.27,
        "threshold": 0.5,
        "symptoms": (
            {"symptom_id": "diarrhea", "weight": 0.4},
            {"symptom_id": "nausea", "weight": 0.3},
            {"symptom_id": "digestive_disorder", "weight": 0.2},
            {"symptom_id": "fever", "weight": 0.1},
            {"symptom_id": "abdominal_pain_mid", "weight": 0.1},
        ),
    },
    {
        "syndrome_id": "gi_bleeding",
        "name": "Hội chứng xuất huyết tiêu hóa",
        "base_score": 0.3,
        "threshold": 0.55,
        "symptoms": (
            {"symptom_id": "vomiting_blood", "weight": 0.5},
            {"symptom_id": "black_stool", "weight": 0.4},
            {"symptom_id": "dizziness", "weight": 0.1},
            {"symptom_id": "abdominal_pain_mid", "weight": 0.1},
        ),
    },
    {
        "syndrome_id": "peptic_ulcer",
        "name": "Hội chứng loét dạ dày tá tràng",
        "base_score": 0.27,
        "threshold": 0.5,
        "symptoms": (
            {"symptom_id": "epigastric_burning", "weight": 0.5},
            {"symptom_id": "abdominal_pain_mid", "weight": 0.3},
            {"symptom_id": "nausea", "weight": 0.2},
            {"symptom_id": "digestive_disorder", "weight": 0.1},
        ),
    },
    {
        "syndrome_id": "dysuria",
        "name": "Hội chứng đái buốt/đái dắt",
        "base_score": 0.27,
        "threshold": 0.5,
        "symptoms": (
            {"symptom_id": "painful_urination", "weight": 0.5},
            {"symptom_id": "frequent_urination", "weight": 0.3},
            {"symptom_id": "fever", "weight": 0.15},
            {"symptom_id": "abdominal_pain_lower", "weight": 0.15},
        ),
    },
    {
        "syndrome_id": "acute_kidney_injury",
        "name": "Hội chứng suy thận cấp",
        "base_score": 0.27,
        "threshold": 0.5,
        "symptoms": (
            {"symptom_id": "reduced_urination", "weight": 0.5},
            {"symptom_id": "swelling_general", "weight": 0.3},
            {"symptom_id": "nausea", "weight": 0.15},
            {"symptom_id": "dizziness", "weight": 0.15},
        ),
    },
    {
        "syndrome_id": "generalized_edema",
        "name": "Hội chứng phù toàn thân",
        "base_score": 0.27,
        "threshold": 0.5,
        "symptoms": (
            {"symptom_id": "swelling_general", "weight": 0.55},
            {"symptom_id": "shortness_of_breath", "weight": 0.2},
            {"symptom_id": "reduced_urination", "weight": 0.2},
            {"symptom_id": "body_ache", "weight": 0.1},
        ),
    },
    {
        "syndrome_id": "acute_stroke",
        "name": "Hội chứng đột quỵ",
        "base_score": 0.3,
        "threshold": 0.55,
        "symptoms": (
            {"symptom_id": "numbness", "weight": 0.4},
            {"symptom_id": "facial_droop", "weight": 0.3},
            {"symptom_id": "speech_difficulty", "weight": 0.3},
            {"symptom_id": "headache_severe", "weight": 0.1},
        ),
    },
    {
        "syndrome_id": "thunderclap_headache",
        "name": "Hội chứng đau đầu dữ dội cấp",
        "base_score": 0.27,
        "threshold": 0.5,
        "symptoms": (
            {"symptom_id": "headache_severe", "weight": 0.5},
            {"symptom_id": "dizziness", "weight": 0.2},
            {"symptom_id": "nausea", "weight": 0.15},
            {"symptom_id": "vision_loss", "weight": 0.15},
            {"symptom_id": "neck_pain", "weight": 0.1},
        ),
    },
    {
        "syndrome_id": "vertigo",
        "name": "Hội chứng chóng mặt mất thăng bằng",
        "base_score": 0.27,
        "threshold": 0.5,
        "symptoms": (
            {"symptom_id": "dizziness", "weight": 0.45},
            {"symptom_id": "loss_of_balance", "weight": 0.35},
            {"symptom_id": "nausea", "weight": 0.15},
            {"symptom_id": "headache_severe", "weight": 0.15},
        ),
    },
    {
        "syndrome_id": "seizure",
        "name": "Hội chứng động kinh/co giật",
        "base_score": 0.3,
        "threshold": 0.55,
        "symptoms": (
            {"symptom_id": "seizure", "weight": 0.55},
            {"symptom_id": "loss_of_consciousness", "weight": 0.3},
            {"symptom_id": "headache_severe", "weight": 0.15},
            {"symptom_id": "fever", "weight": 0.1},
        ),
    },
    {
        "syndrome_id": "peripheral_paresthesia",
        "name": "Hội chứng tê bì tay chân",
        "base_score": 0.27,
        "threshold": 0.5,
        "symptoms": (
            {"symptom_id": "numbness", "weight": 0.5},
            {"symptom_id": "loss_of_balance", "weight": 0.2},
            {"symptom_id": "neck_pain", "weight": 0.2},
            {"symptom_id": "headache_severe", "weight": 0.1},
            {"symptom_id": "speech_difficulty", "weight": 0.1},
        ),
    },
    {
        "syndrome_id": "neck_shoulder_pain",
        "name": "Hội chứng đau cổ vai gáy",
        "base_score": 0.27,
        "threshold": 0.5,
        "symptoms": (
            {"symptom_id": "neck_pain", "weight": 0.5},
            {"symptom_id": "joint_pain", "weight": 0.2},
            {"symptom_id": "numbness", "weight": 0.2},
            {"symptom_id": "headache_severe", "weight": 0.1},
            {"symptom_id": "body_ache", "weight": 0.1},
        ),
    },
    {
        "syndrome_id": "limb_trauma",
        "name": "Hội chứng chấn thương chi thể",
        "base_score": 0.27,
        "threshold": 0.5,
        "symptoms": (
            {"symptom_id": "injury", "weight": 0.5},
            {"symptom_id": "joint_pain", "weight": 0.2},
            {"symptom_id": "swelling_general", "weight": 0.2},
            {"symptom_id": "open_wound", "weight": 0.15},
            {"symptom_id": "body_ache", "weight": 0.05},
        ),
    },
    {
        "syndrome_id": "acute_low_back_pain",
        "name": "Hội chứng đau lưng cấp",
        "base_score": 0.27,
        "threshold": 0.5,
        "symptoms": (
            {"symptom_id": "back_pain", "weight": 0.52},
            {"symptom_id": "injury", "weight": 0.2},
            {"symptom_id": "numbness", "weight": 0.2},
            {"symptom_id": "abdominal_pain_lower", "weight": 0.1},
            {"symptom_id": "body_ache", "weight": 0.1},
        ),
    },
    {
        "syndrome_id": "burn_injury",
        "name": "Hội chứng bỏng",
        "base_score": 0.3,
        "threshold": 0.55,
        "symptoms": (
            {"symptom_id": "burn_injury", "weight": 0.6},
            {"symptom_id": "skin_blister", "weight": 0.2},
            {"symptom_id": "open_wound", "weight": 0.2},
            {"symptom_id": "body_ache", "weight": 0.1},
        ),
    },
    {
        "syndrome_id": "infected_wound",
        "name": "Hội chứng vết thương hở nhiễm trùng",
        "base_score": 0.27,
        "threshold": 0.5,
        "symptoms": (
            {"symptom_id": "open_wound", "weight": 0.4},
            {"symptom_id": "fever", "weight": 0.2},
            {"symptom_id": "skin_ulcer", "weight": 0.2},
            {"symptom_id": "swelling_general", "weight": 0.15},
            {"symptom_id": "skin_rash", "weight": 0.15},
        ),
    },
    {
        "syndrome_id": "allergic_reaction",
        "name": "Hội chứng dị ứng/quincke",
        "base_score": 0.27,
        "threshold": 0.5,
        "symptoms": (
            {"symptom_id": "allergic_reaction", "weight": 0.48},
            {"symptom_id": "skin_rash", "weight": 0.2},
            {"symptom_id": "skin_itching", "weight": 0.2},
            {"symptom_id": "swelling_general", "weight": 0.15},
            {"symptom_id": "runny_nose", "weight": 0.1},
        ),
    },
    {
        "syndrome_id": "anaphylaxis",
        "name": "Hội chứng sốc phản vệ",
        "base_score": 0.3,
        "threshold": 0.55,
        "symptoms": (
            {"symptom_id": "allergic_reaction", "weight": 0.45},
            {"symptom_id": "shortness_of_breath", "weight": 0.35},
            {"symptom_id": "swelling_general", "weight": 0.2},
            {"symptom_id": "dizziness", "weight": 0.1},
            {"symptom_id": "nausea", "weight": 0.1},
        ),
    },
    {
        "syndrome_id": "acute_dermatitis",
        "name": "Hội chứng bệnh ngoài da cấp",
        "base_score": 0.27,
        "threshold": 0.5,
        "symptoms": (
            {"symptom_id": "skin_rash", "weight": 0.4},
            {"symptom_id": "skin_itching", "weight": 0.3},
            {"symptom_id": "skin_blister", "weight": 0.2},
            {"symptom_id": "skin_ulcer", "weight": 0.2},
        ),
    },
    {
        "syndrome_id": "generalized_pruritus",
        "name": "Hội chứng ngứa toàn thân",
        "base_score": 0.27,
        "threshold": 0.5,
        "symptoms": (
            {"symptom_id": "skin_itching", "weight": 0.5},
            {"symptom_id": "skin_rash", "weight": 0.2},
            {"symptom_id": "allergic_reaction", "weight": 0.2},
            {"symptom_id": "swelling_general", "weight": 0.1},
            {"symptom_id": "body_ache", "weight": 0.1},
        ),
    },
    {
        "syndrome_id": "conjunctivitis",
        "name": "Hội chứng đau mắt đỏ",
        "base_score": 0.27,
        "threshold": 0.5,
        "symptoms": (
            {"symptom_id": "red_eye", "weight": 0.45},
            {"symptom_id": "eye_pain", "weight": 0.2},
            {"symptom_id": "watery_eye", "weight": 0.2},
            {"symptom_id": "skin_itching", "weight": 0.1},
            {"symptom_id": "fever", "weight": 0.15},
        ),
    },
    {
        "syndrome_id": "acute_visual_loss",
        "name": "Hội chứng giảm thị lực cấp",
        "base_score": 0.3,
        "threshold": 0.55,
        "symptoms": (
            {"symptom_id": "vision_loss", "weight": 0.55},
            {"symptom_id": "blurred_vision", "weight": 0.3},
            {"symptom_id": "eye_pain", "weight": 0.2},
            {"symptom_id": "headache_severe", "weight": 0.1},
        ),
    },
    {
        "syndrome_id": "ear_infection",
        "name": "Hội chứng tai đau/viêm tai",
        "base_score": 0.27,
        "threshold": 0.5,
        "symptoms": (
            {"symptom_id": "ear_pain", "weight": 0.45},
            {"symptom_id": "fever", "weight": 0.2},
            {"symptom_id": "runny_nose", "weight": 0.2},
            {"symptom_id": "sore_throat", "weight": 0.15},
            {"symptom_id": "dizziness", "weight": 0.1},
        ),
    },
    {
        "syndrome_id": "pharyngitis",
        "name": "Hội chứng viêm họng/viêm amidan",
        "base_score": 0.27,
        "threshold": 0.5,
        "symptoms": (
            {"symptom_id": "sore_throat", "weight": 0.45},
            {"symptom_id": "fever", "weight": 0.2},
            {"symptom_id": "runny_nose", "weight": 0.2},
            {"symptom_id": "acute_cough", "weight": 0.15},
            {"symptom_id": "body_ache", "weight": 0.1},
        ),
    },
    {
        "syndrome_id": "poisoning_foreign_body",
        "name": "Hội chứng tai nạn, ngộ độc/nuốt dị vật",
        "base_score": 0.3,
        "threshold": 0.55,
        "symptoms": (
            {"symptom_id": "poisoning", "weight": 0.5},
            {"symptom_id": "foreign_body_ingestion", "weight": 0.35},
            {"symptom_id": "nausea", "weight": 0.15},
            {"symptom_id": "shortness_of_breath", "weight": 0.1},
            {"symptom_id": "child_fever", "weight": 0.05},
        ),
    },
)


# Fallback mapping from syndrome to triage-unit keys.
DEFAULT_SYNDROME_TRIAGE_UNITS: Dict[str, str] = {
    "cardiac_chest_pain": "cardiology",
    "respiratory_chest_pain": "pulmonology",
    "acute_dyspnea": "emergency",
    "chronic_cough": "pulmonology",
    "asthma_exacerbation": "pulmonology",
    "pneumonia": "pulmonology",
    "fever_with_rash": "infectious_disease",
    "high_fever_chills": "infectious_disease",
    "upper_respiratory_infection": "ent",
    "ruq_abdominal_pain": "gastroenterology",
    "periumbilical_pain": "gastroenterology",
    "lower_abdominal_pain": "gastroenterology",
    "acute_gastroenteritis": "gastroenterology",
    "gi_bleeding": "gastroenterology",
    "peptic_ulcer": "gastroenterology",
    "dysuria": "urology",
    "acute_kidney_injury": "nephrology",
    "generalized_edema": "cardiology",
    "acute_stroke": "neurology",
    "thunderclap_headache": "neurology",
    "vertigo": "neurology",
    "seizure": "neurology",
    "peripheral_paresthesia": "neurology",
    "neck_shoulder_pain": "orthopedics",
    "limb_trauma": "orthopedics",
    "acute_low_back_pain": "orthopedics",
    "burn_injury": "burn_unit",
    "infected_wound": "wound_care",
    "allergic_reaction": "allergy_immunology",
    "anaphylaxis": "emergency",
    "acute_dermatitis": "dermatology",
    "generalized_pruritus": "dermatology",
    "conjunctivitis": "ophthalmology",
    "acute_visual_loss": "ophthalmology",
    "ear_infection": "ent",
    "pharyngitis": "ent",
    "poisoning_foreign_body": "emergency",
}
