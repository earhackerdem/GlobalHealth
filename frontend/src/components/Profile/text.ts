/**
 * A text that shows nothing is a missing one, as in the server (models.py
 * `_is_blank`): only whitespace, controls, format characters (U+200B), any
 * Default_Ignorable_Code_Point (U+034F, U+FE0F, the Hangul fillers…) or the
 * braille blank. Escapes only: the raw characters are invisible in review.
 */
const BLANK = /^[\s\p{Cc}\p{Cf}\p{Default_Ignorable_Code_Point}\u2800]*$/u

export const isBlank = (text: string): boolean => BLANK.test(text)
