from concurrent import futures
import os
import sys
import grpc
import json

current_path = os.path.realpath(__file__)
root_path = os.path.dirname(os.path.dirname(os.path.dirname(current_path)))
sys.path.append(root_path)

import server.spider.spider_pb2 as spider_pb2
import server.spider.spider_pb2_grpc as spider_pd2_grpc
from Logger import log
from conf.conf import Config
from server.spider.logic.zhihu import ZhihuClient
from server.spider.logic.kuaishou import KuaishouClientV2

conf = Config()
zh_client = ZhihuClient(cookie=conf.zhihu_cookie)

ks_client = KuaishouClientV2()


class Spider(spider_pd2_grpc.SpiderServicer):
    def Zhihu(self, request, content):
        try:
            data = request.data
            data = json.loads(data)
            t = data.get('type', None)
            if t not in ['question', 'answer']:
                results = {'status_code': 400, 'message': 'invalid type'}
                return spider_pb2.Results(
                    result=json.dumps(results, ensure_ascii=False))
            page = int(data.get('page', 1))
            if t == 'question':
                kw = data.get('kw', '')
                if not kw:
                    results = {'status_code': 400, 'message': 'invalid kw'}
                    return spider_pb2.Results(
                        result=json.dumps(results, ensure_ascii=False))
                results, code = zh_client.search(type=t, kw=kw, page=page)
                if code != 200:
                    results = {
                        'status_code': code,
                        'message': 'error happened'
                    }
                    return spider_pb2.Results(
                        result=json.dumps(results, ensure_ascii=False))
                results = {'status_code': code, 'message': '', 'data': results}
                return spider_pb2.Results(
                    result=json.dumps(results, ensure_ascii=False))
            elif t == 'answer':
                question_id = data.get('question_id', '')
                if not question_id:
                    results = {
                        'status_code': 400,
                        'message': 'invalid question_id'
                    }
                    return spider_pb2.Results(
                        result=json.dumps(results, ensure_ascii=False))
                results, code = zh_client.search(type=t,
                                                 question_id=question_id,
                                                 page=page)
                if code != 200:
                    results = {
                        'status_code': code,
                        'message': 'error happened'
                    }
                    return spider_pb2.Results(
                        result=json.dumps(results, ensure_ascii=False))
                results = {'status_code': code, 'message': '', 'data': results}
                return spider_pb2.Results(
                    result=json.dumps(results, ensure_ascii=False))
        except Exception as e:
            msg = 'On line {} - {}'.format(sys.exc_info()[2].tb_lineno, e)
            log('Spider.Zhihu').logger.error(msg)
            return

    def Kuaishou(self, request, content):
        try:
            data = request.data
            data = json.loads(data)
            cookie = data.get('cookie', None)
            if cookie is None:
                results = {
                    'status_code': 400,
                    'message': 'cookie can not be none'
                }
                return spider_pb2.Results(
                    result=json.dumps(results, ensure_ascii=False))
            t = data.get('type', None)
            if t == 'video':
                obj = data.get('user_id', None)
            elif t == 'search':
                obj = data.get('kw', None)
            elif t == 'comment':
                obj = data.get('video_id', None)
            else:
                obj = None
            if obj is None:
                results = {
                    'status_code': 400,
                    'message': 'obj can not be none'
                }
                return spider_pb2.Results(
                    result=json.dumps(results, ensure_ascii=False))
            pcursor = data.get('pcursor', None)
            res, code = ks_client.getData(t=t,
                                          obj=obj,
                                          cookie=cookie,
                                          pcursor=pcursor)
            if code != 200:
                if code == 404:
                    results = {
                        'status_code': code,
                        'message': 'error in requests'
                    }
                    return spider_pb2.Results(
                        result=json.dumps(results, ensure_ascii=False))
                else:
                    results = {
                        'status_code': code,
                        'message': 'error happened in code'
                    }
                    return spider_pb2.Results(
                        result=json.dumps(results, ensure_ascii=False))
            else:
                results = {'status_code': code, 'message': '', 'data': res}
                return spider_pb2.Results(
                    result=json.dumps(results, ensure_ascii=False))
        except Exception as e:
            msg = 'On line {} - {}'.format(sys.exc_info()[2].tb_lineno, e)
            log('Spider.Zhihu').logger.error(msg)
            results = {
                'status_code': 400,
                'message': msg,
            }
            return spider_pb2.Results(
                result=json.dumps(results, ensure_ascii=False))


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
    spider_pd2_grpc.add_SpiderServicer_to_server(Spider(), server)
    server.add_insecure_port('[::]:50052')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
