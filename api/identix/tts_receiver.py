"""
api/identix/tts_receiver.py
TTS(Table Top Simulator)에서 대전 데이터 수신 후
통계 집계 트리거를 담당하는 비즈니스 로직
"""
from django.db import transaction
from api.models import Idol, Card
from api.identix.models import DuelRecord, DuelIdolSlot, DuelCardSlot


def parse_deck_code(deck_code: str) -> list[str]:
    """
    TTS 덱코드 파싱 → 카드 ID 리스트 반환
    실제 TTS 포맷에 맞게 파싱 로직 구현 필요
    ex) "card_idol01_001,card_idol01_002,..." 형식 가정
    """
    if not deck_code:
        return []
    return [c.strip() for c in deck_code.split(',') if c.strip()]


@transaction.atomic
def process_duel_data(data: dict) -> DuelRecord:
    """
    TTS API POST 데이터 처리 흐름:
    1. DuelRecord 생성
    2. DuelIdolSlot 생성 (픽/밴 각각)
    3. DuelCardSlot 생성 (덱코드 파싱)
    4. 통계 집계 (aggregate_stats 호출)

    data 예시:
    {
        "player1_name": "Alice",
        "player2_name": "Bob",
        "winner": 1,
        "season": "S1",
        "p1_idol_picks": ["idol_01"],

        "p2_idol_picks": ["idol_03"],

        "p1_leader": "idol_01",
        "p2_leader": "idol_03",
        "p1_deck_code": "card_01,card_02,...",
        "p2_deck_code": "card_10,card_11,...",
    }
    """
    # 1. 대전 기록 생성
    duel = DuelRecord.objects.create(
        source       = 'tts',
        season       = data.get('season', ''),
        player1_name = data['player1_name'],
        player2_name = data['player2_name'],
        winner       = data.get('winner', 0),
        p1_deck_code = data.get('p1_deck_code', ''),
        p2_deck_code = data.get('p2_deck_code', ''),
    )

    # 2. 아이돌 슬롯 생성
    _create_idol_slots(duel, data)

    # 3. 카드 슬롯 생성
    _create_card_slots(duel, data)

    # 4. 통계 집계
    aggregate_stats(duel, data)

    return duel


def _create_idol_slots(duel: DuelRecord, data: dict):
    """픽/밴 슬롯을 DuelIdolSlot에 기록"""
    for player_num, pick_key, ban_key, leader_key in [
        (1, 'p1_idol_picks', 'p1_leader'),
        (2, 'p2_idol_picks', 'p2_leader'),
    ]:
        for idol_id in data.get(pick_key, []):
            idol = Idol.objects.filter(idol_id=idol_id).first()
            if idol:
                DuelIdolSlot.objects.create(
                    duel=duel, idol=idol, player=player_num,
                    slot_type='pick',
                    is_leader=(idol_id == data.get(leader_key))
                )
        for idol_id in data.get(ban_key, []):
            idol = Idol.objects.filter(idol_id=idol_id).first()
            if idol:
                DuelIdolSlot.objects.create(
                    duel=duel, idol=idol, player=player_num,
                    slot_type='ban'
                )


def _create_card_slots(duel: DuelRecord, data: dict):
    """덱코드 파싱 후 DuelCardSlot 생성"""
    for player_num, deck_key in [(1, 'p1_deck_code'), (2, 'p2_deck_code')]:
        card_ids = parse_deck_code(data.get(deck_key, ''))
        for card_id in card_ids:
            card = Card.objects.filter(card_id=card_id).first()
            if card:
                DuelCardSlot.objects.create(duel=duel, card=card, player=player_num)


@transaction.atomic
def aggregate_stats(duel: DuelRecord, data: dict):
    """
    대전 결과를 Idol/Card 통계 컬럼에 반영
    - 픽 → idol.pick_count + 1
    - 밴 → idol.ban_count + 1
    - 승리 측 픽 아이돌 → idol.win_count + 1
    - 카드 include_count, win_count 갱신
    """
    winner = data.get('winner', 0)

    # 아이돌 통계
    for slot in duel.idol_slots.select_related('idol'):
        if slot.slot_type == 'pick':
            slot.idol.pick_count += 1
            if (winner == 1 and slot.player == 1) or (winner == 2 and slot.player == 2):
                slot.idol.win_count += 1
            slot.idol.save(update_fields=['pick_count', 'win_count'])
        elif slot.slot_type == 'ban':
            slot.idol.ban_count += 1
            slot.idol.save(update_fields=['ban_count'])

    # 카드 통계
    for card_slot in duel.card_slots.select_related('card'):
        card_slot.card.include_count += 1
        if (winner == 1 and card_slot.player == 1) or (winner == 2 and card_slot.player == 2):
            card_slot.card.win_count += 1
        card_slot.card.save(update_fields=['include_count', 'win_count'])
