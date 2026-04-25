# String Methods (29 methods)

String manipulation utilities including case conversion, padding, escaping, and templating.

## Case Conversion

### `_.camelCase(string)`

Converts string to camelCase.

```javascript
_.camelCase('Foo Bar');        // => 'fooBar'
_.camelCase('--foo-bar--');    // => 'fooBar'
_.camelCase('__FOO_BAR__');    // => 'fooBar'
```

### `_.kebabCase(string)`

Converts string to kebab-case.

```javascript
_.kebabCase('Foo Bar');        // => 'foo-bar'
_.kebabCase('fooBar');         // => 'foo-bar'
```

### `_.snakeCase(string)`

Converts string to snake_case.

```javascript
_.snakeCase('Foo Bar');        // => 'foo_bar'
_.snakeCase('fooBar');         // => 'foo_bar'
```

### `_.startCase(string)`

Converts string to start case (Title Case).

```javascript
_.startCase('--foo-bar--');    // => 'Foo Bar'
```

### `_.lowerCase(string)`

Converts string to lower case with spaces.

```javascript
_.lowerCase('FOO BAR');        // => 'foo bar'
```

### `_.upperCase(string)`

Converts string to UPPER_CASE with spaces.

```javascript
_.upperCase('foo bar');        // => 'FOO BAR'
```

### `_.capitalize(string)`

Capitalizes first character, lowercases rest.

```javascript
_.capitalize('fred');          // => 'Fred'
```

### `_.lowerFirst(string)`

Lowercases first character.

```javascript
_.lowerFirst('FRED');          // => 'fRED'
```

### `_.upperFirst(string)`

Uppercases first character.

```javascript
_.upperFirst('fred');          // => 'Fred'
```

### `_.toLower(string)`

Converts string to lowercase using Unicode normalization.

```javascript
_.toUpper('Foo Bar');          // => 'foo bar'
```

### `_.toUpper(string)`

Converts string to uppercase using Unicode normalization.

```javascript
_.toUpper('foo bar');          // => 'FOO BAR'
```

## Padding

### `_.pad(string, [length=0], [chars=' '])`

Pads string on both sides to reach length.

```javascript
_.pad('abc', 8);               // => '  abc   '
_.pad('abc', 8, '_-');         // => '_-_abc_-'
```

### `_.padStart(string, [length=0], [chars=' '])`

Pads string on the left to reach length.

```javascript
_.padStart('abc', 6);          // => '   abc'
_.padStart('abc', 6, '0');     // => '000abc'
```

### `_.padEnd(string, [length=0], [chars=' '])`

Pads string on the right to reach length.

```javascript
_.padEnd('abc', 6);            // => 'abc   '
_.padEnd('abc', 6, '0');       // => 'abc000'
```

## Trimming

### `_.trim(string, [chars=whitespace])`

Removes whitespace from both ends.

```javascript
_.trim('  abc  ');             // => 'abc'
_.trim('-abc-', '-');          // => 'abc'
```

### `_.trimStart(string, [chars=whitespace])`

Removes whitespace from the beginning.

```javascript
_.trimStart('  abc  ');        // => 'abc  '
```

### `_.trimEnd(string, [chars=whitespace])`

Removes whitespace from the end.

```javascript
_.trimEnd('  abc  ');          // => '  abc'
```

## Searching

### `_.startsWith(string, [target], [position=0])`

Checks if string starts with target.

```javascript
_.startsWith('abc', 'a');      // => true
_.startsWith('abc', 'b', 1);   // => true
```

### `_.endsWith(string, [target], [position=string.length])`

Checks if string ends with target.

```javascript
_.endsWith('abc', 'c');        // => true
_.endsWith('abc', 'b', 2);     // => true
```

## Splitting

### `_.split(string, separator, [limit])`

Splits string into array of substrings.

```javascript
_.split('a,b,c', ',');         // => ['a', 'b', 'c']
_.split('a,b,c', ',', 2);      // => ['a', 'b']
```

### `_.words(string, [pattern])`

Splits string into array of words.

```javascript
_.words('fred, barney, & pebbles'); // => ['fred', 'barney', 'pebbles']
_.words('fred, barney, & pebbles', /[^, ]+/g); // => ['fred', 'barney', '&', 'pebbles']
```

## Repeating

### `_.repeat(string, [n=1])`

Repeats string n times.

```javascript
_.repeat('*', 3);              // => '***'
```

## Replacement

### `_.replace(string, pattern, replacement)`

Replaces matches in string using RegExp or string pattern.

```javascript
_.replace('Hi Fred', 'Fred', 'Barney'); // => 'Hi Barney'
_.replace('[a-z]+', str => str.toUpperCase()); // Custom replacement
```

