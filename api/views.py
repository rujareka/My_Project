"""
api/views.py
JSON 응답 API 뷰 (viewersPage에서 fetch로 호출 가능)
"""
from django.http import JsonResponse
from api.models import Idol, Card
from api.identix.models import DuelRecord


def idol_list_api(request):
    """GET /api/idols/ - 아이돌 전체 목록 + 통계 반환"""
    idols = Idol.objects.all()
    data = [{
        'idol_id':    idol.idol_id,
        'name':       idol.name,
        'pick_rate':  idol.pick_rate,
        'win_rate':   idol.win_rate,
        'ban_rate':   idol.ban_rate,
        'banner_img': idol.banner_img_url,
    } for idol in idols]
    return JsonResponse({'idols': data})


def card_list_api(request):
    """GET /api/cards/?idol_id=xxx - 카드 목록 반환"""
    idol_id = request.GET.get('idol_id', '')
    qs = Card.objects.select_related('idol')
    if idol_id:
        qs = qs.filter(idol__idol_id=idol_id)
    data = [{
        'card_id':    c.card_id,
        'name':       c.name,
        'idol':       c.idol.name if c.idol else '공용',
        'cost':       c.cost,
        'pick_rate':  c.pick_rate,
        'win_rate':   c.win_rate,
        'img_url':    c.card_img_url,
    } for c in qs]
    return JsonResponse({'cards': data})


def stats_summary_api(request):
    """GET /api/stats/summary/ - 사이트 전체 통계 요약"""
    return JsonResponse({
        'total_duels': DuelRecord.objects.count(),
        'total_idols': Idol.objects.count(),
        'total_cards': Card.objects.count(),
    })
