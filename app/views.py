from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

import time
import random
import requests

from concurrent import futures

# Здесь укажите URL основного сервиса, где находится ваш эндпойнт
CALLBACK_URL = "http://127.0.0.1:8888/SatellitesAsyncStatus/"
passkey = "password"

executor = futures.ThreadPoolExecutor(max_workers=1)

#
def get_random_async_status(satellite_id, i):
    time.sleep(1)
    return {
        "satellite_id": satellite_id,
        "percentage": str(i) + "%",
    }


def async_status_callback(task):
    try:
        result = task.result()
        print("Sending percentage update:", result)
    except futures._base.CancelledError:
        return
    except Exception as e:
        print("Failed to get a result:", e)
        return

    nurl = CALLBACK_URL + str(result["satellite_id"])
    headers = {'Content-Type': 'application/json'}
    answer = {"percentage": result["percentage"], "passkey": passkey}



    # Здесь используем requests.put для отправки обновления статуса
    try:
        response = requests.put(nurl, json=answer, headers=headers, timeout=3)
        response.raise_for_status()
    except requests.RequestException as e:
        print("Failed to send the update:", e)


@api_view(['POST'])
def start_async_update(request):
    satellite_id = request.data.get("satellite_id")
    print(satellite_id)

    if satellite_id:
        for i in range(10,101,10):
            task = executor.submit(get_random_async_status, satellite_id, i)
            task.add_done_callback(async_status_callback)
        return Response({"message": "Update started"}, status=status.HTTP_202_ACCEPTED)
    return Response({"error": "satellite_id is missing"}, status=status.HTTP_400_BAD_REQUEST)
