export function withBase(path: string): string {
  const normalized = path.replace(/^\/+/, '')
  return `${import.meta.env.BASE_URL}${normalized}`.replace(/\/{2,}/g, '/')
}
