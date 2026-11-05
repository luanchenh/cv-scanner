import json
import re
import unicodedata
from functools import lru_cache
from pathlib import Path

from core.parser.pdf_reader import read_pdf
from core.parser.word_reader import read_docx

BASE_DIR = Path(__file__).resolve().parents[2]
SKILL_PATH = BASE_DIR / "data" / "skills.json"

_RANK = {
    "required": 0,
    "preferred": 1,
    "other": 2,
}

_HEAD_REQUIRED = re.compile(
    r"requirements?|required|must[\s-]*have|mandatory|essential|qualifications?|"
    r"yêu cầu|bắt buộc|tiêu chuẩn",
    re.IGNORECASE,
)
_HEAD_PREFERRED = re.compile(
    r"preferred|nice[\s-]*to[\s-]*have|good to have|a plus|bonus|desirable|"
    r"ưu tiên|lợi thế|điểm cộng",
    re.IGNORECASE,
)
_HEAD_OTHER = re.compile(
    r"responsibilit|benefits?|perks|about|what we offer|"
    r"mô tả|trách nhiệm|quyền lợi|phúc lợi|giới thiệu",
    re.IGNORECASE,
)

_LINE_REQUIRED = re.compile(
    r"required|must[\s-]*have|mandatory|essential|bắt buộc",
    re.IGNORECASE,
)
_LINE_PREFERRED = re.compile(
    r"preferred|nice[\s-]*to[\s-]*have|a plus|bonus|desirable|ideally|"
    r"ưu tiên|lợi thế|điểm cộng",
    re.IGNORECASE,
)

_NEGATED = re.compile(
    r"not\s+(?:strictly\s+)?(?:required|necessary|mandatory)|"
    r"không\s+(?:bắt buộc|yêu cầu)",
    re.IGNORECASE,
)

_CLAUSE_SPLIT = re.compile(
    r";|\bbut\b|\bwhile\b|\bnhưng\b",
    re.IGNORECASE,
)

def load_skill_database() -> list[dict]:
    with SKILL_PATH.open("r", encoding="utf-8") as file:
        data = json.load(file)

    return data["skills"]


def read_job_description(file_path: str) -> str:

    path = Path(file_path)

    extension = path.suffix.lower()

    if extension == ".pdf":
        return read_pdf(path)

    elif extension == ".docx":
        return read_docx(path)

    else:
        raise ValueError(
            f"Unsupported file format: {extension}"
        )

@lru_cache(maxsize=1)
def _compiled_skills() -> tuple[tuple[str, re.Pattern], ...]:

    compiled = []

    for skill in load_skill_database():

        terms = {
            term
            for term in [
                skill["name"],
                *skill.get("aliases", [])
            ]
            if term
        }

        regex = "|".join(
            re.escape(term)
            for term in sorted(terms, key=len, reverse=True)
        )

        compiled.append((
            skill["name"],
            re.compile(
                rf"(?<![\w+#])(?:{regex})(?![\w+#])",
                re.IGNORECASE
            )
        ))

    return tuple(compiled)


# Trích xuất kỹ năng
def extract_skills(text: str) -> list[str]:

    if not isinstance(text, str):
        raise TypeError("Input text must be a string")

    text = unicodedata.normalize("NFC", text)

    return [
        name
        for name, pattern in _compiled_skills()
        if pattern.search(text)
    ]


# Xác định loại tiêu đề
def _classify_heading(line: str) -> str | None:

    if not line or len(line) > 60 or line[0] in "-*•":
        return None

    core = line.rstrip(":").strip()

    if not (line.endswith(":") or len(core.split()) <= 5):
        return None

    if _HEAD_PREFERRED.search(core):
        return "preferred"

    if _HEAD_REQUIRED.search(core):
        return "required"

    if _HEAD_OTHER.search(core):
        return "other"

    return None


# Xác định loại kỹ năng trong từng mệnh đề
def _clause_type(clause: str) -> str | None:

    if _NEGATED.search(clause) or _LINE_PREFERRED.search(clause):
        return "preferred"

    if _LINE_REQUIRED.search(clause):
        return "required"

    return None


# Phân loại kỹ năng trong Job Description
def extract_skill_requirements(text: str) -> dict[str, list[str]]:

    if not isinstance(text, str):
        raise TypeError("Input text must be a string")

    text = unicodedata.normalize("NFC", text)

    section: str | None = None

    # Lưu loại kỹ năng có độ ưu tiên cao nhất
    best: dict[str, str] = {}

    for raw in text.splitlines():

        line = raw.strip()

        if not line:
            continue

        heading = _classify_heading(line)

        # Cập nhật section hiện tại
        if heading and (
            line.endswith(":") or not extract_skills(line)
        ):
            section = heading

        # Chia dòng thành các mệnh đề
        for clause in _CLAUSE_SPLIT.split(line):

            kind = (
                _clause_type(clause)
                or heading
                or section
                or "other"
            )

            skills = extract_skills(clause)

            for skill in skills:

                if (
                    skill not in best
                    or _RANK[kind] < _RANK[best[skill]]
                ):
                    best[skill] = kind

    result = {
        "required_skills": [
            skill for skill, kind in best.items()
            if kind == "required"
        ],

        "preferred_skills": [
            skill for skill, kind in best.items()
            if kind == "preferred"
        ],

        "other_skills": [
            skill for skill, kind in best.items()
            if kind == "other"
        ]
    }

    # Dự phòng nếu JD không có dấu hiệu phân loại
    if (
        not result["required_skills"]
        and not result["preferred_skills"]
    ):
        result["required_skills"] = result["other_skills"]
        result["other_skills"] = []

    return result
