# 安装与 API 配置

首次使用或环境报错时读取本参考。

## 一次性准备

1. 安装 ffmpeg/ffprobe。
   - Windows: `winget install Gyan.FFmpeg`，安装后重开终端。
   - Mac: `brew install ffmpeg`。
   - Linux: `sudo apt install ffmpeg`。
2. 安装 Python 依赖：

```bash
pip install -r requirements.txt
```

3. 复制空密钥样例：

```bash
cp _work/.secret.env.example _work/.secret.env
```

4. 在 `_work/.secret.env` 填入自己的 key：

```text
APIMART_TOKEN=[已移除]
ARK_API_KEY=[已移除]
```

`_work/.secret.env` 不要上传、不要打包、不要展示给用户。

## 两条后端

| 镜头类型 | 默认后端 | 原因 |
|---|---|---|
| 有人脸、人物、换装真人 | APIMart Fast | 人脸更稳 |
| 产品、场景、清单、空镜 | 火山方舟 Seedance Mini | 成本低 |

只填一家 key 也能跑，但只能稳定处理对应镜头；缺 key 时如实提示用户。

## 验证 Mini

第一次正式生成前先跑：

```bash
python -m pipeline.verify_mini
```

通过后再复刻。若模型 ID 不匹配，在 `_work/.secret.env` 添加：

```text
FK_MODEL_MINI=正确的mini模型id
```

## 常用开关

```text
FK_FACE_ROUTE=ark     # 有脸镜也走火山 Fast
FK_ROUTE=ark          # 整片强制走火山
FK_RESOLUTION=480p    # 整片强制 480p，省钱草稿
FK_AI_LABEL=1         # 出片叠“AI生成”角标
```

## 成本控制

- 默认无人脸镜走 Mini，人物镜走 Fast。
- 默认产品/场景 480p，人物 720p。
- 先跑 g1 检查，不要直接全量烧钱。
- 某个镜头崩坏只重跑该镜，不整片返工。

成本估算只能作为参考，最终以平台账单为准。
