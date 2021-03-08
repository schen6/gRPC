import random
import re
import requests
import time
from Logger import log


class ZhihuClient(object):
    def __init__(self, random_agent=False, cookie=None):
        '''
        search:offset为20的倍数
        answer:offset为5的倍数
        '''
        self.random_agent = random_agent
        # self.__base_search_url = 'https://www.zhihu.com/api/v4/search_v3?t={}&q={}&offset=%s&limit=20'
        self.__base_search_url = 'https://api.zhihu.com/search_v3?t={}&q={}&offset=%s&limit=20'
        self.__base_answer_url = 'https://www.zhihu.com/api/v4/questions/{}/answers?include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cis_labeled%2Cis_recognized%2Cpaid_info%2Cpaid_info_content%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%2A%5D.topics&limit=5&offset={}&platform=desktop&sort_by=default'
        self.__base_user_url = 'https://api.zhihu.com/people/%s'
        self.__base_comment_answer_url = 'https://www.zhihu.com/api/v4/answers/{}/root_comments?order=reverse&limit=20&offset=%s&status=open'
        self.__base_comment_question_url = 'https://www.zhihu.com/api/v4/questions/{}/root_comments?order=normal&limit=10&offset=%s&status=open'
        self.__base_user_message_url = 'https://www.zhihu.com/api/v4/members/{}/activities?limit=7&desktop=True'
        self.__headers = {
            'referer': 'https://www.zhihu.com',
            'user-agent':
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
            'x-requested-with': 'fetch'
        }
        if cookie:
            self.__headers['cookie'] = cookie
        self.agent_list = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
            'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
            'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
            'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
            'Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon 2.0)',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)'
        ]

    def __cleanText(self, text):
        '''

        :param text:
        :return:
        '''
        text = re.sub('<.*?\w+.*?>', '', text)
        return text

    def __getPictureUrls(self, text):
        '''
        '''
        res = re.findall('<img.*?src="(http.*?)".*?>', text)
        return res

    def __getResponseJson(self, url):
        '''

        :param url:
        :return:
        '''
        try:
            print(url)
            if self.random_agent:
                user_agent = self.agent_list[random.randint(
                    0,
                    len(self.agent_list) - 1)]
                self.__headers['user-agent'] = user_agent
            headers = self.__headers
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                log('ZhihuClient.getResponseJson').logger.error(
                    'error in requests')
                return None
            html = response.json()
            return html
        except Exception as e:
            log('ZhihuClient.getResponseJson').logger.error(e)
            return None

    def __getJsonData(self, html):
        datas = html.get('data')
        if datas is None:
            return None
        # if len(datas) == 0:
        #     return None
        return datas

    def __getJsonDataPaging(self, html):
        paging = html.get('paging')
        if paging is None:
            return None
        return paging

    def __getUserNextUrl(self, html):
        try:
            paging = html.get('paging')
            is_end = paging.get('is_end')
            if is_end:
                return None
            next_url = paging.get('next')
            if next_url is not None:
                return next_url
        except:
            return None

    def __getData(self, url):
        html = self.__getResponseJson(url)
        if html is None:
            return None
        datas = self.__getJsonData(html)
        if datas is None:
            return None

        return datas

    def __getDataV2(self, url):
        html = self.__getResponseJson(url)
        if html is None:
            return None
        datas = self.__getJsonData(html)
        if datas is None:
            return None
        paging = self.__getJsonDataPaging(html)
        return (datas, paging)

    def __getQuestionJsonData(self, datas):
        '''

        :param html:
        :return:
        '''
        for data in datas:
            if data.get('type') is None:
                continue
            else:
                if data['type'] != 'search_result':
                    continue
            yield data

    def __getAnswerJsonData(self, datas):
        '''

        :param html:
        :return:
        '''
        for data in datas:
            if data.get('type') is None:
                continue
            else:
                if data['type'] != 'answer':
                    continue
            yield data

    def __getQuestionDataDict(self, data):
        '''
        分析原始数据， 产出结构化数据
        :param data:
        :return:
        '''
        result = {}
        if data['type'] != 'search_result':
            return None
        if data.get('object').get('question', None) is not None:
            question_id = data.get('object').get('question').get('id')
            title = self.__cleanText(
                data.get('object').get('question').get('name'))
            url = data.get('object').get('question').get('url')
            if question_id is not None:
                result['post_id'] = question_id
                result['title'] = title
                result['url'] = url
                return result
            else:
                return None
        else:
            obj = data.get('object')
            if obj.get('type', '') == 'question':
                question_id = obj.get('id')
                title = self.__cleanText(obj.get('title'))
                url = obj.get('url')
                if question_id is not None:
                    result['post_id'] = question_id
                    result['title'] = title
                    result['url'] = url
                    return result
                else:
                    return None
            else:
                return None

    def __getAnswerDataDict(self, data):
        '''

        :param data:
        :return:
        '''
        result_dict = {}
        question = data.get('question')
        author = data.get('author')
        if question is not None:
            result_dict['post_id'] = question.get('id')
        else:
            result_dict['post_id'] = None
        result_dict['answer_id'] = data.get('id')
        if author is not None:
            result_dict['author_id'] = author.get('id')
            result_dict['author_screen_name'] = author.get('name')
            result_dict['gender'] = author.get('gender')
        else:
            result_dict['author_id'] = None
            result_dict['author_screen_name'] = None
            result_dict['gender'] = None
        # if author.get('name') and author.get('name') == '匿名用户':
        # 	return None
        result_dict['comment_count'] = data.get('comment_count')
        result_dict['like_count'] = data.get('voteup_count')
        result_dict['created_time'] = data.get('created_time')
        result_dict['updated_time'] = data.get('updated_time')
        text = data.get('content')
        if text is not None:
            content = self.__cleanText(text)
            img_urls = self.__getPictureUrls(text)
        # text = re.sub('<p class="ztext-empty"', '', text)
        # text = re.sub('<figure data-size=*.?>', '', text)
        # text = re.sub('<figure data-size=.*?"/>', '', text)
        result_dict['content'] = content
        result_dict['img_urls'] = img_urls
        # result_dict['text'] = text
        result_dict['url'] = data.get('url')
        result_dict['app_code'] = 'zhihu'
        return result_dict

    def __searchQuestion(self, kw, type='general', page=None, full_json=False):
        '''
        查询知乎问题
        :param kw:搜索的关键词
        :param type:搜索的形式,目前只支持综合搜索
        :param max_page:爬取搜索的最大页数, None就是全部爬取
        :return:
        '''
        base_url = self.__base_search_url.format(type, kw)
        results = []
        page = page - 1
        offset = page * 20
        url = base_url % offset
        res = self.__getDataV2(url)
        if res is None:
            return results, 400
        datas, paging = res[0], res[1]
        if not full_json:
            for data in self.__getQuestionJsonData(datas):
                data_dict = self.__getQuestionDataDict(data)
                if data_dict is not None:
                    results.append(data_dict)
        else:
            for data in self.__getQuestionJsonData(datas):
                if data is not None:
                    results.append(data)
        log('ZhihuClient.search').logger.info('search done')
        log('ZhihuClient.searchQuestion').logger.info(
            'start to get page: %s, data: %s' % (page + 1, len(results)))
        return {'results': results, 'paging': paging}, 200

    def __searchAnswer(self, question_id, page=None):
        '''
        查询知乎回答
        :param question_id:问题的id
        :param max_page:最大爬取页数, None就是全部爬取
        :return:
        '''
        results = []
        page = page - 1
        offset = page * 5
        log('ZhihuClient.searchAnswer').logger.info(
            'start to get page: %s, data: %s' % (page + 1, len(results)))
        url = self.__base_answer_url.format(question_id, offset)
        res = self.__getData(url)
        if res is None:
            return results, 400
        datas, paging = res[0], res[1]
        for data in self.__getAnswerJsonData(datas):
            data_dict = self.__getAnswerDataDict(data)
            results.append(data_dict)
        log('ZhihuClient.searchAnswer').logger.info('search done')
        return {'results': results, 'paging': paging}, 200

    def __searchUser(self, user_id):
        '''

        :param user_id:
        :return:
        '''
        try:
            url = self.__base_user_url % user_id
            jsd = self.__getResponseJson(url=url)
            return jsd
        except Exception as e:
            log('ZhihuClient.searchUser').logger.info(e)
            return None

    def __searchUserMessage(self, user_url_token, max_page=None):
        results = []
        page = 0
        next_url = self.__base_user_message_url.format(user_url_token)
        while next_url is not None:
            log('ZhihuClient.searchUserMessage').logger.info(
                'start to get page: %s, data: %s' % (page + 1, len(results)))
            jsd = self.__getResponseJson(url=next_url)
            next_url = self.__getUserNextUrl(jsd)
            data = self.__getJsonData(jsd)
            if data is None:
                break
            results.extend(data)
            page += 1
            time.sleep(random.random())
            if max_page is not None:
                if page >= max_page:
                    log('ZhihuClient.searchUserMessage').logger.info(
                        'get max page: %s' % max_page)
                    break
        log('ZhihuClient.searchUserMessage').logger.info('search done')
        return results

    def __searchComments(self, id, max_page=None, type='answer'):
        '''

        :param answer_id:
        :return:
        '''
        results = []
        page = 0
        if type == 'answer':
            step = 20
        else:
            step = 10
        offset = page * step
        datas = ['']
        if type == 'answer':
            base_url = self.__base_comment_answer_url.format(id)
        else:
            base_url = self.__base_comment_question_url.format(id)
        while datas is not None:
            log('ZhihuClient.searComments').logger.info(
                'start to get page: %s, data: %s' % (page + 1, len(results)))
            url = base_url % offset
            data = self.__getData(url)
            if data is None:
                break
            for d in data:
                if type == 'answer':
                    d['answer_id'] = id
                else:
                    d['question_id'] = id
            results.extend(data)
            page += 1
            offset = page * step
            time.sleep(random.random())
            if max_page is not None:
                if page >= max_page:
                    log('ZhihuClient.searchComment').logger.info(
                        'get max page: %s' % max_page)
                    break
        log('ZhihuClient.searchComment').logger.info('search done')
        return results

    def search(self,
               kw=None,
               question_id=None,
               page=None,
               user_id=None,
               answer_id=None,
               user_url_token=None,
               full_json=False,
               type='question'):
        '''

        :param kw:
        :param question_id:
        :param page:
        :param type: 'question':问题搜索, 'answer':查找回答
        :return:
        '''
        assert type in [
            'question', 'answer', 'user', 'comment_answer', 'user_message',
            'comment_question'
        ], log('ZhihuClient.search').logger.error(
            'type must be question or answer or user or comment')
        if type == 'question':
            assert kw is not None, log('ZhihuClient.search').logger.error(
                'if you want to search question, kw can not be None')
            results, code = self.__searchQuestion(kw=kw,
                                                  page=page,
                                                  full_json=full_json)
            return results, code
        elif type == 'answer':
            assert question_id is not None, log(
                'ZhihuClient.search').logger.error(
                    'if you want to search answer, question_id can not be None'
                )
            results, code = self.__searchAnswer(question_id=question_id,
                                                page=page)
            return results, code
        # elif type == 'user':
        #     assert user_id is not None, log('ZhihuClient.search').logger.error(
        #         'if you want to search user, user_id can not be None')
        #     result = self.__searchUser(user_id=user_id)
        #     return result
        # elif type == 'comment_answer':
        #     assert answer_id is not None, log(
        #         'ZhihuClient.search'
        #     ).logger.error(
        #         'if you want to search comment_answer, answer_id can not be None'
        #     )
        #     result = self.__searchComments(id=answer_id,
        #                                    max_page=page,
        #                                    type='answer')
        #     return result
        # elif type == 'comment_question':
        #     assert question_id is not None, log(
        #         'ZhihuClient.search'
        #     ).logger.error(
        #         'if you want to search comment_question, question_id can not be None'
        #     )
        #     result = self.__searchComments(id=question_id,
        #                                    max_page=page,
        #                                    type='question')
        #     return result
        # elif type == 'user_message':
        #     assert user_url_token is not None, log(
        #         'ZhihuClient.search'
        #     ).logger.error(
        #         'if you want to search user_message, user_url_token can not be None'
        #     )
        #     result = self.__searchUserMessage(user_url_token=user_url_token,
        #                                       max_page=page)
        #     return result


if __name__ == "__main__":
    pass