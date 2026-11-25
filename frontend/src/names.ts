// "Jean Pierre Habimana" → "Jean H.": short enough for tables and cards
export function shortName(fullName: string): string {
  const words = fullName.trim().split(/\s+/)
  if (words.length < 2) return words[0] ?? ''
  return `${words[0]} ${words.at(-1)?.[0]?.toUpperCase()}.`
}
