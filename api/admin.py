"""
api/admin.py
Django 관리자 화면 — 마스터 데이터 입력/관리용

수정 내용:
  - 이미지 미리보기 컬럼 추가 (URL이 올바른지 시각 확인)
  - MemoryCard, DeckLike, DeckComment 등록 추가
  - 카드 레벨/볼티지 필터 추가
  - 대전 기록 인라인 보기 유지
"""
from django.contrib import admin
from django.utils.html import format_html
from api.models import Idol, Card, MemoryCard, PlayerDeck, DeckLike, DeckComment


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 아이돌
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@admin.register(Idol)
class IdolAdmin(admin.ModelAdmin):
    list_display   = ('idol_id', 'name', 'icon_preview',
                      'pick_count', 'win_count', 'ban_count')
    search_fields  = ('name', 'idol_id')
    # 통계 카운터는 TTS 수신 시 자동 갱신 — 직접 수정 금지
    readonly_fields = ('pick_count', 'win_count', 'ban_count',
                       'banner_preview', 'icon_preview')

    # 입력 폼에서 필드 순서/그룹 정리
    fieldsets = (
        ('기본 정보', {
            'fields': ('idol_id', 'name', 'leader_gimmick', 'description')
        }),
        ('이미지 URL (jsDelivr)', {
            'fields': ('banner_img_url', 'banner_preview',
                       'icon_img_url',   'icon_preview'),
            'description': (
                'URL 형식: '
                'https://cdn.jsdelivr.net/gh/rujareka/My_Project@main/static/imgs/...'
            )
        }),
        ('통계 (자동 집계 — 수정 불가)', {
            'fields': ('pick_count', 'win_count', 'ban_count'),
            'classes': ('collapse',)   # 기본 접힘
        }),
    )

    # ── 목록에 아이콘 미리보기 ──
    def icon_preview(self, obj):
        if obj.icon_img_url:
            return format_html(
                '<img src="{}" style="height:36px;border-radius:5px;'
                'border:1px solid #ddd" onerror="this.style.opacity=0.3">',
                obj.icon_img_url
            )
        return '—'
    icon_preview.short_description = '아이콘'

    # ── 폼 상세에 배너 미리보기 ──
    def banner_preview(self, obj):
        if obj.banner_img_url:
            return format_html(
                '<img src="{}" style="max-height:120px;border-radius:6px;'
                'border:1px solid #ddd" onerror="this.style.opacity=0.3">',
                obj.banner_img_url
            )
        return '이미지 없음'
    banner_preview.short_description = '배너 미리보기'


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 카드
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display   = ('card_id', 'name', 'idol', 'card_type',
                      'card_level', 'voltage', 'cost', 'card_preview')
    list_filter    = ('idol', 'card_type', 'card_level')
    search_fields  = ('name', 'card_id')
    readonly_fields = ('include_count', 'win_count', 'card_preview')

    fieldsets = (
        ('기본 정보', {
            'fields': ('card_id', 'name', 'idol', 'card_type',
                       'card_level', 'voltage', 'cost', 'effect')
        }),
        ('이미지 URL (jsDelivr)', {
            'fields': ('card_img_url', 'card_preview'),
        }),
        ('통계 (자동 집계)', {
            'fields': ('include_count', 'win_count'),
            'classes': ('collapse',)
        }),
    )

    def card_preview(self, obj):
        if obj.card_img_url:
            return format_html(
                '<img src="{}" style="height:90px;border-radius:5px;'
                'border:1px solid #ddd" onerror="this.style.opacity=0.3">',
                obj.card_img_url
            )
        return '이미지 없음'
    card_preview.short_description = '카드 이미지'


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 메모리 카드
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@admin.register(MemoryCard)
class MemoryCardAdmin(admin.ModelAdmin):
    list_display   = ('memory_id', 'name', 'idol', 'card_preview')
    list_filter    = ('idol',)
    search_fields  = ('name', 'memory_id')
    readonly_fields = ('card_preview',)

    fieldsets = (
        ('기본 정보', {
            'fields': ('memory_id', 'name', 'idol', 'effect')
        }),
        ('이미지 URL (jsDelivr)', {
            'fields': ('card_img_url', 'card_preview'),
        }),
    )

    def card_preview(self, obj):
        if obj.card_img_url:
            return format_html(
                '<img src="{}" style="height:90px;border-radius:5px;'
                'border:1px solid #ddd" onerror="this.style.opacity=0.3">',
                obj.card_img_url
            )
        return '이미지 없음'
    card_preview.short_description = '이미지'


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 플레이어 덱
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@admin.register(PlayerDeck)
class PlayerDeckAdmin(admin.ModelAdmin):
    list_display   = ('name', 'owner', 'idol', 'card_count',
                      'memory_count', 'is_complete_display',
                      'is_public', 'like_count', 'updated_at')
    list_filter    = ('is_public',)
    search_fields  = ('name', 'owner__username')
    readonly_fields = ('like_count', 'created_at', 'updated_at')

    def card_count(self, obj):
        return f"{obj.cards.count()} / 18"
    card_count.short_description = '메인 카드'

    def memory_count(self, obj):
        return f"{obj.memory_cards.count()} / 3"
    memory_count.short_description = '메모리 카드'

    def is_complete_display(self, obj):
        done = obj.is_complete()
        color = '#2ecc71' if done else '#e67e22'
        label = '완성' if done else '미완성'
        return format_html(
            '<span style="color:{};font-weight:bold">{}</span>', color, label
        )
    is_complete_display.short_description = '완성 여부'


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 덱 추천 / 댓글
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@admin.register(DeckLike)
class DeckLikeAdmin(admin.ModelAdmin):
    list_display  = ('deck', 'user', 'created_at')
    search_fields = ('deck__name', 'user__username')
    readonly_fields = ('created_at',)


@admin.register(DeckComment)
class DeckCommentAdmin(admin.ModelAdmin):
    list_display  = ('deck', 'author', 'body_preview', 'created_at')
    search_fields = ('deck__name', 'author__username', 'body')
    readonly_fields = ('created_at',)

    def body_preview(self, obj):
        return obj.body[:40] + ('...' if len(obj.body) > 40 else '')
    body_preview.short_description = '내용'
