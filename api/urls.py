"""
api/urls.py
백엔드 API 엔드포인트 URL
"""
from django.urls import path
from api import views

app_name = 'api'

urlpatterns = [
    # 아이돌 목록 JSON
    path('idols/', views.idol_list_api, name='idol_list'),
    # 카드 목록 JSON
    path('cards/', views.card_list_api, name='card_list'),
    # 통계 요약 JSON
    path('stats/summary/', views.stats_summary_api, name='stats_summary'),
]
