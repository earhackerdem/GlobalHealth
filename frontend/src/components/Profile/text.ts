/**
 * A text that shows nothing is a missing one, as in the server (models.py
 * `_is_blank`): only whitespace, controls, format characters (U+200B) or the
 * Hangul and braille blank fillers.
 */
const BLANK = /^[\s\p{Cc}\p{Cf}ᅟᅠㅤﾠ⠀]*$/u

export const isBlank = (text: string): boolean => BLANK.test(text)
