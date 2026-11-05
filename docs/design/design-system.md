# Tevrox Design System

## Color Palette

All colors use CSS variables defined in `globals.css` (web) and `tokens.ts` (mobile). Override these values to rebrand.

### Web (CSS Variables)

```css
:root {
  /* Primary brand color */
  --tevrox-primary: 210 90% 42%;        /* hsl() - main action color */
  --tevrox-primary-hover: 210 90% 48%;
  --tevrox-primary-active: 210 90% 38%;

  /* Neutral scale */
  --tevrox-neutral-50: 0 0% 100%;
  --tevrox-neutral-100: 0 0% 98%;
  --tevrox-neutral-200: 0 0% 94%;
  --tevrox-neutral-300: 0 0% 88%;
  --tevrox-neutral-400: 0 0% 78%;
  --tevrox-neutral-500: 0 0% 65%;
  --tevrox-neutral-600: 0 0% 52%;
  --tevrox-neutral-700: 0 0% 38%;
  --tevrox-neutral-800: 0 0% 25%;
  --tevrox-neutral-900: 0 0% 18%;

  /* Status colors */
  --tevrox-success: 142 70% 45%;
  --tevrox-success-hover: 142 70% 51%;
  --tevrox-success-active: 142 70% 39%;

  --tevrox-warning: 45 90% 55%;
  --tevrox-warning-hover: 45 90% 61%;
  --tevrox-warning-active: 45 90% 49%;

  --tevrox-danger: 0 85% 55%;
  --tevrox-danger-hover: 0 85% 61%;
  --tevrox-danger-active: 0 85% 49%;

  --tevrox-info: 210 90% 55%;
  --tevrox-info-hover: 210 90% 61%;
  --tevrox-info-active: 210 90% 49%;

  /* Backgrounds */
  --tevrox-bg: var(--tevrox-neutral-100);
  --tevrox-bg-subtle: var(--tevrox-neutral-100);
  --tevrox-card: var(--tevrox-neutral-100);
  --tevrox-border: var(--tevrox-neutral-300);

  /* Text colors */
  --tevrox-text: var(--tevrox-neutral-900);
  --tevrox-text-muted: var(--tevrox-neutral-600);
  --tevrox-text-inverse: var(--tevrox-neutral-50);
}
```

### Mobile (tokens.ts)

```typescript
export const tokens = {
  primary: "hsl(210, 90%, 42%)",
  primaryHover: "hsl(210, 90%, 48%)",
  primaryActive: "hsl(210, 90%, 38%)",
  
  neutral: {
    50: "#ffffff",
    100: "#fafafa",
    200: "#f5f5f5",
    300: "#e5e5e5",
    400: "#d4d4d4",
    500: "#a3a3a3",
    600: "#737373",
    700: "#525252",
    800: "#3f3f3f",
    900: "#262626",
  },
  
  status: {
    success: "hsl(142, 70%, 45%)",
    warning: "hsl(45, 90%, 55%)",
    danger: "hsl(0, 85%, 55%)",
    info: "hsl(210, 90%, 55%)",
  },
  
  background: "#ffffff",
  card: "#ffffff",
  border: "rgba(0, 0, 0, 0.1)",
  
  text: "#18181b",
  textMuted: "#6b6b6b",
};
```

### Usage Examples

| Component | Web (className) | Mobile (style) |
|-----------|-----------------|----------------|
| Primary button | `bg-primary text-primary-inverse hover:bg-primary-hover` | `{backgroundColor: tokens.primary, color: "#fff", ...}` |
| Success badge | `bg-success text-success-inverse` | `{backgroundColor: tokens.status.success, color: "#fff", ...}` |
| Danger button | `bg-danger text-white hover:bg-danger-hover` | `{backgroundColor: tokens.status.danger, ...}` |
| Card | `bg-card p-4 rounded-md shadow-sm` | `{backgroundColor: tokens.card, padding: 4, borderRadius: 12, ...}` |

## Typography Scale

| Scale | Size | Line Height | Usage |
|-------|------|-------------|-------|
| `text-xs` | 0.75rem (12px) | 1rem | Secondary labels, captions |
| `text-sm` | 0.875rem (14px) | 1.5rem | Body text, smaller |
| `text-base` | 1rem (16px) | 1.75rem | Default body text |
| `text-lg` | 1.125rem (18px) | 2rem | Section headers |
| `text-xl` | 1.25rem (20px) | 2.25rem | Page titles |
| `text-2xl` | 1.5rem (24px) | 2.5rem | Headings, prominent text |
| `text-3xl` | 2rem (32px) | 2.75rem | Major section headers |

### Font Family

- Primary: `system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, "Apple Color Emoji", "Segoe UI Emoji"`
- Apply via CSS class `font-primary` or Tailwind `font-sans`

## Spacing Scale

