"""
api/admin.py
"""
from django.contrib import admin
from django.utils.html import format_html
from api.models import Idol, Card, MemoryCard, PlayerDeck, DeckLike, DeckComment


@admin.register(Idol)
class IdolAdmin(admin.ModelAdmin):
    list_display    = ('idol_id', 'name', 'icon_preview',
                       'start_vol','start_hand','pick_count', 'win_count')
    search_fields   = ('name', 'idol_id')
    readonly_fields = ('pick_count', 'win_count',
                       'banner_preview', 'icon_preview')
    fieldsets = (
        ('기본 정보', {
            'fields': ('idol_id', 'name','start_vol','start_hand','leader_gimmick', 'description')
        }),
        ('이미지 URL (jsDelivr)', {
            'fields': ('banner_img_url', 'banner_preview',
                       'icon_img_url',   'icon_preview'),
        }),
        ('통계 (자동 집계)', {
            'fields': ('pick_count', 'win_count'),
            'classes': ('collapse',)
        }),
    )

    def icon_preview(self, obj):
        if obj.icon_img_url:
            return format_html(
                '<img src="{}" style="height:36px;border-radius:5px;'
                'border:1px solid #ddd">',
                obj.icon_img_url
            )
        return '—'
    icon_preview.short_description = '아이콘'

    def banner_preview(self, obj):
        if obj.banner_img_url:
            return format_html(
                '<img src="{}" style="max-height:120px;border-radius:6px;'
                'border:1px solid #ddd">',
                obj.banner_img_url
            )
        return '이미지 없음'
    banner_preview.short_description = '배너 미리보기'


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display    = ('card_id', 'name', 'idol', 'fan_addition',
                       'card_level', 'voltage', 'card_preview')
    list_filter     = ('idol', 'card_level')
    search_fields   = ('name', 'card_id')
    readonly_fields = ('include_count', 'win_count', 'card_preview')
    fieldsets = (
        ('기본 정보', {
            'fields': ('card_id', 'name', 'idol', 'fan_addition',
                       'card_level', 'voltage', 'effect')
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
                'border:1px solid #ddd">',
                obj.card_img_url
            )
        return '이미지 없음'
    card_preview.short_description = '카드 이미지'


@admin.register(MemoryCard)
class MemoryCardAdmin(admin.ModelAdmin):
    list_display    = ('memory_id', 'name', 'idol', 'card_preview')
    list_filter     = ('idol',)
    search_fields   = ('name', 'memory_id')
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
                'border:1px solid #ddd">',
                obj.card_img_url
            )
        return '이미지 없음'
    card_preview.short_description = '이미지'


@admin.register(PlayerDeck)
class PlayerDeckAdmin(admin.ModelAdmin):
    list_display    = ('name', 'owner', 'idol', 'card_count',
                       'memory_count', 'is_public', 'like_count', 'updated_at')
    list_filter     = ('is_public',)
    search_fields   = ('name', 'owner__username')
    readonly_fields = ('like_count', 'created_at', 'updated_at')

    def card_count(self, obj):
        return f"{obj.cards.count()} / 18"
    card_count.short_description = '메인 카드'

    def memory_count(self, obj):
        return f"{obj.memory_cards.count()} / 3"
    memory_count.short_description = '메모리 카드'


@admin.register(DeckLike)
class DeckLikeAdmin(admin.ModelAdmin):
    list_display    = ('deck', 'user', 'created_at')
    search_fields   = ('deck__name', 'user__username')
    readonly_fields = ('created_at',)


@admin.register(DeckComment)
class DeckCommentAdmin(admin.ModelAdmin):
    list_display    = ('deck', 'author', 'body_preview', 'created_at')
    search_fields   = ('deck__name', 'author__username', 'body')
    readonly_fields = ('created_at',)

    def body_preview(self, obj):
        return obj.body[:40] + ('...' if len(obj.body) > 40 else '')
    body_preview.short_description = '내용'