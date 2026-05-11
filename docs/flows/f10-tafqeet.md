# F10 — Tafqeet Control (Amount-to-Words)

**Roles**: Designer (configure) · Operator (fill forms) · PDF engine (render)  
**Related**: [F04 Design Studio](f04-design-studio.md) · [F06 PDF Engine](f06-pdf-engine.md)

---

## Tafqeet element lifecycle

```mermaid
stateDiagram-v2
    [*] --> placed : Designer drags from palette
    placed --> configured : Source element + language set
    configured --> previewing : Source element has a numeric value
    previewing --> overflow : Text overflows bounding box
    previewing --> configured : Source element deleted
    configured --> rendered : POST /api/pdf/render with data
    overflow --> [*]
    rendered --> [*]
```

---

## Live preview flow

```mermaid
flowchart LR
    A([Designer sets source element]) --> B[Link tafqeet → source element key]
    B --> C{Source element has value?}
    C -- yes --> D[TafqeetConverter.convert numeric value]
    D --> E{language setting}
    E -- Arabic --> F["ألف وخمسمائة جنيه مصري وخمسة وعشرون قرشاً"]
    E -- English --> G["One Thousand Five Hundred Egyptian Pounds and Twenty-Five Piastres"]
    E -- Both --> H[AR line above EN line in bounding box]
    F --> I{text overflows element?}
    G --> I
    H --> I
    I -- yes --> J[Orange warning in properties panel]
    I -- no --> K[Canvas renders converted text]
    C -- no --> L[Placeholder shown]
```

---

## Flows

### 10.1 Designer adds a Tafqeet element

```
Designer drags "Tafqeet" (تفقيط) from element palette onto canvas
→ Element appears as read-only text box with lock icon and "تفقيط" label
→ In properties panel:
    - Source element: dropdown lists all number/currency elements on same page
    - Output language: Arabic / English / Both
    - Show currency name: toggle
    - Prefix / Suffix: optional text (e.g., "فقط" / "لا غير")
→ Preview updates in canvas as properties are set
```

### 10.2 Live preview in canvas

```
Linked source element has value (e.g., 1500.25)
→ Tafqeet element immediately shows:
    AR: "ألف وخمسمائة جنيه مصري وخمسة وعشرون قرشاً"
    EN: "One Thousand Five Hundred Egyptian Pounds and Twenty-Five Piastres"
    Both: Arabic line above English line within bounding box
→ If preview overflows element bounds → orange warning in properties panel
```

### 10.3 PDF rendering with Tafqeet

```
POST /api/pdf/render/{template_id} with data { "amount_field": 2500 }
→ Backend recomputes Tafqeet from data["amount_field"]
→ Outputs words text; renders at exact mm position in PDF
→ Font embedded (Noto Naskh Arabic for AR output)
```

---

## Edge cases

| Input | Output |
|-------|--------|
| 0 | صفر / Zero |
| Negative number | — (blank; logged to audit) |
| > 999,999,999,999 | — (blank; logged to audit) |
| Conversion exception | — (blank; logged to audit) |
| Source element deleted | Element shows placeholder; sourceElementKey cleared |
