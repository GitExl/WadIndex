import { parseImage, type IndexImage } from "@/data/IndexImage";
import APIBase from "./APIBase";
import { FetchResponse } from "ofetch";

export default class GraphicsAPI extends APIBase {

  public async getRandom(): Promise<IndexImage[]> {
    const data: Record<string, any> = await this.fetch<FetchResponse<object>>('/images/random');
    if (!data) {
      throw new Error();
    }

    let graphics: IndexImage[] = [];
    for (let item of Object.values(data)) {
      const image = parseImage(item);
      if (image) {
        graphics.push(image);
      }
    }

    return graphics;
  }

}
