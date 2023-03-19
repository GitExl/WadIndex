import { parseImage, type IndexImage } from "@/data/IndexImage";
import APIBase from "./APIBase";

export default class GraphicsAPI extends APIBase {

  public async getRandom(): Promise<IndexImage[]> {
    const response = await fetch(import.meta.env.VITE_API_BASE_URL + '/graphics/random');
    if (!response) {
      throw new Error();
    }
    const data: Record<string, any> = await response.json();

    let graphics: IndexImage[] = [];
    for (let item of Object.values(data)) {
      graphics.push(parseImage(item));
    }

    return graphics;
  }

}
