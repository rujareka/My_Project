"""
api/identix/views.py
TTS로부터 대전 데이터를 POST로 수신하는 API 엔드포인트
"""
import json
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from api.identix.tts_receiver import process_duel_data


@method_decorator(csrf_exempt, name='dispatch')
class TTSDuelReceiveView(View):
    """
    TTS → 서버 대전 결과 수신
    POST /identix/duel/receive/
    """
    def post(self, request):
        try:
            data = json.loads(request.body)
            duel = process_duel_data(data)
            return JsonResponse({'status': 'ok', 'duel_id': duel.id})
        except KeyError as e:
            return JsonResponse({'status': 'error', 'message': f'필수 필드 누락: {e}'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def get(self, request):
        return JsonResponse({'status': 'ok', 'message': 'TTS 수신 엔드포인트'})
