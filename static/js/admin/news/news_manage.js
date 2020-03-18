$(function () {
   let $startTime = $("input[name=start_time]");
   let $endTime = $("input[name=end_time]");
   const config = {
       // 自动关闭
       autoclose: true,
       // 日期格式
       format: 'yyyy/mm/dd',
       // 选择语言为中文
       language: 'zh-CN',
       // 优化样式
       showButtonPanel: true,
       // 高亮今天
       todayHighlight: true,
       // 是否在周行的左侧显示周数
       calendarWeeks: true,
       // 清除
       clearBtn: true,
       // 0-11 网站上线的时候
       startDate: new Date(2019, 10, 1),
       // 今天
       endDate: new Date(),
   };
   $startTime.datepicker(config);
   $endTime.datepicker(config);

   // 删除标签
    let $newsDel = $(".btn-del");
    $newsDel.click(function () {
        let _this = this;
        let sNewsId = $(this).data('news-id');
        swal({
            title: "确定删除这篇文章吗？",
            text: "删除之后，将无法恢复！",
            type: "warning",
            showCancelButton: true,
            confirmButtonColor: "#DD6B55",
            confirmButtonText: "确定删除",
            cancelButtonText: "取消",
            closeOnConfirm: true,
            animation: 'slide-from-top',
        }, function () {
            $.ajax({
                url: "/admin/news/" + sNewsId + "/",
                type: "DELETE",
                dataType: "json",
            })
                .done(function (res) {
                    if (res.errno === "0"){
                        message.showSuccess("文章删除成功");
                        $(_this).parent('tr').remove();
                    } else {
                        swal({
                            title: res.errmsg,
                            type: "error",
                            timer: 1000,
                            showCancelButton: false,
                            showConfirmButton: false
                        })
                    }
                })
                .fail(function () {
                    message.showError("服务器超时，请重试！")
                });
        });
    });
});