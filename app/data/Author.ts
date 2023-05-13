export interface Author {
  name: string
  fullName?: string
  nickname?: string
  alias: string
}

export function parseAuthor(data: any): Author {
  return {
    name: data.name,
    fullName: data.full_name,
    nickname: data.nickname,
    alias: data.alias,
  }
}
