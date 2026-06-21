import type { ModelOption } from '../api/agent'

export function resizeTextarea(element: HTMLTextAreaElement | null) {
  if (!element) return
  element.style.height = 'auto'
  element.style.height = `${element.scrollHeight}px`
}

export function defaultModelLabel(options: ModelOption[]) {
  const defaultOption = options.find(option => option.is_default)
  return defaultOption ? `（${defaultOption.label}）` : ''
}
