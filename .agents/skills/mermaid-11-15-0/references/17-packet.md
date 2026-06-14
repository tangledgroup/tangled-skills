# Packet Diagrams (v11.0.0+)

Visualize network packet structures and protocol field layouts.

## Syntax

```
packet
    title "TCP Packet"              %% Optional
    0-15: "Source Port"             %% Range syntax
    16-31: "Destination Port"
    32-63: "Sequence Number"
    106: "URG"                      %% Single bit
```

### Bit count syntax (v11.7.0+)

```
packet
    +16: "Source Port"             %% Auto-increment from previous end
    +16: "Destination Port"
    32-47: "Length"                %% Can mix range and count syntax
```

`+N` means N bits starting from the end of the previous field.
