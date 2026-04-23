# claude-mascot 플러그인 설계

**상태**: Draft (브레인스토밍 승인됨, 구현 계획 대기)
**작성일**: 2026-04-23
**작성자**: jungchul (+ Claude Opus 4.7)

## 1. Context & Motivation

현재 `claude_warp_custom` 프로젝트의 tsundere cat "나비" 는 잘 동작하지만:

- 경로가 `/Users/jungchul/...` 하드코딩 → 본인 머신 밖에서 못 씀
- Python 의존성 (`mcp`) 을 유저가 수동으로 설치해야 함
- 다른 유저가 설치하려면 repo clone + venv 생성 + settings.json 수동 편집 필요

이를 **Claude Code 플러그인** 으로 패키징해서:
- `/plugins` UI 한 번으로 설치
- `uv` 가 의존성 자동 관리
- 경로/환경 독립
- GitHub 마켓플레이스로 누구나 설치 가능

## 2. 확정 사항 (브레인스토밍 결과)

| 항목 | 결정 |
| --- | --- |
| 대상 | 오픈소스 공개 (GitHub 마켓플레이스) |
| 플러그인 이름 | `claude-mascot` |
| Python 의존성 | `uv` 로 관리 (`uv run`) |
| v1 스코프 | Nabi (tsundere cat) 한 캐릭터만, 구조는 확장 가능 |
| Display backend | tmux-only (README 에 requirement 명시) |
| 커스터마이즈 | `character`, `language`, `paneHeight`, `stopHookEnabled`, `startupEmotion` |
| 언어 | 한국어 + 영어 번들 (`language` 옵션으로 선택) |
| 라이센스 | MIT |
| 최초 버전 | `0.1.0` |

## 3. 레포 레이아웃

```
claude-mascot/
├── .claude-plugin/
│   ├── plugin.json              # 메타데이터 + userConfig 스키마
│   └── marketplace.json         # single-plugin marketplace 매니페스트
├── hooks/
│   └── hooks.json               # 4개 훅 정의
├── mcp_server/
│   ├── __init__.py
│   ├── server.py                # MCP 서버 엔트리 (show_character, list_emotions)
│   ├── pane.py                  # tmux pane 관리 (_update_tmux_pane, _kill_orphan…)
│   ├── display.py               # 캐릭터 중립 애니메이터
│   ├── inline.py                # PostToolUse 용 인라인 ASCII
│   ├── character.py             # 캐릭터 로더 (character.json 파싱)
│   └── hooks/
│       ├── session_start.py
│       ├── session_end.py
│       └── on_stop.py
├── characters/
│   └── nabi/                    # v1 번들 캐릭터
│       ├── character.json
│       ├── art.py
│       ├── messages.ko.json
│       ├── messages.en.json
│       ├── emotion_rules.json
│       └── ascii/
│           ├── neutral.txt
│           ├── happy.txt
│           ├── angry.txt
│           ├── shy.txt
│           ├── sad.txt
│           ├── surprised.txt
│           └── love.txt
├── pyproject.toml
├── LICENSE                      # MIT
├── README.md
└── CHANGELOG.md
```

**핵심 원칙**:

- 캐릭터는 `characters/<id>/` 디렉토리 단위로 파일시스템 기반 발견
- `mcp_server/` 코드는 캐릭터 중립 — 활성 캐릭터 ID 를 env var 로 받아 해당 디렉토리에서 art/messages 로드
- 훅/MCP 서버 경로는 모두 `${CLAUDE_PLUGIN_ROOT}` 기준

## 4. 플러그인 매니페스트

### `.claude-plugin/plugin.json`

