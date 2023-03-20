import { parseImage } from '@/data/IndexImage';
import type { Author } from "./Author"
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
    authors: data.authors,
    collection: String(data.collection),
    levelCount: Number.parseInt(data.level_count, 10),
    path: String(data.path),
    timestamp: Number.parseInt(data.timestamp, 10),
    title: String(data.title),
    description: String(data.description),
    isSingleplayer: Boolean(data.is_singleplayer),
    isCooperative: Boolean(data.is_cooperative),
    isDeathmatch: Boolean(data.is_deathmatch),
    image: parseImage(data.image),
  };
}
