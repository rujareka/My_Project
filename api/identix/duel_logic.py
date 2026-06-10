"""
api/identix/duel_logic.py
Django ORM 집계 - 통계 쿼리 모음
FuruGG 참고 방식과 동일하게 ORM annotate/aggregate 사용
"""
from django.db.models import Count, Q, F, FloatField, ExpressionWrapper
from api.models import Idol, Card
from api.identix.models import DuelRecord, DuelIdolSlot


def get_idol_tier_list():
    """
    아이돌 티어 리스트 반환
    승률 내림차순 정렬 (FuruGG의 god 티어 페이지 동일 방식)
    """
    return Idol.objects.all().order_by('-win_count')


def get_card_stats_by_idol(idol_id: str = None):
    """
    카드 통계 - 아이돌별 필터 가능
    pick_rate 내림차순
    """
    qs = Card.objects.select_related('idol')
    if idol_id:
        qs = qs.filter(idol__idol_id=idol_id)
    return qs.order_by('-include_count')


def get_partner_stats():
    """
    아이돌 2인 조합(파트너) 통계
    같은 게임에 함께 픽된 조합을 집계
    (추후 구현 - DuelIdolSlot 기반 조합 카운팅)
    """
    # TODO: 같은 duel에서 동일 player의 픽 조합 집계
    raise NotImplementedError


def get_recent_duels(limit: int = 20):
    """최근 대전 기록 조회"""
    return (DuelRecord.objects
            .prefetch_related('idol_slots__idol', 'card_slots__card')
            .order_by('-played_at')[:limit])


def get_duel_search(query: str = '', idol_id: str = ''):
    """
    대전기록 검색
    - query: 플레이어 이름 검색
    - idol_id: 특정 아이돌이 픽된 게임 필터
    """
    qs = DuelRecord.objects.prefetch_related('idol_slots__idol').order_by('-played_at')
    if query:
        qs = qs.filter(
            Q(player1_name__icontains=query) |
            Q(player2_name__icontains=query)
        )
    if idol_id:
        qs = qs.filter(idol_slots__idol__idol_id=idol_id, idol_slots__slot_type='pick')
    return qs
