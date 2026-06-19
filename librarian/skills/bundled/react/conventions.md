# React / Next.js Conventions

## Project Structure (App Router — always prefer over Pages Router)
```
src/
  app/
    layout.tsx          # Root layout (REQUIRED, must have <html> and <body>)
    page.tsx            # Home page
    loading.tsx         # Suspense fallback
    error.tsx           # Error boundary (MUST be Client Component)
    not-found.tsx       # 404 UI
    (route-group)/      # Organize without affecting URL
    [param]/            # Dynamic segments
    api/route.ts        # API routes (.ts NOT .tsx)
  components/
    ui/                 # Low-level primitives
  lib/                  # Utilities, helpers
  hooks/                # Shared custom hooks
public/                 # Static assets
```

## Component Rules
- Functional components ONLY — never class components
- Server Components by default (no directive needed)
- Add `'use client'` only to leaf interactive components (NOT layouts/pages)
- Server Components can be `async`, use `await` directly
- Client Components need `'use client'` at top, can use hooks/events

## File Naming
- Components: PascalCase (`Button.tsx`)
- Pages/Routes: lowercase (`page.tsx`, `layout.tsx`)
- Hooks: camelCase with `use` prefix (`useMediaQuery.ts`)
- Utilities: camelCase (`formatDate.ts`)
- API routes: `route.ts` (NOT .tsx)

## Import Order
1. React/Next.js core (`react`, `next/navigation`, `next/link`)
2. Third-party libraries
3. Internal components (`@/components/...`)
4. Internal hooks/utils (`@/hooks/...`, `@/lib/...`)
5. Types (`import type { ... }`)

Use `@/` path alias for all internal imports.

## State Management
- Local state: `useState` for simple, `useReducer` for complex
- Global state: Context (sparingly) or Zustand
- Server state: React Query / TanStack Query
- Lift state up to closest common parent when shared

## Styling
- Tailwind CSS as default
- Use `cn()` utility (clsx + tailwind-merge) for conditional classes
- Use `className` not `class`
- Avoid inline styles except for dynamic values

## TypeScript
- Never use `any` — use `unknown` and narrow
- Use `React.ReactNode` for children props
- Use type imports: `import type { User } from '@/types'`
- Use Zod for runtime validation

## Data Fetching
- Server Components: direct `await fetch()` or DB queries
- Client Components: React Query or SWR
- Never use `useEffect` for data fetching in Server Components
- Parallel fetching: `Promise.all()`

## Performance
- Don't overuse `memo`, `useMemo`, `useCallback` — only when measured
- Lazy load with `dynamic()` for heavy components
- Use `loading.tsx` for instant loading states

## Anti-Patterns to Avoid
- Class components → functional only
- `'use client'` on root layout → only on leaf components
- `useEffect` for data fetching → Server Components or React Query
- `class` attribute → use `className`
- Barrel exports (`index.ts`) → import directly from files
- `.tsx` for API routes → use `.ts`
- Passing non-serializable props Server→Client
- Missing `<html>` and `<body>` in root layout
- Using Pages Router for new projects
