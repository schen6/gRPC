import os
import sys
import torch
import lightgbm as lgb
import re
import regex
from pytorch_pretrained_bert import BertModel, BertTokenizer

current_path = os.path.realpath(__file__)
root_path = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(current_path))))
sys.path.append(root_path)

from Logger import log
from conf.conf import Config

conf = Config()
tokenizer = BertTokenizer.from_pretrained(
    os.path.join(conf.model_path, 'chinese_L-12_H-768_A-12/vocab.txt'))
bert = BertModel.from_pretrained(
    os.path.join(conf.model_path, 'chinese_L-12_H-768_A-12'))
bert.eval()
for param in bert.parameters():
    param.requires_grad = False
model = lgb.Booster(
    model_file=os.path.join(conf.model_path, 'google_bert_base_lgb_large_202202.txt'))
log('texttools.getSentiment').logger.info('model ready')


def tidyText(text):
    '''

	:param text:string
	:return: 处理过的text:string
	'''
    # removes return carriages, links, newlines, @accounts
    text = str(text)
    text = re.sub(r"\r|\n|http\S+|\\n|@(.*?)(\s|$)", "", text)
    # removes dingbats and other unicode character classes
    text = regex.sub(r"\p{S}|\p{C}|\p{M}|\p{No}", "", text)
    # converts all traditional chinese characters to simplified chinese
    return text


def getSentiment(text):
    log('texttools.getSentiment').logger.info('get sentiment analysis: %s' %
                                              text)
    # text = tidyText(text)
    try:
        if len(text) > 512:
            text = text[:512]
        tokens = tokenizer.tokenize(text)
        tokens = ["[CLS]"] + tokens + ["[SEP]"]
        ids = torch.tensor([tokenizer.convert_tokens_to_ids(tokens)])
        encoded_layers, result = bert(ids)
        # return result
        embedding = encoded_layers[-2].numpy()[0]
        res = sum(embedding) / embedding.shape[0]
        log('texttools.getSentiment').logger.info('get results text: %s' %
                                                  text)
        test_data = [res]
        pred = model.predict(test_data)
        pred = pred[0]
        if pred <= 0.55 and pred > 0.45:
            sentiment = 1
        elif pred > 0.55:
            sentiment = 2
        else:
            sentiment = 0
        return sentiment, pred
    except:
        return None


if __name__ == '__main__':
    print(getSentiment('你妈死了'))
