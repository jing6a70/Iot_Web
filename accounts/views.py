from django.shortcuts import render
from .serializers import MyProfileSerializer
from .models import MyProfile
from rest_framework import viewsets
from rest_framework.response import Response

from rest_framework_simplejwt import authentication
from rest_framework import permissions


from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer



from django.shortcuts import get_object_or_404

class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


class  MyProfileViewSet(viewsets.ModelViewSet):
    """
    list:
    查询个人信息列表

    create:
    创建个人信息

    retrieve:
    查询个人信息详情

    update:
    更新个人信息

    partial_update:
    更新个人信息部分属性

    destroy:
    删除个人信息

    """

    serializer_class =  MyProfileSerializer

    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (authentication.JWTAuthentication,)

    queryset =  MyProfile.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def list(self, request,):
        queryset = MyProfile.objects.filter(user=request.user)
        qs = queryset[0]
        # serializer = MyProfileSerializer(queryset, many=True)
        # return Response(serializer.data)
        info = {'myprofile_id':qs.id,'user_id':qs.user.id,'username':qs.user.username,'email':qs.user.email,'phone_num':qs.phone_num,'mugshot':'/media/'+str(qs.mugshot)}
        return JSONResponse(info)

    def retrieve(self, request, pk=None):
        queryset = MyProfile.objects.filter(user=request.user)
        myprofile = get_object_or_404(queryset, pk=pk)
        serializer = MyProfileSerializer(myprofile)
        return Response(serializer.data)
