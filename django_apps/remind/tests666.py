# # import hashlib
# #
# # import filetype
# # from django.conf import settings
# #
# #
# # def check_file_type(path):
# #     """校验文件类型"""
# #
# #     kind = filetype.guess(path)
# #     if kind is not None:
# #         if kind.extension in ['jpg', 'png']:
# #             return True
# #     return False
# #
# #
# # # 文件大小限制
# # # settings.IMAGE_SIZE_LIMIT是常量配置，设置为10M
# # def check_file_size(size):
# #     """校验文件大小"""
# #
# #     # 10 * 1000 = 10 KB
# #     limit = settings.IMAGE_SIZE_LIMIT
# #     if size <= limit:
# #         return True
# #     return False
# #
# #
# # def check_file_md5(file):
# #     """计算文件的md5"""
# #     s = 'yueyeKIDL'
# #     md_obj = hashlib.md5()
# #     md_obj.update(s.encode())
# #     return md_obj.hexdigest()
# #
# #
# # if __name__ == '__main__':
# #     print(check_file_md5('./timg(1).jpg'))
# from socketserver import ThreadingMixIn
# from xmlrpc.server import SimpleXMLRPCServer
#
#
# class ThreadXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
#     pass
#
#
# def add(x, y):
#     return x + y
#
#
# def subtract(x, y):
#     return x - y
#
#
# def multiply(x, y):
#     return x * y
#
#
# def divide(x, y):
#     return x / y
#
#
# # A simple server with simple arithmetic functions
# server = ThreadXMLRPCServer(("localhost", 8888))
#
# # server.register_multicall_functions()
# server.register_function(add, 'add')
# server.register_function(subtract, 'subtract')
# # server.register_function(multiply, 'multiply')
# # server.register_function(divide, 'divide')
# print("Listening on port 8000...")
# server.serve_forever()


tomato_bell_reply = "fqz 2 15 Let's Go,here we go!"
_, amount, minutes, *tomato_name = tomato_bell_reply.split()
tomato_name = ' '.join(tomato_name)
print(tomato_name == "Let's Go,here we go!")