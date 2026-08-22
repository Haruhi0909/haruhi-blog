from fastapi import APIRouter, Query
import requests
from urllib.parse import urlparse, unquote

router = APIRouter()


def _get_url_filename(url: str) -> str:
    """从URL提取文件名（去扩展名）"""
    try:
        path = urlparse(url).path
        filename = unquote(path.split("/")[-1])
        return filename.rsplit(".", 1)[0] if "." in filename else filename
    except Exception:
        return "自定义音乐"


@router.get("/query")
def query_netease_music(song_id: str = Query(..., alias="id")):
    """查询歌曲详情，支持三种格式：纯网易云ID / 纯URL / ID|自定义URL"""
    print(f"\n[API] 🎵 收到音乐查询请求: {song_id}")

    # 格式1：网易云ID|自定义播放URL（用网易云元数据+自定义播放地址）
    if "|" in song_id:
        netease_id, custom_url = song_id.split("|", 1)
        netease_id = netease_id.strip()
        custom_url = custom_url.strip()
        try:
            api_url = f"https://music.163.com/api/song/detail/?id={netease_id}&ids=[{netease_id}]"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
                "Referer": "https://music.163.com/"
            }
            response = requests.get(api_url, headers=headers, timeout=5)
            data = response.json()
            if data.get("songs") and len(data["songs"]) > 0:
                song = data["songs"][0]
                print(f"[API] ✅ ID|URL 查询成功: {song['name']}")
                return {
                    "success": True,
                    "data": {
                        "id": song_id,
                        "name": song["name"],
                        "artist": song["artists"][0]["name"],
                        "album": song["album"]["name"],
                        "cover": song["album"]["picUrl"]
                    }
                }
        except Exception as e:
            print(f"[API] ⚠️ 网易云元数据获取失败，回退到URL模式: {e}")
        # 回退：只用URL文件名
        name = _get_url_filename(custom_url)
        return {"success": True, "data": {"id": song_id, "name": name, "artist": "自定义音乐", "album": "", "cover": ""}}

    # 格式2：纯URL（只有播放地址，无元数据）
    if song_id.startswith("http://") or song_id.startswith("https://"):
        name = _get_url_filename(song_id)
        print(f"[API] ✅ 纯URL查询: {name}")
        return {"success": True, "data": {"id": song_id, "name": name, "artist": "自定义音乐", "album": "", "cover": ""}}

    # 格式3：纯网易云ID（原有逻辑）
    try:
        api_url = f"https://music.163.com/api/song/detail/?id={song_id}&ids=[{song_id}]"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Referer": "https://music.163.com/"
        }
        response = requests.get(api_url, headers=headers, timeout=5)
        print(f"[API] 📡 网易云响应状态码: {response.status_code}")
        data = response.json()

        if data.get("songs") and len(data["songs"]) > 0:
            song = data["songs"][0]
            print(f"[API] ✅ 查询成功: {song['name']} - {song['artists'][0]['name']}")
            return {
                "success": True,
                "data": {
                    "id": song_id,
                    "name": song["name"],
                    "artist": song["artists"][0]["name"],
                    "album": song["album"]["name"],
                    "cover": song["album"]["picUrl"]
                }
            }
        print(f"[API] ❌ 查无此歌 (ID: {song_id})")
        return {"success": False, "message": "未找到该歌曲，可能是 VIP 歌曲或 ID 错误"}

    except Exception as e:
        print(f"[API] 💥 网易云接口发生严重错误: {str(e)}")
        return {"success": False, "message": f"后端请求失败: {str(e)}"}