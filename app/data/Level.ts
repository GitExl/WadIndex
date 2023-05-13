import { parseAuthor, type Author } from './Author';

export interface Level {
  collection: string
  path: string
  name: string
  title?: string
  musicName?: string
  format: string
  authors: Author[]
}

export function parseLevel(data: any): Level {
  return {
    collection: data.collection,
    path: data.path,
    name: data.name,
    title: data.title,
    musicName: data.music_name,
    format: data.format,
    authors: data.authors?.map(parseAuthor),
  }
}
