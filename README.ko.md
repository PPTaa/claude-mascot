# claude-mascot

[English](README.md) · **한국어**

Claude Code의 활동에 반응하는 츤데레 고양이(와 친구들) 마스코트 — tmux 팬(pane)에서 동작합니다.

## 기능

- tmux 창 하단에 상주하는 마스코트 팬
- Claude 세션 시작 시 자동 생성 / 종료 시 자동 정리
- 매 응답 끝에 반응 업데이트:
  - **우선 경로**: Claude가 이번 턴 문맥을 반영해서 직접 `show_character` 호출 (츤데레 한 줄 생성)
  - **폴백 경로**: Claude가 호출 안 했으면 `Stop` 훅이 트랜스크립트에서 키워드 스캔 → 감정별 메시지 풀에서 랜덤 선택
- tmux 세션당 팬 하나만 유지 — 여러 터미널 탭에서 안전하게 사용 가능
- 언어 설정 가능 (한국어/영어 기본 제공)

## 요구사항

- macOS 또는 Linux
- [`tmux`](https://github.com/tmux/tmux) ≥ 3.0 (필수 — claude-mascot은 tmux 전용)
- [`uv`](https://docs.astral.sh/uv/) ≥ 0.4 (Python venv 자동 관리)
- Claude Code ≥ 1.0

사전 설치:

```bash
# macOS (Homebrew)
brew install tmux uv

# Linux (Ubuntu 예시)
sudo apt install tmux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## 설치

Claude Code에서 이 리포를 마켓플레이스로 추가하고 플러그인 설치:

```
/plugins marketplace add github:PPTaa/claude-mascot
/plugins install claude-mascot@claude-mascot-marketplace
```

tmux 세션 안에서 `claude`를 띄우면 마스코트 팬이 자동으로 뜹니다.

## 설정

모든 옵션은 `~/.claude/settings.json`의 `pluginConfigs["claude-mascot@claude-mascot-marketplace"].options` 아래에 둡니다:

| 옵션 | 타입 | 기본값 | 설명 |
| --- | --- | --- | --- |
| `character` | string | `"nabi"` | 표시할 캐릭터 (현재는 `nabi`만) |
| `language` | `"ko" \| "en"` | `"ko"` | 메시지 언어 |
| `paneHeight` | number (8–30) | `14` | tmux 팬 높이 (행 수) |
| `stopHookEnabled` | boolean | `true` | 응답 끝마다 실행되는 트랜스크립트 스캔 폴백 활성화 |
| `startupEmotion` | emotion enum | `"happy"` | 새 세션 시작 시 첫 감정 |

예시:

```json
{
  "pluginConfigs": {
    "claude-mascot@claude-mascot-marketplace": {
      "options": {
        "language": "ko",
        "paneHeight": 16,
        "startupEmotion": "neutral"
      }
    }
  }
}
```

## 반응 결정 흐름

매 턴마다 팬은 정확히 한 번 업데이트됩니다:

1. Claude가 턴 안에서 `show_character(emotion, message)`를 호출했다면, 세션 단위 마커 파일이 생성되고 그 메시지가 팬에 유지됩니다. `Stop` 훅은 마커를 보고 폴백을 건너뜁니다.
2. 호출 안 했다면, `Stop` 훅이 트랜스크립트의 마지막 user 메시지 + assistant 메시지를 둘 다 읽어서 regex 분류 → `characters/<id>/messages.<lang>.json`의 해당 감정 풀에서 랜덤 한 줄을 고릅니다.

### 감정 트리거 키워드 (폴백 경로)

| 감정 | 대표 키워드 |
| --- | --- |
| angry | 틀렸, 잘못 됐, wrong, mistake, 뒤질, 짜증, 바보, 멍청, angry, shut up |
| happy | 완료, 성공, 해결, done, passed, fixed |
| sad | 에러, 실패, error, failed, broken |
| shy | 감사, 고마, thank, 칭찬, 잘했 |
| surprised | ?!, 어?, wait, 갑자기 |
| neutral | (아무것도 매칭 안 될 때) |

정확한 패턴은 `characters/nabi/emotion_rules.json` 참고.

## 트러블슈팅

- **팬이 안 뜸** — tmux 세션 안에서 `claude`를 띄웠는지 확인. `echo $TMUX`가 비어있지 않아야 함.
- **MCP 로그에 Python 에러** — `uv`가 설치되어 있고 PATH에 있는지 확인. `uv --version`으로 체크.
- **훅 디버그 로그** — `/tmp/claude_mascot_debug.log`에 훅 호출 타임스탬프가 찍힙니다. `skipped: claude already called show_character this turn` 로그는 마커 경로가 동작한 것, `character=… emotion=… user_len=… assistant_len=…` 로그는 폴백이 실행된 것.
- **플러그인 코드 수정 후 반응이 변화 없음** — MCP 서버는 장시간 실행되는 프로세스예요. `/mcp` → `claude-mascot` reconnect 하거나 Claude Code 재시작 필요.
- **여러 탭에서 충돌** — tmux 세션마다 독립적인 팬을 가지며, 다른 세션의 팬은 건드리지 않습니다.

## 기여

### 새 캐릭터 추가

1. `characters/<id>/` 생성, 안에 넣을 것:
   - `character.json` (id, displayName, supportedEmotions, supportedLanguages, defaultLanguage)
   - `art.py` (`EMOTIONS` dict + `render()` — `characters/nabi/art.py` 시그니처 준수)
   - `messages.<lang>.json` (지원 언어별)
   - `emotion_rules.json` (priority + regex 패턴)
   - `ascii/<emotion>.txt` (감정별)
2. 기본 캐릭터를 본인 id로 바꾸고 싶으면 `.claude-plugin/plugin.json`의 `character` 기본값을 수정 (자유 문자열 필드라 enum 수정 필요 없음).
3. 로컬 테스트 후 PR 올리기.

### 테스트 실행

```bash
uv run --extra dev pytest
```

## 라이선스

MIT — `LICENSE` 참고.
