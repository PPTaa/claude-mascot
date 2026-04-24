"""Nabi character art — frames and renderer."""

RENDERER = "programmatic"

# ── Colors ──
O  = "\033[38;5;208m"    # orange
W  = "\033[97m"          # white
PK = "\033[38;5;213m"    # pink
RD = "\033[38;5;196m"    # red
YL = "\033[38;5;220m"    # yellow
CN = "\033[38;5;117m"    # cyan
GY = "\033[38;5;245m"    # gray
BL = "\033[38;5;75m"     # blue
X  = "\033[0m"           # reset

# ── 감정별 설정 ──
EMOTIONS = {
    "neutral": dict(
        pose="relaxed", bc=O, fc=W, eyes="- -", alt_eyes="_ _",
        msg="흥... 뭐야, 볼일 있어?",
        decos=["", f" {GY}·{X}", "", f" {GY}·{X}"],
        sp_eyes="= =", sp_msg="하아암~... 졸린 거 아니야",
    ),
    "happy": dict(
        pose="perky", bc=O, fc=YL, eyes="^ ^", alt_eyes="^ ^",
        msg="후훗... 기분 좋은 건 아니라구!",
        decos=[f" {YL}♪{X}", f" {YL}♫{X}", f" {YL}♪{X}", ""],
        sp_eyes="* *", sp_msg="♪ 라라라~ 냥~",
    ),
    "angry": dict(
        pose="arched", bc=RD, fc=YL, eyes="> <", alt_eyes="> <",
        msg="!! 화났다냥!!",
        decos=[f" {RD}!{X}", f" {RD}!!{X}", f" {RD}!{X}", ""],
        sp_eyes="> <", sp_msg="으르르르...!!!",
    ),
    "shy": dict(
        pose="crouching", bc=O, fc=PK, eyes="u u", alt_eyes="> <",
        msg="그, 그런 말 하지 마...",
        decos=[f" {PK}*{X}", f" {PK}**{X}", f" {PK}*{X}", ""],
        sp_eyes="- -", sp_msg="뭐, 뭐야... 가까이 오지 마",
    ),
    "sad": dict(
        pose="lying", bc=BL, fc=CN, eyes="; ;", alt_eyes="T T",
        msg="...별로 슬프지 않거든...",
        decos=["", f" {BL}.{X}", f" {BL}.{X}", ""],
        sp_eyes="T T", sp_msg="...흑",
    ),
    "surprised": dict(
        pose="alert", bc=O, fc=YL, eyes="O O", alt_eyes="o o",
        msg="냐?! 뭐야 갑자기?!",
        decos=[f" {YL}?{X}", f" {YL}!{X}", f" {YL}?!{X}", ""],
        sp_eyes="@ @", sp_msg="냐아아아?!!",
    ),
    "love": dict(
        pose="relaxed", bc=PK, fc=RD, eyes="♡ ♡", alt_eyes="♡ ♡",
        msg="좋, 좋아하는 거 아니거든!",
        decos=[f" {RD}♥{X}", f" {PK}♥{X}", f" {RD}♥{X}", f" {PK}♥{X}"],
        sp_eyes="♡ ♡", sp_msg="그냥... 할 일이 없어서...",
    ),
}


def render(cfg, eyes, msg, deco, tail_t, shake=0):
    """감정별 포즈로 한 프레임 렌더링 → 13줄 리스트"""
    bc, fc = cfg["bc"], cfg["fc"]
    s = " " * shake
    pose = cfg.get("pose", "relaxed")
    q4 = '""""'
    face = f"{s}  {bc}){fc}{eyes}{bc} '._.-{q4}-."

    # ── 하체 (공통) ──
    lower = [
        f'{s}   {bc}`"`\\       /    /{X}',
        f'{s}       {bc}|    \\ |   /{X}',
        f'{s}        {bc}\\   /- \\  \\{X}',
        f'{s}        {bc}|| |  // /`{X}',
        f'{s}        {bc}((_| ((_/{X}',
    ]

    # ── 완전 다른 자세 ──
    if pose == "arched":
        # 정면 아치 자세 (angry) - 등 세우고 위협
        return [
            '',
            f'{s}      {bc}|\\   /|{X}',
            f'{s}      {bc}| \\_/ |{X}{deco}',
            f'{s}      {bc}) {fc}{eyes}{bc} ({X}',
            f'{s}     {bc}/  _Y_  \\{X}',
            f'{s}    {bc}|  /   \\  |{X}',
            f'{s}    {bc}| |     | |{X}',
            f'{s}     {bc}\\|     |/{X}',
            f'{s}     {bc}||     ||{X}',
            f'{s}    {bc}(__)   (__){X}',
            '',
            f'  {GY}{msg}{X}',
            '',
        ]
    elif pose == "lying":
        # 누워있는 자세 (sad) - 축 늘어짐
        tip = "~_"[tail_t % 2]
        return [
            '',
            '',
            '',
            f'{s}       {bc}|\\_/|{X}{deco}',
            f"{s}  {bc}____){fc}{eyes}{bc}  '.______{X}",
            f'{s} {bc}/ =Y_=            /{tip}{X}',
            f'{s} {bc}|  `"`            |{X}',
            f'{s}  {bc}\\________________/{X}',
            f'{s}      {bc}||       ||{X}',
            f'{s}     {bc}(__)     (__){X}',
            '',
            f'  {GY}{msg}{X}',
            '',
        ]

    # ── 서있는 자세 변형 ──
    elif pose == "perky":
        # 꼬리 쫑긋 위로 (happy)
        tip = ",'"[tail_t % 2]
        upper = [
            f'{s}                    {bc}{tip}{X}',
            f'{s}                    {bc}|{X}',
            f'{s}  {bc}|\\_/|{X}             {bc}|{X}{deco}',
            face + f"  |{X}",
            f'{s} {bc}=\\Y_= /          \\/{X}',
        ]
    elif pose == "crouching":
        # 웅크림, 꼬리 몸에 감싸기 (shy)
        upper = [
            '',
            '',
            f'{s}  {bc}|\\_/|{X}{deco}',
            face + f"{X}",
            f'{s} {bc}=\\Y_= /          \\{X}',
        ]
        lower = [
            f'{s}   {bc}`"`\\       /    |{X}',
            f'{s}       {bc}|    \\ |    |~{X}',
            f'{s}        {bc}\\   /- \\  \\{X}',
            f'{s}        {bc}|| |  // /`{X}',
            f'{s}        {bc}((_| ((_/{X}',
        ]
    elif pose == "alert":
        # 꼬리 곤두섬 (surprised)
        tip_art = "\\|/" if tail_t % 2 == 0 else " ! "
        upper = [
            f'{s}                   {bc}{tip_art}{X}',
            f'{s}                    {bc}|{X}',
            f'{s}  {bc}|\\_/|{X}             {bc}|{X}{deco}',
            face + f"  |{X}",
            f'{s} {bc}=\\Y_= /          \\/{X}',
        ]
    else:
        # relaxed: 기본 자세, 꼬리 위로 감김 (neutral, love)
        tip = "_~"[tail_t % 2]
        upper = [
            f'{s}                    {bc}{tip}{X}',
            f'{s}                    {bc}\\\\{X}',
            f'{s}  {bc}|\\_/|{X}              {bc}||{X}{deco}',
            face + f"  //{X}",
            f'{s} {bc}=\\Y_= /          \\//{X}',
        ]

    return upper + lower + ['', f'  {GY}{msg}{X}', '']
