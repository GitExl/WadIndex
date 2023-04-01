export interface IndexImage {
  href: string
  hrefThumbnail: string
  name: string
  width: number
  height: number
  aspectRatio: number
}

export function parseImage(data?: any): IndexImage|undefined {
  if (!data) {
    return undefined;
  }

  return {
    name: data.name,
    href: data.href,
    hrefThumbnail: data.href_thumbnail,
    width: Number.parseInt(data.width, 10),
    height: Number.parseInt(data.height, 10),
    aspectRatio: data.aspect_ratio,
  };
}
