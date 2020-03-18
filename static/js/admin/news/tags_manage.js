$(function () {
   // 添加标签
   let $tagAdd = $("#btn-add-tag");     // 1.获取添加按钮
    $tagAdd.click(function () {     // 2.点击事件
        fAlert.alertOneInput({
            title: "请输入文章标签",
            text: "长度限制在20字以内",
            placeholder: "请输入文章标签",
            confirmCallback: function comfirmCallback(inputVal) {
                console.log(inputVal);
                if (inputVal === "") {
                    swal.showInputError('标签不能为空');
                    return false;
                }
                let sDataParams = {
                    "name": inputVal
            };
            $.ajax({
                url: "/admin/tags/",
                type: "POST",
                data: JSON.stringify(sDataParams),
                contentType: "application/json; charset=utf-8",
                dataType: "json"
            })
                .done(function (res) {
                    if(res.errno === "0"){
                        fAlert.alertSuccessToast(inputVal + "标签添加成功");
                        setTimeout(function () {
                            window.location.reload();
                        }, 1000)
                    } else {
                        swal.showInputError(res.errmsg);
                    }
                })
                .fail(function () {
                    message.showError('服务器超时，请重试！');
                });
            }
        });
    });

    // 编辑标签
    let $tagEdit = $(".btn-edit");
    $tagEdit.click(function () {
        let _this = this;
        let sTagId = $(this).parents('tr').data('id');
        let sTagName = $(this).parents('tr').data('name');
        fAlert.alertOneInput({
            title: "编辑文章标签",
            text: "你正在编辑" + sTagName + "标签",
            placeholder: "请输入文章标签",
            confirmCallback: function comfirmCallback(inputVal) {
                console.log(inputVal);
                if (inputVal === sTagName) {
                    swal.showInputError('标签名未变化');
                    return false;
                }
                let sDataParams = {
                    "name": inputVal
                };
                $.ajax({
                    url: "/admin/tags/" + sTagId + "/",
                    type: "PUT",
                    data: JSON.stringify(sDataParams),
                    contentType: "application/json; charset=utf-8",
                    dataType: "json"
                })
                    .done(function (res) {
                        if (res.errno === "0") {
                            $(_this).parents('tr').find('td:nth-child(1)').text(inputVal);
                            swal.close();
                            message.showSuccess("标签修改成功")
                        } else {
                            swal.showInputError(res.errmsg);
                        }
                    })
                    .fail(function () {
                        message.showError('服务器超时，请重试！');
                    });
            }
        });
    });

    // 删除标签
    let $tagDel = $(".btn-del");
    $tagDel.click(function () {
        let _this = this;
        let sTagId = $(this).parents('tr').data('id');
        let sTagName = $(this).parents('tr').data('name');
        fAlert.alertConfirm({
            title: "确定删除" + sTagName + "标签吗？",
            type: "error",
            confirmText: "确认删除",
            cancelText: "取消删除",
            confirmCallback: function comfirmCallback() {
                $.ajax({
                    url: "/admin/tags/" + sTagId + "/",
                    type: "DELETE",
                    dataType: "json"
                })
                    .done(function (res) {
                        if (res.errno === "0") {
                            message.showSuccess("标签删除成功");
                            $(_this).parents('tr').remove();
                        } else {
                            swal.showInputError(res.errmsg);
                        }
                    })
                    .fail(function () {
                        message.showError('服务器超时，请重试！');
                    });
            }
        });
    });

});