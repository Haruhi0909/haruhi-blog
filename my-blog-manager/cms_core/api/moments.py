import os
import shutil
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

# 前台博客目录（管理台的上级目录下的 XHBlogs）
CURRENT_API_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_API_DIR, "..", ".."))
FRONTEND_DIR = os.path.abspath(os.path.join(PROJECT_ROOT, "..", "XHBlogs"))


def sync_file_to_frontend(rel_path: str, delete: bool = False):
    """把管理台的文件同步到前台目录"""
    try:
        src = os.path.join(PROJECT_ROOT, rel_path)
        dst = os.path.join(FRONTEND_DIR, rel_path)
        if delete:
            if os.path.exists(dst):
                os.remove(dst)
                print(f"[自动同步] 已删除前台文件: {dst}")
        else:
            if os.path.exists(src):
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)
                print(f"[自动同步] 已复制到前台: {dst}")
    except Exception as e:
        print(f"[自动同步] 失败: {e}")


class MomentPayload(BaseModel):
    id: str
    date: str
    content: str
    location: Optional[str] = ""
    images: List[str] = []


@router.post("/save")
def save_moment(payload: MomentPayload):
    try:
        # 🌟 绝对路径修复魔法 🌟
        # 1. 获取当前 moments.py 文件所在的绝对路径 (也就是 cms_core/api 目录)
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # 2. 往上退两级，定位到你的博客管理端根目录 (my-blog-manager)
        project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))

        # 3. 🎯 精准指向你指定的 moments 文件夹！
        MOMENTS_DIR = os.path.join(project_root, "moments")

        if not os.path.exists(MOMENTS_DIR):
            os.makedirs(MOMENTS_DIR, exist_ok=True)

        # 4. 文件名使用前端传来的唯一 id (格式如 moment-17123456789.md)
        # 这样同一天发多条说说，文件也不会互相覆盖
        file_path = os.path.join(MOMENTS_DIR, f"{payload.id}.md")

        # 构造 Markdown Front-matter
        frontmatter_lines = ["---"]
        frontmatter_lines.append(f'id: "{payload.id}"')
        frontmatter_lines.append(f'date: "{payload.date}"')

        if payload.location:
            frontmatter_lines.append(f'location: "{payload.location}"')

        if payload.images:
            frontmatter_lines.append("images:")
            for img in payload.images:
                frontmatter_lines.append(f"  - '{img}'")

        frontmatter_lines.append("---")
        frontmatter_lines.append("")  # 留一个空行

        file_content = "\n".join(frontmatter_lines) + "\n" + payload.content

        # 写入 .md 文件
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(file_content)

        # 🌟 自动同步到前台
        sync_file_to_frontend(f"moments/{payload.id}.md")

        # 🌟 在 Python 终端里大声喊出文件到底存哪了！
        print(f"\n[成功] 说说已落盘，精准物理路径：{file_path}\n")

        return {"success": True, "message": f"成功保存到: {file_path}"}

    except Exception as e:
        print(f"\n[报错] 写入失败：{str(e)}\n")
        return {"success": False, "message": f"写入物理文件失败: {str(e)}"}


class DeletePayload(BaseModel):
    id: str

@router.post("/delete")
def delete_moment(payload: DeletePayload):
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
        MOMENTS_DIR = os.path.join(project_root, "moments")

        file_path = os.path.join(MOMENTS_DIR, f"{payload.id}.md")

        if os.path.exists(file_path):
            os.remove(file_path)
            # 🌟 自动同步删除前台文件
            sync_file_to_frontend(f"moments/{payload.id}.md", delete=True)
            print(f"\n[删除成功] 物理文件已粉碎：{file_path}\n")
            return {"success": True, "message": "文件已删除"}
        else:
            return {"success": False, "message": "文件不存在，无法删除"}

    except Exception as e:
        print(f"\n[删除报错] {str(e)}\n")
        return {"success": False, "message": f"删除失败: {str(e)}"}