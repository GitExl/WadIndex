import { parseEntry, type EntryData } from './../data/Entry';
import { parseEntryTeaser, type EntryTeaserData } from '@/data/EntryTeaser';
import APIBase from "./APIBase";

export interface SearchResults {
  entries: EntryTeaserData[],
  entriesTotal: number,
  offset: number,
  limit: number,
}

export default class EntriesAPI extends APIBase {

  public async getLatest(): Promise<EntryTeaserData[]> {
    const data: Record<string, any> = await this.fetch('/entries/latest');
    if (!data) {
      throw new Error();
    }

    let entries: EntryTeaserData[] = [];
    for (let item of Object.values(data)) {
      entries.push(parseEntryTeaser(item));
    }

    return entries;
  }

  public async getUpdated(): Promise<EntryTeaserData[]> {
    const data: Record<string, any> = await this.fetch('/entries/updated');
    if (!data) {
      throw new Error();
    }

    let entries: EntryTeaserData[] = [];
    for (let item of Object.values(data)) {
      entries.push(parseEntryTeaser(item));
    }

    return entries;
  }

  public async get(collection: string, path: string): Promise<EntryData> {
    const data: Record<string, any> = await this.fetch('/entries/' + collection + '/' + path);
    if (!data) {
      throw new Error();
    }

    return parseEntry(data);
  }

  public async search(
    searchKey: string, collections: string[], searchFields: string[], filterGameplay: string[],
    filterGame: string[], sortField: string='relevance', sortOrder: string='desc',
    offset: number=0, limit: number=30
  ): Promise<SearchResults> {

    const params = new URLSearchParams({
      collections: collections.join(','),
      search_key: searchKey,
      search_fields: searchFields.join(','),
      filter_gameplay: filterGameplay.join(','),
      filter_game: filterGame.join(','),
      sort_field: sortField,
      sort_order: sortOrder,
      offset: String(offset),
      limit: String(limit),
    });
    const data: Record<string, any> = await this.fetch('/entries/search?' + params.toString());
    if (!data) {
      throw new Error();
    }

    let entries: EntryTeaserData[] = [];
    for (let item of Object.values(data.entries)) {
      entries.push(parseEntryTeaser(item));
    }

    return {
      entries: entries,
      entriesTotal: data.entries_total,
      offset: data.offset,
      limit: data.limit,
    };
  }
}
