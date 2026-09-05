export function formatScore(score: number): string {
  return `${Math.round(score)}%`;
}

export function truncateText(text: string, maxLength: number = 100): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength) + '...';
}