| Scale | Value | Usage |
|-------|-------|-------|
| `px-1` | 0.25rem (4px) | Minimal padding |
| `px-2` | 0.5rem (8px) | Horizontal spacing |
| `px-3` | 0.75rem (12px) | Control padding |
| `px-4` | 1rem (16px) | Standard horizontal |
| `px-6` | 1.5rem (24px) | Section padding |
| `py-2` | 0.5rem (8px) | Vertical spacing |
| `py-4` | 1rem (16px) | Standard vertical |
| `py-6` | 1.5rem (24px) | Section spacing |
| `m-4` | 1rem (16px) | Margin |
| `m-6` | 1.5rem (24px) | Section margin |

## Radius Scale

| Scale | Value | Usage |
|-------|-------|-------|
| `rounded-sm` | 0.125rem (2px) | Small inputs, chips |
| `rounded` | 0.25rem (4px) | Default button corners |
| `rounded-md` | 0.375rem (6px) | Cards, modals |
| `rounded-lg` | 0.5rem (8px) | Elevated cards |
| `rounded-xl` | 0.75rem (12px) | Photo avatars, large cards |
| `rounded-full` | 9999px | Circular avatars, pills |

## Shadow Scale

| Scale | Value | Usage |
|-------|-------|-------|
| `shadow-sm` | `0 1px 2px 0 rgba(0, 0, 0, 0.05)` | Small inputs, subtle |
| `shadow` | `0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.05)` | Cards, default |
| `shadow-md` | `0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)` | Elevated elements |
| `shadow-lg` | `0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)` | Modals, drawers |

## Iconography

- **Web**: `@heroicons/react` (solid for active, outline for inactive) or `lucide-react`
- **Mobile**: `@expo/vector-icons` (ionicons5 style) or `lucide-react-native`
- Icon color: currentColor (inherits text color) or status color
- Size: `h-4 w-4`, `h-5 w-5`, `h-6 w-6` (Tailwind) or `{width: 20, height: 20}` (mobile)

### Status Icon Mapping

| Status | Icon Name | Color |
|--------|-----------|-------|
| Verified | `CheckCircle` | `var(--tevrox-success)` |
| Unverified | `Clock` | `var(--tevrox-warning)` |
| Rejected | `XCircle` | `var(--tevrox-danger)` |
| Unreviewed | `QuestionMark` | `var(--tevrox-info)` |

## Tone of Voice for UI Copy

- **Calm and trustworthy**: Use simple, plain English. No medical claims.
- **Action-oriented**: Buttons say what they do ("Verify", "Reject", "Submit", "Cancel").
- **Educational**: Ingredient descriptions show plain facts, not promises.
- **Error states**: Explain what happened and what to do next, not just codes.
- **Encouraging**: "Your product is queued for review" vs "Pending".

## Accessibility Rules

### Web (Tailwind + Radix/shadcn/ui)

- **Contrast**: All text vs background must meet WCAG AA (4.5:1 minimum). 
  - Neutral-900 vs Neutral-100: ✓ 21:1
  - Neutral-600 vs Neutral-100: ✓ 4.5:1
  - White vs Primary: ✓ 7:1 (verify after color changes)
- **Focus rings**: `focus-visible: outline-2 focus-visible outline-offset-2 focus-visible:ring-2 focus-visible:ring-primary`
- **Touch targets**: Minimum 44px tap area (enforce via `min-h-9 min-w-9` on mobile-friendly web buttons)
- **Semantic HTML**: `<button>` for actions, `<input type="text">` for fields, `<nav>` for navigation
- **ARIA**: Labels on all form fields (`aria-label` or `<label>`), `role="status"` for live region errors, `aria-live="polite"` for toasts
- **Skip links**: `#main-content` skip-to at top of page for keyboard users
- **Color independence**: Never use color alone to convey meaning (e.g., also use text or icons)

### Mobile (React Native + StyleSheet)

- **Touch targets**: Minimum 44×44 dp (enforced via StyleSheet constants)
- **Dynamic type**: Support Text Size accessibility size; use `scale(1)` transforms that don't break layout
- **Contrast**: Same WCAG AA targets as web
- **Screen reader**: `accessibilityLabel` on all tappable elements, `accessibilityHint` for complex controls
- **Focus**: Virtual focus ring on iOS when navigating with keyboard (Tab key), `accessible={true}` on all interactive elements
- **No color-only meaning**: Same as web - use text labels + icons

## Verification Badge Colors

| Status | Background | Text | Icon |
|--------|-----------|------|------|
| **Verified** | `var(--tevrox-success)` or `hsl(142, 70%, 45%)` | White (`#fff`) | Check circle |
| **Unverified** | `var(--tevrox-warning)` or `hsl(45, 90%, 55%)` | White (`#fff`) | Clock |
| **Rejected** | `var(--tevrox-danger)` or `hsl(0, 85%, 55%)` | White (`#fff`) | X circle |
| **Unreviewed ingredient** | `var(--tevrox-info)` or `hsl(210, 90%, 55%)` | White (`#fff`) | Question mark |

## Coming Soon Status Badge

Used for disabled feature registry entries:

```
Coming Soon
```

- Background: `var(--tevrox-neutral-200)` or `hsl(0, 0%, 94%)`
- Text: `var(--tevrox-neutral-700)` or `hsl(0, 0%, 38%)`
- Font size: text-sm
- Border: 1px solid var(--tevrox-neutral-300)

---