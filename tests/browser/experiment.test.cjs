// Integration checks and genuine screenshots, using scripted synthetic input only.
const assert = require('node:assert/strict');
const fs = require('node:fs/promises');
const path = require('node:path');
const crypto = require('node:crypto');
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const base = process.env.EXPERIMENT_URL || 'http://127.0.0.1:8877/apps/browser/';
const output = process.env.CAPTURE_DIR || path.resolve(__dirname,'../../docs/screenshots/browser');
const errors = [];
const checks = [];
const capture = async (page,name) => {
  await page.evaluate(() => document.fonts.ready);
  await page.screenshot({path:path.join(output,name + '.png'),fullPage:true});
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth > innerWidth);
  assert.equal(overflow,false,'Horizontal overflow: ' + name);
};
const checkpoint = message => { checks.push(message); console.log('PASS',message); };
async function fill(page,code='2') {
  await page.locator('[name=subjectName]').fill('Synthetic demonstration');
  await page.locator('[name=subjectCode]').fill(code);
  await page.locator('[name=age]').fill('28');
  await page.locator('[name=gender]').selectOption('Other');
  await page.locator('[name=handedness]').selectOption('Right');
  await page.locator('[type=submit]').click();
  await page.locator('.survey').waitFor({timeout:20000});
}
async function survey(page) {
  await page.locator('[data-rating=arousal][data-value="5"]').click();
  await page.locator('[data-rating=pleasure][data-value="5"]').click();
  await page.locator('[data-action=advance]').click();
}
async function skipVideo(page) {
  await page.locator('.video-screen').waitFor();
  // Exercise real playback and pause rather than mocking a video element.
  await page.locator('[data-action=play]').click();
  await page.waitForFunction(() => document.querySelector('video').currentTime > 0);
  await page.locator('[data-action=pause]').click();
  assert.equal(await page.locator('video').evaluate(el => el.paused),true);
  await page.locator('[data-action=replay]').click();
  await page.waitForFunction(() => !document.querySelector('video').paused);
  await page.keyboard.press('i');
  await page.locator('.survey').waitFor();
}
async function rows(page) {
  return page.evaluate(() => Object.keys(localStorage).filter(key => key.startsWith('bart-igt:v1:')).map(key => JSON.parse(localStorage.getItem(key))).sort((a,b) => b.created.localeCompare(a.created))[0]);
}
(async () => {
  await fs.mkdir(output,{recursive:true});
  const browser = await chromium.launch({headless:true,...(process.env.BROWSER_CHANNEL ? {channel:process.env.BROWSER_CHANNEL} : {})});
  try {
    const context = await browser.newContext({viewport:{width:1440,height:900},acceptDownloads:true});
    const page = await context.newPage();
    page.on('pageerror',error => errors.push(error.message));
    page.on('response',response => { if (response.status() >= 400) errors.push(`HTTP ${response.status()}: ${response.url()}`); });
    // Deterministic RNG for repeatable captures; scientific rules still run unchanged.
    await page.addInitScript(() => { let seed=7; Math.random=() => {seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296;}; });
    await page.goto(base);
    await page.locator('.welcome').waitFor();
    await capture(page,'english-setup');
    await fill(page);
    assert.equal(await page.locator('[data-action=advance]').isDisabled(),true);
    await capture(page,'english-survey');
    await survey(page); await skipVideo(page); await survey(page);
    await page.locator('.instructions').waitFor();
    await capture(page,'english-igt-instructions');
    await page.keyboard.down(' '); await page.keyboard.up(' ');
    await page.locator('.deck-arena').waitFor();
    assert.ok(await page.locator('.deck-mark').first().evaluate(el => el.getBoundingClientRect().width) > 80,'Card art has a real rendered area');
    await capture(page,'english-igt-choice');
    for (let i=1;i<=5;i++) {
      await page.locator('[data-deck="1"]:not(:disabled)').click();
      if (i===1) { await page.waitForTimeout(450); await capture(page,'english-igt-reveal'); }
      assert.equal((await rows(page)).rows.filter(row => row.section==='IGT').length,i);
      if (i<5) await page.locator('[data-deck="1"]:not(:disabled)').waitFor();
    }
    await page.locator('.instructions').waitFor();
    await capture(page,'english-bart-instructions');
    await page.locator('[data-action=advance]').click();
    await page.locator('.balloon-layout').waitFor();
    await capture(page,'english-bart-start');
    const fixedGeometry = () => page.evaluate(() => Object.fromEntries(['balloon-neck','balloon-knot','balloon-rope'].map(name => [name,document.querySelector('.'+name).getAttribute('d')])));
    const attachmentAtStart = await fixedGeometry();
    const topAtStart = await page.locator('.balloon-body').evaluate(el => el.getBoundingClientRect().top);
    const bottomAtStart = await page.locator('.balloon-body').evaluate(el => el.getBoundingClientRect().bottom);
    // Avoid bursts in this geometry capture using the boundary RNG sample 0.
    // Separate tests below exercise forced bursts; this fixture is explicit in provenance.
    await page.evaluate(() => {Math.random=() => 0;});
    await page.keyboard.down(' '); await page.waitForTimeout(120); await page.keyboard.up(' ');
    assert.equal((await rows(page)).events.filter(e => e.type==='bart-pump').length,1,'Held Space pumps once');
    for(let i=1;i<20;i++) await page.keyboard.press(' ');
    assert.deepEqual(await fixedGeometry(),attachmentAtStart,'Inflation must not move or resize neck, knot or rope');
    assert.ok(await page.locator('.balloon-body').evaluate(el => el.getBoundingClientRect().top) < topAtStart);
    assert.ok(Math.abs(await page.locator('.balloon-body').evaluate(el => el.getBoundingClientRect().bottom) - bottomAtStart) < .01);
    await capture(page,'english-bart-pumped');
    await page.setViewportSize({width:390,height:844});
    await capture(page,'english-bart-mobile');
    await page.setViewportSize({width:1440,height:900});
    for(let i=20;i<127;i++) await page.keyboard.press(' ');
    assert.deepEqual(await fixedGeometry(),attachmentAtStart,'Attachments remain fixed even at 127 pumps');
    await capture(page,'english-bart-large');
    await page.keyboard.press('Enter');
    assert.equal((await rows(page)).rows.find(row => row.section==='BART').pumps,127);
    assert.ok(Math.abs((await rows(page)).rows.find(row => row.section==='BART').gain - 6.35) < 1e-12);
    await page.evaluate(() => {Math.random=() => .999999;});
    await page.keyboard.press(' ');
    const burstRow = (await rows(page)).rows.filter(row => row.section==='BART')[1];
    assert.equal(burstRow.explosion,1); assert.equal(burstRow.gain,0);
    for(let i=0;i<3;i++) { await page.waitForTimeout(40); await page.keyboard.press('Enter'); }
    await page.locator('.finish').waitFor();
    const record = await rows(page);
    assert.equal(record.status,'completed'); assert.equal(record.rows.length,13);
    assert.equal(record.rows[0].gender,'Other'); assert.equal(record.rows[0].handedness,'Right');
    assert.equal(record.rows[1].section,'before video'); assert.equal(record.rows[2].section,'after video');
    await capture(page,'english-completion');
    const downloadEvent = page.waitForEvent('download'); await page.locator('#journal').click();
    const download = await downloadEvent; const journalPath = path.join(output,'synthetic-session.jsonl');
    await download.saveAs(journalPath);
    assert.equal((await fs.readFile(journalPath,'utf8')).trim().split('\n').length,14);
    checkpoint('Complete English session: SAM, real video playback/pause/replay, 5 IGT choices, collection, burst, exports');
    checkpoint('Held-key suppression; canonical metadata and rows; zero-value collection; 127-pump growth');
    await page.reload(); await page.locator('#recovery-select').waitFor();
    checkpoint('Completed session retained after reload with recovery downloads');
    await page.setViewportSize({width:390,height:844});
    await page.goto(base + '?lang=fa'); await page.locator('.welcome').waitFor();
    await capture(page,'persian-setup-mobile');
    await fill(page,'1'); await capture(page,'persian-survey-mobile');
    await survey(page); await skipVideo(page); await survey(page);
    await page.locator('.instructions').waitFor();
    assert.ok((await page.locator('.instruction-heading h1').textContent()).includes('بادکنک'));
    await capture(page,'persian-bart-instructions-mobile');
    await page.locator('[data-action=advance]').click(); await page.locator('.balloon-layout').waitFor();
    await capture(page,'persian-bart-mobile');
    await page.evaluate(() => window.dispatchEvent(new Event('blur')));
    await page.locator('.interruption').waitFor();
    await page.locator('#resume').click();
    await page.keyboard.press('i');
    await page.locator('.instructions').waitFor();
    await page.locator('[data-action=advance]').click(); await page.locator('.deck-arena').waitFor();
    await capture(page,'persian-igt-mobile');
    await page.locator('[data-deck="2"]').click();
    await page.waitForTimeout(450); await capture(page,'persian-igt-reveal-mobile');
    await page.keyboard.press('Escape'); await page.locator('.finish').waitFor();
    assert.equal((await rows(page)).status,'stopped');
    assert.ok((await rows(page)).events.some(e => e.type==='focus-lost'));
    assert.equal((await rows(page)).rows.filter(r => r.section==='IGT').length,1);
    checkpoint('Persian RTL; odd-code BART-first order; skip; interruption logging; safe abort retains response');
    // A full browser storage quota / blocked-write is a hard stop with memory downloads.
    const failedContext = await browser.newContext({viewport:{width:1280,height:800}});
    const failedPage = await failedContext.newPage();
    await failedPage.goto(base); await failedPage.locator('.welcome').waitFor(); await fill(failedPage);
    await failedPage.evaluate(() => {Storage.prototype.setItem=() => {throw new DOMException('Quota exceeded','QuotaExceededError');};});
    await failedPage.locator('[data-rating=arousal][data-value="3"]').click();
    await failedPage.locator('[data-rating=pleasure][data-value="4"]').click();
    await failedPage.locator('[data-action=advance]').click();
    await failedPage.locator('.finish').waitFor();
    assert.ok((await failedPage.locator('.finish-copy p').textContent()).includes('could not save'));
    checkpoint('Storage failure prevents continuation and offers retained in-memory downloads');
    await failedContext.close();
    assert.deepEqual(errors,[]);
    const provenance = {kind:'Scripted browser demonstrations, not participant sessions',capturedAt:new Date().toISOString(),browser:await browser.version(),runtime:'jsPsych 8.3.0',viewports:[{width:1440,height:900},{width:390,height:844}],seed:7,geometryFixture:'Math.random returns 0 for the 20/127-pump growth captures; .999999 exercises a burst in a separate trial. These are explicitly synthetic fixtures, not natural sampled sessions.',video:'Original neutral video played, paused, replayed, then operator-skipped. Full-duration playback and audio perception are not validated.',checks,errors};
    provenance.sourceFiles = {};
    for (const name of ['apps/browser/experiment.js','apps/browser/styles.css','apps/browser/study-model.js','study/browser-settings.json','apps/browser/instruction-layouts.json','apps/browser/locales/en.json','apps/browser/locales/fa.json','study/locales/en.json','study/locales/fa.json']) provenance.sourceFiles[name] = crypto.createHash('sha256').update(await fs.readFile(path.resolve(__dirname,'../../',name))).digest('hex');
    await fs.writeFile(path.join(output,'provenance.json'),JSON.stringify(provenance,null,2)+'\n');
    await context.close();
    console.log('All browser integration checks passed. Captures:',output);
  } finally {await browser.close();}
})().catch(error => {console.error(error); process.exitCode=1;});
