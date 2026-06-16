# Railroad Diagrams (v11.15.0+)

Railroad diagrams visualize context-free grammars using EBNF notation. Start with `railroad-diagram`, optionally add a `title`, then define grammar rules as `rule_name = definition ;`.

## Syntax

```
railroad-diagram
  title "Number Grammar"

  sign = "+" | "-" ;
  number = sign? digit+ ;
  digit = "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" ;
```

### Rule structure

- `rule_name = definition ;` — each rule ends with a semicolon
- Terminals: `"text"` or `'text'` (literal strings)
- Non-terminals: bare identifiers referencing other rules

```
letter = "a" | "b" | "c" ;
identifier = letter ;
```

### EBNF operators

| Feature       | W3C Notation    | ISO 14977 Notation | Description        |
|---------------|-----------------|--------------------|--------------------|
| Sequence      | `A B`           | `A , B`            | Concatenation      |
| Choice        | `A \| B`        | `A \| B`           | Alternation        |
| Optional      | `A?`            | `[ A ]`            | Zero or one        |
| Repetition 0+ | `A*`            | `{ A }`            | Zero or more       |
| Repetition 1+ | `A+`            | —                  | One or more        |
| Grouping      | `( A B )`       | `( A B )`          | Group elements     |
| Comment       | `/* text */`    | `(* text *)`       | Comment            |
| Special       | —               | `? text ?`         | Special sequence   |
| Exception     | `A - B`         | `A - B`            | Exclusion          |

### Grouping and nesting

Parentheses group elements for repetition or alternation:

```
expression = term ( ( "+" | "-" ) term )* ;
term = factor ( ( "*" | "/" ) factor )* ;
factor = number | "(" expression ")" ;
number = digit+ ;
digit = "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" ;
```

### Visual elements

- **Terminals**: Rounded rectangles (theme-aware)
- **Non-terminals**: Regular rectangles
- **Start/End**: Small circles
- **Branches**: Curved paths for choices
- **Loops**: Backward paths for repetition

## Gotchas

- Hand-drawn mode (`look: handDrawn`) is not supported.
- Keep rules simple — break complex rules into smaller, reusable components.
- Stick to either W3C or ISO 14977 notation consistently throughout a diagram.
