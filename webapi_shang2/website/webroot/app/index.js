var prefix = 'http://192.168.1.234';
var prefix = 'http://192.168.1.123';
var prefix = 'http://localhost:3000';
var prefix = 'http://172.24.150.103:8899';
var prefix = 'http://192.168.1.123';
var prefix = 'http://192.168.2.202';
var prefix = 'http://192.168.1.254';
var LOCATION = 'firstbatch';

var api = {
    getSysStatus: prefix + '/api/system/status',
    createTask: prefix + '/api/lanemarking/status',
    loadLanePics: prefix + '/api/lanemarking/packages/' + LOCATION + '.tar.gz',
    loadSignPics: prefix + '/api/roadsign/packages/roadsign.zip',
    openCaremaSwitch: prefix + '/api/roadsign/status',
    changeUploadStatus: prefix + '/api/uploads/status',
    uploadLaneMarking: prefix + '/api/uploads/packages/lanemarking',
    uploadRoadsSign: prefix + '/api/uploads/packages/roadsign',
    uploadActions: prefix + '/api/uploads/packages/actions',
    runningmodels: prefix + '/api/runningmodels/status',
    getSignImg: prefix + '/api/roadsign/image',
    getSignLabel: prefix + '/api/roadsign/label'
};

var validStatusArr = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
// var canCameraOpenSys = [1, 4, 5, 6];

function isValidStatusArr(status) {
    return validStatusArr.indexOf(status) !== -1;
}

function getCookie(name) {
    var start = 0;
    var end = 0;

    if (document.cookie.length > 0) {
        start = document.cookie.indexOf(name + '=');

        if (start !== -1) {
            start = start + name.length + 1;
            end = document.cookie.indexOf(';', start);

            if (end === -1) {
                end = document.cookie.length;
            }

            return unescape(document.cookie.substring(start, end));
        }
    }

    return '';
}

function setCookie(key, value, day, path) {
    // var domain = ';domain=.baidu.com';
    var domain = '';
    path = path ? `;path=${path}` : ';path=/';
    if (!day) {
        document.cookie = key + '=' + value + domain + path;
        return;
    }
    var d = new Date();
    d.setTime(d.getTime() + (day * 24 * 60 * 60 * 1000));
    var expires = ';expires=' + d.toUTCString();
    document.cookie = key + '=' + value + domain + expires + path;
}

// 系统状态
var sysStatus;
// 前一个系统状态
var preSysStatus = 'pre status';
// 系统的数据
var sysData = {};
// 记录是否进行了标志采集
var isSignCollect = false;
// 记录是否选中了车道线模型
var isLaneUploadChoose = false;
// 记录是否选中了标志模型
var isSignUploadChoose = false;
// 记录是否上传了参数
var isParamChoose = false;

