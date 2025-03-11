import os
import pickle

from utils import logger

class Config(object):
    def __init__(self, cache: str):
        if not os.path.exists(cache):
            os.makedirs(cache)
        
        self.__config = os.path.join(cache, "config.bin")
        self.__media_token_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mediaUserToken.txt")

        if not os.path.exists(self.__config):
            mediaUserToken = self.__read_media_user_token()
            storeFront = input("\tstoreFront: ") 
            language = input("\tlanguage: ") 

            if not mediaUserToken:
                logger.info(
                "Warning: mediaUserToken.txt not found or the file is empty. The program will continue to run, but lyrics cannot be retrieved."
            )
            
            print()

            __config = {
                "contentType": "configuration",
                "mediaUserToken": mediaUserToken,
                "storeFront": storeFront,
                "language": language,
            }

            with open(self.__config, 'wb') as c:
                pickle.dump(__config, c)

    def get(self, key):
        with open(self.__config, 'rb') as c:
            __config = pickle.load(c)
        return __config.get(key)

    def set(self, key, value):
        with open(self.__config, 'rb') as c:
            __config = pickle.load(c)

        __config[key] = value

        with open(self.__config, 'wb') as c:
            pickle.dump(__config, c)

    def delete(self, key):
        with open(self.__config, 'rb') as c:
            __config = pickle.load(c)

        if key in __config:
            del __config[key]

        with open(self.__config, 'wb') as c:
            pickle.dump(__config, c)

    def __read_media_user_token(self):
        try:
            with open(self.__media_token_file, 'r') as f:
                token = f.read() 
                logger.info("Token read successfully!")
                return token if token else None
        except FileNotFoundError:
            return None