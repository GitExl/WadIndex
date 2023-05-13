import { $Fetch } from "ofetch";
import EntriesAPI from "./EntriesAPI";
import GraphicsAPI from "./GraphicsAPI";

export class API {
  public readonly graphics: GraphicsAPI;
  public readonly entries: EntriesAPI;

  constructor(fetch: $Fetch) {
    this.graphics = new GraphicsAPI(fetch);
    this.entries = new EntriesAPI(fetch);
  }
}
