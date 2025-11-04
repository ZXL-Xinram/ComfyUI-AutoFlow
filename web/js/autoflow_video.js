import { app } from '../../../scripts/app.js'
import { api } from '../../../scripts/api.js'

// 上传文件到ComfyUI
async function uploadFile(file) {
    try {
        const body = new FormData();
        body.append("image", file);
        body.append("subfolder", "");
        body.append("type", "input");
        
        const resp = await api.fetchApi("/upload/image", {
            method: "POST",
            body,
        });
        
        return resp;
    } catch (error) {
        console.error("Error uploading file:", error);
        throw error;
    }
}

// 调整节点高度以适应预览
function fitHeight(node) {
    node.setSize([node.size[0], node.computeSize([node.size[0], node.size[1]])[1]]);
    app?.graph?.setDirtyCanvas(true);
}

// 为节点添加视频预览widget
function addVideoPreview(node, videoWidget) {
    // 创建预览容器
    const element = document.createElement("div");
    
    // 添加DOM widget
    const previewWidget = node.addDOMWidget("videopreview", "preview", element, {
        serialize: false,
        hideOnZoom: false,
        getValue() {
            return element.value;
        },
        setValue(v) {
            element.value = v;
        },
    });
    
    // 计算预览尺寸
    previewWidget.computeSize = function(width) {
        if (this.aspectRatio && !this.parentEl.hidden) {
            let height = (node.size[0] - 20) / this.aspectRatio + 10;
            if (!(height > 0)) {
                height = 0;
            }
            this.computedHeight = height + 10;
            return [width, height];
        }
        return [width, -4]; // 没有视频时不显示
    };
    
    // 使用单独的对象存储预览状态，避免与element.value冲突
    previewWidget.previewState = { 
        hidden: false, 
        paused: false, 
        filename: null 
    };
    
    // 创建预览容器元素
    previewWidget.parentEl = document.createElement("div");
    previewWidget.parentEl.className = "autoflow_preview";
    previewWidget.parentEl.style.width = "100%";
    element.appendChild(previewWidget.parentEl);
    
    // 创建video元素
    previewWidget.videoEl = document.createElement("video");
    previewWidget.videoEl.controls = false;
    previewWidget.videoEl.loop = true;
    previewWidget.videoEl.muted = true;
    previewWidget.videoEl.autoplay = true;
    previewWidget.videoEl.style.width = "100%";
    previewWidget.videoEl.style.borderRadius = "4px";
    
    // 监听视频元数据加载
    previewWidget.videoEl.addEventListener("loadedmetadata", () => {
        previewWidget.aspectRatio = previewWidget.videoEl.videoWidth / previewWidget.videoEl.videoHeight;
        fitHeight(node);
    });
    
    // 监听视频加载错误
    previewWidget.videoEl.addEventListener("error", () => {
        previewWidget.parentEl.hidden = true;
        fitHeight(node);
    });
    
    // 鼠标悬停时取消静音
    previewWidget.videoEl.onmouseenter = () => {
        previewWidget.videoEl.muted = false;
    };
    
    previewWidget.videoEl.onmouseleave = () => {
        previewWidget.videoEl.muted = true;
    };
    
    previewWidget.parentEl.appendChild(previewWidget.videoEl);
    
    // 更新预览源
    previewWidget.updateSource = function(filename) {
        if (!filename) {
            this.parentEl.hidden = true;
            fitHeight(node);
            return;
        }
        
        // 更新预览状态
        this.previewState.filename = filename;
        
        // 构建视频URL
        const params = new URLSearchParams({
            filename: filename,
            type: "input",
            subfolder: ""
        });
        
        this.videoEl.src = api.apiURL('/view?' + params.toString());
        this.videoEl.hidden = false;
        this.parentEl.hidden = false;
        
        fitHeight(node);
    };
    
    return previewWidget;
}

