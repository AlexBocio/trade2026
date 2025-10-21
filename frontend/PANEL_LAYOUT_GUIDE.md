# Panel Layout Guide - Trade2025

## Overview
This guide explains the standard panel layout system for Trade2025. All panels automatically handle overflow and maintain consistent spacing.

## Core Components

### 1. Panel (Main Container)
```tsx
import { Panel } from '../components/common/Panel';

<Panel>
  {/* Content here */}
</Panel>
```
- Automatically handles overflow
- Uses flexbox for internal layout
- Has dark gray background and border

### 2. PanelHeader (Fixed Header)
```tsx
<Panel>
  <PanelHeader>
    <h2>Panel Title</h2>
  </PanelHeader>
  {/* Other content */}
</Panel>
```
- Fixed at top (doesn't scroll)
- Always visible
- Has bottom border

### 3. PanelContent (Scrollable Content)
```tsx
<Panel>
  <PanelHeader>Title</PanelHeader>
  <PanelContent>
    {/* Scrollable content here */}
  </PanelContent>
</Panel>
```
- Automatically scrolls when content overflows
- Grows to fill available space
- Has padding built-in

### 4. PanelFooter (Fixed Footer)
```tsx
<Panel>
  <PanelHeader>Title</PanelHeader>
  <PanelContent>Content</PanelContent>
  <PanelFooter>
    <button>Action</button>
  </PanelFooter>
</Panel>
```
- Fixed at bottom (doesn't scroll)
- Always visible
- Has top border

### 5. PanelGrid (Responsive Grid)
```tsx
import { PanelGrid, Panel } from '../components/common/Panel';

<PanelGrid cols={2} minHeight="600px">
  <Panel>Panel 1</Panel>
  <Panel>Panel 2</Panel>
  <Panel>Panel 3</Panel>
  <Panel>Panel 4</Panel>
</PanelGrid>
```
- Responsive grid layout
- `cols`: 1, 2, 3, or 4 columns
- `minHeight`: Minimum height for each panel (default: 600px)

## Complete Example

```tsx
import { Panel, PanelHeader, PanelContent, PanelFooter, PanelGrid } from '../components/common/Panel';

export function MyPage() {
  return (
    <div className="space-y-6">
      {/* Page Title */}
      <h1>My Page</h1>

      {/* 2x2 Grid of Panels */}
      <PanelGrid cols={2} minHeight="650px">
        {/* Panel 1 */}
        <Panel>
          <PanelHeader>
            <h3 className="text-lg font-semibold">Panel 1</h3>
          </PanelHeader>
          <PanelContent>
            {/* This content will scroll if it overflows */}
            <div>Long content...</div>
          </PanelContent>
          <PanelFooter>
            <button>Action</button>
          </PanelFooter>
        </Panel>

        {/* Panel 2 */}
        <Panel>
          <PanelHeader>
            <h3 className="text-lg font-semibold">Panel 2</h3>
          </PanelHeader>
          <PanelContent>
            {/* Content */}
          </PanelContent>
        </Panel>

        {/* Panel 3 */}
        <Panel>
          <PanelHeader>
            <h3 className="text-lg font-semibold">Panel 3</h3>
          </PanelHeader>
          <PanelContent>
            {/* Content */}
          </PanelContent>
        </Panel>

        {/* Panel 4 */}
        <Panel>
          <PanelHeader>
            <h3 className="text-lg font-semibold">Panel 4</h3>
          </PanelHeader>
          <PanelContent>
            {/* Content */}
          </PanelContent>
        </Panel>
      </PanelGrid>
    </div>
  );
}
```

## Benefits

✅ **Automatic Overflow**: Content scrolls automatically when it exceeds panel height
✅ **Consistent Spacing**: All panels have the same padding and margins
✅ **Fixed Headers/Footers**: Headers and footers stay visible while content scrolls
✅ **Responsive**: Grid adapts to screen size
✅ **Flexible**: Easy to add/remove panels without layout issues
✅ **Type-Safe**: Full TypeScript support

## CSS Utility Classes (Alternative)

If you don't want to use the components, you can use these utility classes:

```tsx
{/* Panel with automatic overflow */}
<div className="panel-container">
  <div className="panel-header">
    <h3>Title</h3>
  </div>
  <div className="panel-content">
    {/* Scrollable content */}
  </div>
  <div className="panel-footer">
    <button>Action</button>
  </div>
</div>
```

## Migration Guide

### Before (Manual Overflow Handling)
```tsx
<div className="bg-gray-900 rounded-lg p-4 h-[600px] overflow-auto">
  <h3>Title</h3>
  <div>Content</div>
</div>
```

### After (Using Panel Components)
```tsx
<Panel>
  <PanelHeader>
    <h3>Title</h3>
  </PanelHeader>
  <PanelContent>
    <div>Content</div>
  </PanelContent>
</Panel>
```

## Common Patterns

### Dashboard with Multiple Panels
```tsx
<PanelGrid cols={2}>
  <Panel>...</Panel>
  <Panel>...</Panel>
  <Panel>...</Panel>
  <Panel>...</Panel>
</PanelGrid>
```

### Full-Width Panel
```tsx
<Panel className="w-full">
  <PanelContent>...</PanelContent>
</Panel>
```

### Panel with Actions
```tsx
<Panel>
  <PanelHeader>
    <div className="flex justify-between items-center">
      <h3>Title</h3>
      <button>Action</button>
    </div>
  </PanelHeader>
  <PanelContent>...</PanelContent>
</Panel>
```

### Nested Sections
```tsx
<PanelContent>
  <PanelSection>
    <h4>Section 1</h4>
    <p>Content</p>
  </PanelSection>
  <PanelSection>
    <h4>Section 2</h4>
    <p>Content</p>
  </PanelSection>
</PanelContent>
```

## Tips

1. **Always wrap content in PanelContent** if you want it to scroll
2. **Use PanelHeader for titles/controls** that should stay visible
3. **Use PanelFooter for actions** that should always be accessible
4. **Set minHeight on PanelGrid** to ensure consistent panel sizes
5. **Use flex-shrink-0** on items that shouldn't shrink when space is limited

## Troubleshooting

**Problem**: Content overflows but doesn't scroll
- **Solution**: Make sure you're using `<PanelContent>` not just a `<div>` inside `<Panel>`

**Problem**: Header scrolls with content
- **Solution**: Use `<PanelHeader>` instead of putting it in `<PanelContent>`

**Problem**: Panels have different heights
- **Solution**: Set a consistent `minHeight` on `<PanelGrid>`

**Problem**: Footer overlaps content
- **Solution**: Ensure `<Panel>` has `h-full` and is inside a container with defined height
