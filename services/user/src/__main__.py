from concurrent import futures
import logging
import os

from pymongo.mongo_client import MongoClient
from services.jwt_service import JwtService
from grpc_transport.interceptors.auth import JwtAuthInterceptor
from repositories.user_repository import UserRepository
from services.auth_service import AuthService
from grpc_transport.user_service import UserServiceGrpc
from api.user_pb2_grpc import add_UserServiceServicer_to_server
import grpc


def serve():
    client = MongoClient('mongodb://%s:%s@127.0.0.1' %
                         (os.getenv("MONGODB_USER"), os.getenv("MONGODB_PASSWORD")))
    logging.info('Connected to DB')
    jwt_service = JwtService('secret')
    user_repository = UserRepository(client=client)
    auth_service = AuthService(
        user_repository=user_repository, jwt_service=jwt_service)
    server = grpc.server(futures.ThreadPoolExecutor(
        max_workers=10), interceptors=[JwtAuthInterceptor(jwt_service=jwt_service)])
    add_UserServiceServicer_to_server(
        UserServiceGrpc(auth_service=auth_service), server)
    server.add_insecure_port(f'[::]:{os.getenv("port", 50051)}')
    server.start()
    logging.info('Starting...')
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig(level=0)
    serve()
