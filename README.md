# WinProb — 야구 승률 시뮬레이터

세이버메트릭스 기반 KBO 승률 시뮬레이터. 브라우저에서 몬테카를로 시뮬레이션이 실시간으로 돌아가는 단일 파일 웹앱입니다.

- 알고리즘: odds-ratio 매치업 확률 → 이벤트 기반 몬테카를로 이닝 시뮬레이션 → 경기 승률
- KBO 10개 팀 데이터 내장(드롭다운으로 불러오기)
- 변수: 타자 좌우, 투구폼, 직구 구사율, 출루율(OBP), WHIP

## 로컬 실행
`index.html`을 더블클릭하면 바로 열립니다. (그래프용 Chart.js를 CDN에서 불러오므로 인터넷 연결 필요)

## 실제 URL로 배포하기 (무료, 가장 쉬운 순서)

### 1) Netlify Drop — 가장 빠름 (계정 불필요)
1. https://app.netlify.com/drop 접속
2. `winprob_site` 폴더를 통째로 드래그 앤 드롭
3. 즉시 `https://랜덤이름.netlify.app` 형태의 공개 URL 생성

### 2) GitHub Pages — 포트폴리오에 좋음
1. GitHub에 새 저장소 생성 후 이 폴더의 파일 업로드
2. Settings ▸ Pages ▸ Branch를 `main` / `(root)`로 설정
3. `https://<아이디>.github.io/<저장소>/` 로 공개

### 3) Vercel / Cloudflare Pages
- vercel.com 또는 pages.cloudflare.com에서 GitHub 저장소를 연결하면 자동 배포·커스텀 도메인 연결 가능

## 팀 데이터 갱신 (Statiz)
`index.html` 상단의 `KBO` 배열을 수정하면 됩니다. 각 항목은 `[팀명, 팀 출루율(OBP), 팀 투수 WHIP]`.

```js
const KBO=[
  ['두산',.355,1.38], ['LG',.360,1.30], ...
];
```

Statiz(https://www.statiz.co.kr) 의 팀 타격 OBP와 팀 투수 WHIP를 보고 숫자만 바꾸면 최신 시즌으로 갱신됩니다.

## 실시간 자동 연동을 원한다면
정적 웹페이지는 브라우저 보안 정책(CORS) 때문에 statiz.co.kr를 직접 호출할 수 없습니다. 자동 연동하려면:
1. 작은 백엔드(예: Node/Express, Python/FastAPI)나 서버리스 함수(Vercel/Cloudflare Functions)를 두고
2. 서버에서 Statiz 데이터를 주기적으로 수집·정제해 자체 JSON API로 제공한 뒤
3. 프런트엔드가 그 JSON을 `fetch` 하도록 바꾸면 됩니다.

> 네이버 클라우드의 서버리스/클라우드 함수로 이 수집 파이프라인을 구성하면, 보고서의 "클라우드 기반 실시간 추론" 구상과도 자연스럽게 연결됩니다.

ⓒ 2026 트윈스 · 김재일
