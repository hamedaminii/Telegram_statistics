import json
from collections import Counter, defaultdict
from typing import Union
from pathlib import Path
from loguru import logger
from src.data import DATA_DIR

from wordcloud import WordCloud
from bidi.algorithm import get_display
import arabic_reshaper



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
        self.stop_words = set(map(str.strip, stop_words))

    @staticmethod
    def rebuild_messages(sub_messages):
        """Rebuild masseges with unsuitable content
        """
        msg_txt = ''
        for sub in sub_messages:
            if isinstance(sub, str):
                msg_txt += sub
            elif 'text' in sub:
                msg_txt += sub['text']
        return msg_txt

    def msg_has_question(self, msg):
        """The message is question or not?
        :param msg: message to check
        """
        if not isinstance(msg['text'], str):
            msg['text'] = self.rebuild_messages(msg['text'])
        if ('?' in msg['text']) or ('؟' in msg['text']):
            return True
    

    def get_top_users(self, top_n: int = 10) :
        """identifying top users
        :param top_n: numbert of top users, defaults to 10
        :return: dict of top users
        """
        is_question = defaultdict(bool)
        for msg in self.chat_data['messages']:
            if not isinstance(msg['text'], str):
                msg['text'] = self.rebuild_messages(msg['text'])
            if ('?' in msg['text']) or ('؟' in msg['text']):
                is_question[msg['id']] = True

        logger.info("Getting top users")
        # top users based on replying to question messages
        Reply_Users = []
        for msg in self.chat_data['messages']:
            if not msg.get('from'):
                continue
            if not msg.get('reply_to_message_id'):
                continue
            if is_question[msg['reply_to_message_id']] is False:
                continue
            Reply_Users.append(msg['from'])
        return dict(Counter(Reply_Users).most_common(top_n))

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
        text_content = get_display(text_content)
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
top_users = chatstats.get_top_users()
print(top_users)

print('Done !') 

