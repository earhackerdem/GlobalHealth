import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

/** `spokenLabel`: the accessible name when the visible text is a symbol ("A-"). */
export type ChipOption<V extends string> = {
  value: V
  label: string
  spokenLabel?: string
}

/** Chips under their own subtitle, inside the same group (chronic "Salud mental y adicciones"). */
export type ChipSubgroup<V extends string> = {
  label: string
  options: readonly ChipOption<V>[]
}

/**
 * Single-choice chips (prototype v4): a group (fieldset) named by `label`, one
 * toggle button per option with `aria-pressed`. Tapping the chosen chip again
 * clears it (`onChange(null)`), so every answer stays optional. `required`
 * only adds the visual asterisk: the group's name stays the clean label. An
 * entry of `options` may be a subgroup: a nested fieldset whose legend is its
 * subtitle, still one choice for the whole group.
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
  options: readonly (ChipOption<V> | ChipSubgroup<V>)[]
  value: V | null
  onChange: (next: V | null) => void
  showLabel?: boolean
  required?: boolean
  invalid?: boolean
  describedBy?: string
  className?: string
}) {
  const chip = (option: ChipOption<V>) => {
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
  }

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
        {options.map((option) =>
          "options" in option ? (
            <fieldset
              key={option.label}
              className="m-0 flex min-w-0 basis-full flex-wrap gap-2 border-0 p-0"
            >
              <legend className="mb-2 text-sm text-muted-foreground">
                {option.label}
              </legend>
              {option.options.map(chip)}
            </fieldset>
          ) : (
            chip(option)
          ),
        )}
      </fieldset>
    </div>
  )
}

export default ChipGroup
