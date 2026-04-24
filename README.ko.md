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

Claude Code 안에서 이 리포를 마켓플레이스로 등록한 뒤 플러그인을 설치합니다:

```
/plugin marketplace add PPTaa/claude-mascot
/plugin install claude-mascot@claude-mascot-marketplace
```

그다음 tmux 세션 안에서 `claude`를 실행하면 마스코트 팬이 하단에 자동으로 뜹니다.

## 캐릭터

플러그인은 두 가지 캐릭터를 내장합니다. `character` userConfig로 전환할 수 있어요.

| ID | 이름 | 렌더러 | 설명 |
| --- | --- | --- | --- |
| `nabi` | Nabi (츤데레 고양이) | `programmatic` | 눈 깜빡임·꼬리·데코가 있는 프로그래매틱 ANSI 아트. 기본값. |
| `fubao` | Fubao (느긋한 판다) | `frames` | CC 라이선스 판다 사진을 `chafa`로 프리렌더한 ANSI 프레임. |

`frames` 렌더러 캐릭터를 직접 추가하려면:

1. `characters/fubao/` 구조를 따라서 `character.json`(`"renderer": "frames"`), `emotion_rules.json`, `messages.<lang>.json`, `art.py`(`RENDERER = "frames"`)을 만듭니다.
2. 원본 이미지를 `characters/<name>/raw/`에 `<emotion>_<state>.{jpg,png,webp}` 형식으로 둡니다.
3. 로컬에 `chafa` 설치 (`brew install chafa` 등).
4. `uv run scripts/prerender.py <name>` 실행 — `frames/{small,medium,large}/*.txt`가 생성됩니다.
5. `.claude-plugin/plugin.json`의 `character` enum에 새 id 추가.

최종 사용자는 `chafa` 설치 불필요 — 커밋된 `frames/` 파일만으로 런타임이 동작합니다.

## 설정

모든 옵션은 `~/.claude/settings.json`의 `pluginConfigs["claude-mascot@claude-mascot-marketplace"].options` 아래에 둡니다:

| 옵션 | 타입 | 기본값 | 설명 |
| --- | --- | --- | --- |
| `character` | `"nabi" \| "fubao"` | `"nabi"` | 표시할 캐릭터 |
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

위 "캐릭터" 섹션의 빠른 레시피 참고. 두 가지 렌더러가 모두 지원됩니다:

- **`RENDERER = "programmatic"`** — `render()`가 매 틱마다 ANSI 줄을 반환 (`characters/nabi/art.py` 참고). 살아있는 ASCII 아트에 적합.
- **`RENDERER = "frames"`** — 미리 렌더된 ANSI 텍스트 파일을 런타임에 로드 (`characters/fubao/art.py` 참고). 사진/일러스트 기반 캐릭터에 적합.

`.claude-plugin/plugin.json`의 `character` enum에 새 id를 추가하고, 로컬 테스트 후 PR 올리기.

### 테스트 실행

```bash
uv run --extra dev pytest
```

## 라이선스

MIT — `LICENSE` 참고.
