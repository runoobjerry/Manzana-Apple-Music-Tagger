import re
import json
import requests

from bs4 import BeautifulSoup
from urllib.parse import urlparse
from urllib.request import urlopen
from urllib.error import URLError, HTTPError

from utils import Cache
from utils import Config
from utils import logger

from api.parse import parseJson

class AppleMusic(object):
    def __init__(self, cache, sync, skipVideo):
        self.session = requests.Session()
        self.session.headers = {
            'content-type': 'application/json;charset=utf-8',
            'connection': 'keep-alive',
            'accept': 'application/json',
            'origin': 'https://music.apple.com',
            'referer': 'https://music.apple.com/',
            'accept-encoding': 'gzip, deflate, br',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
        }

        self.__cache = Cache(cache)
        self.__config = Config(cache)

        self.sync = int(sync)
        self.skipVideo = skipVideo

        self.__accessToken()
        self.__mediaUserToken()

    def __checkUrl(self, url):
        try:
            urlopen(url)
            return True
        except (URLError, HTTPError):
            return False

    def __getUrl(self, url):
        __url = urlparse(url)

        if not __url.scheme:
            url = f"https://{url}"

        if __url.netloc == "music.apple.com":
            if self.__checkUrl(url):
                splits = url.split('/')

                id = splits[-1]
                kind = splits[4]

                if kind == "album":
                    if len(id.split('?i=')) > 1:
                        id = id.split('?i=')[1]
                        kind = "song"

                self.kind = kind
                self.id = id

            else: logger.error("URL is invalid!", 1)
        else: logger.error("URL is invalid!", 1)

    def __accessToken(self):
        accessToken = self.__cache.get("accessToken")

        if not accessToken:
            logger.info("Fetching access token from web...")
            response = requests.get('https://music.apple.com/us/browse')

            if response.status_code != 200:
                logger.error("Failed to get music.apple.com! Please re-try...", 1)
            
            content = BeautifulSoup(response.text, "html.parser")

            indexJs = content.find(
                "script",
                attrs={
                    'type': 'module',
                    'crossorigin': True,
                    'src': True
                }
            ).get('src')

            response = requests.get(f'https://music.apple.com{indexJs}')

            if response.status_code != 200:
                logger.error("Failed to get JavaScript library! Please re-try...", 1)

            accessToken = re.search('(?=eyJh)(.*?)(?=")', response.text).group(1)
            self.__cache.set("accessToken", accessToken)
        else:
            logger.info("Checking access token found in cache...")

            self.session.headers.update(
                {
                    'authorization': f'Bearer {accessToken}'
                }
            )

            response = self.session.get("https://amp-api.music.apple.com/v1/catalog/us/songs/1450330685")

            if response.text == '':
                logger.info("Access token found in cache is expired!")

                self.__cache.delete("access_token")
                self.__accessToken()
        
        self.session.headers.update(
            {
                'authorization': f'Bearer {accessToken}'
            }
        )

    def __mediaUserToken(self):
        if self.__config.get('mediaUserToken'):
            logger.info("Checking media-user-token...")

            self.session.headers.update(
                {
                    "media-user-token": self.__config.get("mediaUserToken")
                }
            )

            response = self.session.get("https://amp-api.music.apple.com/v1/me/storefront")

            if response.status_code == 200:
                response = json.loads(response.text)

                self.storefront = response["data"][0]["id"]
                self.language = response["data"][0]["attributes"]["defaultLanguageTag"]

                self.session.headers.update(
                    {
                        'accept-language': f'{self.language},en;q=0.9'
                    }
                )

                self.isMediaUserToken = True
            else:
                logger.error("Invalid media-user-token! Passing over the user subscription...")
                self.__config.delete('mediaUserToken')
        else:
            self.storefront = 'cn'
            self.language = 'zh-Hans-CN'
            self.isMediaUserToken = False

    def __getErrors(self, errors):
        if not isinstance(errors, list):
            errors = [errors]
        for error in errors:
            err_status = error.get("status")
            err_detail = error.get("detail")
            logger.error(f"{err_status} - {err_detail}", 1)

    def __getJson(self, storefront=None):
        """获取指定storefront的API数据"""
        original_storefront = self.storefront
        original_language = self.language

        # 临时切换storefront和language
        if storefront:
            self.storefront = storefront
            self.language = 'en-US' if storefront == 'us' else 'en-GB'

        apiUrl = f'https://amp-api.music.apple.com/v1/catalog/{self.storefront}/{self.kind}s/{self.id}'
        
        # 参数逻辑（根据kind调整）
        if self.kind in ["album", "song"]:
            params = {
                'extend': 'editorialVideo',
                'include[songs]': 'albums,lyrics,credits',
                'l': self.language
            }
        elif self.kind == "music-video":
            params = {'l': self.language}

        self.session.params = params

        # 发送请求
        response = self.session.get(apiUrl)
        response_data = json.loads(response.text)

        # 恢复原始storefront和language
        if storefront:
            self.storefront = original_storefront
            self.language = original_language

        if "errors" in response_data:
            self.__getErrors(response_data)
        else:
            cacheKey = f"{self.id}:{storefront}" if storefront else f"{self.id}:{original_storefront}"
            self.__cache.set(cacheKey, response_data)
            return response_data

    def getInfo(self, url):
        self.__getUrl(url)

        # 第一次请求：用户指定地区的API（获取常规标签和Credits的值）
        local_data = self.__getJson()

        # 第二次请求：US地区的API（仅获取Credits的键名）
        us_data = self.__getJson(storefront='us')

        # 合并Credits的键名和值
        if self.kind == "song":
            local_credits = local_data["data"][0]["relationships"].get("credits", {}).get("data", [])
            us_credits = us_data["data"][0]["relationships"].get("credits", {}).get("data", [])
            merged_credits = self.__merge_credits(local_credits, us_credits)
            local_data["data"][0]["relationships"]["credits"]["data"] = merged_credits
        elif self.kind == "album":
            local_tracks = local_data["data"][0]["relationships"]["tracks"]["data"]
            us_tracks = us_data["data"][0]["relationships"]["tracks"]["data"]
            for local_track, us_track in zip(local_tracks, us_tracks):
                local_credits = local_track["relationships"].get("credits", {}).get("data", [])
                us_credits = us_track["relationships"].get("credits", {}).get("data", [])
                merged_credits = self.__merge_credits(local_credits, us_credits)
                local_track["relationships"]["credits"]["data"] = merged_credits

        # 传递给parseJson处理
        if self.kind == "album":
            return parseJson(
                local_data["data"][0]["relationships"]["tracks"]["data"],
                self.sync,
                self.skipVideo
            )
        elif self.kind == "song":
            return parseJson(
                local_data["data"],
                self.sync
            )
        elif self.kind == "music-video":
            return parseJson(
                local_data["data"],
                self.sync
            )
    def __merge_credits(self, local_credits, us_credits):
        merged = []
        # 构建US Credits的艺术家ID到角色名的映射
        us_role_map = {}
        for category in us_credits:
            for credit in category["relationships"]["credit-artists"]["data"]:
                artist_id = credit["id"]
                us_role_map[artist_id] = credit["attributes"]["roleNames"]
        # 合并数据
        for category in local_credits:
            new_category = {"relationships": {"credit-artists": {"data": []}}}
            for credit in category["relationships"]["credit-artists"]["data"]:
                artist_id = credit["id"]
                # 使用US的键名，保留本地的艺术家名称
                merged_credit = {
                    "id": artist_id,
                    "attributes": {
                        "name": credit["attributes"]["name"],
                        "roleNames": us_role_map.get(artist_id, ["Unknown"])
                    }
                }
                new_category["relationships"]["credit-artists"]["data"].append(merged_credit)
            merged.append(new_category)
        return merged