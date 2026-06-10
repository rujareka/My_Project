"""
viewersPage/urls.py
유저 화면 URL 정의
"""
from django.urls import path
from viewersPage import views

app_name = 'viewersPage'

urlpatterns = [
    # 메인
    path('', views.main_page, name='main'),

    # 아이돌 티어
    path('idol/',               views.idol_tier,        name='idol_tier'),
    path('idol/<str:idol_id>/', views.idol_detail,      name='idol_detail'),

    # ── 덱 ──────────────────────────────────────
    path('deck/',                          views.my_decks,         name='my_decks'),
    path('deck/new/',                      views.deck_new,          name='deck_new'),
    path('deck/edit/',                     views.deck_edit_new,     name='deck_edit_new'),  # 신규 덱 카드 편집
    path('deck/<int:deck_id>/edit/',       views.deck_edit,         name='deck_edit'),      # 기존 덱 편집
    path('deck/save/',                     views.deck_save,         name='deck_save'),
    path('deck/<int:deck_id>/delete/',     views.deck_delete,       name='deck_delete'),
    path('deck/<int:deck_id>/toggle/',     views.deck_toggle_public,name='deck_toggle_public'),

    # ── 덱 일람 (공개) ──────────────────────────
    path('decklist/', views.decklist, name='deck_list'),

    # ── 카드 일람 ───────────────────────────────
    path('card/', views.card_list, name='card_list'),

    # ── 통계 ────────────────────────────────────
    path('statistics/', views.statistics, name='statistics'),

    # ── 대전 기록 ───────────────────────────────
    path('duel/', views.duel_archive, name='duel_list'),

    # ── 인증 ────────────────────────────────────
    path('auth/login/',  views.login_view,  name='login'),
    path('auth/logout/', views.logout_view, name='logout_view'),
    path('auth/signup/', views.signup_view, name='signup'),
]