```json
{
  "name": "claude-mascot",
  "version": "0.1.0",
  "description": "A tsundere cat mascot (and friends) reacting to Claude Code activity in a tmux pane",
  "author": { "name": "<TBD>", "url": "https://github.com/<owner>" },
  "license": "MIT",
  "requirements": {
    "claudeCode": ">=1.0.0",
    "externalTools": ["tmux", "uv"]
  },
  "userConfig": {
    "character": {
      "type": "string",
      "description": "Which mascot character to display",
      "default": "nabi",
      "enum": ["nabi"]
    },
    "language": {
      "type": "string",
      "description": "Message language",
      "default": "ko",
      "enum": ["ko", "en"]
    },
    "paneHeight": {
      "type": "number",
      "description": "Height of the tmux pane in rows",
      "default": 14,
      "minimum": 8,
      "maximum": 30
    },
    "stopHookEnabled": {
      "type": "boolean",
      "description": "Auto-update mascot emotion at end of each Claude response",
      "default": true
    },
    "startupEmotion": {
      "type": "string",
      "description": "Emotion shown when a new session starts",
      "default": "happy",
      "enum": ["neutral","happy","angry","shy","sad","surprised","love"]
    }
  }
}
```

### 설정 읽는 방식

Claude Code 가 훅/MCP 서버 실행 시 userConfig 값을 env var 로 주입:
- `CLAUDE_PLUGIN_USERCONFIG_CHARACTER`
- `CLAUDE_PLUGIN_USERCONFIG_LANGUAGE`
- `CLAUDE_PLUGIN_USERCONFIG_PANEHEIGHT`
- 등등

스크립트에서:
```python
character = os.environ.get("CLAUDE_PLUGIN_USERCONFIG_CHARACTER", "nabi")
language  = os.environ.get("CLAUDE_PLUGIN_USERCONFIG_LANGUAGE", "ko")
```

## 5. MCP 서버 Bootstrap (uv)

### `pyproject.toml`

```toml
[project]
name = "claude-mascot"
version = "0.1.0"
description = "Tsundere cat mascot for Claude Code"
requires-python = ">=3.10"
dependencies = ["mcp>=1.0"]

[project.scripts]
claude-mascot-server = "mcp_server.server:main"
```

### 플러그인 내부 `.mcp.json`

```json
{
  "mcpServers": {
    "claude-mascot": {
      "type": "stdio",
      "command": "uv",
      "args": [
        "run",
        "--directory", "${CLAUDE_PLUGIN_ROOT}",
        "python", "-m", "mcp_server.server"
      ]
    }
  }
}
```

**동작 흐름**:
1. 유저가 `/plugins` 로 설치 → Claude Code 가 `.mcp.json` 파싱
2. 세션 시작 시 `uv run ...` 자동 실행
3. 첫 실행: `uv` 가 isolated venv 생성 + `mcp` 설치 (수 초)
4. 이후: 캐시돼서 즉시 기동
5. MCP 툴 노출:
   - `mcp__claude-mascot__show_character(emotion, message)`
   - `mcp__claude-mascot__list_emotions()`

## 6. 훅

