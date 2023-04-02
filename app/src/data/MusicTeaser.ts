export interface MusicTeaserData {
  name: string
  hash: string
  duration?: number
  type: string
  href: string
}

export function parseMusicTeaserData(data: any): MusicTeaserData {
  return {
    name: data.name,
    hash: data.hash,
    duration: data.duration ?? undefined,
    type: data.type,
    href: data.href,
  }
}
