import { $Fetch } from 'ofetch';
export default abstract class APIBase {

  protected fetch: $Fetch;

  constructor(fetch: $Fetch) {
    this.fetch = fetch;
  }
}
