# BittaraPhoto UI Design Guidelines

This document serves as the single source of truth for the BittaraPhoto application's user interface design. All future UI modifications must adhere to these guidelines to ensure consistency and a premium user experience.

## 1. Design Philosophy
- **Modern & Clean**: Use ample whitespace, rounded corners, and subtle gradients.
- **Visual Feedback**: Provide clear visual cues for interactions (hover, focus, active states).
- **Consistency**: Reuse defined colors, fonts, and widget styles from `ui/styles.py`.

## 2. Color Palette
All colors are defined in `ui/styles.py` under the `Colors` class.

| Role | Variable | Hex Code | Usage |
| :--- | :--- | :--- | :--- |
| **Primary** | `Colors.PRIMARY` | `#2196F3` | Main actions, focus borders, active tabs |
| **Primary Hover** | `Colors.PRIMARY_HOVER` | `#1976D2` | Hover state for primary buttons |
| **Secondary** | `Colors.SECONDARY` | `#78909C` | Secondary text, subtle borders |
| **Accent** | `Colors.ACCENT` | `#FFC107` | Warnings, highlights |
| **Destructive** | `Colors.DESTRUCTIVE` | `#EF5350` | Delete, remove, cancel actions |
| **Success** | `Colors.SUCCESS` | `#4CAF50` | Success states, completion messages |
| **Background** | `Colors.BACKGROUND` | `#F5F5F5` | Main window background (Off-White) |
| **Surface** | `Colors.SURFACE` | `#FFFFFF` | Cards, input fields, dialogs |
| **Text Primary** | `Colors.TEXT_PRIMARY` | `#333333` | Main content text |
| **Text Secondary** | `Colors.TEXT_SECONDARY` | `#757575` | Subtitles, hints, disabled text |
| **Border** | `Colors.BORDER` | `#E0E0E0` | Dividers, widget borders |

## 3. Typography
Font settings are centralized in `ui/styles.py` under the `Fonts` class.

- **Font Family**: `"Malgun Gothic"` (Windows default for clean Korean support)
- **Sizes**:
    - **Title**: `20px Bold` (Main headers)
    - **Heading**: `14px Bold` (Section headers)
    - **Body**: `12px` (Standard text, inputs, buttons)
    - **Subtitle**: `11px` (Helper text)

## 4. Component Styles

### 4.1 Buttons
Buttons use a flat design with rounded corners (`4px`).
- **Primary**: Blue background, white text. No border.
- **Secondary**: White background, dark text, gray border.
- **Destructive**: Red background, white text.
- **Icon**: Transparent background, hover effect only.

### 4.2 Inputs (Critical)
Inputs (`QLineEdit`, `QSpinBox`, `QComboBox`) must maintain consistent sizing and appearance.

- **Normal**: White background, `1px solid #E0E0E0` border, `4px` radius, `4px 8px` padding.
- **Focus**: `2px solid #2196F3` border.
- **Disabled/ReadOnly**:
    - **Background**: `#F5F5F5`
    - **Text**: `#757575` (Text Secondary)
    - **Border**: `1px solid #E0E0E0`
    - **CRITICAL**: You **MUST** re-declare `padding`, `border-radius`, `font-family`, and `font-size` in the `:disabled` or `[readOnly="true"]` pseudo-states. Failure to do so will cause the widget to collapse or look broken.

### 4.3 Drop Zones
Drop zones (`ui/drop_zone.py`) use dynamic styles based on state.
- **Default**: Dashed border (`#E0E0E0`), subtle gradient background.
- **Drag Enter**: Solid Blue border (`#2196F3`), blue gradient background.
- **Filled (Success)**: Solid Green border (`#4CAF50`), green gradient background.
- **Size**: Minimum `150x120`, expanding policy.

### 4.4 Tabs (Settings Dialog)
Tabs use a modern, flat style.
- **Pane**: White background, gray border.
- **Tab Bar**:
    - **Normal**: Light gray (`#E0E0E0`) background, gray text.
    - **Selected**: White background, Blue text (`#2196F3`), bottom border blends with pane.
    - **Hover**: Very light gray (`#F5F5F5`).

### 4.5 Dialogs/Popups
**CRITICAL**: Do NOT use the native `QMessageBox` for confirmation or alerts, as it breaks UI consistency.
Instead, use the custom `MessageBox` class (to be implemented) which inherits from `QDialog` and uses the application's style.

- **Window**: White background, rounded corners.
- **Title Bar**: Minimalist or hidden (custom implementation).
- **Content**: `14px` text, `Colors.TEXT_PRIMARY`.
- **Buttons**: Use `Styles.BTN_PRIMARY` for positive actions (Yes/OK) and `Styles.BTN_SECONDARY` for negative actions (No/Cancel).

### 4.6 Status Messages
**CRITICAL**: Use the `StatusCard` component for all inline status feedback (Info, Success, Error).
Do NOT use ad-hoc `QLabel`s with custom colors.

- **Component**: `ui/status_card.py` -> `StatusCard` class.
- **Usage**:
    - `card.show_info("message")`: Blue background, Info icon.
    - `card.show_success("message")`: Green background, Check icon.
    - `card.show_error("message")`: Red background, Warning icon.
- **Placement**: Below input fields or action areas.

## 5. Implementation Patterns

### 5.1 Centralized Styles
**ALWAYS** use `ui/styles.py`. Do not hardcode hex values in widget files unless implementing dynamic logic (like DropZone gradients).
- **Usage**: `widget.setStyleSheet(Styles.BTN_PRIMARY)`

### 5.2 Input "Disabling" Logic
Do **NOT** use `setEnabled(False)` for inputs that need to remain readable and maintain their exact shape (like the folder number input after confirmation).
- **Why?**: The native `disabled` state often overrides styles unpredictably across platforms.
- **Solution**: Use `setReadOnly(True)`.
- **Style**: Ensure `Styles.INPUT` includes a `QLineEdit[readOnly="true"]` block that mirrors the normal style but with a gray background.

### 5.3 F-String Escaping in Stylesheets
When defining stylesheets in Python f-strings (like in `ui/styles.py`), you **MUST** double the braces for CSS blocks.
- **Wrong**: `QLineEdit { color: {Colors.TEXT}; }` -> Raises `NameError` or `ValueError`
- **Correct**: `QLineEdit {{ color: {Colors.TEXT}; }}` -> Renders as `QLineEdit { color: #333333; }`

### 5.4 Layouts
- **Margins**: Standard margins are `10px` or `20px` for main containers.
- **Spacing**: Standard spacing between widgets is `10px`.
- **Sizing**: Prefer `QSizePolicy.Expanding` over fixed sizes to ensure responsiveness. Use `setMinimumSize` to prevent collapse.
