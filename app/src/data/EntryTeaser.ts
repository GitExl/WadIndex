import { parseImage } from '@/data/IndexImage';
import { parseAuthor, type Author } from "./Author"
import type { IndexImage } from "./IndexImage"

export interface EntryTeaserData {
  collection: string
  path: string
  title: string
  timestamp: number
  isSingleplayer: boolean
  isCooperative: boolean
  isDeathmatch: boolean
  description?: string
  authors: Author[]
  levelCount: number
  image?: IndexImage
}

export function parseEntryTeaser(data: any): EntryTeaserData {
  return {
    authors: data.authors.map(parseAuthor),
    collection: data.collection,
    levelCount: Number.parseInt(data.level_count, 10),
    path: data.path,
    timestamp: Number.parseInt(data.timestamp, 10),
    title: data.title,
    description: data.description,
    isSingleplayer: Boolean(data.is_singleplayer),
    isCooperative: Boolean(data.is_cooperative),
    isDeathmatch: Boolean(data.is_deathmatch),
    image: parseImage(data.image),
  };
}
