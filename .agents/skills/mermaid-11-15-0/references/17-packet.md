# Packet Diagrams (v11.0.0+)

Visualize network packet structures and protocol field layouts.

## Syntax

```
packet
    title "TCP Header"
    0-15: "Source Port"
    16-31: "Destination Port"
    32-63: "Sequence Number"
    64-95: "Acknowledgment Number"
    96-99: "Data Offset"
    100-111: "Flags"
```

### Range syntax

| Syntax | Meaning |
| --- | --- |
| `0-15` | Bits 0 through 15 (inclusive) |
| `106` | Single bit at position 106 |

Ranges indicate absolute bit positions. Each line defines one field.

### Bit count syntax (v11.7.0+)

```
packet
    +16: "Source Port"             %% Auto-increment from previous end
    +16: "Destination Port"
    32-47: "Length"                %% Can mix range and count syntax
```

`+N` means N bits starting from the end of the previous field. Mix range and count syntax freely.

### Sub-fields (v11+)

Fields can be subdivided with nested `+` counts:

```
packet
    title "Ethernet Header"
    0-47: "Destination MAC"
    48-63: "Source MAC"
    +16: "EtherType"
```

## Configuration

Packet diagrams accept config under the `packet` key, but theme variables are currently non-functional due to an upstream bug (values do not propagate into the rendering styles).

## Gotchas

- Theme variables (`byteFontSize`, `startByteColor`, `endByteColor`, `labelColor`) exist in the schema but are not applied at render time. Check upstream for fixes.
