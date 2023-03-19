export interface IndexImage {
  href: string
  hrefThumbnail: string
  name: string
  width: number
  height: number
}

export function parseImage(data?: any): IndexImage|undefined {
  if (!data) {
    return undefined;
  }

  return {
    name: String(data.name),
    href: String(data.href),
    hrefThumbnail: String(data.href_thumbnail),
    width: Number.parseInt(data.width, 10),
    height: Number.parseInt(data.height, 10),
  };
}
