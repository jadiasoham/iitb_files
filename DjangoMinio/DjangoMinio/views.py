# from django.http import HttpResponse, JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from django.conf import settings
# from minio_client import get_minio_client
# from django.core.files.storage import default_storage
# from django.core.files.base import ContentFile
# from django.core.exceptions import SuspiciousOperation
# from django.shortcuts import render

# DEFAULT_BUCKET = 'ai-bucket'

# @csrf_exempt
# def upload_file(request):
#     # Check if the request method is POST and there is a file selected to upload:
#     if request.method == 'POST' and request.FILES.get('file'):
#         file = request.FILES['file']
#         bucket_name = request.POST.get('bucket_name', DEFAULT_BUCKET)
#         prefix = request.POST.get('prefix', '')
        
#         client = get_minio_client()

#         try:
#             if not client.bucket_exists(bucket_name):
#                 return HttpResponse(f'The bucket: {bucket_name} does not exist.', status= 400)
#             object_key = f'{prefix}/{file.name}' if prefix else file.name
#             # Upload file to minIO:
#             client.put_object(
#                 bucket_name,
#                 object_key,
#                 file,
#                 length= file.size,
#                 part_size= 10*1024*1024
#             )
#             return HttpResponse('File uploaded successfully', status= 200)
#         except Exception as e:
#             return HttpResponse(f'Unknown Error: {e}', status= 500)
#     return render(request, 'upload.html')

# def download_file(request, filename):
#     client = get_minio_client()
#     bucket_name = 'ai-bucket'

#     try:
#         # Download the file from minio:
#         response = client.get_object(bucket_name, filename)
#         file_content = response.read()

#         return HttpResponse(file_content, content_type = 'application/octet-stream')
#     except Exception as e:
#         return JsonResponse({'error':f'{e}'}, status= 500)

# def create_bucket(request):
#     if request.method == 'POST':
#         bucket_name = request.POST.get('bucket_name')
#         if not bucket_name:
#             return HttpResponse('Bucket name is required', status= 400)
        
#         client = get_minio_client()

#         try:
#             if not client.bucket_exists(bucket_name):
#                 client.make_bucket(bucket_name, object_lock= False)
#                 return HttpResponse(f'Bucket {bucket_name} created successfully')
#             else:
#                 return HttpResponse(f'Bucket {bucket_name} already exits.', status= 400)
#         except Exception as e:
#             return HttpResponse(f'Error: {e}', status= 500)
        
#     return render(request, 'create_bucket.html')

# def list_buckets(request):
#     client = get_minio_client()
#     all_buckets = dict()

#     try:
#         buckets = client.list_buckets()
#         for bucket in buckets:
#             all_buckets[bucket.name] = bucket.creation_date

#         return render(request, 'list_buckets.html', {'buckets': all_buckets})
#     except Exception as e:
#         return HttpResponse(f'Unknown error: {e}', status= 500)
    
# def list_objects(request):
#     client = get_minio_client()
#     all_objects = []
#     buckets = []

#     try:
#         buckets = client.list_buckets()
#         bucket_names = [bucket.name for bucket in buckets]

#         selected_bucket = request.GET.get('bucket_name')
#         if selected_bucket:
#             objects = client.list_objects(selected_bucket, recursive= True)
#             for obj in objects:
#                 this_object = {
#                     'name':obj.object_name,
#                     'size':obj.size / 1024 if obj.size else 0, # size in KB
#                     'last_mod':obj.last_modified,
#                 }
#                 all_objects.append(this_object)

#         return render(request, 'list_objects.html', {'objects': all_objects, 'buckets':bucket_names})
#     except Exception as e:
#         return HttpResponse('Unknown Error: {e}', status= 500)


# Imports:
from typing import Any
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from minio_client import get_minio_client
from .serializers import BucketSerializer, ObjectSerializer
from django.views.decorators.csrf import csrf_exempt

# Defaults:
DEFAULT_BUCKET = 'ai-bucket'
int_server_err_msg = lambda err_msg: {'error':f'Unknown Error: {err_msg}'}