// 为单个widget添加上传按钮和预览
function setupVideoWidget(node, widgetName) {
    // 查找视频选择widget
    const videoWidget = node.widgets?.find(w => w.name === widgetName);
    
    if (!videoWidget) {
        console.warn(`[AutoFlow] Widget ${widgetName} not found`);
        return;
    }
    
    // 添加视频预览
    const previewWidget = addVideoPreview(node, videoWidget);
    
    // 创建隐藏的文件输入元素
    const fileInput = document.createElement("input");
    Object.assign(fileInput, {
        type: "file",
        accept: "video/mp4,video/avi,video/mov,video/mkv,video/webm,video/flv,video/wmv,video/mpg,video/mpeg,video/m4v",
        style: "display: none",
        onchange: async () => {
            if (fileInput.files.length) {
                try {
                    const resp = await uploadFile(fileInput.files[0]);
                    if (resp.status === 200 || resp.status === 201) {
                        const data = await resp.json();
                        const filename = data.name;
                        
                        // 确保 options 和 values 存在
                        if (!videoWidget.options) {
                            videoWidget.options = {};
                        }
                        if (!videoWidget.options.values) {
                            videoWidget.options.values = [];
                        }
                        
                        // 添加到选项列表
                        if (!videoWidget.options.values.includes(filename)) {
                            videoWidget.options.values.push(filename);
                        }
                        
                        // 设置为当前值
                        videoWidget.value = filename;
                        
                        // 触发回调
                        if (videoWidget.callback) {
                            videoWidget.callback(filename);
                        }
                        
                        // 更新预览
                        previewWidget.updateSource(filename);
                        
                        console.log(`[AutoFlow] Video uploaded: ${filename}`);
                    } else {
                        console.error("[AutoFlow] Upload failed:", resp.status);
                        alert("Video upload failed. Please try again.");
                    }
                } catch (error) {
                    console.error("[AutoFlow] Upload error:", error);
                    alert("Error uploading video: " + error.message);
                }
            }
        },
    });
    
    document.body.append(fileInput);
    
    // 添加上传按钮widget
    const uploadButton = node.addWidget(
        "button",
        "choose video to upload",
        null,
        () => {
            // 清除活动点击事件
            app.canvas.node_widget = null;
            fileInput.click();
        }
    );
    
    // 不序列化按钮状态
    uploadButton.serialize = false;
    
    // 保存预览widget引用到videoWidget，以便callback可以访问
    if (!videoWidget._autoflow_preview_widgets) {
        videoWidget._autoflow_preview_widgets = [];
    }
    videoWidget._autoflow_preview_widgets.push(previewWidget);
    
    // 只在第一次设置callback
    if (!videoWidget._autoflow_callback_set) {
        const originalCallback = videoWidget.callback;
        videoWidget.callback = function(value) {
            // 先调用原始callback
            if (originalCallback) {
                originalCallback.apply(this, arguments);
            }
            // 更新所有预览
            if (value && this._autoflow_preview_widgets) {
                for (const preview of this._autoflow_preview_widgets) {
                    preview.updateSource(value);
                }
            }
        };
        // 标记已设置callback
        videoWidget._autoflow_callback_set = true;
    }
    
    // 如果已经有选中的视频，立即显示预览
    if (videoWidget.value) {
        previewWidget.updateSource(videoWidget.value);
    }
}

// 为节点类型添加多个视频上传widget
function addVideoUploadWidgets(nodeType, widgetNames) {
    const onNodeCreated = nodeType.prototype.onNodeCreated;
    
    nodeType.prototype.onNodeCreated = function() {
        const result = onNodeCreated?.apply(this, arguments);
        
        // 为每个widget设置上传按钮和预览
        for (const widgetName of widgetNames) {
            setupVideoWidget(this, widgetName);
        }
        
        return result;
    };
}

// 注册节点扩展
app.registerExtension({
    name: "AutoFlow.VideoNodes",
    
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        // 为 AutoFlowVideoToImages 节点添加上传按钮和预览
        if (nodeData.name === "AutoFlowVideoToImages") {
            addVideoUploadWidgets(nodeType, ["video_upload"]);
        }
        
        // 为 AutoFlowCombineVideoAndMask 节点添加上传按钮和预览
        if (nodeData.name === "AutoFlowCombineVideoAndMask") {
            addVideoUploadWidgets(nodeType, ["original_video_upload", "mask_video_upload"]);
        }
    },
});

console.log("[AutoFlow] Video upload extension with preview loaded");
