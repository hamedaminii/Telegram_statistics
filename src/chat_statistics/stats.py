from typing import Union
from pathlib import Path
import json
from src.data import DATA_DIR

from collections import Counter
from wordcloud import WordCloud
from bidi.algorithm import get_display
import arabic_reshaper
from loguru import logger


class Chatstatistics:

    def __init__(self, chat_Json: Union[str, Path] ):
        """
        :param chat_Json: Json file of telegram chats
        """
        # reading Json file
        logger.info(f'loading chat data from {chat_Json}')
        with open(chat_Json) as f:
            self.chat_data = json.load(f)
        # reading stop_words
        logger.info(f"loading stopwords from {DATA_DIR / 'Stop_words.txt'}")
        stop_words = open(DATA_DIR / 'Stop_words.txt').readlines()
        self.stop_words = list(map(str.strip, stop_words))


    def generate_wordcloud(
        self, 
        output_dir = Union[str, Path], 
        width: int = 1000, height: int = 800,
        max_font_size: int = 250,
        ): 
        """Generating wordcloud from chat_Json file0
        :param output_dir: saving directory of wordcloud image
        :param width: wordcloud width
        :param height:wordcloud height
        """
        self.width = width
        self.height = height
        #genrating text_content
        logger.info('Generating text content')
        text_content = ''
        for msg in self.chat_data['messages']:
            if type(msg['text']) is  str:
                tokens = msg['text'].split()
                tokens = list(filter(lambda item: item not in self.stop_words, tokens))           
                text_content += f" {' '.join(tokens)}"
        
        text_content = arabic_reshaper.reshape(text_content)
        #Generating wordcloud
        logger.info('Generating word cloud')
        wordcloud = WordCloud( 
            width= self.width, height = self.height,
            max_font_size = max_font_size,
            font_path = str(DATA_DIR / 'font.ttf'),
            ).generate(text_content)
        logger.info(f'Saving word cloud to {output_dir}')
        wordcloud.to_file(str(Path(output_dir) / 'wordcloud.png' ))



chatstats = Chatstatistics(chat_Json = DATA_DIR / 'result-koperz.json') 
chatstats.generate_wordcloud(output_dir = DATA_DIR)

print('Done !') 

