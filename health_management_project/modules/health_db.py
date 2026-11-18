"""모듈 1: 데이터 구조화 및 파일 영구 저장 (JSON, CSV, TXT, Pickle)"""
import os
import json
import csv
import pickle
from datetime import datetime

# modules/ 의 상위 폴더(프로젝트 루트) 아래 data/ 폴더를 사용
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

FIELDS = ["id", "name", "birth_year", "gender", "height", "weight", "bmi", "status"]


def calc_bmi(height, weight):
    """BMI = 체중(kg) / (키(m))^2, 소수 둘째 자리 반올림. height는 cm."""
    return round(weight / ((height / 100) ** 2), 2)


def get_status(bmi):
    """BMI 수치로 비만도 판정 (대한비만학회 아시아-태평양 기준)."""
    if bmi < 18.5:
        return "저체중"
    elif bmi < 23:
        return "정상"
    elif bmi < 25:
        return "과체중"
    return "비만"


class HealthRecord:
    """한 사람의 건강정보를 저장하는 클래스."""

    def __init__(self, id, name, birth_year, gender, height, weight):
        self.id = id
        self.name = name
        self.birth_year = int(birth_year)
        self.gender = gender
        self.height = float(height)
        self.weight = float(weight)
        self.bmi = 0.0
        self.status = ""
        self.update_bmi()

    def update_bmi(self):
        """키/몸무게로 BMI와 비만도를 (재)계산한다."""
        self.bmi = calc_bmi(self.height, self.weight)
        self.status = get_status(self.bmi)

    def to_dict(self):
        """딕셔너리로 변환 (JSON/CSV/TXT 저장용)."""
        return {
            "id": self.id,
            "name": self.name,
            "birth_year": self.birth_year,
            "gender": self.gender,
            "height": self.height,
            "weight": self.weight,
            "bmi": self.bmi,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, d):
        """딕셔너리로부터 HealthRecord 객체를 만든다."""
        return cls(d["id"], d["name"], d["birth_year"], d["gender"],
                   d["height"], d["weight"])

    def __str__(self):
        return (f"{self.id} | {self.name} | {self.birth_year} | {self.gender} | "
                f"{self.height}cm | {self.weight}kg | BMI {self.bmi} ({self.status})")


class HealthManager:
    """건강정보 객체 목록을 관리하고 파일 입출력을 담당하는 클래스."""

    def __init__(self):
        self.records = []

    # ---------- 목록 관리 ----------
    def generate_id(self):
        """고유 식별번호 생성: P{올해}-{4자리 일련번호}"""
        prefix = f"P{datetime.now().year}-"
        numbers = [int(r.id.split("-")[1]) for r in self.records
                   if r.id.startswith(prefix)]
        next_no = max(numbers) + 1 if numbers else 1
        return f"{prefix}{next_no:04d}"

    def add_record(self, name, birth_year, gender, height, weight):
        """새 레코드를 만들어 목록에 추가하고 반환한다."""
        record = HealthRecord(self.generate_id(), name, birth_year,
                              gender, height, weight)
        self.records.append(record)
        return record

    def print_all(self, records=None, title=""):
        """목록을 화면에 출력한다."""
        records = self.records if records is None else records
        if title:
            print(f"=== {title} ===")
        for r in records:
            print(r)

    # ---------- 파일 경로 ----------
    def _path(self, filename):
        os.makedirs(DATA_DIR, exist_ok=True)
        return os.path.join(DATA_DIR, filename)

    # ---------- JSON ----------
    def save_json(self, filename="health_data.json"):
        try:
            with open(self._path(filename), "w", encoding="utf-8") as f:
                json.dump([r.to_dict() for r in self.records], f,
                          ensure_ascii=False, indent=4)
            return True
        except OSError as e:
            print(f"[JSON 저장 오류] {e}")
            return False

    def load_json(self, filename="health_data.json"):
        try:
            with open(self._path(filename), "r", encoding="utf-8") as f:
                return [HealthRecord.from_dict(d) for d in json.load(f)]
        except (OSError, json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"[JSON 불러오기 오류] {e}")
            return []

    # ---------- CSV ----------
    def save_csv(self, filename="health_data.csv"):
        try:
            with open(self._path(filename), "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=FIELDS)
                writer.writeheader()
                for r in self.records:
                    writer.writerow(r.to_dict())
            return True
        except OSError as e:
            print(f"[CSV 저장 오류] {e}")
            return False

    def load_csv(self, filename="health_data.csv"):
        try:
            with open(self._path(filename), "r", encoding="utf-8", newline="") as f:
                return [HealthRecord.from_dict(row) for row in csv.DictReader(f)]
        except (OSError, KeyError, ValueError) as e:
            print(f"[CSV 불러오기 오류] {e}")
            return []

    # ---------- TXT ----------
    def save_txt(self, filename="health_data.txt"):
        try:
            with open(self._path(filename), "w", encoding="utf-8") as f:
                for r in self.records:
                    d = r.to_dict()
                    f.write(",".join(str(d[k]) for k in FIELDS) + "\n")
            return True
        except OSError as e:
            print(f"[TXT 저장 오류] {e}")
            return False

    def load_txt(self, filename="health_data.txt"):
        records = []
        try:
            with open(self._path(filename), "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    d = dict(zip(FIELDS, line.split(",")))
                    records.append(HealthRecord.from_dict(d))
            return records
        except (OSError, KeyError, ValueError) as e:
            print(f"[TXT 불러오기 오류] {e}")
            return []

    # ---------- Pickle ----------
    def save_pickle(self, filename="health_data.pkl"):
        try:
            with open(self._path(filename), "wb") as f:
                pickle.dump(self.records, f)
            return True
        except (OSError, pickle.PicklingError) as e:
            print(f"[Pickle 저장 오류] {e}")
            return False

    def load_pickle(self, filename="health_data.pkl"):
        try:
            with open(self._path(filename), "rb") as f:
                return pickle.load(f)
        except (OSError, pickle.UnpicklingError, EOFError, AttributeError) as e:
            print(f"[Pickle 불러오기 오류] {e}")
            return []