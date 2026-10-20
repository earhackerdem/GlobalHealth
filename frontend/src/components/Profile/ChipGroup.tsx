import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

/** `spokenLabel`: the accessible name when the visible text is a symbol ("A-"). */
export type ChipOption<V extends string> = {
  value: V
  label: string
  spokenLabel?: string
}

/**
 * Single-choice chips (prototype v4): a group (fieldset) named by `label`, one
 * toggle button per option with `aria-pressed`. Tapping the chosen chip again
 * clears it (`onChange(null)`), so every answer stays optional. `required`
 * only adds the visual asterisk: the group's name stays the clean label.
 */
function ChipGroup<V extends string>({
  label,
  options,
  value,
  onChange,
  showLabel = true,
  required = false,
  invalid = false,
  describedBy,
  className,
}: {
  label: string
  options: readonly ChipOption<V>[]
  value: V | null
  onChange: (next: V | null) => void
  showLabel?: boolean
  required?: boolean
  invalid?: boolean
  describedBy?: string
  className?: string
}) {
  return (
    <div className={cn("grid gap-2", className)}>
      {showLabel && (
        <span className="text-sm font-medium" aria-hidden="true">
          {label}
          {required && (
            <>
              {" "}
              <span className="text-destructive">*</span>
            </>
          )}
        </span>
      )}
      {/* A fieldset is the native role="group"; aria-label names it (K5). */}
      <fieldset
        aria-label={label}
        aria-describedby={describedBy}
        data-invalid={invalid || undefined}
        className="m-0 flex min-w-0 flex-wrap gap-2 border-0 p-0"
      >
        {options.map((option) => {
          const pressed = value === option.value
          return (
            <Button
              key={option.value}
              type="button"
              size="sm"
              variant={pressed ? "default" : "outline"}
              aria-pressed={pressed}
              aria-label={option.spokenLabel}
              onClick={() => onChange(pressed ? null : option.value)}
            >
              {option.label}
            </Button>
          )
        })}
      </fieldset>
    </div>
  )
}

export default ChipGroup
