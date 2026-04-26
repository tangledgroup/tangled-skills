# String Methods

String methods provide formatting, case conversion, escaping, padding, and templating utilities.

## Case Conversion

### `_.camelCase([string=''])`

Converts string to camel case.

```js
_.camelCase('Foo Bar');        // → 'fooBar'
_.camelCase('--foo-bar--');    // → 'fooBar'
_.camelCase('__FOO_BAR__');    // → 'fooBar'
```

### `_.kebabCase([string=''])` / `_.snakeCase([string=''])`

Converts to kebab-case or snake_case.

```js
_.kebabCase('Foo Bar');   // → 'foo-bar'
_.snakeCase('Foo Bar');   // → 'foo_bar'
```

### `_.lowerCase([string=''])` / `_.upperCase([string=''])`

Converts to lower case or upper case with spaces between words.

```js
_.lowerCase('--Foo-Bar--'); // → 'foo bar'
_.upperCase('--Foo-Bar--'); // → 'FOO BAR'
```

### `_.startCase([string=''])`

Converts to start case (each word capitalized).

```js
_.startCase('--foo-bar--');  // → 'Foo Bar'
_.startCase('__foo_bar__');  // → 'Foo Bar'
```

### `_.capitalize([string=''])`

Capitalizes the first character.

```js
_.capitalize('fred'); // → 'Fred'
```

### `_.lowerFirst([string=''])` / `_.upperFirst([string=''])`

Converts the first character to lower/upper case.

```js
_.lowerFirst('Fred');  // → 'fred'
_.upperFirst('fred');  // → 'Fred'
```

## Trimming and Padding

### `_.trim([string=''], [chars=whitespace])` / `_.trimStart()` / `_.trimEnd()`

Removes specified characters from the beginning/end of string. Default chars is whitespace.

```js
_.trim('  abc  ');           // → 'abc'
_.trim('-_-abc-_-', '_-');   // → 'abc'
_.trimStart('_-abc-_', '_-'); // → 'abc-_'
_.trimEnd('_-abc-_', '_-');   // → '_-abc'
```

### `_.pad([string=''], [length=0], [chars=' '])` / `_.padStart()` / `_.padEnd()`

Pads string on both sides (or one side) to reach target length. Characters are truncated if needed.

```js
_.pad('abc', 8);        // → '  abc   '
_.pad('abc', 8, '_-');  // → '_-abc_-_'
_.padStart('abc', 6, '-'); // → '---abc'
_.padEnd('abc', 6, '-');   // → 'abc---'
```

## Searching and Matching

### `_.startsWith([string=''], [target], [position=0])` / `_.endsWith([string=''], [target], [position=string.length])`

Checks if string starts/ends with target. Position parameter controls where to check.

```js
_.startsWith('abc', 'b');     // → false
_.startsWith('abc', 'b', 1);  // → true
_.endsWith('abc', 'c');        // → true
_.endsWith('abc', 'b', 2);     // → false
```

### `_.includes(collection, value, [fromIndex=0])`

Also works on strings — checks if string contains target.

```js
_.includes('hello', 'ell'); // → true
_.includes('hello', 'ell', 2); // → false
```

### `_.replace([string=''], pattern, replacement)`

Replaces occurrences matching pattern with replacement. Pattern can be a RegExp or string.

```js
_.replace('hello fred', 'fred', 'pebbles');
// → 'hello pebbles'

_.replace(['abc', 'def'], /bc|ef/g, '-');
// → ['a-', 'd-']
```

### `_.words([string=''], [pattern])`

Splits string into an array of words. Default pattern matches sequences of alphabetic characters.

```js
_.words('fred, barney, & pebbles');
// → ['fred', 'barney', 'pebbles']

_.words('fred, barney, & pebbles', /[^, ]+/g);
// → ['fred', 'barney', '&', 'pebbles']
```

### `_.split([string=''], separator, [limit])`

Splits string by separator into an array.

```js
_.split('a-b-c', '-'); // → ['a', 'b', 'c']
```

## Escaping

### `_.escape([string=''])` / `_.unescape([string=''])`

Converts special characters to HTML entities and back.

```js
_.escape('fred, barney, & pebbles');
// → 'fred, barney, &amp; pebbles'

_.unescape('&lt;b&gt;Hello&lt;/b&gt;');
// → '<b>Hello</b>'
```

### `_.escapeRegExp([string=''])`

Escapes RegExp special characters.

```js
_.escapeRegExp('<lodash>');
// → '\<lodash\>'
```

## Truncation

### `_.truncate([string=''], [options={}])`

Truncates string if it exceeds length. Options:
- `length` — maximum string length (default: 30)
- `omission` — string to indicate text was omitted (default: '...')
- `separator` — separator pattern to truncate at

```js
_.truncate('hi-diddly-ho there, neighborino');
// → 'hi-diddly-ho there, neighbo...'

_.truncate('hi-diddly-ho there, neighborino', {
  'length': 24,
  'separator': ' '
});
// → 'hi-diddly-ho there,...'

_.truncate('hi-diddly-ho there, neighborino', {
  'length': 24,
  'omission': ' [...]'
});
// → 'hi-diddly-ho there, [ ...]'
```

## Templating

### `_.template([string=''], [options={}])`

Creates a compiled callback function that returns the interpolated string. Supports three interpolation modes:

- **escape** `<%= %>` — escapes HTML entities
- **evaluate** `<% %>` — executes JavaScript
- **interpolate** `<%= %>` or `{{ }}` — inserts values

```js
var compiled = _.template('hello <%= user %>!');
compiled({ 'user': 'fred' });
// → 'hello fred!'

// Using custom interpolation
var template = _.template('<% _.forEach(users, function(user) { %><li><%= user %></li><% }); %>');
template({ 'users': ['fred', 'barney'] });
// → '<li>fred</li><li>barney</li>'

// Custom delimiters
_.templateSettings.interpolate = /{{([\s\S]+?)}}/g;
var compiled = _.template('Hello {{ name }}!');
compiled({ 'name': 'Fred' });
// → 'Hello Fred!'
```

Template settings are configurable via `_.templateSettings`:

- `escape` — RegExp for escape delimiters (default: `/<%-([\s\S]+?)%>/g`)
- `evaluate` — RegExp for evaluate delimiters (default: `/<%([\s\S]+?)%>/g`)
- `interpolate` — RegExp for interpolate delimiters (default: `/<%=([\s\S]+?)%>/g`)
- `variable` — data object name (default: `''`)
- `imports` — object of functions available in template scope (default: `{ '_': lodash }`)

## Other String Methods

### `_.deburr([string=''])`

Removes combining diacritical marks, replacing them with basic Latin letters.

```js
_.deburr('déjà vu'); // → 'deja vu'
```

### `_.parseInt(string, [radix=10])`

Parses string to an integer of the given radix. Returns NaN if parsing fails. Unlike native parseInt, it doesn't silently parse octal from strings starting with '0'.

```js
_.parseInt('08'); // → 8
parseInt('08');   // → 0 (in some environments)
```

### `_.repeat([string=''], [n=1])`

Repeats string n times.

```js
_.repeat('*', 3); // → '***'
```
