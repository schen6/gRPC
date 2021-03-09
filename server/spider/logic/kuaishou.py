# coding:utf-8
import os
import sys
import requests
import time
from Logger import log


class KuaishouClientV2:
    def __init__(self):
        self.__headers = {
            'User-Agent':
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
            'Host': 'video.kuaishou.com'
        }
        self.__graphql = 'https://video.kuaishou.com/graphql'
        self.__user_video_json = {
            "operationName":
            "visionProfilePhotoList",
            "variables": {
                "userId": "3xssjbdgqd35xfi",
                "pcursor": "",
                "page": "profile"
            },
            "query":
            "query visionProfilePhotoList($pcursor: String, $userId: String, $page: String) {\n  visionProfilePhotoList(pcursor: $pcursor, userId: $userId, page: $page) {\n    result\n    llsid\n    feeds {\n      type\n      author {\n        id\n        name\n        following\n        headerUrl\n        headerUrls {\n          cdn\n          url\n          __typename\n        }\n        __typename\n      }\n      tags {\n        type\n        name\n        __typename\n      }\n      photo {\n        id\n        duration\n        caption\n        likeCount\n        realLikeCount\n        coverUrl\n        coverUrls {\n          cdn\n          url\n          __typename\n        }\n        photoUrls {\n          cdn\n          url\n          __typename\n        }\n        photoUrl\n        liked\n        timestamp\n        expTag\n        __typename\n      }\n      canAddComment\n      currentPcursor\n      llsid\n      status\n      __typename\n    }\n    hostName\n    pcursor\n    __typename\n  }\n}\n"
        }
        self.__search_video_json = {
            "operationName":
            "visionSearchPhoto",
            "variables": {
                "keyword": "搜索",
                "pcursor": "",
                "page": "searchPhoto"
            },
            "query":
            "query visionSearchPhoto($keyword: String, $pcursor: String, $searchSessionId: String, $page: String) {\n  visionSearchPhoto(keyword: $keyword, pcursor: $pcursor, searchSessionId: $searchSessionId, page: $page) {\n    result\n    llsid\n    feeds {\n      type\n      author {\n        id\n        name\n        following\n        headerUrl\n        headerUrls {\n          cdn\n          url\n          __typename\n        }\n        __typename\n      }\n      tags {\n        type\n        name\n        __typename\n      }\n      photo {\n        id\n        duration\n        caption\n        likeCount\n        realLikeCount\n        coverUrl\n        photoUrl\n        liked\n        timestamp\n        expTag\n        coverUrls {\n          cdn\n          url\n          __typename\n        }\n        photoUrls {\n          cdn\n          url\n          __typename\n        }\n        __typename\n      }\n      canAddComment\n      currentPcursor\n      llsid\n      status\n      __typename\n    }\n    searchSessionId\n    pcursor\n    aladdinBanner {\n      imgUrl\n      link\n      __typename\n    }\n    __typename\n  }\n}\n"
        }
        self.__comment_json = {
            "operationName":
            "commentListQuery",
            "variables": {
                "photoId": "",
                "pcursor": ""
            },
            "query":
            "query commentListQuery($photoId: String, $pcursor: String) {\n  visionCommentList(photoId: $photoId, pcursor: $pcursor) {\n    commentCount\n    pcursor\n    rootComments {\n      commentId\n      authorId\n      authorName\n      content\n      headurl\n      timestamp\n      likedCount\n      realLikedCount\n      liked\n      status\n      subCommentCount\n      subCommentsPcursor\n      subComments {\n        commentId\n        authorId\n        authorName\n        content\n        headurl\n        timestamp\n        likedCount\n        realLikedCount\n        liked\n        status\n        replyToUserName\n        replyTo\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n"
        }

    def __getResponse(self, url, proxy=None, ajax=True, type='video'):
        '''

        :param url:
        :param ajax:
        :param proxy:
        :param type: ['video', 'search', 'comment']
        :return:
        '''
        try:
            type_dict = {
                'video': self.__user_video_json,
                'search': self.__search_video_json,
                'comment': self.__comment_json
            }
            count = 0
            while count < 5:
                if proxy is not None:
                    p = proxy()
                    proxies = {'http': 'http://' + p, 'https': 'https://' + p}
                    response = requests.post(url,
                                             headers=self.__headers,
                                             json=type_dict.get(type),
                                             proxies=proxies)
                else:
                    response = requests.post(url,
                                             headers=self.__headers,
                                             json=type_dict.get(type))
                if response.status_code != 200:
                    log('KuaishouClient.__getResponse').logger.error(
                        'error in request')
                else:
                    break
                count += 1
            if response.status_code != 200:
                log('KuaishouClient.__getResponse').logger.error(
                    'error in request')
                return None
            response.encoding = 'utf-8'
            if ajax:
                return response.json()
            else:
                return response.text
        except Exception as e:
            msg = 'On line {} - {}'.format(sys.exc_info()[2].tb_lineno, e)
            log('KuaishouClient.__getResponse').logger.error(msg)
            return None

    def __getPcursor(self, jsd, type='video'):
        '''
        获取翻页的pcursor
        :param jsd:
        :param type: ['video', 'search']
        :return:
        '''
        assert jsd is not None, log(
            'KuaishouClient.__getPcursor').logger.error('jsd is None')
        try:
            pcursor = None
            data = jsd.get('data')
            if type == 'video':
                visionProfilePhotoList = data.get('visionProfilePhotoList', {})
                pcursor = visionProfilePhotoList.get('pcursor', None)
            elif type == 'search':
                visionSearchPhoto = data.get('visionSearchPhoto', {})
                pcursor = visionSearchPhoto.get('pcursor', None)
            elif type == 'comment':
                visionCommentList = data.get('visionCommentList', {})
                pcursor = visionCommentList.get('pcursor', None)
            if pcursor is not None:
                return pcursor
            else:
                return None
        except Exception as e:
            msg = 'On line {} - {}'.format(sys.exc_info()[2].tb_lineno, e)
            log('KuaishouClient.__getPcursor').logger.error(msg)
            return None

    def __getUserVideoList(self, jsd):
        '''

        :param jsd:
        :return:
        '''
        assert jsd is not None, log(
            'KuaishouClient.__getUserVideoList').logger.error('jsd is None')
        try:
            data = jsd.get('data')
            visionProfilePhotoList = data.get('visionProfilePhotoList')
            videoList = visionProfilePhotoList.get('feeds')
            if videoList is not None and len(videoList) > 0:
                return videoList
            else:
                return None
        except Exception as e:
            msg = 'On line {} - {}'.format(sys.exc_info()[2].tb_lineno, e)
            log('KuaishouClient.__getUserVideoList').logger.error(msg)
            return None

    def __getSearchVideoList(self, jsd):
        assert jsd is not None, log(
            'KuaishouClient.__getSearchVideoList').logger.error('jsd is None')
        try:
            data = jsd.get('data')
            visionSearchPhoto = data.get('visionSearchPhoto')
            videoList = visionSearchPhoto.get('feeds')
            if videoList is not None and len(videoList) > 0:
                return videoList
            else:
                return None
        except Exception as e:
            msg = 'On line {} - {}'.format(sys.exc_info()[2].tb_lineno, e)
            log('KuaishouClient.__getSearchVideoList').logger.error(msg)
            return None

    def __getCommentList(self, jsd):
        assert jsd is not None, log(
            'KuaishouClient.__getCommentList').logger.error('jsd is None')
        try:
            data = jsd.get('data')
            visionCommentList = data.get('visionCommentList')
            commentCount = visionCommentList.get('commentCount', 0)
            commentList = visionCommentList.get('rootComments')

            def func(item):
                item['totalCommentCount'] = commentCount
                return item

            commentList = [func(i) for i in commentList]
            if commentList is not None and len(commentList) > 0:
                return commentList
            else:
                return None
        except Exception as e:
            msg = 'On line {} - {}'.format(sys.exc_info()[2].tb_lineno, e)
            log('KuaishouClient.__getSearchVideoList').logger.error(msg)
            return None

    def getUserVideoData(self, user_id, proxy=None, max_size=20):
        '''

        :param user_id:
        :return:
        '''
        data = {}
        videoLists = []
        url = self.__graphql
        self.__user_video_json['variables']['principalId'] = str(user_id)
        count = 0
        try:
            jsd = self.__getResponse(url=url,
                                     ajax=True,
                                     type='video',
                                     proxy=proxy)
            pcursor = self.__getPcursor(jsd, type='video')
            videoList = self.__getUserVideoList(jsd)
            videoLists.extend(videoList)
            while pcursor is not None and pcursor != 'no_more':
                self.__user_video_json['variables']['pcursor'] = pcursor
                jsd = self.__getResponse(url=url,
                                         ajax=True,
                                         type='video',
                                         proxy=proxy)
                pcursor = self.__getPcursor(jsd, type='video')
                videoList = self.__getUserVideoList(jsd)
                count += len(videoList)
                time.sleep(0.2)
                if videoList is None or len(videoList) == 0:
                    continue
                videoLists.extend(videoList)
                print('already get %s data' % count)
                if count > max_size:
                    break
            data['videoLists'] = videoLists
            return data
        except Exception as e:
            msg = 'On line {} - {}'.format(sys.exc_info()[2].tb_lineno, e)
            log('KuaishouClient.getVideoData').logger.error(msg)
            return data

    def getSearchVideoData(self, kw, proxy=None, max_size=20):
        '''

        :param kw:
        :return:
        '''
        data = {}
        videoLists = []
        url = self.__graphql
        self.__search_video_json['variables']['keyword'] = kw
        count = 0
        try:
            jsd = self.__getResponse(url=url,
                                     ajax=True,
                                     type='search',
                                     proxy=proxy)
            pcursor = self.__getPcursor(jsd, type='search')
            videoList = self.__getSearchVideoList(jsd)
            videoLists.extend(videoList)
            while pcursor is not None and pcursor != 'no_more':
                self.__search_video_json['variables']['pcursor'] = pcursor
                jsd = self.__getResponse(url=url,
                                         ajax=True,
                                         type='search',
                                         proxy=proxy)
                pcursor = self.__getPcursor(jsd, type='search')
                videoList = self.__getSearchVideoList(jsd)
                count += len(videoList)
                time.sleep(0.2)
                if videoList is None or len(videoList) == 0:
                    continue
                videoLists.extend(videoList)
                print('already get %s data' % count)
                if count > max_size:
                    break
            data['videoLists'] = videoLists
            return data
        except Exception as e:
            msg = 'On line {} - {}'.format(sys.exc_info()[2].tb_lineno, e)
            log('KuaishouClient.getVideoData').logger.error(msg)
            return data

    def getCommentData(self, video_id, proxy=None, max_size=20):
        '''
        '''
        data = {}
        commentLists = []
        url = self.__graphql
        self.__comment_json['variables']['photoId'] = video_id
        count = 0
        try:
            jsd = self.__getResponse(url=url,
                                     ajax=True,
                                     type='comment',
                                     proxy=proxy)
            pcursor = self.__getPcursor(jsd, type='comment')
            commentList = self.__getCommentList(jsd)
            commentLists.extend(commentList)
            while pcursor is not None and pcursor != 'no_more':
                self.__comment_json['variables']['pcursor'] = pcursor
                jsd = self.__getResponse(url=url,
                                         ajax=True,
                                         type='comment',
                                         proxy=proxy)
                pcursor = self.__getPcursor(jsd, type='comment')
                commentList = self.__getCommentList(jsd)
                count += len(commentList)
                time.sleep(0.2)
                if commentList is None or len(commentList) == 0:
                    continue
                commentLists.extend(commentList)
                print('already get %s data' % count)
                if count > max_size:
                    break
            data['commentLists'] = commentLists
            return data
        except Exception as e:
            msg = 'On line {} - {}'.format(sys.exc_info()[2].tb_lineno, e)
            log('KuaishouClient.getCommentData').logger.error(msg)
            return data

    def getData(self, t, obj, cookie=None, proxy=None, pcursor=None):
        '''
        t: ['video', 'search', 'comment']
        obj: 
            t='video' -> obj is user_id
            t='search' -> obj is search kw
            t='comment' -> obj is video_id
        '''
        # cookie必须有而且不为空
        if cookie is not None and len(cookie) > 0:
            self.__headers['Cookie'] = cookie
        else:
            return None, 404
        dataLists = []
        url = self.__graphql
        count = 0
        try:
            if t not in ['video', 'search', 'comment']:
                return None, 400
            type_dict = {
                'video': (self.__user_video_json, 'principalId',
                          self.__getUserVideoList),
                'search': (self.__search_video_json, 'keyword',
                           self.__getSearchVideoList),
                'comment':
                (self.__comment_json, 'photoId', self.__getCommentList)
            }
            json_data, json_kw, getListFunc = type_dict.get(t, None)
            json_data['variables'][json_kw] = obj
            if pcursor is not None:
                json_data['variables']['pcursor'] = pcursor
            jsd = self.__getResponse(url=url, ajax=True, type=t, proxy=proxy)
            print(jsd)
            if jsd is None:
                return None, 404
            pcursor = self.__getPcursor(jsd, type=t)
            dataList = getListFunc(jsd)
            count += len(dataList)
            print('already get %s data' % count)
            dataLists.extend(dataList)
            return {'results': dataLists, 'pcursor': pcursor}, 200
        except Exception as e:
            msg = 'On line {} - {}'.format(sys.exc_info()[2].tb_lineno, e)
            log('KuaishouClient.getData').logger.error(msg)
            return None, 400


if __name__ == "__main__":
    #example:
    cookie = ''
    client = KuaishouClientV2()
    # result = client.getData(t='search', obj="干饭人", max_page=3)
    result = client.getData(t='comment', obj='3xutz63pmuquyqm', cookie=cookie)
    # result = client.getData(t='video', obj='3xssjbdgqd35xfi', max_page=1)
    print(result)
