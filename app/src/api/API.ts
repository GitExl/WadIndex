import EntriesAPI from "./EntriesAPI";
import GraphicsAPI from "./GraphicsAPI";

export class API {
  public readonly graphics: GraphicsAPI;
  public readonly entries: EntriesAPI;

  constructor() {
    this.graphics = new GraphicsAPI();
    this.entries = new EntriesAPI();
  }
}

export default new API();
