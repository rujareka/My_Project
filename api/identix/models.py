"""
api/identix/models.py
대전 기록 관련 DB 모델
- DuelRecord  : TTS에서 수신한 1게임 단위 대전 데이터
- DuelIdolSlot: 1게임 내 각 플레이어의 아이돌 슬롯
"""
from django.db import models
from django.contrib.auth.models import User
from api.models import Idol, Card


# ──────────────────────────────────────────────
# 대전 DB
# ──────────────────────────────────────────────
class DuelRecord(models.Model):
    """
    TTS API로부터 수신한 1경기 단위 대전 기록
    수신 후 identix/tts_receiver.py 에서 통계 집계 트리거
    """
    SOURCE_CHOICES = [
        ('tts',    'Table Top Simulator'),
        ('manual', '수동 입력'),
    ]

    source      = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='tts')
    played_at   = models.DateTimeField(auto_now_add=True)
    season      = models.CharField(max_length=20, blank=True)       # 시즌 구분 ex) "S1"

    # 플레이어 (비로그인 대전도 허용, username 문자열로 저장)
    player1_name = models.CharField(max_length=50)
    player2_name = models.CharField(max_length=50)
    player1_user = models.ForeignKey(User, null=True, blank=True,
                                     on_delete=models.SET_NULL, related_name='p1_duels')
    player2_user = models.ForeignKey(User, null=True, blank=True,
                                     on_delete=models.SET_NULL, related_name='p2_duels')

    # 승패 (1 or 2, 0=무승부)
    winner = models.IntegerField(choices=[(0,'무'), (1,'P1'), (2,'P2')], default=0)

    # TTS 덱코드 (원본 보존용)
    p1_deck_code = models.CharField(max_length=500, blank=True)
    p2_deck_code = models.CharField(max_length=500, blank=True)

    class Meta:
        ordering = ['-played_at']
        verbose_name = '대전 기록'

    def __str__(self):
        return f"{self.player1_name} vs {self.player2_name} ({self.played_at:%Y-%m-%d})"


class DuelIdolSlot(models.Model):
    """
    1경기 내 각 플레이어의 아이돌 선택 슬롯
    픽/밴 구분, 어느 플레이어인지 기록
    """
    SLOT_TYPE_CHOICES = [
        ('pick', '픽'),
        ('ban',  '밴'),
    ]

    duel    = models.ForeignKey(DuelRecord, on_delete=models.CASCADE, related_name='idol_slots')
    idol    = models.ForeignKey(Idol, on_delete=models.CASCADE)
    player  = models.IntegerField(choices=[(1, 'P1'), (2, 'P2')])   # 어느 플레이어
    slot_type = models.CharField(max_length=10, choices=SLOT_TYPE_CHOICES)
    is_leader = models.BooleanField(default=False)                  # 리더 아이돌 여부

    class Meta:
        verbose_name = '대전 아이돌 슬롯'

    def __str__(self):
        return f"{self.duel} | P{self.player} {self.idol.name} ({self.slot_type})"


class DuelCardSlot(models.Model):
    """
    1경기 내 각 플레이어가 덱에 포함한 카드 기록
    """
    duel   = models.ForeignKey(DuelRecord, on_delete=models.CASCADE, related_name='card_slots')
    card   = models.ForeignKey(Card, on_delete=models.CASCADE)
    player = models.IntegerField(choices=[(1, 'P1'), (2, 'P2')])

    class Meta:
        verbose_name = '대전 카드 슬롯'
