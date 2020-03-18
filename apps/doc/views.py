import logging
from django.core.paginator import Paginator
from django.http import FileResponse, Http404
from django.shortcuts import render
from django.utils.encoding import escape_uri_path
from django.views import View

from utils.json_fun import json_response
from .models import Doc
from .import constants
from django.conf import settings


logger = logging.getLogger('django')

# Create your views here.
class DocView(View):
    """
    文档下载页面视图
    """
    def get(self, request):
        return render(request, 'doc/docDownload.html')


class DocListView(View):
    def get(self, request):
        # 1.拿到所有文档
        docs = Doc.objects.values('file_url', 'file_name', 'title', 'desc', 'image_url').filter(is_delete=False)
        # 2.分页
        paginator = Paginator(docs, constants.PER_PAGE_DOC_COUNT)
        try:
            page = paginator.get_page(int(request.GET.get('page')))
        except Exception as e:
            logger.error('错误：\n{}'.format(e))
            page = paginator.get_page(1)
        data = {
            'total_page': paginator.num_pages,
            'docs': list(page)
        }
        return json_response(data=data)


class DocDownload(View):
    """
    文档下载
    """
    def get(self, request, doc_id):
        doc = Doc.objects.only('file_url').filter(is_delete=False, id=doc_id).first()
        if doc:
            doc_url = doc.file_url
            doc_url = settings.SITE_DOMAIN_PORT + doc_url
            try:
                # stream 设置需要的时候才下载
                # 如果没有stream 先从七牛云下载到服务器，再传给用户
                res = FileResponse(request.get(doc_url), stream=True)
            except Exception as e:
                logger.info("获取文档内容出现异常：\n{}".format(e))
                raise Http404("文档下载异常！")

            # 设置Content-type格式
            ex_name = doc_url.split('.')[-1]  # 文件后缀，表明文件类型
            if not ex_name:
                raise Http404("文档url异常！")
            else:
                ex_name = ex_name.lower()

            if ex_name == "pdf":
                res["Content-type"] = "application/pdf"
            elif ex_name == "zip":
                res["Content-type"] = "application/zip"
            elif ex_name == "doc":
                res["Content-type"] = "application/msword"
            elif ex_name == "xls":
                res["Content-type"] = "application/vnd.ms-excel"
            elif ex_name == "docx":
                res["Content-type"] = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            elif ex_name == "ppt":
                res["Content-type"] = "application/vnd.ms-powerpoint"
            elif ex_name == "pptx":
                res["Content-type"] = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
            else:
                raise Http404("文档格式不正确！")
            # 下载的文件名
            doc_filename = escape_uri_path(doc_url.split('/'))[-1]
            # 设置为inline，会直接打开, 要设置utf8编码
            res["Content-Disposition"] = "attachment; filename*=UTF-8''{}".format(doc_filename)
            # res["Content-Disposition"] = "inline; filename*=UTF-8''{}".format(doc_filename)
            return res
        else:
            return Http404("文档不存在！")
