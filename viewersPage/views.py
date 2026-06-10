# Create your views here.

"""
viewersPage/views.py
실제 유저가 보는 HTML 페이지 뷰
- 각 페이지의 비즈니스 로직 + 템플릿 렌더
- 로그인 필요 여부 데코레이터로 구분
"""
import json
from django.core.paginator import Paginator

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from api.models import Idol, Card, PlayerDeck, MemoryCard, DeckLike
from api.identix.models import DuelRecord
from api.identix.duel_logic import (
    get_idol_tier_list, get_card_stats_by_idol,
    get_recent_duels, get_duel_search
)


# # ── 메인 페이지 ──────────────────────────────
# def main_page(request):
#     top_idols = get_idol_tier_list()[:10]
#     context = {
#         'top_idols': top_idols,
#         'stats': {'total_duels': ..., 'total_idols': ..., 'total_cards': ...},
#         'chart_labels': json.dumps([i.name for i in top_idols[:5]]),
#         'chart_win_rates': json.dumps([i.win_rate for i in top_idols[:5]]),
#         'chart_pick_rates': json.dumps([i.pick_rate for i in top_idols[:5]]),
#         'top_combos': [],  # 추후 duel_logic.py에서 구현
#     }
#     """/ - 메인: 상위 아이돌 + 최근 대전 요약"""
#     top_idols = get_idol_tier_list()[:10]
#     recent_duels = get_recent_duels(5)
#     return render(request, 'main_index.html', {
#         'top_idols':    top_idols,
#         'recent_duels': recent_duels,
#     })

def main_page(request):
    """
    GET /
    상위 아이돌 바 차트 + 최근 대전 + 조합 통계 요약
    """
    top_idols    = get_idol_tier_list()[:10]
    recent_duels = get_recent_duels(5)

    # Chart.js 에 넘길 JSON (템플릿에서 |safe 로 출력)
    chart_idols = top_idols[:6]
    context = {
        'top_idols':         top_idols,
        'recent_duels':      recent_duels,
        'top_combos':        [],          # 추후 duel_logic.py에서 구현
        'chart_labels':      json.dumps([i.name      for i in chart_idols]),
        'chart_win_rates':   json.dumps([i.win_rate  for i in chart_idols]),
        'chart_pick_rates':  json.dumps([i.pick_rate for i in chart_idols]),
        'stats': {
            'total_duels': DuelRecord.objects.count(),
            'total_idols': Idol.objects.count(),
            'total_cards': Card.objects.count(),
        },
    }
    return render(request, 'main_index.html', context)



# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 카드 일람
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def card_list(request):
    """GET /card/"""
    cards  = Card.objects.select_related('idol').order_by('idol', 'card_level', 'card_id')
    idols  = Idol.objects.all()
    return render(request, 'card_list.html', {
        'cards':       cards,
        'idols':       idols,
        'total_cards': cards.count(),
    })


# ── 덱 빌더 (로그인 필수) ──────────────────
@login_required
def my_decks(request):
    """GET /deck/"""
    decks = (PlayerDeck.objects
             .filter(owner=request.user)
             .prefetch_related('cards', 'memory_cards', 'idol')
             .order_by('-updated_at'))
    return render(request, 'my_deck.html', {'decks': decks})

@login_required
def deck_new(request):
    """GET /deck/new/  — 캐릭터 9명 중 3명 선택 화면"""
    idols = Idol.objects.all()[:9]
    return render(request, 'deck_new.html', {'idols': idols})

@login_required
def deck_edit_new(request):
    """
    GET /deck/edit/?idols=idol_01,idol_02,idol_03
    신규 덱 카드 편집 화면 — deck=None
    """
    idol_ids_str = request.GET.get('idols', '')
    idol_ids     = [i.strip() for i in idol_ids_str.split(',') if i.strip()]
    if len(idol_ids) != 3:
        messages.error(request, '캐릭터를 정확히 3명 선택해주세요.')
        return redirect('ViewersPage:deck_new')

    selected_idols = list(Idol.objects.filter(idol_id__in=idol_ids)
                          .prefetch_related('cards'))
    memory_cards   = MemoryCard.objects.all()
    return render(request, 'deck_edit.html', {
        'selected_idols': selected_idols,
        'memory_cards':   memory_cards,
        'idol_ids':       idol_ids_str,
        'deck':           None,
    })


