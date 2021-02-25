from concurrent import futures
import os
import sys
import grpc
import json
import sentiment_pb2
import sentiment_pb2_grpc

current_path = os.path.realpath(__file__)
root_path = os.path.dirname(os.path.dirname(os.path.dirname(current_path)))
sys.path.append(root_path)
from Logger import log
from server.sentiment.logic.sentiment import getSentiment


class Sentiment(sentiment_pb2_grpc.SentimentServicer):
    def GetSentiment(self, request, context):
        log().logger.info('get request')
        text = request.text
        res = getSentiment(text=text)
        if res is None:
            result = {
                'status_code': 400,
                'message': 'some error happen in getSentiment',
                'text': text
            }
        else:
            sentiment, pre = res[0], res[1]
            result = {
                'status_code': 200,
                'text': text,
                'sentiment': sentiment,
                'pre': pre,
                'message': 'getSentiment run successfully'
            }
        return sentiment_pb2.Results(
            result=json.dumps(result, ensure_ascii=False))


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    sentiment_pb2_grpc.add_SentimentServicer_to_server(Sentiment(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    print(root_path)
    log().logger.info('server start')
    serve()