$(document).ready(function () {
    var connectStatusEle = $('header').find('.connect-status');
    var connectTextEle = $('header').find('.connect-text');
    var toastEle = $('#toast');
    var taskInputEle = $('#input-task');
    var createTaskEle = $('#create-task-btn');
    var loadLanePicsBtn = $('#load-lanepic-btn');
    var cameraSwitch = $('.switch-icon');
    var switchText = $('.switch-text');
    var LoadSignPicsBtn = $('#load-sign-btn');
    var lanePicNum = $('#lane-pic-num');
    var signPicNum = $('#sign-pic-num');
    var errorText = $('.input-wrap').find('.error');
    var laneUploadRadio = $('.lane-upload-radio .radio-content');
    var signUploadRadio = $('.sign-upload-radio .radio-content');
    var laneModelUpload = $('#lane-model-upload');
    var signModelUpload = $('#sign-model-upload');
    var laneModelUpload = $('#lane-model-upload');
    var paramUpload = $('#param-upload');
    var paramUpload = $('#param-upload');
    var runBtn = $('#operating-btn');
    var actionCenter = $('.action-center');
    var chooseImg = $('.choose-icon');
    var quitImg = $('.close-icon');
    var signFile = $('#sign-file');
    var laneFile = $('#lane-file');
    var paramFile = $('#param-file');
    var dataCollectEmpty = $('.card-empty');
    var signModelFileName = $('.sign-upload-radio .file-name');
    var laneModelFileName = $('.lane-upload-radio .file-name');
    var paramsFileName = $('.param-upload .file-name');

    // 已经连接
    function connectSuccess() {
        connectStatusEle.removeClass('connect-fail').addClass('connect-success');
        connectTextEle.removeClass('normal-text').addClass('active-text');
        connectTextEle[0].innerText = '已连接';
    }

     // 未连接
    function connectFail() {
        connectStatusEle.removeClass('connect-success').addClass('connect-fail');
        connectTextEle.removeClass('active-text').addClass('normal-text');
        connectTextEle[0].innerText = '已断开';
    }

    function resetSysStatus() {
        return new Promise(function (resolve, reject) {
            $.ajax({
                type: 'POST',
                url: api.getSysStatus,
                contentType: 'application/json',
                success: function (res) {
                    resolve(res);
                },
                error: function (error) {
                    reject(error);
                }
            });
        });
    }

     // 点击重置
    $('#refresh').click(function () {
        resetSysStatus().then(function (res) {
            if (res.errno === 0) {
                handleReset();
                showToast('重置成功');
            }
            else {
                showToast('重置失败');
            }
        });
    });

    function handleReset() {
        setCookie('lane-speed-num', 0, 365);
        // 车道线图片下载disable
        if (loadLanePicsBtn.hasClass('action-bth-normal')) {
            loadLanePicsBtn.removeClass('action-bth-normal').addClass('action-bth-disable');
        }
        // 隐藏下载数据
        if (lanePicNum.find('div').hasClass('show')) {
            lanePicNum.find('div').removeClass('show').addClass('hide');
            lanePicNum.find('.pic-num')[0].innerText = 0;
        }
        // 关闭摄像头
        if (cameraSwitch.hasClass('switch-open')) {
            cameraOpenFail();
        }
        // 标志采集图片下载disable
        if (LoadSignPicsBtn.hasClass('action-bth-normal')) {
            LoadSignPicsBtn.removeClass('action-bth-normal').addClass('action-bth-disable');
        }
        // 隐藏下载数据
        if (signPicNum.find('div').hasClass('show')) {
            signPicNum.find('div').removeClass('show').addClass('hide');
            signPicNum.find('.pic-num')[0].innerText = 0;
        }
        // 隐藏数据采集
        if ($('.data-collection .label-result').hasClass('show')) {
            $('.data-collection .label-result').removeClass('show').addClass('hide');
            dataCollectEmpty.show();
        }
        // 文件置空
        if (signModelFileName[0].innerText) {
            signModelFileName[0].innerText = '';
        }
        if (laneModelFileName[0].innerText) {
            laneModelFileName[0].innerText = '';
        }
        if (paramsFileName[0].innerText) {
            paramsFileName[0].innerText = '';
        }
        if (laneUploadRadio.find('.radio-wrap').hasClass('radio-check')) {
            laneUploadRadio.find('.radio-wrap').removeClass('radio-check');
        }
        if (signUploadRadio.find('.radio-wrap').hasClass('radio-check')) {
            signUploadRadio.find('.radio-wrap').removeClass('radio-check');
        }
        runBtn.hide();
        $('.progress').hide();
        $('.progress .progress-inner').css('width', 0);
    }

    // toast提示
    function showToast(toastText = '') {
        var textWrap = toastEle.find('p')[0];
        if (textWrap) {
            textWrap.innerText = toastText;
            toastEle.fadeIn(500).delay(800).fadeOut(500);
        }
    }

    // 速度输入
    function handleTaskInput() {
        var inputValue = taskInputEle.val();
        inputValue = inputValue.replace(/[^\d\.]/g, '');
        taskInputEle.val(inputValue);
    }

    // 输入速度
    taskInputEle.keyup(function () {
        handleTaskInput();
    });

    taskInputEle.blur(function () {
        handleTaskInput();
    });

    // 创建任务
    createTaskEle.click(function () {
        if (sysStatus === 1 || sysStatus === 4) {
            var speedValue = taskInputEle.val().trim();
            if (!speedValue) {
                errorText.show();
                return;
            }
            else {
                errorText.hide();
            }
            var params = {
                'speed': speedValue,
                'camera': '/dev/video2',
                'downusb': '/dev/usb',
                'location': 'firstbatch'
            };

            $.ajax({
                type: 'POST',
                url: api.createTask,
                contentType: 'application/json',
                data: JSON.stringify(params),
                success: function (res) {
                    if (res.errno === 0) {
                        showToast('创建任务成功');
                        setCookie('lane-speed-num', speedValue, 365);
                        return;
                    }
                    if (res.errno === 1002) {
                        showToast('创建任务失败,请重置');
                        return;
                    }
                    if (res.errno === 1003) {
                        showToast('速度输入有误,请重输');
                    }
                },
                error: function () {
                    showToast('创建任务失败');
                }
            });
        }

    });

    // 车道线采集图片下载
    loadLanePicsBtn.click(function () {
        if (sysStatus === 4) {
            // $.ajax({
            //     type: 'GET',
            //     url: api.loadLanePics,
            //     success: function () {
            //     },
            //     error: function () {
            //     },
            //     xhr: function () {
            //         var xhr = new XMLHttpRequest();
            //         if (xhr.upload) {
            //             xhr.upload.addEventListener('progress', function (ev) {
            //                 var progressRate = (ev.loaded / ev.total) * 100 + '%';
            //                 $('#lane-load-progress').find('.progress-inner').css('width', progressRate);
            //             });
            //         }
            //         return xhr;
            //     }
            // });
            window.open(api.loadLanePics, '_self');
        }
    });

    cameraSwitch.click(function () {
        // 关闭摄像头
        if (cameraSwitch.hasClass('switch-open')) {
            cameraOpenFail();
            hanleImgAction('process');
        }
        // 开启摄像头
        else {
            handleOpenCamera();
        }
    });

    function handleOpenCamera() {
        if (sysStatus === 1 || sysStatus === 4) {
            var params = {
                'camera': '/dev/video2',                              /* 摄像头设备串口名称  */
                'downusb': '/dev/usb',                                /* 下位机串口设备名称  */
                'location': 'secondbatch'                             /* 保存路径  */
            };
            cameraSwitch.removeClass('switch-close').addClass('switch-open');
            $.ajax({
                type: 'POST',
                url: api.openCaremaSwitch,
                contentType: 'application/json',
                data: JSON.stringify(params),
                success: function (res) {
                    res.errno === 0 && cameraOpenSucc();
                },
                error: function () {
                    cameraOpenFail();
                }
            });
        }
    }

    // 摄像头开启成功
    function cameraOpenSucc() {
        switchText[0].innerText = '图片采集中';
        switchText.addClass('active-text');
        isSignCollect = true;
    }

    // 摄像头开启失败或者关闭摄像头
    function cameraOpenFail() {
        switchText[0].innerText = '未打开';
        switchText.removeClass('active-text');
        cameraSwitch.removeClass('switch-open').addClass('switch-close');
    }

    // 更改模型及动作上传状态
    function changeUploadStatus() {
        return new Promise(function (resolve, reject) {
            $.ajax({
                type: 'POST',
                url: api.changeUploadStatus,
                success: function (res) {
                    resolve(res);
                },
                error: function (res) {
                    reject(res);
                }
            });
        });
    }

    // 标志模型上传
    signModelUpload.click(function () {
        if (sysStatus === 9) {
            signFile.click();
        }
        else if (sysStatus === 1) {
            changeUploadStatus()
            .then(function (res) {
                res.errno === 0 && signFile.click();
            });
        }
        else {
            resetSysStatus() // 重置为1
            .then(function (res) {
                if (res.errno === 0) {
                    return changeUploadStatus(); // 重置为9
                }
            })
            .then(function (res) {
                res.errno === 0 && signFile.click();
            });
        }
    });

    signFile.change(function () {
        if ($(this).val() !== '') {
            $('#sign-progress').show();

            function resetCallBack() {
                $('#sign-progress').hide();
                $('#sign-progress').find('.progress-inner').css('width', 0);
                $('#sign-progress').find('.file-origin')[0].innerHTML = '';
                $('#sign-progress').find('.file-size')[0].innerHTML = '';
            }

            fileload(({
                ele: this,
                url: api.uploadRoadsSign,
                type: 'sign',
                succCallBack: function (name) {
                    signModelFileName[0].innerText = name;
                    showToast('上传成功');
                    resetCallBack();
                },
                failCallBack: function () {
                    signModelFileName[0].innerText = '';
                    showToast('上传成功');
                    resetCallBack();
                }
            }));
        }
    });

    // 车道线模型上传
    laneModelUpload.click(function () {
        if (sysStatus === 9) {
            laneFile.click();
        }
        else if (sysStatus === 1) {
            changeUploadStatus()
            .then(function (res) {
                res.errno === 0 && laneFile.click();
            });
        }
        else {
            resetSysStatus() // 重置为1
            .then(function (res) {
                if (res.errno === 0) {
                    return changeUploadStatus(); // 重置为9
                }
            })
            .then(function (res) {
                res.errno === 0 && laneFile.click();
            });
        }
    });

    laneFile.change(function () {
        if ($(this).val() !== '') {
            $('#lane-progress').show();

            function resetCallBack() {
                $('#lane-progress').hide();
                $('#lane-progress').find('.progress-inner').css('width', 0);
                $('#lane-progress').find('.file-origin')[0].innerHTML = '';
                $('#lane-progress').find('.file-size')[0].innerHTML = '';
            }

            fileload(({
                ele: this,
                type: 'lane',
                url: api.uploadLaneMarking,
                succCallBack: function (name) {
                    laneModelFileName[0].innerText = name;
                    showToast('上传成功');
                    resetCallBack();
                },
                failCallBack: function () {
                    laneModelFileName[0].innerText = '';
                    showToast('上传成功');
                    resetCallBack();
                }
            }));
        }
    });

    function fileload(params) {
        var ele = params.ele;
        var formData = new FormData();
        var files = $(ele)[0].files[0];
        formData.append('files', files);
        var fileSize = (files.size || 0) / 1024 / 1024;
        fileSize = fileSize.toFixed(1);
        var fileName = files.name;

        $.ajax({
            type: 'POST',
            url: params.url,
            data: formData,
            dataType: 'json',
            cache: false,
            contentType: false,
            processData: false,
            success: function () {
                params.succCallBack(files.name);
            },
            error: function () {
                params.failCallBack();
            },
            xhr: function () {
                var xhr = new XMLHttpRequest();
                if (xhr.upload) {
                    xhr.upload.addEventListener('progress', function (ev) {
                        var progressRate = (ev.loaded / ev.total) * 100 + '%';
                        var id = '#' + params.type + '-progress';
                        var size = fileSize + 'M(' +  progressRate  + ')';
                        $(id).find('.file-origin')[0].innerHTML = fileName;
                        $(id).find('.file-size')[0].innerHTML = size;
                        $(id).find('.progress-inner').css('width', progressRate);
                    });
                }
                return xhr;
            }
        });
    }

    // 参数上传
    paramUpload.click(function () {
        if (sysStatus === 9) {
            paramFile.click();
        }
        else if (sysStatus === 1) {
            changeUploadStatus()
            .then(function (res) {
                res.errno === 0 && paramFile.click();
            });
        }
        else {
            resetSysStatus() // 重置为1
            .then(function (res) {
                if (res.errno === 0) {
                    return changeUploadStatus(); // 重置为9
                }
            })
            .then(function (res) {
                if (res.errno === 0) {
                    res.errno === 0 && paramFile.click();
                }
            });
        }
    });

    paramFile.change(function () {
        if ($(this).val() !== '') {
            $('#param-progress').show();

            function resetCallBack() {
                $('#param-progress').hide();
                $('#param-progress').find('.progress-inner').css('width', 0);
                $('#param-progress').find('.file-origin')[0].innerHTML = '';
                $('#param-progress').find('.file-size')[0].innerHTML = '';
            }

            fileload(({
                ele: this,
                url: api.uploadActions,
                type: 'param',
                succCallBack: function (name) {
                    paramsFileName[0].innerText = name;
                    showToast('上传成功');
                    isParamChoose = true;
                    resetCallBack();
                },
                failCallBack: function () {
                    paramsFileName[0].innerText = '';
                    showToast('上传成功');
                    isParamChoose = false;
                    resetCallBack();
                }
            }));
        }
    });

    function hanleImgAction(type) {
        var params = JSON.stringify({
            action: type
        });
        $.ajax({
            type: 'POST',
            url: api.getSignImg,
            contentType: 'application/json',
            data: params,
            success: function (res) {
                // 刷新下一张图和标签
                if (res.errno === 0 && type !== 'process') {
                    getSignLabel();
                    getSignImg();
                }
            },
            error: function () {
            }
        });
    }

    // 选中图片
    chooseImg.click(function () {
        if (sysStatus !== 6) {
            return;
        }
        hanleImgAction('ok');
    });

    // 不要图片
    quitImg.click(function () {
        if (sysStatus !== 6) {
            return;
        }
        hanleImgAction('cancel');
    });

    // 刷新标志采集图片
    function getSignImg() {
        var img = new Image();
        img.src = api.getSignImg + '?' + 't=' + new Date().getTime();
        img.className = 'img-lane';
        // img.src = 'https://ss2.bdstatic.com/70cFvnSh_Q1YnxGkpoWK1HF6hhy/it/u=3031309961,2051994865&fm=26&gp=0.jpg';
        actionCenter.children('.img-lane').replaceWith(img);
    }

    // 获取图片标签
    function getSignLabel() {
        $.ajax({
            type: 'GET',
            url: api.getSignLabel,
            success: function (res) {
                dataCollectEmpty.hide();
                $('.data-collection .label-result').show();
                $('.data-collection .data-collection-text')[0].innerText = res.label || '';
                $('.data-collection .data-collection-picnum')[0].innerHTML = sysData.totals || 0;
            },
            error: function () {
            }
        });
    }

    laneUploadRadio.click(function () {
        if ($('.lane-upload-radio .file-name')[0].innerText === '') {
            return;
        }
        laneUploadRadio.find('.radio-wrap').toggleClass('radio-check');
        isLaneUploadChoose = laneUploadRadio.find('.radio-wrap').hasClass('radio-check');
    });

    signUploadRadio.click(function () {
        if ($('.sign-upload-radio .file-name')[0].innerText === '') {
            return;
        }
        signUploadRadio.find('.radio-wrap').toggleClass('radio-check');
        isSignUploadChoose = signUploadRadio.find('.radio-wrap').hasClass('radio-check');
    });

    LoadSignPicsBtn.click(function () {
        if (sysStatus === 8) {
            // $.ajax({
            //     type: 'GET',
            //     url: api.loadSignPics,
            //     success: function () {
            //     },
            //     error: function () {
            //     },
            //     xhr: function () {
            //         var xhr = new XMLHttpRequest();
            //         if (xhr.upload) {
            //             xhr.upload.addEventListener('progress', function (ev) {
            //                 var progressRate = (ev.loaded / ev.total) * 100 + '%';
            //                 $('#sign-load-progress').find('.progress-inner').css('width', progressRate);
            //             });
            //         }
            //         return xhr;
            //     }
            // });
            window.open(api.loadSignPics, '_self');
        }
    });

    function isShowOperatingBtn() {
        if ((isLaneUploadChoose || isSignUploadChoose) && isParamChoose) {
            return true;
        }
        return false;
    }

    runBtn.click(function () {
        var params = {
            'speed': taskInputEle.val(),                          /* 小车跑动速度  */
            'camera': '/dev/video2',                              /* 摄像头设备串口名称  */
            'downusb': '/dev/usb',                                /* 下位机串口设备名称  */
            'lanemarking': isLaneUploadChoose,                    /* 跑不跑车道线模型  */
            'roadsign': isSignUploadChoose                        /* 跑不跑标志检测模型  */
        };
        $.ajax({
            type: 'POST',
            url: api.runningmodels,
            data: JSON.stringify(params),
            contentType: 'application/json',
            success: function (res) {
                if (res.errno === 0) {
                    showToast('运行成功');
                }
                if (res.errno === 1010) {
                }
                if (res.errno === 1011) {
                    showToast('运行错误');
                }
            },
            error: function () {
                showToast('运行失败');
            }
        });
    });

    setInterval(() => {
        $.ajax({
            type: 'GET',
            url: api.getSysStatus,
            success: function (res) {
                var data = res && res.data || {};
                sysStatus = data.status || '';
                sysData = data.data || {};

                if (sysStatus === 6) {
                    getSignLabel();
                }
                if ((sysStatus === 9 || sysStatus === 10) && isShowOperatingBtn()) {
                    runBtn.show();
                } else {
                    runBtn.hide();
                }

                // 系统状态无变化，不更新dom
                if (sysStatus === preSysStatus) {
                    return;
                }
                // 记录前一个状态
                preSysStatus = sysStatus;

                if (!isValidStatusArr(sysStatus)) {
                    connectFail();
                    return;
                }
                connectSuccess();

                // 车道线检测
                if (sysStatus >= 1) {
                    var laneSpeedNum = getCookie('lane-speed-num');
                    taskInputEle.val(laneSpeedNum || 0);
                    createTaskEle.removeClass('action-bth-active-disable').addClass('action-bth-active');
                }
                else {
                    createTaskEle.removeClass('action-bth-active').addClass('action-bth-active-disable');
                }

                // 创建车道采集任务后，状态在4的时候可以下载图片
                if (sysStatus === 4) {
                    loadLanePicsBtn.removeClass('action-bth-disable').addClass('action-bth-normal');
                    lanePicNum.find('div').show();
                    lanePicNum.find('.pic-num')[0].innerText = sysData.pictures || 0;
                }
                else {
                    loadLanePicsBtn.removeClass('action-bth-normal').addClass('action-bth-disable');
                    lanePicNum.find('div').hide();
                    lanePicNum.find('.pic-num')[0].innerText = 0;
                }

                // 摄像头开启中，展示图片加载中
                if (sysStatus === 5) {
                    actionCenter.find('.img-loading').show();
                    actionCenter.find('.img-default').hide();
                }

                // 摄像头开启成功，显示标志图片
                if (sysStatus === 6) {
                    actionCenter.find('.img-loading').hide();
                    actionCenter.find('.img-default').hide();
                    actionCenter.find('.img-action').show();
                    actionCenter.find('.img-show').hide();
                    getSignImg();
                    getSignLabel();
                }

                // 图片和标签打包中
                if (sysStatus === 7) {
                    actionCenter.find('.img-loading').hide();
                    actionCenter.find('.img-default').show();
                    actionCenter.find('.img-action').hide();
                    actionCenter.find('.img-lane').hide();
                    dataCollectEmpty.show();
                    $('.data-collection .label-result').hide();
                }

                // 做完标志采集任务后，状态在8的时候可以下载图片
                if (sysStatus === 8) {
                    LoadSignPicsBtn.removeClass('action-bth-disable').addClass('action-bth-normal');
                    signPicNum.find('div').show();
                    signPicNum.find('.pic-num')[0].innerText = sysData['totals-packaged'] || 0;
                }
            },
            error: function (XMLHttpRequest, textStatus) {
            }
        });
    }, 1000);
});
