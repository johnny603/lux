# Artist & Visual Designer Contribution Guide (`CONTRIBUTING_DESIGN.md`)

Welcome! We are excited to collaborate with visual designers, UI/UX artists, concept artists, and illustrators to build immersive escape rooms and puzzle interfaces in Lux.

Artists do **not** need deep coding knowledge to contribute. This guide outlines everything you need to create, test, and submit your designs.

---

## 📁 Asset Directory Structure

All visual assets reside under the `/assets/` directory:

```text
assets/
├── backgrounds/      # Room backgrounds, banners, and environmental art
├── icons/            # Items, objects, navigation buttons, and status icons
├── themes/           # CSS palette variable files per room (e.g. theme_<room_id>.css)
├── concepts/         # Moodboards, reference sketches, and wireframes
└── README.md         # Directory overview
```

---

## 🎨 Asset Guidelines & File Specifications

### 1. Icons and Interactive Objects (`/assets/icons/`)
- **Format**: `.svg` preferred (vector scalable).
- **Alternative**: `.png` (transparent background, 2x export, max 128x128 px).
- **Max File Size**: 50 KB.
- **Naming Convention**: `object_<item_name>_<variant>.svg` (e.g., `object_key_gold.svg`, `object_flask_chemical.svg`).

### 2. Room Backgrounds (`/assets/backgrounds/`)
- **Format**: `.webp`, `.png`, or `.svg`.
- **Recommended Aspect Ratio**: 16:9 (1920×1080 resolution).
- **Max File Size**: 200 KB (use image compression tools such as Squoosh, TinyPNG, or svgo).
- **Naming Convention**: `room_<room_id_or_slug>_bg.<ext>` (e.g., `room_abandoned_lab_bg.webp`).

### 3. Room Themes (`/assets/themes/`)
- **Format**: `.css` file containing CSS design tokens.
- **Naming Convention**: `theme_<room_id>.css` (e.g., `theme_room_1.css`).
- **Required Tokens**:
  ```css
  :root {
    --room-bg-color: #0b132b;
    --room-card-bg: rgba(28, 37, 65, 0.85);
    --room-accent: #6fffe9;
    --room-accent-secondary: #5bc0be;
    --room-text-color: #e0fbfc;
    --room-border-color: rgba(111, 255, 233, 0.3);
    --room-glow: 0 0 15px rgba(111, 255, 233, 0.4);
  }
  ```

---

## 🛠️ Instant Room Preview Tool (`design_preview.html`)

You can preview your room theme, background, and icons locally in any browser without running a server:

1. Open `templates/design_preview.html` directly in your web browser (or navigate to `/design-preview` if running the server).
2. Select a room theme from the dropdown, or customize colors dynamically.
3. Test how interactable items and text contrast appear across different display sizes.

---

## 🚀 How to Propose & Submit Designs

### Step 1: Open a Design Issue
- Open a GitHub Issue using the `[DESIGN]` tag.
- Share your concept, moodboard, sketches, or color story references.

### Step 2: Prepare Your Assets
- Check that your assets meet size limits (max 200KB for backgrounds, max 50KB for icons).
- Verify WCAG AA color contrast (at least 4.5:1 text-to-background contrast ratio).

### Step 3: Submit a Pull Request
- Place your assets in `/assets/backgrounds/`, `/assets/icons/`, or `/assets/themes/`.
- Mention the related Issue in your PR description.
- Maintainers and developers will test responsiveness, contrast, and integrate the theme!

---

## 🏆 Hacktoberfest & Open Source Recognition

Every approved design contribution is credited in [`contributors.json`](contributors.json) and displayed on the Lux Contributor Showcase.
