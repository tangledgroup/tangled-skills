# Packet Diagram Reference

## Description

Packet diagrams illustrate the structure and contents of network packets. Fields are defined by bit ranges or bit counts, with labels for each field. Useful for network engineering and protocol documentation.

> **Note:** Uses `packet` keyword. Bit count syntax (`+N`) available since v11.7.0+.

## Basic Syntax

```mermaid
packet
    0-15: "Source Port"
    16-31: "Destination Port"
    32-63: "Sequence Number"
    64-95: "Acknowledgment Number"
```

## Bit Range Syntax

```
start-end: "Field Name"
```

- `start` — Starting bit position
- `end` — Ending bit position
- Single-bit fields: `100: "Flag"` (same start and end)

## Bit Count Syntax (v11.7.0+)

```
+N: "Field Name"
```

- `+N` — Number of bits from the end of the previous field
- Fields are placed sequentially, auto-calculating positions

### Mixed Syntax

Both styles can be combined:

```mermaid
packet
    +16: "Source Port"
    +16: "Destination Port"
    32-63: "Manual range still works"
    +8: "Next field auto-positions"
```

## Comments

Use `%%` for inline comments:

```mermaid
packet
    0-15: "Source Port"   %% TCP/UDP source port
    16-31: "Dest Port"    %% TCP/UDP destination port
```

## Examples

### TCP Packet

```mermaid
packet
    title "TCP Packet"
    0-15: "Source Port"
    16-31: "Destination Port"
    32-63: "Sequence Number"
    64-95: "Acknowledgment Number"
    96-99: "Data Offset"
    100-105: "Reserved"
    106: "URG"
    107: "ACK"
    108: "PSH"
    109: "RST"
    110: "SYN"
    111: "FIN"
    112-127: "Window"
    128-143: "Checksum"
    144-159: "Urgent Pointer"
    160-191: "Options and Padding"
```

### Custom Protocol

```mermaid
packet
    title "Custom Protocol Header"
    +8: "Version"
    +8: "Type"
    +16: "Length"
    +32: "Timestamp"
    +64: "Message ID"
    +16: "Checksum"
```

### Ethernet Frame

```mermaid
packet
    title "Ethernet II Frame"
    0-47: "Destination MAC"
    48-95: "Source MAC"
    96-111: "EtherType"
    112-143: "Payload (start)"
    144-159: "FCS"
```