## Escaping

### `_.escape(string)`

Converts HTML entities (&, <, >, ", ',`) to their escaped versions.

```javascript
_.escape('fred, barney, & pebbles'); // => 'fred, barney, &amp; pebbles'
```

### `_.unescape(string)`

Converts escaped HTML entities back to characters.

```javascript
_.unescape('fred, barney, &amp; pebbles'); // => 'fred, barney, & pebbles'
```

### `_.escapeRegExp(string)`

Escapes RegExp special characters in string.

```javascript
_.escapeRegExp('[lodash](https://lodash.com/)'); // => '\[lodash\]\(https://lodash\.com/\)'
```

## Special Characters

### `_.deburr(string)`

Converts latin-1 supplementary characters to basic latin equivalents.

```javascript
_.deburr('déjà vu');           // => 'deja vu'
```

## Truncation

### `_.truncate(string, [options={ }])`

Truncates string if longer than length.

**Options:**
- `length`: Max length (default 30)
- `omission`: Trailing chars (default '...')
- `separator`: Where to break (default null)

```javascript
_.truncate('hi-diddly-ho there, neighborino'); // => 'hi-diddly-ho there, neigh...'

_.truncate('hi-diddly-ho there, neighborino', { length: 24 }); 
// => 'hi-diddly-ho there,...'

_.truncate('hi-diddly-ho there, neighborino', { length: 24, omission: '...' });
// => 'hi-diddly-ho there,...'

_.truncate('hi-diddly-ho there, neighborino', { separator: ' ' });
// => 'hi-diddly-ho there,...' (breaks at word boundary)
```

## Parsing

### `_.parseInt(string, [radix=10])`

Parses string as integer with specified radix.

```javascript
_.parseInt('08');              // => 8 (unlike native parseInt which gives 0)
_.parseInt('10px', 10);        // => 10
```

## Templating

### `_.template(string, [options={ }])`

Creates template function from string with interpolation.

**Default delimiters:**
- `<%= %>`: Escape and interpolate
- `<% %>`: Evaluate JavaScript
- `<%- %>`: Interpolate without escaping

```javascript
var tpl = _.template('Hello <%= name %>!');
tpl({ name: 'Fred' }); // => 'Hello Fred!'

// With escaping
var tpl = _.template('<%= value %>');
tpl({ value: '<script>' }); // => '&lt;script&gt;'

// Custom delimiters
_.templateSettings.interpolate = /\{\{(.+?)\}\}/g;
var tpl = _.template('Hello {{ name }}!');
tpl({ name: 'Fred' }); // => 'Hello Fred!'

// With evaluation
var list = '<% _.forEach(items, function(item) { %><li><%= item %></li><% }); %>';
var tpl = _.template(list);
tpl({ items: ['apple', 'banana'] }); 
// => '<li>apple</li><li>banana</li>'
```

**Template Settings:**
```javascript
_.templateSettings = {
  escape: /\<%-([\s\S]+?)%\>/g,     // Escaped interpolation
  evaluate: /\<%([\s\S]+?)%\>/g,    // Evaluation
  interpolate: /\<%=([\s\S]+?)%\>/g,// Interpolation
  imports: { _: _ },                // Available in template
  variable: 'data'                  // Variable name for data
};
```

## Common Patterns

### Case Conversion Pipeline

```javascript
// Convert various formats to camelCase
const normalize = str => _.camelCase(str);
normalize('foo-bar');      // 'fooBar'
normalize('Foo Bar');      // 'fooBar'
normalize('__FOO_BAR__');  // 'fooBar'
```

### Safe String Operations

```javascript
// Trim and lowercase
const clean = str => _.toLower(_.trim(str || ''));

// Pad numbers with zeros
const padNumber = n => _.padStart(String(n), 3, '0');
padNumber(5); // '005'
```

### HTML Escaping

```javascript
// Escape user input for HTML
const safeOutput = _.escape(userInput);

// Escape regex special chars
const pattern = new RegExp(_.escapeRegExp(searchTerm));
```

### Text Truncation

```javascript
// Truncate with word boundary
const summary = _.truncate(longText, { length: 100, separator: ' ' });

// Custom truncation
const short = _.truncate(text, { 
  length: 50, 
  omission: ' [read more]' 
});
```

### Template Rendering

```javascript
// Simple template
const greeting = _.template('Hello, <%= name %>!');
greeting({ name: 'Fred' }); // 'Hello, Fred!'

// With partials
const card = _.template(`
  <div class="card">
    <h2><%= title %></h2>
    <p><%- body %></p>
  </div>
`);
```
