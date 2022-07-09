import time
import requests

token = input('Введите Access Token: ')
group_id = input('Введите id группы (должен начинаться с "-"): ')

notified_videos = []


def get_new_streams():
    print('Обновление данных...\n')
    http = requests.Session()
    http.headers['User-agent'] = 'Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0'

    response = http.post(
        'https://api.vk.com/method/video.get',
        {'owner_id': group_id,
         'offset': 0,
         'v': '5.92',
         'access_token': token},
    )

    if response.ok:
        data = response.json()
        if 'error' in data:
            raise Exception(f'Произошла ошибка:\n'
                            f'{data["error"]}')

        response = data['response']

    else:
        raise Exception(f'Не удалось выполнить запрос. {response}')

    for video in response['items']:
        if not video.get('live', None):
            continue

        video_id = video['id']

        if video.get('live_status') and video['live_status'] == 'started':

            if video_id in notified_videos:
                continue

            url = f'https://vk.com/video/?z=video{group_id}_{video_id}'
            spectators = video['spectators']

            print('=== В группе началась новая трансляция ===\n'
                  f'Название: {video["title"]}\n'
                  f'Ссылка: {url}\n'
                  f'Количество зрителей: {spectators}')
            print('=======\n')

            notified_videos.append(video_id)

        else:
            try:
                notified_videos.remove(video_id)
            except:
                pass


print('Ожидание новых трансляций запущено\n')
while True:
    get_new_streams()
    time.sleep(60)