class FilesView(APIView):
    def __init__(self) -> None:
        self.client = get_minio_client()

    @csrf_exempt
    def post(self, request):
        file = request.FILES.get('file')
        bucket_name = request.data.get('bucket_name', DEFAULT_BUCKET)
        prefix = request.data.get('prefix', '')
        if file:
            try:
                if not self.client.bucket_exists(bucket_name):
                    err_msg = {'error':f'Error\nbucket name: {bucket_name}\nNo such bucket exists.'}
                    return Response(err_msg, status= status.HTTP_400_BAD_REQUEST)
                object_name = f'{prefix}/{file.name}' if prefix else file.name
                self.client.put_object(
                    bucket_name= bucket_name,
                    object_name= object_name,
                    data= file,
                    length= file.size,
                    part_size= 10*1024*1024,
                )
                reply = {'message':f'Object {file.name} uploaded in bucket {bucket_name} succcessfully.\nAvailable at {object_name}'}
                return Response(reply, status= status.HTTP_200_OK)
            except Exception as e:
                return Response(int_server_err_msg(e), status= status.HTTP_500_INTERNAL_SERVER_ERROR)
        err_msg = {'error': 'Please select a file to upload'}
        return Response(err_msg, status= status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        bucket_name = request.GET.get('bucket_name', DEFAULT_BUCKET)
        file_name = request.data.get('file_name', '')
        try:
            file = self.client.get_object(bucket_name= bucket_name, object_name= file_name)
            file_content = file.read()
            return Response(file_content, content_type= 'application/octet-stream')
        except TypeError:
            err_msg = {'error':'select atleast one file to download'}
            return Response(err_msg, status= status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(int_server_err_msg(e), status= status.HTTP_500_INTERNAL_SERVER_ERROR)


class BucketsView(APIView):
    def __init__(self) -> None:
        self.client = get_minio_client()

    def post(self, request):
        action = request.data.get('action')
        bucket_name = request.data.get('bucket_name')

        if not bucket_name:
            err_msg = {'error':'bucket_name is required.'}
            return Response(err_msg, status= status.HTTP_400_BAD_REQUEST)
        
        try:
            if action.lower() == 'delete':
                if self.client.bucket_exists(bucket_name):
                    self.client.remove_bucket(bucket_name= bucket_name)
                    return Response({'message':f'bucket: {bucket_name} successfully deleted.'}, status= status.HTTP_200_OK)
                else:
                    err_msg = {'error':'No such bucket exists.'}
                    return Response(err_msg, status= status.HTTP_400_BAD_REQUEST)
            elif action.lower() == 'create':
                if not self.client.bucket_exists(bucket_name):
                    self.client.make_bucket(bucket_name)
                    reply = {'message':f'bucket: {bucket_name} created successfully.'}
                    return Response(reply, status= status.HTTP_200_OK)
                else:
                    err_msg = {'error':f'bucket: {bucket_name} already exists'}
                    return Response(err_msg, status= status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(int_server_err_msg(e), status= status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def get(self, reqeust):
        all_buckets = list()
        try:
            buckets = self.client.list_buckets()
            for bucket in buckets:
                this_bucket = {
                    'name': bucket.name,
                    'created_on': bucket.creation_date,
                }
                all_buckets.append(this_bucket)
            serializer = BucketSerializer(all_buckets, many= True)
            return Response(serializer.data)
        except Exception as e:
            return Response(int_server_err_msg(e), status= status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ObjectsView(APIView):
    def __init__(self) -> None:
        self.client = get_minio_client()

    def get(self, request):
        bucket_names = list()
        all_objects = list()
        
        try:
            buckets = self.client.list_buckets()
            for bucket in buckets:
                bucket_names.append(bucket.name)
            
            selected_bucket = request.GET.get('bucket.name', DEFAULT_BUCKET)
            objects = self.client.list_objects(selected_bucket, recursive= True)

            for obj in objects:
                this_obj = {
                    'name': obj.object_name,
                    'size': obj.size / 1024 if obj.size else 0, # size in KB
                    'last_mod': obj.last_modified,
                }
                all_objects.append(this_obj)

            serializer = ObjectSerializer(all_objects, many= True)
            return Response(serializer.data)
        except Exception as e:
            return Response(int_server_err_msg(e), status= status.HTTP_500_INTERNAL_SERVER_ERROR)
