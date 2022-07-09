import io
import textwrap
from datetime import datetime

import numpy
import requests
from PIL import Image, ImageFont
from PIL import ImageDraw
from moviepy import editor

token = input('Введите Access Token: ')
group_id = input('Введите id группы (должен начинаться с "-"): ')

videos_count = input('Введите количество видео для видеотрейлера (оставьте пустым, чтобы обработать все видео): ')
if not videos_count:
    videos_count = None
else:
    videos_count = int(videos_count)

clips = []


def get_new_streams():
    http = requests.Session()
    http.headers['User-agent'] = 'Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0'

    print('Получение данных...')
    response = http.post(
        'https://api.vk.com/method/video.get',
        {
            'owner_id': group_id,
            'offset': 0,
            'v': '5.92',
            'access_token': token
        },
    )

    if response.ok:
        data = response.json()
        if 'error' in data:
            raise Exception(f'Произошла ошибка:\n'
                            f'{data["error"]}')

        response = data['response']

    else:
        raise Exception(f'Не удалось выполнить запрос. {response}')

    videos = sorted(response['items'], key=lambda d: d['views'], reverse=True)

    i = 0
    for video in videos:

        if videos_count is not None:
            if i >= videos_count:
                break
        i += 1

        if not video.get('photo_1280'):
            continue

        img_data = requests.get(video['photo_1280']).content
        img = Image.open(io.BytesIO(img_data))

        font = ImageFont.truetype('sans-serif.ttf', 42)
        image_draw = ImageDraw.Draw(img)

        # разделяем текст на строки
        wrapper = textwrap.TextWrapper(width=42)
        word_list = wrapper.wrap(text=video['title'])
        caption_new = ''
        for ii in word_list[:-1]:
            caption_new = caption_new + ii + '\n'
        caption_new += word_list[-1]

        # добавляем обводку тексту
        offset = 4
        shadow_color = 'black'
        image_text_x = 50
        image_text_y = 550
        for off in range(offset):
            image_draw.text((image_text_x - off, image_text_y), caption_new, font=font, fill=shadow_color)
            image_draw.text((image_text_x + off, image_text_y), caption_new, font=font, fill=shadow_color)
            image_draw.text((image_text_x, image_text_y + off), caption_new, font=font, fill=shadow_color)
            image_draw.text((image_text_x, image_text_y - off), caption_new, font=font, fill=shadow_color)
            image_draw.text((image_text_x - off, image_text_y + off), caption_new, font=font, fill=shadow_color)
            image_draw.text((image_text_x + off, image_text_y + off), caption_new, font=font, fill=shadow_color)
            image_draw.text((image_text_x - off, image_text_y - off), caption_new, font=font, fill=shadow_color)
            image_draw.text((image_text_x + off, image_text_y - off), caption_new, font=font, fill=shadow_color)

        # пишем текст на изображении
        image_draw.text((image_text_x, image_text_y), caption_new, fill=(255, 255, 255), font=font)

        pix = numpy.array(img)
        clips.append(editor.ImageClip(pix).set_duration(5))


get_new_streams()
final_clip = editor.concatenate_videoclips(clips, method='compose')
now = datetime.now()
file_name = f'result_{now.strftime("%Y%m%d%M%S")}.webm'
final_clip.write_videofile(file_name, fps=5)

print(f'Видеотрейлер сгенерирован. Имя файла: {file_name}')
