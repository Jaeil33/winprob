#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KBO 팀 성적(팀 출루율 OBP, 팀 투수 WHIP)을 수집해 data.json을 갱신한다.

설계 원칙
- 안전 우선: 수집/파싱에 실패하면 기존 data.json을 '건드리지 않고' 종료한다.
  (사이트는 항상 마지막으로 성공한 데이터를 계속 보여준다.)
- 소스 비종속: 어떤 JSON 구조가 오더라도 team/obp/whip 값을 탐색하도록 작성.
- 데이터 소스 구조가 바뀌면 SOURCES/parse 부분만 손보면 된다.

수동 테스트:  python scripts/update_kbo.py
GitHub Actions에서 매일 자동 실행되며, 변경이 있을 때만 커밋한다.
"""
import json, sys, datetime, os
import requests

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(HERE, "data.json")
YEAR = datetime.datetime.now().year
HEADERS = {"User-Agent": "Mozilla/5.0", "Referer": "https://m.sports.naver.com/"}

# 네이버 스포츠 KBO 팀 기록(JSON). 시즌/구조 변경 시 URL만 조정하면 된다.
SOURCES = {
    "batting":  f"https://api-gw.sports.naver.com/statistics/categories/kbo/seasons/{YEAR}/teams?categoryType=batting",
    "pitching": f"https://api-gw.sports.naver.com/statistics/categories/kbo/seasons/{YEAR}/teams?categoryType=pitching",
}

# 네이버 팀 코드/표기 -> 사이트 표기
TEAM_MAP = {
    "두산": "두산", "OB": "두산",
    "LG": "LG",
    "KIA": "KIA", "HT": "KIA", "기아": "KIA",
    "삼성": "삼성", "SS": "삼성",
    "SSG": "SSG", "SK": "SSG",
    "롯데": "롯데", "LT": "롯데",
    "한화": "한화", "HH": "한화",
    "NC": "NC",
    "KT": "KT", "kt": "KT",
    "키움": "키움", "WO": "키움", "넥센": "키움",
}
ORDER = ["두산", "LG", "KIA", "삼성", "SSG", "롯데", "한화", "NC", "KT", "키움"]


def walk_records(obj):
    """중첩 JSON 어디에 있든 'team/name' 키를 가진 dict 들을 모은다."""
    out = []
    def rec(o):
        if isinstance(o, dict):
            low = {k.lower() for k in o.keys()}
            if any(("team" in k or "name" in k) for k in low):
                out.append(o)
            for v in o.values():
                rec(v)
        elif isinstance(o, list):
            for v in o:
                rec(v)
    rec(obj)
    return out


def team_of(d):
    for k, v in d.items():
        if isinstance(v, str) and ("team" in k.lower() or "name" in k.lower()):
            name = v.strip()
            return TEAM_MAP.get(name, TEAM_MAP.get(name.upper(), name))
    return None


def num_of(d, *cands):
    for k, v in d.items():
        lk = k.lower().replace("_", "").replace("-", "")
        if lk in cands:
            try:
                return round(float(v), 3)
            except (TypeError, ValueError):
                pass
    return None


def fetch(url):
    r = requests.get(url, headers=HEADERS, timeout=20)
    r.raise_for_status()
    return r.json()


def collect():
    obp, whip = {}, {}
    for rec in walk_records(fetch(SOURCES["batting"])):
        t = team_of(rec); v = num_of(rec, "obp", "출루율")
        if t and v and 0.25 < v < 0.45:
            obp[t] = v
    for rec in walk_records(fetch(SOURCES["pitching"])):
        t = team_of(rec); v = num_of(rec, "whip")
        if t and v and 0.9 < v < 2.0:
            whip[t] = v
    teams = []
    for t in ORDER:
        if t in obp and t in whip:
            teams.append({"name": t, "obp": obp[t], "whip": whip[t]})
    return teams


def main():
    try:
        teams = collect()
    except Exception as e:
        print(f"[skip] 수집 실패 — 기존 data.json 유지: {e}")
        return 0
    if len(teams) < 8:
        print(f"[skip] 유효 팀 {len(teams)}개(<8) — 기존 data.json 유지. 소스 구조 변경 가능성.")
        return 0
    payload = {
        "season": str(YEAR),
        "updated": datetime.date.today().isoformat(),
        "source": "naver-sports",
        "teams": teams,
    }
    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"[ok] {len(teams)}개 팀 갱신 완료 ({payload['updated']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
