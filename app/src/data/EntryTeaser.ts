import type { Author } from "./Author"
import type { IndexImage } from "./IndexImage"

export interface EntryTeaserData {
  collection: string
  path: string
  title: string
  timestamp: number
  game?: string
  description?: string
  authors: Author[]
  levelCount: number
  image?: IndexImage
}
