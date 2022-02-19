import json
import logging
import sqlite3
import requests
from pathlib import Path
from requests import adapters
from concurrent.futures import ThreadPoolExecutor

# https://stackoverflow.com/a/68583332/10144204
session = requests.Session()
session.mount('https://', requests.adapters.HTTPAdapter(pool_maxsize=16, max_retries=5, pool_block=True))


def get(url):
    response = session.get(url)
    if response.status_code == 200:
        logging.info('Downloaded ' + url)
        with open('assets/' + response.url.split('&')[-1].split('/')[-1].split('?')[0].split('=')[-1], 'wb') as f:
            f.write(response.content)
    else:
        logging.error('Error downloading %s: %s', url, response.status_code)
    return


def download_and_save(urls):
    with ThreadPoolExecutor(max_workers=16) as executor:
        executor.map(get, urls)


def make_emoticon_list():
    emoticon_list = []
    for emoticon_id in range(1, 51):  # 泡泡
        emoticon_list.append('https://tb2.bdstatic.com/tb/editor/images/client/image_emoticon' + str(emoticon_id) + '.png')
    for emoticon_id in range(61, 102):  # 移动端新版泡泡
        emoticon_list.append('https://tb2.bdstatic.com/tb/editor/images/client/image_emoticon' + str(emoticon_id) + '.png')
    for emoticon_id in range(129, 133):  # 不明
        emoticon_list.append('https://tb2.bdstatic.com/tb/editor/images/client/image_emoticon' + str(emoticon_id) + '.png')
    for emoticon_id in range(1, 56):  # .gif后缀名泡泡
        emoticon_list.append('https://tb2.bdstatic.com/tb/editor/images/wise/smart/image_editoricon' + str(emoticon_id) + '.gif')
    for emoticon_id in range(1, 52):  # 旧版泡泡
        emoticon_list.append('https://img.baidu.com/hi/face/i_f' + "{:02d}".format(emoticon_id) + '.gif')
    for emoticon_id in range(1, 41):  # 兔斯基
        emoticon_list.append('https://tb2.bdstatic.com/tb/editor/images/tsj/t_00' + "{:02d}".format(emoticon_id) + '.gif')
    for emoticon_id in range(1, 54):  # 绿豆蛙
        emoticon_list.append('https://tb2.bdstatic.com/tb/editor/images/ldw/w_00' + "{:02d}".format(emoticon_id) + '.gif')
    for emoticon_id in range(1, 71):  # 阿狸
        emoticon_list.append('https://tb2.bdstatic.com/tb/editor/images/ali/ali_0' + "{:02d}".format(emoticon_id) + '.gif')
    for emoticon_id in range(1, 63):  # 气泡熊
        emoticon_list.append('https://tb2.bdstatic.com/tb/editor/images/qpx_n/b' + "{:02d}".format(emoticon_id) + '.gif')
    for emoticon_id in range(1, 61):  # 熊孩子
        emoticon_list.append('https://tb2.bdstatic.com/tb/editor/images/bearchildren/bearchildren_' + "{:02d}".format(emoticon_id) + '.gif')
    for emoticon_id in range(1, 47):  # 影子
        emoticon_list.append('https://tb2.bdstatic.com/tb/editor/images/shadow/yz_0' + "{:02d}".format(emoticon_id) + '.gif')
    return emoticon_list


def main():
    logging.basicConfig(
        format='%(asctime)s [%(levelname)s] %(message)s',
        level=logging.INFO,
        handlers=[
            logging.FileHandler('proma_takeout.log', encoding='utf-8'),
            logging.StreamHandler()
        ])
    Path("./assets").mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect('proma.db')
    db = conn.cursor()

    biglist = make_emoticon_list()
    contents = db.execute('select content from post')
    for row in contents:
        content = json.loads(row[0])
        for item in content:
            if item['type'] == 'image':
                biglist.append(item['content'])
            if item['type'] == 'audio':
                biglist.append('https://tieba.baidu.com/c/p/voice?play_from=pb_voice_play&voice_md5=' + item['content'])
            if item['type'] == 'album':
                for image in item['content']:
                    biglist.append(image['url'])

    signatures = db.execute('select signature from post')
    for row in signatures:
        biglist.append(row[0])

    avatars = db.execute('select avatar from user')
    for row in avatars:
        biglist.append('https://himg.bdimg.com/sys/portraith/item/' + row[0].split('?')[0] + '.jpg')

    conn.close()
    biglist = list(set(biglist))  # Dedup

    logging.info('''
    Starting proma_takeout
    
    Total items: {}
    
    Weigh anchor!
    '''.format(len(biglist)))
    download_and_save(biglist)
    logging.info('All done! Have fun!')


if __name__ == '__main__':
    main()
