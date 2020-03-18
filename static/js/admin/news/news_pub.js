$(function () {
   let $e = window.wangEditor;
   window.editor = new $e('#news-content');
   window.editor.create();

   // 获取缩略图输入框元素
   let $thumbnailUrl = $("#news-thumbnail-url");
   // 上传图片文件至服务器
   let $upload_to_server = $("#upload-news-thumbnail");
   $upload_to_server.change(function () {
      let file = this.file[0];
      let oFormData = new FormData();
      oFormData.append("image_file", file);
      // 发送请求
      $.ajax({
         url: "/admin/news/images/",
         method: "POST",
         data: oFormData,
         processData: false,  //定义文件的传输
         contentType: false
      })
          .done(function (res) {
             if(res.errno === "0"){
                message.showSuccess("图片上传成功");
                let sImageUrl = res["data"]["image_url"];
                $thumbnailUrl.val('');
                $thumbnailUrl.val(sImageUrl);
             } else {
                message.showError(res.errmsg)
             }
          })
          .fail(function () {
             message.showError("服务器超时，请重试");
          })
   })

   // 上传至七牛
   let $progressBar = $(".progress-bar");
   QINIU.upload({
      "domain": "http://p13yncrle.bkt.clouddn.com/",
      "uptoken_url": "/admin/token/",
      "browse_btn": "upload-btn",
      "success": function (up, file, info) {
         let domain = up.getOptions('domain');
         let res = JSON.parse(info);
         let filePath = doamin + res.key;
         console.log(filePath);
         $thumbnailUrl.val('');
      },
      "error": function (up, err, errTip) {
         console.log(up);
         console.log(err);
         console.log(errTip);
         message.showError(errTip);
      },
      "progress": function (up, file) {
         let percent = file.percent;
         $progressBar.parent().css("display: block;");
         $progressBar.css("width", percent + '%');
         $progressBar.text(parseInt(percent) + '%');
      },
      "complete": function () {
         $progressBar.parent().css("display: none;");
         $progressBar.css("width", '0%');
         $progressBar.text('0%');
      }
   });

   // 发布文章
   let $newsBtn = $("#btn-pub-news");
   $newsBtn.click(function () {
      let sTitle = $("#news-title").val();
      if (!sTitle) {
         message.showError("请填写文章标题！");
         return
      }
      // 判断文章摘要是否为空
      let sDesc = $("#news-desc").val();
      if (!sDesc) {
         message.showError("请填写文章摘要！");
         return
      }

      let sTagId = $("#news-category").val();
      if (!sTagId || sTagId === '0') {
         message.showError("请选择文章标签！");
         return
      }

      let sThumbnailUrl = $thumbnailUrl.val();
      if (!sThumbnailUrl) {
         message.showError("请山川文章缩略图！");
         return
      }

      let sContentHtml = window.editor.txt.html();
      if (!sContentHtml || sContentHtml === '<p><br></p>') {
         message.showError("请山川文章缩略图！");
         return
      }

      let newsId = $(this).data("news-id");
      let url = newsId ? 'admin/news/' + newsId + '/' : '/admin/news/pub/';
      let data = {
         "title": sTitle,
         "digest": sDesc,
         "tag": sTagId,
         "image_url": sThumbnailUrl,
         "content": sContentHtml
      };

      $.ajax({
         url: url,
         type: newsId ? 'PUT' : 'POST',
         data: JSON.stringify(data),
         contentType: 'application/json: charset=utf-8',
         dataType: "json"
      })
          .done(function (res) {
             if (res.errno === "0") {
                if (newsId) {
                   fAlert.alertNewsSuccessCallback("文章更新成功", '跳到后台首页', function () {
                      window.location.href = '/admin'
                   });
                } else {
                   fAlert.alertNewsSuccessCallback("文章发表成功", '跳到后台首页', function () {
                      window.location.href = '/admin'
                   });
                }
             } else {
                fAlert.alertErrorToast(res.errmsg);
             }
          })
          .fail(function () {
             message.showError("服务器超时，请重试！")
          })
   })
});