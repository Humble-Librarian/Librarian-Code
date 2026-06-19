# Web Development Conventions

## File Structure
- Single-file apps: `< 300 LOC` → single `index.html` with inline `<style>` and `<script>`
- Multi-file apps: `index.html` + `css/` + `js/` + `assets/`
- Files: lowercase-kebab-case (`my-component.js`)
- CSS classes: BEM or kebab-case (`.card__title--large`)
- JS variables/functions: camelCase

## HTML Rules
- Always include: `<!DOCTYPE html>`, `<html lang="en">`, `<meta charset="UTF-8">`, viewport meta
- Use semantic elements: `<header>`, `<nav>`, `<main>`, `<article>`, `<section>`, `<footer>`
- Every `<img>` must have `alt` attribute
- Use `<button>` for actions, `<a>` for navigation (not `<div onclick>`)
- Maintain heading hierarchy: h1 > h2 > h3 (never skip)
- Add `rel="noopener noreferrer"` on `target="_blank"` links

## CSS Rules
- Use CSS custom properties for repeated values
- Use `box-sizing: border-box` universally
- Use `rem` for spacing/sizing, `px` only for borders
- Mobile-first responsive design with `min-width` media queries
- Flexbox for 1D layouts, Grid for 2D layouts
- Use `gap` property over margin hacks
- Never use `float` for layout, never use `!important`
- Max selector depth: 3 levels
- Use `clamp()` for fluid typography

## JavaScript Rules
- Always use `const` by default, `let` when reassignment needed, never `var`
- Always use `addEventListener`, never inline handlers
- Use `textContent` for user-provided text (XSS prevention), never `innerHTML` with unsanitized input
- Always use `try/catch` with async operations
- Use `===` not `==`
- Use arrow functions for callbacks
- Use template literals over string concatenation
- Use optional chaining `?.` and nullish coalescing `??`
- Never use `eval()`

## Security
- Never insert user input as HTML (use `textContent`)
- Validate client-side AND server-side
- Never store secrets in localStorage
- Use HTTPS for all external resources
- Don't expose API keys in client-side code

## Anti-Patterns to Avoid
- `<div onclick>` → use `<button>` or `addEventListener`
- `float: left` for grid → use flexbox or grid
- `var` → use `const`/`let`
- `==` → use `===`
- `innerHTML = userInput` → use `textContent`
- Global variables → use modules or block scope
- `.then()` chains → use `async/await`
