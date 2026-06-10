"""
api/identix/admin.py
대전 기록 관리자 화면
"""
from django.contrib import admin
from api.identix.models import DuelRecord, DuelIdolSlot, DuelCardSlot


class DuelIdolSlotInline(admin.TabularInline):
    model = DuelIdolSlot
    extra = 0


class DuelCardSlotInline(admin.TabularInline):
    model = DuelCardSlot
    extra = 0


@admin.register(DuelRecord)
class DuelRecordAdmin(admin.ModelAdmin):
    list_display  = ('id', 'player1_name', 'player2_name', 'winner', 'season', 'played_at', 'source')
    list_filter   = ('season', 'source', 'winner')
    search_fields = ('player1_name', 'player2_name')
    inlines       = [DuelIdolSlotInline, DuelCardSlotInline]
