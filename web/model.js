// Scientific rules live here, independently of the browser and presentation.
export function validateConfig(c) {
  const nonnegative = value => typeof value === 'number' && Number.isFinite(value) && value >= 0;
  if (c.schema !== 1 || !Array.isArray(c.columns) || new Set(c.columns).size !== c.columns.length) throw Error('Invalid result schema');
  const required = ['subjectName','subjectCode','gender','age','handedness','video','section','arousal','pleasure','trial','choice','gain','loss','RT','pumps','explosion'];
  if (required.some(key => !c.columns.includes(key)) || c.columns.length !== required.length) throw Error('Invalid result columns');
  for (const task of ['igt','bart']) if (!Number.isInteger(c[task].trials) || c[task].trials < 0) throw Error('Invalid trial count');
  if (!Number.isInteger(c.bart.capacity) || c.bart.capacity < 1 || !nonnegative(c.bart.reward)) throw Error('Invalid balloon settings');
  if (c.bart.repeatPumps !== false) throw Error('Browser requires fresh presses; repeat pumping is unsupported');
  for (const value of [c.igt.initialBalance,c.igt.feedbackMs,c.fixationMs,c.exchangeRate]) if (!nonnegative(value)) throw Error('Invalid amount or duration');
  if (c.igt.decks.length !== 4 || c.igt.decks.some(d => !nonnegative(d.gain) || !d.losses.length || d.losses.some(n => !nonnegative(n)))) throw Error('Invalid decks');
  const actions = ['advance','pump','collect','skip','replay','pause','abort'];
  if (Object.keys(c.controls).length !== actions.length || actions.some(a => typeof c.controls[a] !== 'string' || !c.controls[a])) throw Error('Invalid controls');
  if (c.controls.pump === c.controls.collect || c.controls.abort === c.controls.pump || c.controls.abort === c.controls.collect) throw Error('Conflicting task controls');
  return c;
}
export function taskOrder(code) {
  // Match Python int(): non-integer strings use IGT first, including "1.0".
  const value = String(code ?? '').trim().replace(/\p{Decimal_Number}/gu, char => {
    const point = char.codePointAt(0); let zero = point;
    while (/\p{Decimal_Number}/u.test(String.fromCodePoint(zero - 1))) zero--;
    return String((point - zero) % 10);
  });
  return /^[+-]?\d(?:_?\d)*$/.test(value) && BigInt(value.replaceAll('_','')) % 2n !== 0n ? ['BART','IGT'] : ['IGT','BART'];
}
export function createDecks(config, random = Math.random) {
  const remaining = config.decks.map(() => []);
  return deck => {
    if (!Number.isInteger(deck) || deck < 1 || deck > 4) throw Error('Invalid deck');
    const index = deck - 1;
    if (!remaining[index].length) {
      remaining[index] = [...config.decks[index].losses];
      for (let i = remaining[index].length - 1; i > 0; i--) {
        const j = Math.floor(random() * (i + 1));
        [remaining[index][i], remaining[index][j]] = [remaining[index][j], remaining[index][i]];
      }
    }
    return {gain:config.decks[index].gain, loss:remaining[index].pop()};
  };
}
export function burst(pumps, capacity, random = Math.random) {
  if (!Number.isInteger(capacity) || capacity < 1 || !Number.isInteger(pumps) || pumps < 1 || pumps > capacity) throw Error('Invalid pump count');
  return random() >= 1 - 1 / (capacity + 1 - pumps);
}
export function balloonSize(pumps, capacity) {
  const growth = Math.min(1, Math.max(0, pumps / capacity));
  return {width: 0.19 + 0.55 * growth, height:0.23 + 0.57 * growth};
}
export function csv(columns, rows) {
  const cell = value => {
    let text = value == null ? '' : String(value);
    // Spreadsheet-safe text. Numeric loss/gain values stay numeric.
    if (typeof value === 'string' && /^[\s]*[=+\-@\t\r]/.test(text)) text = "'" + text;
    return '"' + text.replaceAll('"','""') + '"';
  };
  return '\uFEFF' + [columns, ...rows.map(row => columns.map(key => row[key]))].map(row => row.map(cell).join(',')).join('\r\n');
}
export function journal(columns, rows) {
  return [{columns}, ...rows].map(row => JSON.stringify(row)).join('\n') + '\n';
}
export function format(template, values = {}) {
  return template.replace(/\{(\w+)(?::([^}]+))?\}/g, (_, key, spec) => {
    if (!(key in values)) throw Error(`Missing translation argument: ${key}`);
    if (spec === '.2f') return Number(values[key]).toFixed(2);
    if (spec === '02d') return String(values[key]).padStart(2, '0');
    return String(values[key]);
  });
}
