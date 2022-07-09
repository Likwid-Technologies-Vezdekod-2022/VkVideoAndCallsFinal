import io
import os
import textwrap
from datetime import datetime

import numpy
import requests
from PIL import Image, ImageFont
from PIL import ImageDraw
from moviepy import editor

token = 'vk1.a.8gR9eVLluZLKRFH36hm3dqNBhv-s2l7DXVmcgFoW_qvKCX9hRuA0RhyUMn3pdciqpnYYTR5t7crojhledPH-rA4DP9y-ShULJ62l3nlgIicmkgdu-gQgp8XQl-GcIbZEfu3vn1s9No5Qw6uQHhq5Vms8tCpLZJHXwmQZata2b9idKcLR1RJ9vTZqnSf1Gwhc'  # input('Введите Access Token: ')
group_id = '-72495085'  # input('Введите id группы (должен начинаться с "-"): ')

d = r'C:\Users\12\Pictures\Saved Pictures'
files = os.listdir(d)
images = list(filter(lambda x: x.endswith('.jpg') or x.endswith('.png'), files))
print(images)

# for image in images:
#     img = Image.open(f'{d}\\{image}')
#     font = ImageFont.truetype("sans-serif.ttf", 56)
#     # Call draw Method to add 2D graphis in an image
#     I1 = ImageDraw.Draw(img)
#     # Add Text to an image
#
#     caption = 'LASD ASD ЫФВЙЦУЙЦУ SA DSADSA DQWE QW S AD A DQWE SAD sd sad qwe qdfs sa dsadsadsa sadssad sadsadsad йцуйц asd qwe '
#
#     wrapper = textwrap.TextWrapper(width=30)
#     word_list = wrapper.wrap(text=caption)
#     caption_new = ''
#     for ii in word_list[:-1]:
#         caption_new = caption_new + ii + '\n'
#     caption_new += word_list[-1]
#
#     I1.text((28, 36), caption_new, fill=(255, 0, 0), font=font)
#     # Display edited image
#     img.show()
#     # Save the edited image
#     # img.save("car2.png")
#     exit()
#
# exit()


clips = []


def get_new_streams():
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

    i = 0
    for video in response['items']:
        i += 1
        if i >= 10:
            break
        print(video['photo_800'])
        img_data = requests.get(video['photo_800']).content
        print(type(img_data))
        img = Image.open(io.BytesIO(img_data))

        font = ImageFont.truetype("sans-serif.ttf", 32)
        # Call draw Method to add 2D graphis in an image
        I1 = ImageDraw.Draw(img)
        # Add Text to an image

        wrapper = textwrap.TextWrapper(width=36)
        word_list = wrapper.wrap(text=video['title'])
        caption_new = ''
        for ii in word_list[:-1]:
            caption_new = caption_new + ii + '\n'
        caption_new += word_list[-1]

        I1.text((28, 36), caption_new, fill=(255, 0, 0), font=font)

        pix = numpy.array(img)
        clips.append(editor.ImageClip(pix).set_duration(5))


get_new_streams()
final_clip = editor.concatenate_videoclips(clips, method='compose')
now = datetime.now()
final_clip.write_videofile(f'test_{now.strftime("%Y%m%d%M%S")}.webm', fps=24)
