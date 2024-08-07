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
download_slide_tool_site = config.DOWNLOAD_SLIDE_TOOL_SITE
download_slide_video_tool_site = config.DOWNLOAD_SLIDE_VIDEO_TOOL_SITE
download_tool_site_2 = config.DOWNLOAD_TOOL_SITE_2


def iri_to_uri(iri):
    parts = urlsplit(iri)
    uri = urlunsplit(
        (
            parts.scheme,
            parts.netloc.encode("idna").decode("ascii"),
            quote(parts.path),
            quote(parts.query, "="),
            quote(parts.fragment),
        )
    )
    return uri

def get_current_time():
    now = datetime.now()
    return now.strftime("%d/%m/%Y %H:%M:%S")

def get_chat_identity(message):
    chat_identity = "Chat ID: " + str(message.chat.id) + "\n"
    if message.chat.title:
        chat_identity = chat_identity + "Chat title: " + message.chat.title + "\n"
    if message.from_user.username:
        chat_identity = chat_identity + "Username: " + message.from_user.username + "\n"
    if message.from_user.full_name:
        chat_identity = (
            chat_identity + "Full name: " + message.from_user.full_name + "\n"
        )

    return chat_identity

def get_post_description(url):
    post_description = ''
    try:
        req = urllib.request.Request(
            url,
            data=None,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
            },
        )
        url_response = urllib.request.urlopen(req)
        response_data = url_response.read().decode("utf-8")
        soup = BeautifulSoup(response_data, "html.parser")
        author = soup.find("span", {"data-e2e": "browse-username"}).text
        capations = soup.find("meta", {"property":"og:description"})["content"]
        post_description = "@" + author + "\n" + capations
    except Exception as e:
        print("Post description has no find")
    return post_description


@bot.message_handler(content_types=["text"])
def get__content(message):
    if "tiktok.com/" in message.text:
        chat_identity = get_chat_identity(message)

        processing_message = bot.reply_to(message, "Please, wait...\nDownloading...")

        try:
            file = open("id.txt", "r")
        except Exception as e:
            file = open("id.txt", "w")
            file.close()
            file = open("id.txt", "r")
        s = file.read()
        id = int(s) if s != "" else 1
        file.close()
        file = open("id.txt", "w")
        file.write(str(id + 1))
        file.close()
        print(
            "-------------------------"
            + "\n"
            + get_current_time()
            + " id: "
            + str(id)
            + " Chat identity: "
            + "\n"
            + chat_identity
        )
        url_message = message.text
        start_url = url_message.find("https")
        url = iri_to_uri(url_message[start_url:])
        post_description = get_post_description(url)
        print(get_current_time() + " id: " + str(id) + " URL: " + url)

        data = urllib.parse.urlencode(
            {"q": url}
        )
        data = data.encode("ascii")
        req = urllib.request.Request(
            download_tool_site_2,
            data=data,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            },
        )
        try:
            url_response = urllib.request.urlopen(req)
            response_data = url_response.read().decode("utf-8")
            soup = BeautifulSoup(response_data, "html.parser")
            video_link_raw = soup.find_all('a')
            video_link = video_link_raw[0]["href"].replace('"', '').replace("\\", "")
            print('Video link: ' + video_link)
            if video_link != '#':
                opener = urllib.request.build_opener()
                opener.addheaders = [('User-Agent', 'MyApp/1.0')]
                urllib.request.install_opener(opener)
                urllib.request.urlretrieve(video_link, str(id) + ".mp4")
            else:
                data = urllib.parse.urlencode(
                    {"id": url, "locale": "en", "tt": download_tool_site_tt}
                )
                data = data.encode("ascii")
                req = urllib.request.Request(
                    download_tool_site,
                    data=data,
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                    },
                )
                url_response = urllib.request.urlopen(req)
                response_data = url_response.read().decode("utf-8")
                soup = BeautifulSoup(response_data, "html.parser")
                slides_data_element = soup.select('input[name="slides_data"]')
                slides_data_value = slides_data_element[0]["value"]
                data = urllib.parse.urlencode({"slides_data": slides_data_value})
                data = data.encode("ascii")
                req = urllib.request.Request(
                    download_slide_tool_site,
                    data=data,
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
                    },
                )
                slider_url_responce = urllib.request.urlopen(req)
                hx_redirect = slider_url_responce.getheader("Hx-Redirect")
                x_orign = slider_url_responce.getheader("X-Origin")
                slider_video_id = hx_redirect[hx_redirect.rfind("/") + 1 :]
                if 'gor.ssstik.io' not in hx_redirect:
                    slider_video_link = hx_redirect
                else:
                    slider_video_link = (
                        "https://"
                        + x_orign
                        + download_slide_video_tool_site
                        + str(slider_video_id)
                    )
                print(
                    get_current_time()
                    + " id: "
                    + str(id)
                    + " Slider video link: "
                    + slider_video_link
                )
                urllib.request.urlretrieve(slider_video_link, str(id) + ".mp4")

            retry_count = 1
            while retry_count <= 10:
                video = None
                try:
                    video = open(str(id) + ".mp4", "rb")
                    # if retry_count != 1:
                    #     time.sleep(0.5)
                    bot.send_media_group(
                        message.chat.id,
                        [InputMediaVideo(video, None, post_description)],
                        None,
                        message.id,
                    )
                    break
                except Exception as e:
                    bot.send_message(
                        dev_chat_id,
                        "Chat identity: "
                        + chat_identity
                        + "\n"
                        + "Retry send message - "
                        + str(retry_count),
                    )
                    retry_count += 1
                    video.close()
                    if retry_count == 11:
                        raise e

            video.close()
            os.remove(str(id) + ".mp4")
            print(get_current_time() + " id: " + str(id) + " Success")

            bot.delete_message(message.chat.id, processing_message.id)

        except Exception as e:

            bot.delete_message(message.chat.id, processing_message.id)

            if e.args[0] == 'A request to the Telegram API was unsuccessful. Error code: 413. Description: Request Entity Too Large':
                bot.reply_to(message, "Content Entity Too Large!")
            else:
                bot.reply_to(message, "something went wrong")
            print(e.args[0])
            bot.send_message(
                dev_chat_id,
                "Chat identity: "
                + chat_identity
                + "\n"
                + "Error: "
                + str(e)
                + "\n"
                + "URL: "
                + url,
            )
            file = open("logs_errors.txt", "a")
            file.write(
                get_current_time()
                + " id: "
                + str(id)
                + "\n"
                + str(message.chat.id)
                + "\n"
                + url
                + "\n"
                + str(e)
                + "\n"
                + "\n"
            )
            file.close()
            print(
                get_current_time()
                + " id: "
                + str(id)
                + " something went wrong"
                + "\n"
                + str(e)
            )
            try:
                if video:
                    video.close()
                    os.remove(str(id) + ".mp4")
            except Exception as e:
                bot.send_message(
                dev_chat_id,
                "Chat identity: "
                + chat_identity
                + "\n"
                + "Error: "
                + str(e)
                + "\n"
                + "URL: "
                + url,
            )


bot.polling(none_stop=True)
