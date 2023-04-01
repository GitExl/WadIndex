import { parseAuthor, type Author } from './Author';

export interface LevelTeaserData {
  collection: string
  path: string
  name: string
  title?: string
  musicName?: string
  format: string
  next: string
  nextSecret: string
  authors: Author[]
}

export function parseLevelTeaserData(data: any): LevelTeaserData {
  return {
    collection: data.collection,
    path: data.path,
    name: data.name,
    title: data.title,
    musicName: data.music_name,
    format: data.format,
    next: data.next,
    nextSecret: data.next_secret,
    authors: data.authors?.map(parseAuthor),
  }
}