### `hooks/hooks.json`

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [{
          "type": "command",
          "command": "uv run --directory ${CLAUDE_PLUGIN_ROOT} python -m mcp_server.hooks.session_start"
        }]
      }
    ],
    "SessionEnd": [
      {
        "hooks": [{
          "type": "command",
          "command": "uv run --directory ${CLAUDE_PLUGIN_ROOT} python -m mcp_server.hooks.session_end"
        }]
      }
    ],
    "Stop": [
      {
        "hooks": [{
          "type": "command",
          "async": true,
          "command": "uv run --directory ${CLAUDE_PLUGIN_ROOT} python -m mcp_server.hooks.on_stop"
        }]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "mcp__claude-mascot__show_character",
        "hooks": [{
          "type": "command",
          "command": "uv run --directory ${CLAUDE_PLUGIN_ROOT} python -m mcp_server.inline"
        }]
      }
    ]
  }
}
```

### 훅별 동작 요약

| 훅 | source/reason 별 분기 | 주 동작 |
| --- | --- | --- |
| SessionStart | `startup`/`resume`/`clear` → 감정 매핑, `compact` → no-op | tmux pane 열기 (userConfig.startupEmotion) |
| SessionEnd | 모든 reason | 현재 tmux 세션의 나비 pane kill |
| Stop | userConfig.stopHookEnabled=false 면 즉시 return | transcript 마지막 assistant 메시지 키워드 분석 → pane 감정/대사 갱신 |
| PostToolUse (show_character matcher) | — | 채팅 라인에 ASCII 아트 인라인 출력 |

## 7. 캐릭터 디렉토리 구조

### `characters/nabi/character.json`

```json
{
  "id": "nabi",
  "displayName": "Nabi (츤데레 고양이)",
  "license": "MIT",
  "supportedEmotions": ["neutral","happy","angry","shy","sad","surprised","love"],
  "defaultLanguage": "ko",
  "supportedLanguages": ["ko","en"]
}
```

**언어 결정 우선순위** (높은 것부터):
1. `userConfig.language` (유저가 명시적으로 선택한 값)
2. `character.defaultLanguage` (캐릭터 기본 언어, userConfig 언어가 `supportedLanguages` 에 없을 때 fallback)
3. 하드코딩 기본값 `"ko"` (character.json 로드 실패 시 최종 fallback)

예: 유저가 `language="ja"` 설정했는데 nabi 가 `["ko","en"]` 만 지원하면 → `ko` 로 fallback, 디버그 로그에 경고 기록.

### `characters/nabi/messages.<lang>.json`

감정별 tsundere 스타일 메시지 풀. `on_stop.py` 가 감정 결정 후 pool 에서 랜덤 선택.

```json
{
  "happy": ["흥, 이 정도는 기본이라냥.", "..."],
  "sad":   ["으... 이거 안 풀리네냥...", "..."],
  "angry": ["...", "..."],
  "shy":   ["...", "..."],
  "surprised": ["...", "..."],
  "love":  ["...", "..."],
  "neutral": ["...", "..."]
}
```

### `characters/nabi/emotion_rules.json`

현재 `on_stop.py` 에 하드코딩된 regex 를 JSON 으로 외부화:

```json
{
  "priority": ["angry","happy","sad","shy","surprised"],
  "patterns": {
    "angry": "(틀렸|잘못\\s*됐|같은\\s*실수|wrong\\b|mistake)",
    "happy": "(완료|성공|잘\\s*됐|done\\b|works?\\b|passed|fixed|해결(?!\\s*안))",
    "sad":   "(에러|실패|fail(?:ed|ure)?|error|broken|안\\s*되)",
    "shy":   "(감사|고마|thank|칭찬|잘했)",
    "surprised": "(\\?!|어\\?|왜\\?|이상한데|wait\\b|갑자기|헉)"
  }
}
```

### `characters/nabi/art.py`

기존 `nabi_display.py` 의 `EMOTIONS` dict 와 `render()` 함수를 캐릭터별 모듈로 추출.

`mcp_server/display.py` 가 `importlib` 로 `characters.<id>.art` 를 동적 로드.

### `characters/nabi/ascii/*.txt`

PostToolUse 훅의 `inline.py` 가 사용하는 정적 ASCII. 기존 `characters/tsundere_cat/ascii/` 내용을 그대로 이전.

## 8. 배포

### Single-plugin marketplace (v1 방식)

`claude-mascot` repo 루트에 `.claude-plugin/marketplace.json`:

```json
{
  "name": "claude-mascot-marketplace",
  "owner": { "name": "<owner>", "url": "https://github.com/<owner>" },
  "plugins": [{ "name": "claude-mascot", "source": "./" }]
}
```

유저 설치 흐름:
1. `~/.claude/settings.json` 에 `extraKnownMarketplaces` 로 `github:<owner>/claude-mascot` 추가
2. `/plugins` UI 에서 `claude-mascot@claude-mascot-marketplace` 설치
3. 완료

### 버전 관리

- SemVer, v1 = `0.1.0` (pre-stable)
- git tag 와 `plugin.json.version` 동기화
- `CHANGELOG.md` 는 Keep a Changelog 포맷

### README 필수 섹션

- Hero screenshot/gif (tmux pane 녹화)
- 요구사항: macOS/Linux, tmux, uv
- 3줄 설치 가이드
- userConfig 레퍼런스 표
- 감정 트리거 키워드 표
- 트러블슈팅 (`/tmp/nabi_debug.log` 확인)
- 기여 가이드 (새 캐릭터 추가법)

## 9. 검증 계획

| 검증 항목 | 방법 | 통과 기준 |
| --- | --- | --- |
| plugin.json 유효성 | JSON schema 검증 | exit 0 |
| MCP 서버 부팅 | `uv run --directory <plugin_root> python -m mcp_server.server` 직접 실행 후 stdio 응답 확인 | `initialize` 응답 수신 |
| 훅 4종 발화 | 각 이벤트 stdin payload mock → 파이프 실행 | 각 훅 exit 0, 디버그 로그 기록 |
| 다중 tmux 세션 안전 | 세션 A/B 각각 claude 기동, 상호간섭 체크 | 서로의 pane 안 죽임 |
| userConfig 오버라이드 | `CLAUDE_PLUGIN_USERCONFIG_PANEHEIGHT=20` 주입 후 실행 | pane 높이 20 반영 |
| `stopHookEnabled=false` | env var 주입 후 Stop 훅 실행 | pane 변화 없음 |
| 언어 전환 | `CLAUDE_PLUGIN_USERCONFIG_LANGUAGE=en` 주입 | 영어 메시지 출력 |
| End-to-end 설치 | 깨끗한 macOS 계정에서 `brew install uv tmux` → `/plugins` 설치 → 새 탭에서 Claude 기동 | 나비 pane 자동 표시, 4개 훅 전부 동작 |

## 10. 비목표 (Out of Scope for v1)

- 외부 캐릭터 플러그인 생태계 (v3+ 고려)
- tmux 외 display backend (GNU Screen, Zellij, inline-only 등)
- 감정-키워드 매핑 유저 오버라이드 (character 내부에 하드코딩)
- LLM 기반 감정 판단 (Stop 에서 Haiku 호출 등)
- Windows 지원 (WSL 은 가능하지만 native cmd/powershell 은 제외)
- 캐릭터 간 대화/상호작용

## 11. 유저(=작성자) 가 구현 전에 확정해야 할 것

spec 내에 `<TBD>` 또는 `<owner>` 로 비워둔 placeholder —

- `plugin.json.author.name` / `plugin.json.author.url` — 플러그인 작성자 정보 (예: `"jungchul"`, `"https://github.com/jungchul"`)
- `marketplace.json.owner` — 마켓플레이스 owner (같은 값일 가능성 높음)
- GitHub repo 경로 (`github:<owner>/claude-mascot`)

이 값들은 구현 계획에서 "셋업" 태스크에 포함해서 첫 커밋 때 반영.

## 12. 의존성 및 리스크

**외부 의존**:
- `uv` >= 0.4 — 유저가 설치해야 함. `brew install uv` 로 간단.
- `tmux` >= 3.0 — 거의 모든 \*nix 기본 설치
- Claude Code >= 1.0 — 플러그인 시스템 필요

**리스크**:
- `uv` 미설치 유저 (Windows native 에서 빈번) → README 에 명확히 명시, 설치 링크 제공
- `${CLAUDE_PLUGIN_ROOT}` env var 동작이 Claude Code 버전에 따라 다를 가능성 → 최소 버전 명시
- Tool deferral 로 인해 `show_character` 가 매 턴 자동 호출 안 됨 (기존 한계 그대로) — README FAQ 에 Stop 훅이 이를 보완하는 메커니즘 설명
