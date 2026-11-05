from core.matching.jd_analyzer import (
    extract_skills,
    extract_skill_requirements
)


def match_skills(cv_text: str, job_text: str) -> dict[str, list[str]]:

    
    cv_skills = extract_skills(cv_text)
    job_requirements = extract_skill_requirements(job_text)

    required_skills = job_requirements["required_skills"]
    preferred_skills = job_requirements["preferred_skills"]
    other_skills = job_requirements["other_skills"]

    cv_skill_set = {
        skill.casefold()
        for skill in cv_skills
    }

    # 4. Tạo danh sách tất cả kỹ năng JD
    job_skills = (
        required_skills
        + preferred_skills
        + other_skills
    )

    
    matched_required = [
        skill for skill in required_skills
        if skill.casefold() in cv_skill_set
    ]

    
    missing_required = [
        skill for skill in required_skills
        if skill.casefold() not in cv_skill_set
    ]

    matched_preferred = [
        skill for skill in preferred_skills
        if skill.casefold() in cv_skill_set
    ]

    missing_preferred = [
        skill for skill in preferred_skills
        if skill.casefold() not in cv_skill_set
    ]

    matched_other = [
        skill for skill in other_skills
        if skill.casefold() in cv_skill_set
    ]

    missing_other = [
        skill for skill in other_skills
        if skill.casefold() not in cv_skill_set
    ]

    job_skill_set = {
        skill.casefold()
        for skill in job_skills
    }

    extra_skills = [
        skill for skill in cv_skills
        if skill.casefold() not in job_skill_set
    ]

    # 12. Trả về kết quả
    return {
        "cv_skills": cv_skills,
        "job_skills": job_skills,

        "required_skills": required_skills,
        "preferred_skills": preferred_skills,
        "other_skills": other_skills,

        "matched_required": matched_required,
        "missing_required": missing_required,

        "matched_preferred": matched_preferred,
        "missing_preferred": missing_preferred,

        "matched_other": matched_other,
        "missing_other": missing_other,

        "matched_skills": (
            matched_required
            + matched_preferred
            + matched_other
        ),

        "missing_skills": (
            missing_required
            + missing_preferred
            + missing_other
        ),

        "extra_skills": extra_skills
    }
