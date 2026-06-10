"""
api/models.py
핵심 DB 모델 정의
- Idol       : 아이돌 마스터 데이터 + 통계
- Card       : 카드 마스터 데이터
- PlayerDeck : 플레이어 덱 저장
"""
from django.db import models
from django.contrib.auth.models import User


# ──────────────────────────────────────────────
# 아이돌 DB
# ──────────────────────────────────────────────
class Idol(models.Model):
    """
    각 아이돌의 마스터 정보 + 실시간 통계
    /idols.json 으로 초기 데이터 로드
    """
    idol_id    = models.CharField(max_length=20, unique=True)       # ex) "idol_01"
    name       = models.CharField(max_length=50)                    # 아이돌 이름
    leader_gimmick = models.TextField(blank=True)                   # 리더 기믹 설명
    description    = models.TextField(blank=True)                   # 아이돌 소개

    start_vol = models.IntegerField(default=0)
    start_hand = models.IntegerField(default=0)

    # 통계 (대전 결과 수신 시 갱신)
    pick_count = models.IntegerField(default=0)                     # 픽 횟수
    win_count  = models.IntegerField(default=0)                     # 승리 횟수

    # 이미지 (jsDelivr CDN URL 저장 방식 사용)
    banner_img_url = models.URLField(blank=True)                    # 배너 이미지
    icon_img_url   = models.URLField(blank=True)                    # 아이콘 이미지

    class Meta:
        ordering = ['idol_id']
        verbose_name = '아이돌'
        verbose_name_plural = '아이돌'
    def __str__(self):
        return self.name

    # ── 통계 계산 프로퍼티 ──
    @property
    def pick_rate(self):
        """픽률 = 픽 횟수 / 전체 게임 수 (Duel.total_games 참조)"""
        from api.identix.models import DuelRecord
        total = DuelRecord.objects.count()
        if total == 0:
            return 0.0
        return round(self.pick_count / total * 100, 1)

    @property
    def win_rate(self):
        """승률 = 승리 횟수 / (픽 횟수 - 밴 횟수)"""
        denom = self.pick_count
        if denom <= 0:
            return 0.0
        return round(self.win_count / denom * 100, 1)


# ──────────────────────────────────────────────
# 카드 DB
# ──────────────────────────────────────────────
class Card(models.Model):
    """
    카드 마스터 데이터
    /cards.json 으로 초기 데이터 로드
    """
    card_id    = models.CharField(max_length=30, unique=True)       # ex) "card_idol01_001"
    name       = models.CharField(max_length=100)
    idol       = models.ForeignKey(
        Idol, on_delete=models.CASCADE,
        related_name='cards',
        null=True, blank=True                                       # 공용 카드는 null
    )
    effect     = models.TextField(blank=True)                       # 카드 효과 텍스트
    card_img_url = models.URLField(blank=True)                      # jsDelivr CDN URL

    # 카드 통계 (덱에 포함된 횟수 기반)
    include_count = models.IntegerField(default=0)                  # 덱에 포함된 횟수
    win_count     = models.IntegerField(default=0)                  # 해당 카드 포함 덱의 승리 수

    PERSON_CHOICES = [(1,'P.1'),(2,'P.2'),(3,'P.3')]
    card_level = models.IntegerField(choices=PERSON_CHOICES, default=1)
    voltage    = models.IntegerField(default=0)
    fan_addition = models.IntegerField(default=0) # 얻는 팬수

    class Meta:
        ordering = ['idol', 'card_id']
        verbose_name = '카드'
        verbose_name_plural = '카드'
    def __str__(self):
        return f"{self.idol.name if self.idol else '공용'} - {self.name}"

    @property
    def pick_rate(self):
        """카드 픽률 = 포함 횟수 / 해당 아이돌 픽 수"""
        denom = self.idol.pick_count if self.idol else 1
        if denom == 0:
            return 0.0
        return round(self.include_count / denom * 100, 1)

    @property
    def win_rate(self):
        if self.include_count == 0:
            return 0.0
        return round(self.win_count / self.include_count * 100, 1)

class MemoryCard(models.Model):
    """메모리 카드 — 덱에 3장 편성"""
    memory_id    = models.CharField(max_length=30, unique=True)
    name         = models.CharField(max_length=100)
    idol         = models.ForeignKey(
        'Idol', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='memory_cards'
    )
    effect       = models.TextField(blank=True)
    card_img_url = models.URLField(blank=True)

    class Meta:
        ordering = ['memory_id']
        verbose_name = '메모리 카드'
        verbose_name_plural = '메모리 카드'

    def __str__(self):
        return self.name

# ──────────────────────────────────────────────
# 플레이어 덱 DB
# ──────────────────────────────────────────────
class PlayerDeck(models.Model):
    """
    로그인한 플레이어가 저장하는 덱
    - 로그인 필수 (User FK)
    - 아이돌 1명 + 카드 선택 조합
    """
    owner    = models.ForeignKey(User, on_delete=models.CASCADE, related_name='decks')
    idol     = models.ForeignKey(Idol, on_delete=models.SET_NULL, null=True)
    name     = models.CharField(max_length=100)                     # 덱 이름
    cards    = models.ManyToManyField(Card, blank=True)             # 덱에 포함된 카드
    memory_cards = models.ManyToManyField('MemoryCard', blank=True)
    description = models.TextField(blank=True, max_length=1000)
    like_count = models.IntegerField(default=0)
    deck_code = models.CharField(max_length=200, blank=True)        # TTS 덱코드 (외부 연동용)
    memo     = models.TextField(blank=True)                         # 메모
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_public  = models.BooleanField(default=False)                 # 덱 공개 여부
    card_list_json = models.TextField(blank=True, default='[]')
    class Meta:
        ordering = ['-updated_at']
        verbose_name = '플레이어 덱'
        verbose_name_plural = '플레이어 덱'

    def __str__(self):
        return f"{self.owner.username} - {self.name}"

    def is_complete(self):
        return self.cards.count() == 18 and self.memory_cards.count() == 3

    def sync_like_count(self):
        self.like_count = self.likes.count()
        self.save(update_fields=['like_count'])

class DeckLike(models.Model):
    """덱 추천 (한 유저가 같은 덱에 중복 추천 불가)"""
    deck       = models.ForeignKey('PlayerDeck', on_delete=models.CASCADE, related_name='likes')
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='liked_decks')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('deck', 'user')
        verbose_name    = '덱 추천'
        verbose_name_plural = '덱 추천'

    def __str__(self):
        return f"{self.user.username} → {self.deck.name}"

class DeckComment(models.Model):
    """덱 코멘트"""
    deck       = models.ForeignKey('PlayerDeck', on_delete=models.CASCADE, related_name='comments')
    author     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='deck_comments')
    body       = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering   = ['created_at']
        verbose_name = '덱 코멘트'
        verbose_name_plural = '덱 코멘트'

    def __str__(self):
        return f"{self.author.username}: {self.body[:30]}"
