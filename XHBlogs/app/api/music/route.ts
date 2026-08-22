import { NextRequest, NextResponse } from 'next/server'

const NET_EASE_HEADERS = {
  'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
  Referer: 'https://music.163.com/',
}

type SongResult = {
  id: string
  name?: string
  artist?: string
  author?: string
  cover?: string
  pic?: string
  url?: string
  lrc?: string
  error?: string
}

export async function GET(request: NextRequest) {
  const ids = request.nextUrl.searchParams.get('ids')
  if (!ids) {
    return NextResponse.json({ error: 'Missing ids parameter' }, { status: 400 })
  }

  const songIds = ids.split(',').map((id) => id.trim()).filter(Boolean)

  const results: SongResult[] = await Promise.all(
    songIds.map(async (songId): Promise<SongResult> => {
      // 格式1：网易云ID|自定义播放URL（用网易云元数据+自定义播放地址）
      if (songId.includes('|')) {
        const [neteaseId, customUrl] = songId.split('|').map(s => s.trim())
        try {
          const [detailRes, lrcRes] = await Promise.all([
            fetch(
              `https://music.163.com/api/song/detail/?id=${neteaseId}&ids=[${neteaseId}]`,
              { headers: NET_EASE_HEADERS, signal: AbortSignal.timeout(6000) },
            ),
            fetch(
              `https://music.163.com/api/song/lyric?id=${neteaseId}&lv=-1&kv=-1&tv=-1`,
              { headers: NET_EASE_HEADERS, signal: AbortSignal.timeout(6000) },
            ).catch(() => null),
          ])
          const detail = await detailRes.json()
          const song = detail.songs?.[0]
          let lrcText = ''
          if (lrcRes && lrcRes.ok) {
            try {
              const lrcData = await lrcRes.json()
              lrcText = lrcData.lrc?.lyric || ''
            } catch { /* 歌词可选 */ }
          }
          if (song) {
            const artistName = song.artists?.[0]?.name || '未知歌手'
            return {
              id: songId,
              name: song.name,
              artist: artistName,
              author: artistName,
              cover: song.album?.picUrl || '',
              pic: song.album?.picUrl || '',
              url: customUrl,
              lrc: lrcText,
            }
          }
        } catch { /* 网易云元数据获取失败，回退到纯URL模式 */ }
        // 回退：只用自定义URL的基本信息
        try {
          const urlObj = new URL(customUrl)
          const fileName = decodeURIComponent(urlObj.pathname.split('/').pop() || '自定义音乐')
          return { id: songId, name: fileName.replace(/\.[^.]+$/, ''), artist: '自定义音乐', author: '自定义音乐', cover: '', pic: '', url: customUrl, lrc: '' }
        } catch {
          return { id: songId, name: '自定义音乐', url: customUrl, error: 'invalid_url' }
        }
      }

      // 格式2：纯URL（只有播放地址，无元数据）
      if (songId.startsWith('http://') || songId.startsWith('https://')) {
        try {
          const urlObj = new URL(songId)
          const fileName = decodeURIComponent(urlObj.pathname.split('/').pop() || '自定义音乐')
          const songName = fileName.replace(/\.[^.]+$/, '')
          return {
            id: songId,
            name: songName,
            artist: '自定义音乐',
            author: '自定义音乐',
            cover: '',
            pic: '',
            url: songId,
            lrc: '',
          }
        } catch {
          return { id: songId, name: '自定义音乐', url: songId, error: 'invalid_url' }
        }
      }

      // 格式3：纯网易云ID
      try {
        const [detailRes, lrcRes] = await Promise.all([
          fetch(
            `https://music.163.com/api/song/detail/?id=${songId}&ids=[${songId}]`,
            { headers: NET_EASE_HEADERS, signal: AbortSignal.timeout(6000) },
          ),
          fetch(
            `https://music.163.com/api/song/lyric?id=${songId}&lv=-1&kv=-1&tv=-1`,
            { headers: NET_EASE_HEADERS, signal: AbortSignal.timeout(6000) },
          ).catch(() => null),
        ])

        const detail = await detailRes.json()
        const song = detail.songs?.[0]

        if (!song) {
          return { id: songId, error: 'not_found' }
        }

        let lrcText = ''
        if (lrcRes && lrcRes.ok) {
          try {
            const lrcData = await lrcRes.json()
            lrcText = lrcData.lrc?.lyric || ''
          } catch {
            /* 歌词可选，失败不影响主流程 */
          }
        }

        const artistName = song.artists?.[0]?.name || '未知歌手'

        return {
          id: songId,
          name: song.name,
          artist: artistName,
          author: artistName,
          cover: song.album?.picUrl || '',
          pic: song.album?.picUrl || '',
          url: `https://music.163.com/song/media/outer/url?id=${songId}.mp3`,
          lrc: lrcText,
        }
      } catch (error) {
        console.error(`[api/music] 获取歌曲 ${songId} 失败:`, error)
        return { id: songId, error: String(error) }
      }
    }),
  )

  return NextResponse.json(results)
}
