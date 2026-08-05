import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'

const LANGUAGES = [
  'English',
  'Hindi',
  'Kannada',
  'Tamil',
  'Telugu',
  'Malayalam',
  'Marathi',
  'Bengali',
  'Gujarati',
  'Punjabi',
  'Odia',
  'Assamese',
  'Urdu',
]

interface LanguageSelectProps {
  value: string
  onChange: (value: string) => void
}

export function LanguageSelect({ value, onChange }: LanguageSelectProps) {
  return (
    <Select
      value={value}
      onValueChange={(value) => value && onChange(value)}
    >
      <SelectTrigger className="w-[160px]">
        <SelectValue placeholder="Language" />
      </SelectTrigger>
      <SelectContent>
        {LANGUAGES.map((lang) => (
          <SelectItem key={lang} value={lang}>{lang}</SelectItem>
        ))}
      </SelectContent>
    </Select>
  )
}
