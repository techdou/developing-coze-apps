# Image Generation for Single-HTML Pages

The default image source is the image-generation integration available in the current Coze Coding environment. The user may explicitly direct the Agent to another Coze image skill or prompt specification; that changes the image-generation subtask, not the packaging contract.

## Workflow

1. Select the HTML template before generating images.
2. Produce an image-slot plan:

| Slot | Purpose | Aspect ratio | Minimum size | Text inside image? | Alt text |
|---|---|---:|---:|---|---|

3. Generate images through a server-side Coze integration or designated image skill.
4. Persist generated output immediately. Do not rely on temporary signed URLs as final assets.
5. For offline/self-contained HTML, download the final images and convert them to data URIs during rendering.
6. For network-dependent output, use stable public URLs only and disclose the dependency.
7. Add meaningful `alt` text and avoid placing essential instructional text only inside images.

## Prompt ownership

This skill defines layout slots, aspect ratios, consistency requirements, filenames, and alt text. It does not override a user-selected image-prompt skill. When another image skill is used:

- pass the slot specification to that skill;
- require consistent character/object/style across all images when relevant;
- return final local files or stable URLs to the single-HTML builder;
- keep exact model IDs runtime-verified rather than hard-coded.

## Suggested image slots by template

| Template | Typical slots |
|---|---|
| `editorial-image-text` | 1 hero + 2-6 section images |
| `visual-story` | 3-8 wide narrative images |
| `course-article` | 1 cover + diagrams/examples as needed |
| `gallery-showcase` | 4-12 consistent cards |
| `split-intro-iframe` | Optional cover/thumbnail in intro panel |
| `cover-launch-iframe` | 1 immersive cover image |