@login_required
def deck_edit(request, deck_id):
    """GET /deck/<id>/edit/  — 기존 덱 편집 화면"""
    deck = get_object_or_404(PlayerDeck, id=deck_id, owner=request.user)
    idol_ids_str   = request.GET.get('idols') or (deck.idol.idol_id if deck.idol else '')
    selected_idols = list(Idol.objects.filter(idol_id__in=idol_ids_str.split(','))
                          .prefetch_related('cards'))
    memory_cards   = MemoryCard.objects.all()
    return render(request, 'deck_edit.html', {
        'selected_idols': selected_idols,
        'memory_cards':   memory_cards,
        'idol_ids':       idol_ids_str,
        'deck':           deck,
    })


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 덱 저장
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@login_required
def deck_save(request):
    """POST /deck/save/"""
    if request.method != 'POST':
        return redirect('ViewersPage:deck_list')

    deck_id   = request.POST.get('deck_id')   # 기존 덱이면 id 존재
    name      = request.POST.get('name', '').strip()
    idol_ids  = request.POST.get('idol_ids', '')
    card_ids  = [c for c in request.POST.get('selected_cards', '').split(',') if c]
    mem_ids   = [m for m in request.POST.get('selected_memories', '').split(',') if m]
    desc      = request.POST.get('description', '')
    is_public = request.POST.get('is_public') == 'on'

    # 유효성 검사
    if not name:
        messages.error(request, '덱 이름을 입력해주세요.')
        return redirect('ViewersPage:deck_list')
    if len(card_ids) != 18:
        messages.error(request, f'메인 카드는 정확히 18장이어야 합니다. (현재 {len(card_ids)}장)')
        return redirect('ViewersPage:deck_list')
    if len(mem_ids) != 3:
        messages.error(request, f'메모리 카드는 정확히 3장이어야 합니다. (현재 {len(mem_ids)}장)')
        return redirect('ViewersPage:deck_list')

    # 대표 아이돌: idol_ids 첫 번째
    first_idol_id = idol_ids.split(',')[0].strip()
    idol = Idol.objects.filter(idol_id=first_idol_id).first()

    cards   = Card.objects.filter(card_id__in=card_ids)
    memories = MemoryCard.objects.filter(memory_id__in=mem_ids)

    if deck_id:
        deck = get_object_or_404(PlayerDeck, id=deck_id, owner=request.user)
        deck.name        = name
        deck.idol        = idol
        deck.description = desc
        deck.is_public   = is_public
        deck.save()
        deck.cards.set(cards)
        deck.memory_cards.set(memories)
        messages.success(request, f'덱 "{name}"이 수정되었습니다.')
    else:
        deck = PlayerDeck.objects.create(
            owner=request.user, name=name, idol=idol,
            description=desc, is_public=is_public
        )
        deck.cards.set(cards)
        deck.memory_cards.set(memories)
        messages.success(request, f'덱 "{name}"이 저장되었습니다.')

    return redirect('ViewersPage:deck_list')


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 공개/비공개 토글
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@login_required
def deck_toggle_public(request, deck_id):
    """POST /deck/<id>/toggle-public/"""
    deck = get_object_or_404(PlayerDeck, id=deck_id, owner=request.user)
    deck.is_public = not deck.is_public
    deck.save(update_fields=['is_public'])
    status = '공개' if deck.is_public else '비공개'
    messages.success(request, f'덱 "{deck.name}"이 {status}로 변경되었습니다.')
    return redirect('ViewersPage:deck_list')

# 덱 삭제 기능

@login_required
def deck_delete(request, deck_id):
    deck = get_object_or_404(PlayerDeck, id=deck_id, owner=request.user)
    if request.method == 'POST':
        name = deck.name
        deck.delete()
        messages.success(request, f'덱 "{name}"이 삭제되었습니다.')
    return redirect('ViewersPage:deck_list')


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 덱 일람 (공개 덱 목록)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def decklist(request):
    """GET /decklist/"""
    sort = request.GET.get('sort', 'like')
    sort_map = {
        'like':    '-like_count',
        'new':     '-created_at',
        'comment': '-comment_count',
    }
    order = sort_map.get(sort, '-like_count')

    qs = (PlayerDeck.objects
          .filter(is_public=True)
          .select_related('owner', 'idol')
          .prefetch_related('comments')
          .order_by(order))

    paginator = Paginator(qs, 20)  # 페이지당 20개
    page_obj  = paginator.get_page(request.GET.get('page', 1))

    return render(request, 'deck_list.html', {
        'page_obj': page_obj,
        'sort':     sort,
    })




# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 통계
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def statistics(request):
    """GET /statistics/"""
    idols        = Idol.objects.all()
    sorted_idols = sorted(idols, key=lambda i: i.pick_rate, reverse=True)
    total_duels  = DuelRecord.objects.count()

    context = {
        'idols':           sorted_idols,
        'total_duels':     total_duels,
        'chart_labels':    json.dumps([i.name      for i in sorted_idols]),
        'chart_win_rates': json.dumps([i.win_rate  for i in sorted_idols]),
        'chart_pick_rates':json.dumps([i.pick_rate for i in sorted_idols]),
    }
    return render(request, 'statistics.html', context)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 대전 기록
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def duel_archive(request):
    """GET /duel/"""
    from django.db.models import Q
    query        = request.GET.get('q', '')
    selected_idol = request.GET.get('idol', '')

    qs = (DuelRecord.objects
          .prefetch_related('idol_slots__idol')
          .order_by('-played_at'))

    if query:
        qs = qs.filter(Q(player1_name__icontains=query) | Q(player2_name__icontains=query))
    if selected_idol:
        qs = qs.filter(idol_slots__idol__idol_id=selected_idol, idol_slots__slot_type='pick')

    paginator   = Paginator(qs, 20)
    page_obj    = paginator.get_page(request.GET.get('page', 1))
    page_offset = (page_obj.number - 1) * 20

    return render(request, 'duel_archive.html', {
        'page_obj':      page_obj,
        'query':         query,
        'selected_idol': selected_idol,
        'idols':         Idol.objects.all(),
        'page_offset':   page_offset,
    })

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 인증 — 회원가입 / 로그인 / 로그아웃
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def signup_view(request):
    """
    GET  /auth/signup/ — 회원가입 폼 표시
    POST /auth/signup/ — 유효성 검사 후 계정 생성 + 자동 로그인
    """
    # 이미 로그인된 경우 메인으로
    if request.user.is_authenticated:
        return redirect('viewersPage:main')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        confirm  = request.POST.get('confirm', '')

        # ── 유효성 검사 (순서대로 체크) ──
        error = None
        if not username or not password:
            error = 'ID와 비밀번호를 입력해주세요.'
        elif len(username) < 3:
            error = '아이디는 3자 이상이어야 합니다.'
        elif len(username) > 20:
            error = '아이디는 20자 이하이어야 합니다.'
        elif not username.isalnum():
            error = '아이디는 영문자와 숫자만 사용할 수 있습니다.'
        elif password != confirm:
            error = '비밀번호가 일치하지 않습니다.'
        elif len(password) < 8:
            error = '비밀번호는 8자 이상이어야 합니다.'
        elif User.objects.filter(username=username).exists():
            error = '이미 사용 중인 아이디입니다.'

        if error:
            messages.error(request, error)
            # 입력값 보존 (비밀번호 제외)
            return render(request, 'auth_signup.html', {'username_input': username})

        # ── 계정 생성 + 자동 로그인 ──
        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        messages.success(request, f'환영합니다, {username}님! 계정이 생성되었습니다.')
        return redirect('viewersPage:main')

    return render(request, 'auth_signup.html')


def login_view(request):
    """
    GET  /auth/login/ — 로그인 폼 표시
    POST /auth/login/ — 인증 후 로그인 처리

    next 파라미터: 로그인 후 원래 요청 페이지로 리다이렉트
    ex) /auth/login/?next=/deck/create/
    """
    # 이미 로그인된 경우 메인으로
    if request.user.is_authenticated:
        return redirect('viewersPage:main')

    next_url = request.GET.get('next') or request.POST.get('next') or 'viewersPage:main'

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        # ── 기본 입력값 검사 ──
        if not username or not password:
            messages.error(request, 'ID와 비밀번호를 입력해주세요.')
            return render(request, 'auth_login.html', {
                'username_input': username,
                'next': next_url,
            })

        # ── Django 인증 ──
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # 계정이 활성화 상태인지 확인 (관리자가 비활성화 처리한 계정 차단)
            if not user.is_active:
                messages.error(request, '비활성화된 계정입니다. 관리자에게 문의하세요.')
                return render(request, 'auth_login.html', {
                    'username_input': username,
                    'next': next_url,
                })
            login(request, user)
            messages.success(request, f'{username}님, 환영합니다!')
            # next URL이 외부 도메인이면 메인으로 (오픈 리다이렉트 방지)
            if next_url.startswith('http'):
                next_url = 'viewersPage:main'
            return redirect(next_url)
        else:
            messages.error(request, '아이디 또는 비밀번호가 올바르지 않습니다.')
            return render(request, 'auth_login.html', {
                'username_input': username,
                'next': next_url,
            })

    return render(request, 'auth_login.html', {'next': next_url})


def logout_view(request):
    """
    POST /auth/logout/ — 로그아웃
    GET  요청은 메인으로 리다이렉트 (직접 URL 입력 방지)
    """
    if request.method == 'POST':
        logout(request)
        messages.info(request, '로그아웃되었습니다.')
    return redirect('viewersPage:main_page')

def idol_tier(request):
    """/idol - 전체 아이돌 승률/픽률/밴율 티어표"""
    idols = get_idol_tier_list()
    return render(request, 'god/tier.html', {'idols': idols})


def idol_detail(request, idol_id):
    """/idol/<idol_id> - 아이돌 상세 + 보유 카드"""
    idol = get_object_or_404(Idol, idol_id=idol_id)
    cards = get_card_stats_by_idol(idol_id)
    return render(request, 'god/detail.html', {'idol': idol, 'cards': cards})

# ── 대전 기록 ──────────────────────────────
def duel_list(request):
    """/duel - 대전 기록 목록 + 검색"""
    query    = request.GET.get('q', '')
    idol_id  = request.GET.get('idol', '')
    duels = get_duel_search(query, idol_id)
    idols = Idol.objects.all()
    return render(request, 'duel/archive.html', {
        'duels':  duels,
        'idols':  idols,
        'query':  query,
        'selected_idol': idol_id,
    })