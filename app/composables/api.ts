import { ofetch } from "ofetch";
import { API } from "~/api/API";

let api: API | undefined;

export const useApi = (): API => {
  if (api === undefined) {
    const runtimeConfig = useRuntimeConfig();
    const apiFetch = ofetch.create({ baseURL: runtimeConfig.public.apiBase, parseResponse: JSON.parse })
    api = new API(apiFetch);
  }
  return api;
}
