from fastapi import APIRouter, Body, UploadFile, File, Form
import httpx
import os
import uuid
from datetime import datetime

router = APIRouter()

# 本地上传目录：my-blog-manager/public/uploads
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
UPLOAD_DIR = os.path.join(PROJECT_ROOT, "public", "uploads")


@router.post("/test")
async def test_picbed_connection(payload: dict = Body(...)):
    url = payload.get("url", "").strip().rstrip('/')
    token = payload.get("token", "").strip()

    if not url or not token:
        return {"success": False, "message": "图床 API 地址和 Token 不能为空"}

    test_endpoint = f"{url}/api/v1/profile"
    if not token.startswith("Bearer "):
        token = f"Bearer {token}"

    headers = {"Authorization": token, "Accept": "application/json"}

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            response = await client.get(test_endpoint, headers=headers)
            if response.status_code != 200:
                return {"success": False, "message": f"校验失败，服务器返回了 {response.status_code} 错误"}

            data = response.json()
            if data.get("status") is True:
                user_email = data.get("data", {}).get("email", "未知用户")
                return {"success": True, "message": f"连接成功！当前账户: {user_email}"}
            else:
                return {"success": False, "message": f"Token 无效: {data.get('message', '未知错误')}"}
    except Exception as e:
        return {"success": False, "message": f"网络异常: {str(e)}"}


# 👇 【全新追加】：真实的图床图片上传接口
@router.post("/upload")
async def upload_image(
        file: UploadFile = File(...),
        url: str = Form(...),
        token: str = Form(...)
):
    url = url.strip().rstrip('/')
    token = token.strip()

    if not token.startswith("Bearer "):
        token = f"Bearer {token}"

    upload_endpoint = f"{url}/api/v1/upload"
    headers = {
        "Authorization": token,
        "Accept": "application/json"
    }

    try:
        content = await file.read()
        # 封装为 httpx 支持的文件上传格式
        files = {'file': (file.filename, content, file.content_type)}

        # 上传图片可能较慢，将超时设置为 30 秒
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(upload_endpoint, headers=headers, files=files)

            if response.status_code != 200:
                return {"success": False, "message": f"上传失败，图床返回了 {response.status_code} 错误"}

            data = response.json()
            # 兼容 Lsky Pro 的返回格式
            if data.get("status") is True:
                img_url = data.get("data", {}).get("links", {}).get("url")
                return {"success": True, "message": "上传成功", "url": img_url}
            else:
                return {"success": False, "message": f"图床拒绝接收: {data.get('message', '未知')}"}
    except httpx.ReadTimeout:
        return {"success": False, "message": "图片上传超时，请检查网络或图片是否过大"}
    except Exception as e:
        return {"success": False, "message": f"服务器异常: {str(e)}"}


# 👇 本地存储模式：图片保存到本地 public/uploads，无需第三方图床
@router.post("/upload_local")
async def upload_image_local(file: UploadFile = File(...)):
    try:
        # 确保上传目录存在
        os.makedirs(UPLOAD_DIR, exist_ok=True)

        # 生成唯一文件名（时间戳+随机串）
        ext = os.path.splitext(file.filename or "image.png")[1].lower()
        if ext not in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.avif', '.bmp']:
            ext = '.png'
        unique_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}{ext}"
        save_path = os.path.join(UPLOAD_DIR, unique_name)

        # 保存文件
        content = await file.read()
        with open(save_path, "wb") as f:
            f.write(content)

        # 返回可访问的 URL（通过 Next.js 的 public 目录访问）
        local_url = f"/uploads/{unique_name}"
        return {"success": True, "message": "本地保存成功", "url": local_url}
    except Exception as e:
        return {"success": False, "message": f"本地保存失败: {str(e)}"}


@router.get("/list_local")
async def list_local_images():
    """列出本地已上传的所有图片"""
    try:
        if not os.path.exists(UPLOAD_DIR):
            return {"success": True, "images": []}
        files = []
        for f in sorted(os.listdir(UPLOAD_DIR), reverse=True):
            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.avif', '.bmp')):
                files.append({"url": f"/uploads/{f}", "name": f})
        return {"success": True, "images": files}
    except Exception as e:
        return {"success": False, "message": str(e), "images": []}