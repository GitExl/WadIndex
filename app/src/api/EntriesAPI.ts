import { parseEntry, type EntryData } from './../data/Entry';
import { parseEntryTeaser, type EntryTeaserData } from '@/data/EntryTeaser';
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

}
