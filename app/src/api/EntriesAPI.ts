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
    const response = await fetch(import.meta.env.VITE_API_BASE_URL + '/entries/latest');
    if (!response) {
      throw new Error();
    }
    const data: Record<string, any> = await response.json();

    let entries: EntryTeaserData[] = [];
    for (let item of Object.values(data)) {
      entries.push(parseEntryTeaser(item));
    }

    return entries;
  }

  public async getUpdated(): Promise<EntryTeaserData[]> {
    const response = await fetch(import.meta.env.VITE_API_BASE_URL + '/entries/updated');
    if (!response) {
      throw new Error();
    }
    const data: Record<string, any> = await response.json();

    let entries: EntryTeaserData[] = [];
    for (let item of Object.values(data)) {
      entries.push(parseEntryTeaser(item));
    }

    return entries;
  }

  public async get(collection: string, path: string): Promise<EntryData> {
    const response = await fetch(import.meta.env.VITE_API_BASE_URL + '/entries/' + collection + '/' + path);
    if (!response) {
      throw new Error();
    }
    const data: Record<string, any> = await response.json();

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
    const response = await fetch(import.meta.env.VITE_API_BASE_URL + '/entries/search?' + params.toString());
    if (!response) {
      throw new Error();
    }
    const data: Record<string, any> = await response.json();

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
