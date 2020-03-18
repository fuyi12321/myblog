$(function () {
    // 获取id标签
    let $username = $('#user_name');
    // $开头是获取元素标签
    let $img = $('.form-item .captcha-graph-img img');  // 获取图片标签元素
    //s开头是字符串
    let sImageCodeId = "";

    // 定义状态变量
    let isUsernameReady = false,
        isPasswordReady = false,
        isMobileReady = false;
    // 1.图像验证码逻辑
    generateImageCode();
    $img.click(generateImageCode);

    // 2.用户名验证逻辑
    // houer 光标进来
    // blur 鼠标移出
    $username.blur(function () {
        fnCheckUsername();
    });

    // 生成图片UUID验证码，并设置页面中图片验证码img标签的src属性
    function generateUUID() {
        // let d = new Date().getTime();
        // if(window.performance && typeof window.performance.now == "function") {
        //     d += performance.now();
        // }
        //          123e4567-e89b-12d3-a456-426655440000
        // let uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxx'.replace(/[xy]/g, function (c) {
        //     let r = (d + Math.random() * 16) | 0;
        //     d = Math.floor(d / 16);
        //     return (c == 'x' ? r : (r & 0x3 | 0x8)).toString(16);
        // });
        // return uuid;
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
            var r = Math.random() * 16 | 0,
                v = c == 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }
    
    // 生成一个图片验证码的编号，并设置页面中图片验证码img标签的src属性
    function generateImageCode() {
        // 1.生成一个图片验证码随机编号
        sImageCodeId = generateUUID();
        // 2.拼接请求url
        let imageCodeUrl = "/image_codes/" + sImageCodeId + "/";
        // 3.修改验证码图片src地址
        $img.attr('src', imageCodeUrl)
    }

    // 判断用户名是否已经注册
    function fnCheckUsername(){
        isUsernameReady = false;
        let sUsername = $username.val();    //获取用户字符串
        if (sUsername === ""){
            message.showError('用户名不能为空！');  // 更好看
            // alert('用户名不能为空！');
            return
        }
        // 正则
        if (!(/^\w{5,20}$/).test(sUsername)){
            message.showError('请输入5-20个字符的用户名');
            // alert('请输入5-20个字符的用户名');
            return
        }
        // 发送ajax请求，去后端查询用户名是否存在
        $.ajax({
            url: '/username/' + sUsername + '/',
            type: 'GET',
            // 后端传给我的类型是json
            contentType: 'json',
            // 后端正常响应
            success: function (res) {
                if(res.data.count !== 0){
                    message.showError(res.data.username + '已经注册了，请重新输入！');
                }else {
                    message.showInfo(res.data.username + '可以正常使用！');
                    isUsernameReady = true;
                }
            },
            error: function (xhr, msg) {
                message.showError('服务器超时，请重试！')
            }
        });
    }

    // 3.检测密码是否一致
    let $passwordRepeat = $("input[name='password_repeat']");
    $passwordRepeat.blur(fnCheckPassword);

    function fnCheckPassword () {
        isPasswordReady = false;
        let password = $("input[name='password']").val();
        let passwordRepeat = $passwordRepeat.val();
        if (password === '' || passwordRepeat === ''){
            message.showError('密码不能为空');
            return
        }
        if (password !== passwordRepeat){
            message.showError('两次密码输入不一致');
            return
        }
        if (password === passwordRepeat){
            isPasswordReady = true
        }
    }

    // 4.检查手机号码是否可用
    let $mobile = $('#mobile');
    $mobile.blur(fnCheckMobile);

    function fnCheckMobile () {
        isMobileReady = true;
        SreturnValue = "";
        let sMobile = $mobile.val();
        if(sMobile === ''){
            message.showError('手机号码不能为空');
            return
        }
        if(!(/^1[3-9]\d{9}$/).test(sMobile)){
            message.showError('手机号码格式不正确');
            return
        }

        $.ajax({
            url: '/mobile/' + sMobile + '/',
            type: 'GET',
            dataType: 'json',
            async: false,    //把async关掉 把异步请求关掉，默认为true，
            success: function (res) {
                if(res.data.count !== 0){
                    message.showError(res.data.mobile + '已经注册，请重新输入！');
                    SreturnValue = "";
                }else {
                    message.showSuccess(res.data.mobile + '可以正常使用！');
                    SreturnValue = "succes";
                    isMobileReady = true
                }
            },
            error: function (xhr, msg) {
                message.showError('服务器超时，请重试！')
            }
        });
        return SreturnValue
    }

    // 5.发送手机验证码
    let $smsButton = $('.sms-captcha');
    $smsButton.click(function () {
        // 判断用户是哦福输入图片验证码
        let sCaptcha = $("input[name='captcha_graph']").val();
        if(sCaptcha === ''){
            message.showError('请输入验证码');
            return
        }
        // 判断手机号是否输入
        if(!isMobileReady){
            fnCheckMobile();
            return
        }
        // 判断是否生成UUID
        if (!sImageCodeId){
            message.showError('图片UUID为空');
            return
        }
        // var csrf = $("input[name='csrfmiddlewaretoken']").val();
        let SdataParams = {
            'mobile': $mobile.val(),
            'captcha': sCaptcha,
            'image_code_id': sImageCodeId,
            // 'csrfmiddlewaretoken': csrf
        };
        $.ajax({
            url: '/sms_code/',
            type: 'POST',
            data: JSON.stringify(SdataParams),
            dataType: 'json',
            contentType: 'application/json: charset=utf-8',
            async: false,
            success: function (res) {
                if(res.errno !== '0'){
                    message.showError(res.errmsg)
                }else {
                    message.showSuccess(res.errmsg);
                    let num = 60;
                    //设置计时器
                    let t = setInterval(function () {
                        if(num===1){
                            // 如果计时器到最后，清除计时器对象
                            clearInterval(t);
                            // 将点击获取验证码的按钮展示的文本恢复成原始文本
                            $smsButton.html("获取短信验证码");
                        } else {
                            num -= 1;
                            // 展示倒计时信息
                            $smsButton.html(num + "秒");
                        }
                    }, 1000);
                }
            },
            error: function (xhr, msg) {
                message.showError('服务器超时，请重试！')
            }
        });

    });

    // 6.注册
    let $register = $('.form-contain');
    $register.submit(function (e) {
        //阻止默认提交
        e.preventDefault();
        // 1.检查用户名
        if(!isUsernameReady){
            fnCheckUsername();
            return
        }
        // 2.检查密码
        if(!isPasswordReady){
            fnCheckPassword();
            return
        }
        // 3.检查电话号码
        if(!isMobileReady){
            fnCheckMobile();
            return
        }
        // 4.检查短信验证码
        let sSmsCode = $("input[name='sms_captcha']").val();
        if(sSmsCode === ''){
            message.showError('短信验证码不能为空！');
            return
        }
        if(!(/^\d{4}$/).test(sSmsCode)){
            message.showError('短信验证码长度不正确，必须是4位数字！');
            return
        }

        let SdataParams = {
                username: $username.val(),
                password: $("input[name='password']").val(),
                password_repeat: $passwordRepeat.val(),
                mobile: $mobile.val(),
                sms_code: sSmsCode
            };
        $.ajax({
            url: '/user/register/',
            type: 'POST',
            data: JSON.stringify(SdataParams),
            contentType: 'application/json: charset=utf-8',
            async: false,
            dataType: 'json',
            success: function (res) {
                if(res.errno === '0'){
                    message.showSuccess('恭喜您，注册成功!');
                    setTimeout(function () {
                        //注册成功后应该返回到上一页
                        window.location.href = document.referrer
                    }, 3000)
                }else{
                    //注册失败
                    message.showError(res.errmsg)
                }
            },
            error: function () {
                message.showError('服务器超时，请重试！')
            }
        })

    });
});