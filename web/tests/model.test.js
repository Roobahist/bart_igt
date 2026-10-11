import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { validateConfig, taskOrder, createDecks, burst, csv, journal, format, balloonSize, instructionSections } from '../model.js';
const config = JSON.parse(readFileSync(new URL('../study-config.json',import.meta.url)));
test('configuration retains canonical columns and rejects unsafe settings', () => {
  validateConfig(config);
  for (const mutate of [c => c.bart.capacity = 0,c => c.igt.decks[0].losses = [],c => c.igt.feedbackMs = -1,c => c.bart.repeatPumps = true,c => c.controls.collect = c.controls.pump]) {
    const copy = structuredClone(config); mutate(copy); assert.throws(() => validateConfig(copy));
  }
});
test('counterbalancing matches integer codes, negatives, and non-numeric codes', () => {
  for (const code of ['1','003','-3',' +5 ','99999999999999999999999','۱','٣','１','1_1']) assert.deepEqual(taskOrder(code),['BART','IGT']);
  for (const code of ['2','0','-4','participant','1.0','','3abc','۲','²','1__1']) assert.deepEqual(taskOrder(code),['IGT','BART']);
});
test('each deck replenishes complete configured loss blocks, independently', () => {
  const draw = createDecks(config.igt, () => .37);
  for (let block = 0; block < 4; block++) for (let deck = 1; deck <= 4; deck++) {
    const outcomes = Array.from({length:config.igt.decks[deck-1].losses.length},() => draw(deck));
    assert.deepEqual(outcomes.map(o => o.loss).sort((a,b) => a-b), [...config.igt.decks[deck-1].losses].sort((a,b) => a-b));
    assert.ok(outcomes.every(o => o.gain === config.igt.decks[deck-1].gain));
  }
  assert.throws(() => draw(0)); assert.throws(() => draw(1.5));
});
test('conditional burst hazard matches Python weighted choices and guarantees terminal burst', () => {
  for (let capacity = 1; capacity <= 128; capacity++) for (let pumps = 1; pumps <= capacity; pumps++) {
    const threshold = 1 - 1 / (capacity + 1 - pumps);
    assert.equal(burst(pumps,capacity, () => 0),pumps === capacity);
    if (threshold > 0) assert.equal(burst(pumps,capacity, () => threshold - Number.EPSILON),false);
    assert.equal(burst(pumps,capacity, () => threshold),true);
  }
  assert.throws(() => burst(0,128)); assert.throws(() => burst(129,128));
});
test('CSV protects participant text and keeps sparse metadata-first rows', () => {
  const output = csv(['subjectName','gain'],[{subjectName:'=HYPERLINK("bad")'},{gain:-1}]);
  assert.ok(output.includes('"\'=HYPERLINK(""bad"")"'));
  assert.ok(output.endsWith('"","-1"'));
  assert.equal(journal(['gain'],[{gain:.05}]),'{"columns":["gain"]}\n{"gain":0.05}\n');
});
test('locale key and parameter parity includes browser screens', () => {
  const locale = code => ({...JSON.parse(readFileSync(new URL('../../locales/'+code+'.json',import.meta.url))).messages,...JSON.parse(readFileSync(new URL('../locales/'+code+'.json',import.meta.url)))});
  const en = locale('en'), fa = locale('fa');
  assert.deepEqual(Object.keys(en).sort(),Object.keys(fa).sort());
  const args = text => [...text.matchAll(/\{(\w+)(?::[^}]+)?\}/g)].map(match => match[1]).sort();
  for (const key of Object.keys(en)) assert.deepEqual(args(en[key]),args(fa[key]),key);
  assert.equal(format(en.igt_amount,{amount:.05}),'$0.05');
  assert.throws(() => format(en.deck,{}));
});
test('balloon geometry grows continuously without a frame or threshold mark', () => {
  const first = balloonSize(0,128), last = balloonSize(128,128);
  assert.ok(first.width < last.width && first.height < last.height);
  assert.ok(Math.abs(last.height - .8) < 1e-12);
});

test('structured instructions preserve every original word and template argument', () => {
  const layouts = JSON.parse(readFileSync(new URL('../instruction-layouts.json',import.meta.url)));
  const normalize = text => text.replace(/\s+/g,' ').trim();
  for (const code of ['en','fa']) {
    const messages = JSON.parse(readFileSync(new URL('../../locales/'+code+'.json',import.meta.url))).messages;
    for (const task of ['bart','igt']) {
      const text = messages[task+'_instructions'];
      const sections = instructionSections(text,layouts[code][task]);
      assert.equal(normalize(sections.flatMap(s => s.paragraphs).join(' ')),normalize(text));
      assert.throws(() => instructionSections(text,layouts[code][task].slice(1)));
    }
  }
});
