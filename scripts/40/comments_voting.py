import requests
import re

token = input('Введите Access Token: ')
video_id = input('Введите id видео: ')
owner_id = input('Введите owner_id видео: ')

print('Введите варианты ответов (каждый с новой строки). Вариант ответа может быть регулярным выражением\n'
      'Чтобы закончить ввод нажмите Enter 2 раза:')

answers = []
while True:
    answer = input()
    if not answer:
        break
    answers.append(answer.strip())

results = {answer: 0 for answer in answers}


def get_counts():
    http = requests.Session()
    http.headers['User-agent'] = 'Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0'

    response = http.post(
        'https://api.vk.com/method/video.getComments',
        {
            'owner_id': owner_id,
            'video_id': video_id,
            'offset': 0,
            'v': '5.92',
            'access_token': token
        },
    )

    if response.ok:
        data = response.json()
        if 'error' in data:
            raise Exception(f'Ошибка VK API:\n'
                            f'{data["error"]}')

        response = data['response']

    else:
        raise Exception(f'Не удалось выполнить запрос. {response}')

    for comment in response['items']:
        comment_text = comment['text']
        for pattern in answers:

            try:
                find = re.search(pattern, comment_text, flags=re.IGNORECASE)
            except:
                raise Exception(f'Проверьте синтаксис регулярного выражения: `{pattern}`')
            if find:
                results[pattern] += 1
                break

    print('Результаты:\n'
          '============')
    for pattern, count in results.items():
        print(pattern, '---', count)


get_counts()
