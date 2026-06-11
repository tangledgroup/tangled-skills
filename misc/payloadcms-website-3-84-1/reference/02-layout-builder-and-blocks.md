# Layout Builder and Blocks

## Overview

The layout builder enables composable page design through a blocks field. Each block type defines its own fields and has a corresponding React component that renders it on the frontend. Pages use the layout builder for their main content area, while Posts use Lexical rich text with inline blocks.

## Block Types

### Hero (Group Field, Not a Block)

The hero is defined as a group field rather than a block. It controls the top section of every page:

```typescript
export const hero: Field = {
  name: 'hero',
  type: 'group',
  fields: [
    {
      name: 'type',
      type: 'select',
      defaultValue: 'lowImpact',
      options: [
        { label: 'None', value: 'none' },
        { label: 'High Impact', value: 'highImpact' },
        { label: 'Medium Impact', value: 'mediumImpact' },
        { label: 'Low Impact', value: 'lowImpact' },
      ],
      required: true,
    },
    {
      name: 'richText',
      type: 'richText',
      editor: lexicalEditor({
        features: ({ rootFeatures }) => [
          ...rootFeatures,
          HeadingFeature({ enabledHeadingSizes: ['h1', 'h2', 'h3', 'h4'] }),
          FixedToolbarFeature(),
          InlineToolbarFeature(),
        ],
      }),
    },
    linkGroup({ overrides: { maxRows: 2 } }),
    {
      name: 'media',
      type: 'upload',
      relationTo: 'media',
      required: true,
      admin: { condition: (_, { type }) => ['highImpact', 'mediumImpact'].includes(type) },
    },
  ],
}
```

Hero types determine visual prominence:
- **none** — No hero section rendered
- **lowImpact** — Text-only hero, no media
- **mediumImpact** — Side-by-side text and media
- **highImpact** — Full-width media background with overlaid text

### Content Block

Standard content block for text and column-based layouts. Used within the Pages layout builder.

### MediaBlock

Renders a single media item from the Media collection with optional caption. Supports the focal point cropping feature configured on the Media collection.

### CallToAction Block

Promotional section with heading, rich text body, and links. Used for conversion-focused page sections.

### Archive Block

The Archive block lists posts dynamically. It supports two modes:

```typescript
export const Archive: Block = {
  slug: 'archive',
  interfaceName: 'ArchiveBlock',
  fields: [
    { name: 'introContent', type: 'richText', label: 'Intro Content' },
    {
      name: 'populateBy',
      type: 'select',
      defaultValue: 'collection',
      options: [
        { label: 'Collection', value: 'collection' },
        { label: 'Individual Selection', value: 'selection' },
      ],
    },
    {
      name: 'relationTo',
      type: 'select',
      defaultValue: 'posts',
      options: [{ label: 'Posts', value: 'posts' }],
      admin: { condition: (_, siblingData) => siblingData.populateBy === 'collection' },
    },
    {
      name: 'categories',
      type: 'relationship',
      hasMany: true,
      relationTo: 'categories',
      admin: { condition: (_, siblingData) => siblingData.populateBy === 'collection' },
    },
    {
      name: 'limit',
      type: 'number',
      defaultValue: 10,
      admin: {
        condition: (_, siblingData) => siblingData.populateBy === 'collection',
        step: 1,
      },
    },
    {
      name: 'selectedDocs',
      type: 'relationship',
      hasMany: true,
      relationTo: ['posts'],
      admin: { condition: (_, siblingData) => siblingData.populateBy === 'selection' },
    },
  ],
}
```

- **Collection mode** — Automatically queries posts, optionally filtered by categories, with a configurable limit
- **Individual Selection mode** — Manually selects specific posts to display

### Form Block

Embeds forms created through the form builder plugin directly within page layouts.

## Inline Blocks (Posts Only)

Posts use Lexical rich text with inline blocks rather than the page-level layout builder:

- **Banner** — Highlighted callout banner within article content
- **Code** — Code block with syntax highlighting (uses prism-react-renderer)
- **MediaBlock** — Inline media within the article flow

```typescript
editor: lexicalEditor({
  features: ({ rootFeatures }) => [
    ...rootFeatures,
    HeadingFeature({ enabledHeadingSizes: ['h1', 'h2', 'h3', 'h4'] }),
    BlocksFeature({ blocks: [Banner, Code, MediaBlock] }),
    FixedToolbarFeature(),
    InlineToolbarFeature(),
    HorizontalRuleFeature(),
  ],
})
```

## RenderBlocks Component

The frontend uses a dispatcher pattern to render blocks:

```typescript
// src/blocks/RenderBlocks.tsx
import { CallToAction } from '@/blocks/CallToAction/Component'
import { Content } from '@/blocks/Content/Component'
import { MediaBlock } from '@/blocks/MediaBlock/Component'
import { Archive } from '@/blocks/ArchiveBlock/Component'
import { FormBlock } from '@/blocks/Form/Component'

export const RenderBlocks = ({ blocks }: { blocks: any[] }) => {
  return (
    <>
      {blocks?.map((block, index) => {
        switch (block.blockType) {
          case 'callToAction':
            return <CallToAction key={index} {...block} />
          case 'content':
            return <Content key={index} {...block} />
          case 'mediaBlock':
            return <MediaBlock key={index} {...block} />
          case 'archive':
            return <Archive key={index} {...block} />
          case 'form-block':
            return <FormBlock key={index} {...block} />
          default:
            return null
        }
      })}
    </>
  )
}
```

Each block type has a corresponding React component in its directory under `src/blocks/<BlockName>/Component.tsx`. The `blockType` field (auto-generated from the block slug) determines which component renders.

## Hero Rendering

Heroes use a similar dispatcher pattern via `RenderHero`:

```typescript
// Conceptual pattern from src/heros/
switch (hero.type) {
  case 'highImpact':
    return <HighImpactHero {...hero} />
  case 'mediumImpact':
    return <MediumImpactHero {...hero} />
  case 'lowImpact':
    return <LowImpactHero {...hero} />
  default:
    return null
}
```

## Link Field Definition

The reusable `link` field supports both internal document references and external URLs:

```typescript
export const link: LinkType = ({ appearances, disableLabel, overrides } = {}) => {
  // Returns a GroupField with:
  // - type (radio): 'reference' (internal) or 'custom' (external URL)
  // - newTab (checkbox): Open in new tab
  // - reference (relationship): Link to pages or posts
  // - url (text): Custom URL
  // - label (text): Display text for the link
  // - appearance (select): 'default' or 'outline' styling
}
```

The `linkGroup` variant wraps multiple link fields in an array for use in hero sections and other multi-link contexts.

## Adding New Blocks

To add a new block type:

1. Create the block config in `src/blocks/<Name>/config.ts`
2. Create the React component in `src/blocks/<Name>/Component.tsx`
3. Add the block to the blocks array in the Pages collection layout field
4. Add a case to `RenderBlocks.tsx` dispatcher
5. Run `pnpm generate:types` to update TypeScript types
