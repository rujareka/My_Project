"""
api/identix/urls.py
identix 앱 전용 URL 정의
- TTS 대전 데이터 수신
"""
from django.urls import path
from api.identix.views import TTSDuelReceiveView

app_name = 'identix'

urlpatterns = [
    path('duel/receive/', TTSDuelReceiveView.as_view(), name='duel_receive'),
]
