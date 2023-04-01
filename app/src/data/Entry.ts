import { type MirrorUrl, parseMirrorUrl } from './MirrorUrl';
import { parseImage } from '@/data/IndexImage';
import { parseAuthor, type Author } from "./Author"
import type { IndexImage } from "./IndexImage"
import { parseLevelTeaserData, type LevelTeaserData } from './LevelTeaser';

export interface EntryData {
  collection: string
  path: string
  title: string
  size: number
  timestamp: Date
  game: string
  engine: string
  isSingleplayer: boolean
  isCooperative: boolean
  isDeathmatch: boolean

  description?: string
  toolsUsed?: string
  credits?: string
  knownBugs?: string
  comments?: string

  mirrorUrls: MirrorUrl[]
  authors: Author[]
  images: IndexImage[]
  levels: LevelTeaserData[]
  // music: Music[]
}

export function parseEntry(data: any): EntryData {
  return {
    collection: data.collection,
    path: data.path,
    title: data.title,
    size: Number.parseInt(data.size, 10),
    timestamp: new Date(data.timestamp * 1000),
    game: data.game,
    engine: data.engine,
    isSingleplayer: Boolean(data.is_singleplayer),
    isCooperative: Boolean(data.is_cooperative),
    isDeathmatch: Boolean(data.is_deathmatch),

    description: data.description,
    toolsUsed: data.toolsUsed,
    credits: data.credits,
    knownBugs: data.knownBugs,
    comments: data.comments,

    mirrorUrls: data.mirror_urls?.map(parseMirrorUrl),
    authors: data.authors?.map(parseAuthor),
    images: data.images?.map(parseImage),
    levels: data.maps?.map(parseLevelTeaserData),
  };
}
