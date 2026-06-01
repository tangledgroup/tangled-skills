# Packet Diagram

## Contents
- Bit Range Syntax
- Bit Count Syntax (v11.7.0+)
- Configuration
- Theme Variables

## Overview

Packet diagrams visualize network packet structures as bit-level field layouts. Available since v11.0.0.

```mermaid
packet
    0-15: "Source Port"
    16-31: "Dest Port"
    32-63: "Sequence Num"
    64-95: "Ack Number"
```

## Bit Range Syntax

`start-end: "Block name"` for multi-bit blocks, `bit: "name"` for single bits.

```mermaid
packet
    0-15: "Source Port"
    16-31: "Dest Port"
    32-63: "Sequence"
    106: "URG flag"
```

## Bit Count Syntax (v11.7.0+)

Use `+N` for bit count from end of previous field:

```mermaid
packet
    +16: "Source Port"
    +16: "Dest Port"
    +32: "Sequence"
    +8: "Flags"
```

Mix and match both syntaxes in the same diagram.

## Configuration

```mermaid
---
config:
  packet:
    titleFontSize: 20
    showBitScale: true
    bitFontSize: 12
---
packet
    +16: "Field"
```

## Theme Variables

```mermaid
---
config:
  themeVariables:
    packet:
      packetBackground: '#f5f5f5'
      packetStrokeColor: '#333'
      packetTitleColor: '#000'
      bitLabelColor: '#666'
---
packet
    +8: "Byte"
```
