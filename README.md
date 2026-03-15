# 🍄 MySpirit — Spirit Island Template CLI

A Python CLI tool for designing custom **Spirit Island** board game components. Define spirits, power cards, adversaries, and more as simple YAML files — then compile them to print-ready HTML, PNG, and PDF.

Built on top of the [Spirit Island Template](https://github.com/resonant-gamedesign/spirit-island-template) project.

---

## ✨ Features

- **YAML-based design** — define components in readable YAML instead of raw HTML
- **Compile to HTML + PNG** — generates standalone HTML (viewable in any browser) and high-quality PNG screenshots
- **Print-ready PDF** — arrange all components onto A4 pages with correct physical dimensions
- **AI artwork generation** — generate card and spirit art via Google Gemini (Nano Banana 2)
- **Custom icons** — use your own token icons with `{icon}` syntax in rules text
- **Spirit bootstrapping** — scaffold a new spirit folder with template files in one command

## 📦 Installation

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager

### Setup

```bash
# Clone the repository
git clone <repo-url>
cd spirit-island-template

# Install in development mode
uv pip install -e .

# Install Playwright browser (needed for PNG rendering)
.venv/bin/playwright install chromium
```

### API Key (optional, for artwork generation)

Create a `.env` file in the project root:

```
GOOGLE_API_KEY=your-google-api-key-here
```

Get a key from [Google AI Studio](https://aistudio.google.com/apikey).

---

## 🚀 Quickstart

### 1. Bootstrap a new spirit

```bash
myspirit bootstrap-spirit "Ember of Dawn" --cards 4 --output-dir spirits/
```

This creates `spirits/ember-of-dawn/` with template YAML files:

```
spirits/ember-of-dawn/
├── board_front.yaml    # Spirit board (growth, presence, innate powers)
├── board_lore.yaml     # Lore, setup, play style, complexity
├── card_back.yaml      # Card back design
├── card-1.yaml         # Power card
├── card-2.yaml         # Power card
├── card-3.yaml         # Power card
└── card-4.yaml         # Power card
```

### 2. Edit the YAML files

Power cards look like this:

```yaml
type: card
name: "Threads Beneath the Roots"
speed: fast
cost: 0
image: artwork.png
elements:
  - plant
  - earth
range: "1"
target: "{no-sand}"
target_title: "TARGET LAND"
rules: |
  Place 1 {spore} on target land.
  Push 1 {explorer} from that land.
```

Use `{icon}` syntax for game icons: `{fire}`, `{dahan}`, `{sacred-site}`, `{presence}`, etc.

### 3. Generate artwork (optional)

Add an `art_prompt` field to any YAML file, then:

```bash
myspirit generate-art spirits/ember-of-dawn/card-1.yaml
```

Pass custom reference images for style matching:

```bash
myspirit generate-art card-1.yaml --reference inspo.png --style-examples 2
```

### 4. Compile

Compile a single file:

```bash
myspirit compile spirits/ember-of-dawn/board_front.yaml
```

Or compile everything at once:

```bash
myspirit compile-all spirits/ember-of-dawn/
```

Output goes to `output/ember-of-dawn/` with `.html` and `.png` for each component.

### 5. Print layout

Generate a print-ready A4 PDF from the compiled output:

```bash
myspirit print-layout output/ember-of-dawn/
```

Creates `print-layout.pdf` with:
- Spirit board front and back at exact 228×152mm
- Power cards at 63.5×88mm in a grid
- Card backs mirrored for double-sided printing

---

## 🛠️ CLI Reference

| Command | Description |
|---------|-------------|
| `myspirit bootstrap-spirit <name>` | Scaffold a new spirit folder with template YAMLs |
| `myspirit compile <file.yaml>` | Compile a single YAML to HTML + PNG |
| `myspirit compile-all <folder>` | Compile all YAMLs in a folder |
| `myspirit generate-art <file.yaml>` | Generate artwork from the `art_prompt` field |
| `myspirit print-layout <output-folder>` | Arrange compiled PNGs onto A4 pages as PDF |

### Common options

```bash
myspirit bootstrap-spirit <name> --cards 6 --output-dir spirits/
myspirit generate-art <file> --timeout 300 --style-examples 2 --reference ref.png
```

---

## 📄 YAML Component Types

| Type | `type:` field | Description |
|------|--------------|-------------|
| Spirit Board | `board_front` | Growth, presence tracks, innate powers, special rules |
| Lore Board | `board_lore` | Backstory, setup, play style, complexity |
| Power Card | `card` | Speed, cost, elements, range, target, rules |
| Card Back | `card_back` | Custom card back with artwork |
| Adversary | `adversary` | Loss condition, escalation, 6 difficulty levels |
| Aspect | `aspect` | Alternative rules/innate powers for existing spirits |

### Custom Icons

Define custom icons per component:

```yaml
custom_icons:
  spore: spore_token.png
```

Then use `{spore}` anywhere in rules text, targets, or special rules. The `{no-spore}` syntax renders the icon with a crossed-out overlay.

---

## 🏗️ Project Structure

```
spirit-island-template/
├── _global/              # Shared CSS, JS, fonts, icons (original template)
├── _examples/            # HTML examples (original template)
├── spirit_cli/           # Python CLI package
│   ├── cli/              # Command mixins and display
│   ├── templates/        # Jinja2 HTML templates
│   ├── models.py         # Pydantic YAML validation
│   ├── compiler.py       # YAML → HTML → PNG pipeline
│   ├── art.py            # Gemini API integration
│   ├── print_layout.py   # PDF generation
│   └── bootstrap.py      # Spirit scaffolding
├── spirits/              # Your custom spirits (YAML + art)
├── output/               # Compiled output (HTML, PNG, PDF)
├── pyproject.toml        # Python project config
└── .env                  # API keys (gitignored)
```

---

## 🙏 Credits

- **Original Template**: [Spirit Island Template](https://github.com/resonant-gamedesign/spirit-island-template) by resonant-gamedesign — the HTML/CSS/JS rendering engine that powers all component generation
- **Spirit Island**: Created by R. Eric Reuss, published by Greater Than Games
- **Icons**: From the [Spirit Island Wiki](https://spiritislandwiki.com/) under [Creative Commons Attribution-NonCommercial-ShareAlike](https://creativecommons.org/licenses/by-nc-sa/4.0/)
- **Fonts**: JosefinSans, Lato, Mouse Memoirs, Noto Sans (bundled, Open Font License); DK Snemand and Gobold (optional, download separately)
- **AI Artwork**: Generated via Google Gemini (Nano Banana 2)

---

## 📜 License

CLI code is available under the MIT License. Fonts and game images have their own licenses — see the original template for details.
