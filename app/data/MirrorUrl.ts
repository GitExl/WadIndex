export interface MirrorUrl {
  title: string
  url: string
  location: string
  isHttpOnly: boolean
}

export function parseMirrorUrl(data: any): MirrorUrl {
  return {
    title: data.title,
    url: data.url,
    location: data.location,
    isHttpOnly: data.http_only ?? false
  };
}
