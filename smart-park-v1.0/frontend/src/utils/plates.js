export function parsePlateNumbers(value) {
  if (!value) return []
  if (Array.isArray(value)) return value.map(v => String(v).trim()).filter(Boolean)

  const raw = String(value).trim()
  if (!raw) return []

  try {
    const parsed = JSON.parse(raw)
    if (Array.isArray(parsed)) return parsed.map(v => String(v).trim()).filter(Boolean)
  } catch {
    // Fall back to plain text parsing.
  }

  return raw
    .replace(/^\[|\]$/g, '')
    .split(/[,，;；\s]+/)
    .map(v => v.replace(/^['"]|['"]$/g, '').trim())
    .filter(Boolean)
}

export function firstPlateNumber(value) {
  return parsePlateNumbers(value)[0] || ''
}

export function formatPlateNumbers(value) {
  return parsePlateNumbers(value).join(',')
}
