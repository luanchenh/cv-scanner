"""
R = số bắt buộc khớp / tổng bắt buộc
P = số ưu tiên khớp  / tổng ưu tiên

điểm_cơ_bản = 100 × (0.75 × R + 0.25 × P)
thưởng      = min(số_skill_thừa × 1, 5)        # tối đa +5 điểm
điểm        = min(điểm_cơ_bản + thưởng, 100)

"""

def calculate_score(
    match_result: dict,
) -> dict:

    matched_required = match_result["matched_required"]
    required_skills = match_result["required_skills"]

    matched_preferred = match_result["matched_preferred"]
    preferred_skills = match_result["preferred_skills"]

    extra_skills = match_result["extra_skills"]

    if required_skills:
        R = len(matched_required) / len(required_skills)
    else:
        R = 1.0

    
    if preferred_skills:
        P = len(matched_preferred) / len(preferred_skills)
    else:
        P = 0.0

    if not preferred_skills:
        base_score = 100 * R
    elif not required_skills:
        base_score = 100 * P
    else:
        base_score = 100 * (0.75 * R + 0.25 * P)

    bonus = min(len(extra_skills) * 1, 5)

    score = min(base_score + bonus, 100)

    if R < 0.5:
        score = min(score, 60)

    score = round(score, 2)


    return {
        "required_ratio": round(R * 100, 2),
        "preferred_ratio": round(P * 100, 2),
        "base_score": round(base_score, 2),
        "bonus": bonus,
        "final_score": score,
        
    }

