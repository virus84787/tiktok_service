import os

import telebot
from telebot.types import InputMediaVideo

import config
import time
import urllib.request
from datetime import datetime
from urllib.parse import quote, urlsplit, urlunsplit
from bs4 import BeautifulSoup

bot = telebot.TeleBot(config.TOKEN)
dev_chat_id = config.DEV_CHAT_ID
download_tool_site = config.DOWNLOAD_TOOL_SITE
download_tool_site_tt = config.DOWNLOAD_TOOL_SITE_TT

def iri_to_uri(iri):
    parts = urlsplit(iri)
    uri = urlunsplit((
        parts.scheme,
        parts.netloc.encode('idna').decode('ascii'),
        quote(parts.path),
        quote(parts.query, '='),
        quote(parts.fragment),
    ))
    return uri


def get_current_time():
    now = datetime.now()
    return now.strftime("%d/%m/%Y %H:%M:%S")


@bot.message_handler(content_types=['text'])
def get__content(message):
    if "tiktok.com/" in message.text:
        chat_identity = message.chat.title if message.chat.id < 0 else str(
            message.chat.id)
        try:
            file = open("id.txt", "r")
        except Exception as e:
            file = open("id.txt", "w")
            file.close()
            file = open("id.txt", "r")
        s = file.read()
        id = int(s) if s != '' else 1
        file.close()
        file = open("id.txt", "w")
        file.write(str(id + 1))
        file.close()      
        print('-------------------------' + '\n' + get_current_time() + " id: " + str(
            id) + " Chat identity: " + chat_identity)
        url_message = message.text
        start_url = url_message.find("https")
        url = iri_to_uri(url_message[start_url:])
        print(get_current_time() + " id: " + str(id) + " URL: " + url)

        data = urllib.parse.urlencode(
            {'id': url, 'locale': 'en', 'tt': download_tool_site_tt})
        data = data.encode('ascii')
        req = urllib.request.Request(
            download_tool_site,
            data=data,
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
            }
        )
        try:
            retry_count = 1
            while (retry_count <= 10):
                    try:
                        time.sleep(0.1)
                        url_response = urllib.request.urlopen(req)
                        break
                    except Exception as e:
                        bot.send_message(dev_chat_id,
                                        "Chat identity: " + chat_identity + '\n' + "Retry - " + str(retry_count))
                        retry_count += 1

            response_data = url_response.read().decode('utf-8')
            soup = BeautifulSoup(response_data, 'html.parser')
            video_link = soup.select('a[class*="pure-button pure-button-primary is-center u-bl dl-button download_link without_watermark vignette_active"]')
            urllib.request.urlretrieve(video_link[0]['href'], str(id) + ".mp4")
                    
            retry_count = 1
            while (retry_count <= 10):
                    try:
                        video = open(str(id) + '.mp4', 'rb')
                        if retry_count != 1:
                            time.sleep(0.5)
                        bot.send_media_group(message.chat.id, [InputMediaVideo(video, None, None)],
                            None, message.id)
                        break
                    except Exception as e:
                        bot.send_message(dev_chat_id,
                                        "Chat identity: " + chat_identity + '\n' + "Retry send message - " + str(retry_count))
                        retry_count += 1
                        video.close()
                        if retry_count == 11:
                            raise e
            
            video.close()
            os.remove(str(id) + ".mp4")
            print(get_current_time() + " id: " +
                str(id) + ' Success')

        except Exception as e:
            bot.send_message(dev_chat_id, "Chat identity: " +
                            chat_identity + '\n' + 'Error: ' + str(e))
            file = open("logs_errors.txt", "a")
            file.write(get_current_time() + " id: " + str(id) + '\n' + str(message.chat.id) + '\n' + url + '\n' + str(
                e) + '\n' + '\n')
            file.close()
            bot.reply_to(message, "something went wrong")
            print(get_current_time() + " id: " + str(id) +
                ' something went wrong' + '\n' + str(e))


bot.polling(none_stop=True)
