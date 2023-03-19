import { parseImage } from '@/data/IndexImage';
import type { EntryTeaserData } from '@/data/EntryTeaser';
import APIBase from "./APIBase";

export default class EntriesAPI extends APIBase {

  public async getLatest(): Promise<EntryTeaserData[]> {
    const response = await fetch(import.meta.env.VITE_API_BASE_URL + '/entries/latest');
    if (!response) {
      throw new Error();
    }
    const data: Record<string, any> = await response.json();

    let entries: EntryTeaserData[] = [];
    for (let item of Object.values(data)) {
      entries.push({
        authors: item.authors,
        collection: String(item.collection),
        levelCount: Number.parseInt(item.level_count, 10),
        path: String(item.path),
        timestamp: Number.parseInt(item.timestamp, 10),
        title: String(item.title),
        description: String(item.description),
        game: String(item.game),
        image: parseImage(item.image),
      });
    }

    return entries;
  }

}
