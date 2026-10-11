import { validateConfig, taskOrder, createDecks, burst, balloonSize, csv, journal, format, instructionSections } from './model.js';

const root = document.querySelector('#app');
const prefix = 'bart-igt:v1:';
const escapeHTML = value => String(value).replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
const arrow = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><path d="M4 12h15m-6-6 6 6-6 6"/></svg>';
const downloadIcon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><path d="M12 3v12m-5-5 5 5 5-5M4 16v5h16v-5"/></svg>';
let config, catalogs, instructionLayouts, language, session, jsPsych, deckDraw;
let finishPhase, cleanup = () => {}, currentActions = {}, phase = '', busy = false, paused = false, onset = 0;
let total = 0, balance = 0, bank = 0, trialNumber = 0, pumps = 0;
let interruptionStarted = null, interruptionTimer = null, videoWasPlaying = false;
const sounds = {};
const t = (key, values) => format(catalogs[language][key] ?? (() => { throw Error(`Missing translation: ${key}`); })(), values);
const h = (key, values) => escapeHTML(t(key, values));
const money = amount => `<bdi class="money">${h('igt_amount', {amount})}</bdi>`;
const keyName = action => ({space:'SPACE', return:'ENTER', escape:'ESC'})[config.controls[action]] || config.controls[action].toUpperCase();
const keyValue = action => ({space:' ', return:'Enter', escape:'Escape'})[config.controls[action]] || config.controls[action];
const sameKey = (event, action) => event.key.toLowerCase() === keyValue(action).toLowerCase();
const button = (label, action, primary = false) => `<button class="action${primary ? ' primary' : ''}" data-action="${action}">${h(label)}${arrow}</button>`;

function storedSessions() {
  const entries = [];
  for (let i = 0; i < localStorage.length; i++) {
    const key = localStorage.key(i);
    if (!key.startsWith(prefix) || key.endsWith('probe')) continue;
    try {
      const data = JSON.parse(localStorage.getItem(key));
      if (data.schema === 1 && Array.isArray(data.rows)) entries.push(data);
    } catch { /* An unreadable record is retained for manual recovery. */ }
  }
  return entries.sort((a,b) => b.created.localeCompare(a.created));
}
function save() {
  session.updated = new Date().toISOString();
  localStorage.setItem(prefix + session.id, JSON.stringify(session));
}
function append(row) {
  if (Object.keys(row).some(key => !config.columns.includes(key))) throw Error('Unknown result field');
  session.rows.push(row);
  save();
}
function eventRecord(type, details = {}) {
  session.events.push({type, phase, at:new Date().toISOString(), elapsed:performance.now(), ...details});
  save();
}
function download(data, type) {
  const filename = `bart-igt-${data.created.slice(0,10)}-${data.id}`;
  const payload = type === 'csv' ? csv(data.config.columns, data.rows) : type === 'jsonl' ? journal(data.config.columns, data.rows) : JSON.stringify(data, null, 2);
  const blob = new Blob([payload], {type:type === 'csv' ? 'text/csv;charset=utf-8' : 'application/json;charset=utf-8'});
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a'); anchor.href = url; anchor.download = filename + '.' + type;
  anchor.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
}
function masthead(active = false) {
  return `<header class="masthead"><div class="brand"><img src="icon.svg" alt=""><span>BART / IGT</span></div>${active ? '' : `<nav class="locale" aria-label="${h('language')}"><button data-language="en" aria-pressed="${language === 'en'}" lang="en">English</button><button data-language="fa" aria-pressed="${language === 'fa'}" lang="fa">فارسی</button></nav>`}</header>`;
}
function utility() {
  return `<footer class="utility"><span>${h('local_notice')}</span><details class="operator"><summary>${h('operator_controls')}</summary><div class="operator-menu"><button data-action="skip">${h('skip')} <kbd>${escapeHTML(keyName('skip'))}</kbd></button><button data-action="abort">${h('stop')} <kbd>${escapeHTML(keyName('abort'))}</kbd></button></div></details></footer>`;
}
function render(content, className = '', active = true) {
  root.innerHTML = `<div class="shell ${className}">${masthead(active)}${content}${active ? utility() : ''}</div>`;
  root.querySelectorAll('[data-action]').forEach(el => el.addEventListener('click', e => action(el.dataset.action, {input:e.detail === 0 ? 'keyboard-button' : 'pointer'})));
}
function clearPhase() {
  cleanup(); cleanup = () => {};
  currentActions = {}; busy = false;
  clearTimeout(interruptionTimer); interruptionTimer = null;
}
function complete() {
  const done = finishPhase; finishPhase = null;
  clearPhase();
  if (done) done({phase});
}
function stop(storageError = false) {
  clearPhase(); paused = false;
  document.querySelector('.interruption')?.remove(); root.inert = false;
  if (session) {
    session.status = 'stopped';
    try { save(); } catch { /* In-memory responses remain downloadable. */ }
  }
  finishPhase = null;
  if (jsPsych) jsPsych.abortExperiment();
  showFinish(storageError ? 'storage_error' : 'interrupted_body', true);
}
function action(name, details = {}) {
  if (paused || !session || session.status !== 'active') return;
  try {
    if (name === 'abort') { eventRecord('abort', details); stop(); return; }
    if (name === 'skip') { if (currentActions.skip) { eventRecord('skip', details); currentActions.skip(); } return; }
    if (!busy && currentActions[name]) currentActions[name](details);
  } catch (error) { console.error(error); stop(true); }
}
function announce(text) {
  const node = root.querySelector('[role="status"]');
  if (node) node.textContent = text;
}
function startClock() {
  onset = null;
  requestAnimationFrame(() => { if (session?.status === 'active') onset = performance.now(); });
}
const rt = () => Math.max(0,(performance.now() - (onset ?? performance.now())) / 1000);
function safeClick(id, callback) { document.querySelector(id)?.addEventListener('click', callback); }

function showWelcome() {
  session = null; phase = 'setup';
  document.documentElement.lang = language;
  document.documentElement.dir = language === 'fa' ? 'rtl' : 'ltr';
  const options = (values, label) => `<option value="">${h(label)}</option>` + values.map(value => `<option value="${value}">${h('choice.' + value)}</option>`).join('');
  const fields = [['subjectName','text'],['subjectCode','text'],['age','number']].map(([name,type]) => `<label class="field ${name === 'subjectName' ? 'wide' : ''}">${h('field.' + name)}<input name="${name}" type="${type}" ${type === 'number' ? 'min="1" max="120" step="1"' : 'maxlength="120"'} required autocomplete="off"></label>`);
  render(`<section class="welcome"><div class="welcome-copy"><h1>${h('welcome')}</h1><p class="muted">${h('welcome_body')}</p><p class="sequence muted">${h('setup_footer')}</p></div><div class="form-section"><h2>${h('session_details')}</h2><form id="participant"><div class="form-grid">${fields.join('')}<label class="field">${h('field.gender')}<select name="gender" required>${options(['Male','Female','Other'],'field.gender')}</select></label><label class="field">${h('field.handedness')}<select name="handedness" required>${options(['Right','Left'],'field.handedness')}</select></label></div><button class="action primary full" type="submit">${h('start_session')}${arrow}</button><p class="footnote">${h('local_notice')}</p><p id="setup-status" class="notice" role="status"></p></form><div id="recovery"></div></div></section>`, '', false);
  root.querySelectorAll('[data-language]').forEach(el => el.addEventListener('click', () => { language = el.dataset.language; showWelcome(); }));
  let records = [];
  try {
    localStorage.setItem(prefix + 'probe','1'); localStorage.removeItem(prefix + 'probe');
    records = storedSessions();
  } catch { root.querySelector('[type=submit]').disabled = true; announce(t('storage_unavailable')); }
  if (records.length) {
    document.querySelector('#recovery').innerHTML = `<section class="recovery"><h3>${h('recovery_title')}</h3><p class="footnote">${h('recovery_body')}</p><select id="recovery-select" aria-label="${h('recovery_title')}">${records.map((s,i) => `<option value="${i}">${escapeHTML(s.created.replace('T',' ').slice(0,19))} · ${h(s.status === 'completed' ? 'completed_status' : s.status === 'stopped' ? 'stopped_status' : 'active_status')} · ${s.rows.length - 1}</option>`).join('')}</select><button class="action" id="recover-journal">${h('download_journal')}</button> <button class="action" id="recover-detail">${h('download_detail')}</button></section>`;
    const chosen = () => records[Number(document.querySelector('#recovery-select').value)];
    safeClick('#recover-journal', () => download(chosen(), 'jsonl'));
    safeClick('#recover-detail', () => download(chosen(), 'json'));
  }
  document.querySelector('#participant').addEventListener('submit', async e => {
    e.preventDefault();
    const metadata = Object.fromEntries(new FormData(e.target));
    if (Object.values(metadata).some(value => !value.trim())) { announce(t('required')); return; }
    metadata.age = Number(metadata.age);
    const submit = e.target.querySelector('[type=submit]'); submit.disabled = true; announce(t('loading'));
    try {
      await preflight();
      await document.fonts.ready;
      if (config.fullscreen) await document.documentElement.requestFullscreen().catch(() => {});
      startSession(metadata);
    } catch (error) {
      console.error(error); submit.disabled = false;
      if (session) stop(true); else announce(t('media_error'));
    }
  });
}
async function preflight() {
  const imagePaths = Object.values(config.sam).flat();
  await Promise.all(imagePaths.map(src => new Promise((resolve,reject) => { const img = new Image(); img.onload = resolve; img.onerror = reject; img.src = src; })));
  for (const [name, sound] of Object.entries(config.bart.sounds)) {
    if (!sound.enabled) continue;
    // Decode before tasks so a missing/unsupported sound cannot silently change a protocol.
    const audio = new Audio(sound.path); audio.preload = 'auto';
    await new Promise((resolve,reject) => {
      const timer = setTimeout(() => reject(Error('Audio loading timed out')),15000);
      audio.addEventListener('canplaythrough', () => { clearTimeout(timer); resolve(); }, {once:true});
      audio.addEventListener('error', () => { clearTimeout(timer); reject(Error('Audio loading failed')); }, {once:true}); audio.load();
    });
    sounds[name] = audio;
  }
}
function playSound(name) {
  if (!sounds[name]) return;
  sounds[name].currentTime = 0;
  sounds[name].play().catch(() => {
    try { eventRecord('audio-playback-failed',{sound:name}); } catch { stop(true); }
  });
}
function startSession(metadata) {
  total = 0; balance = config.igt.initialBalance; bank = 0;
  session = {schema:1, id:crypto.randomUUID(), created:new Date().toISOString(), status:'active', language, config:structuredClone(config), rows:[], events:[], environment:{userAgent:navigator.userAgent, width:innerWidth,height:innerHeight,devicePixelRatio, reducedMotion:matchMedia('(prefers-reduced-motion: reduce)').matches, runtime:'jsPsych 8.3.0'}};
  append({...metadata,video:config.video.name});
  deckDraw = createDecks(config.igt);
  class ScreenPlugin {
    static info = {name:'bart-igt-screen',version:'1.0.0',parameters:{phase:{type:jsPsychModule.ParameterType.STRING},number:{type:jsPsychModule.ParameterType.INT,default:0}}};
    constructor(engine) { this.engine = engine; }
    async trial(display, trial) {
      return new Promise(resolve => {
        clearPhase(); phase = trial.phase; trialNumber = trial.number;
        finishPhase = resolve;
        try {
          eventRecord('screen',{number:trialNumber});
          if (phase === 'fixation') {
            render('<div class="fixation" aria-hidden="true">+</div>');
            const timeout = setTimeout(complete,config.fixationMs); cleanup = () => clearTimeout(timeout);
          } else if (phase.startsWith('survey')) showSurvey(phase === 'survey-before' ? 'before video' : 'after video');
          else if (phase === 'video') showVideo();
          else if (phase.startsWith('instructions')) showInstructions(phase.split('-')[1]);
          else if (phase === 'IGT') showIgt();
          else if (phase === 'BART') showBart();
        } catch (error) { console.error(error); stop(true); }
      });
    }
  }
  const timeline = [{type:ScreenPlugin,phase:'fixation'},{type:ScreenPlugin,phase:'survey-before'},{type:ScreenPlugin,phase:'video'},{type:ScreenPlugin,phase:'survey-after'}];
  for (const task of taskOrder(metadata.subjectCode)) {
    if (config[task.toLowerCase()].skip) continue;
    timeline.push({type:ScreenPlugin,phase:'instructions-' + task});
    for (let number = 1; number <= config[task.toLowerCase()].trials; number++) timeline.push({timeline:[{type:ScreenPlugin,phase:task,number}],conditional_function:() => !session.skipped?.includes(task)});
  }
  jsPsych = initJsPsych({display_element:root, on_finish:() => {
    if (session?.status !== 'active') return;
    session.status = 'completed'; session.total = total;
    try { save(); showFinish(); } catch { stop(true); }
  }});
  jsPsych.run(timeline).catch(error => { console.error(error); if (session?.status === 'active') stop(true); });
}
function skipTask(task) {
  session.skipped ??= []; session.skipped.push(task); save(); complete();
}
function showInstructions(task) {
  const type = task.toLowerCase();
  const values = {trials:config[type].trials,advance_key:keyName('advance'),pump_key:keyName('pump'),collect_key:keyName('collect')};
  const art = task === 'IGT' ? '<div class="mini-card">1</div><div class="mini-card">2</div>' : '<div class="instruction-balloon-field">' + balloonMarkup() + '</div>';
  const sections = instructionSections(t(type + '_instructions',values),instructionLayouts[language][type]);
  const copy = sections.map(section => `<section class="instruction-section${section.heading ? '' : ' instruction-ready'}">${section.heading ? `<h2>${h(section.heading)}</h2>` : ''}${section.paragraphs.map(paragraph => `<p>${escapeHTML(paragraph)}</p>`).join('')}</section>`).join('');
  render(`<section class="instructions"><div class="instruction-heading"><h1>${h(type + '_title')}</h1><p>${h('instructions_label')}</p><div class="instruction-art" aria-hidden="true">${art}</div></div><div class="instruction-copy">${copy}${button('begin_task','advance',true)}</div></section>`);
  if (task === 'BART') drawBalloon(root.querySelector('.instruction-balloon-field'),config.bart.capacity*.6,config.bart.capacity);
  currentActions = {advance:complete,skip:() => skipTask(task)};
}
function showSurvey(section) {
  const ratings = {arousal:null,pleasure:null};
  const scale = (kind,low,high) => `<section class="scale" aria-labelledby="${kind}-heading"><div class="scale-heading"><h3 id="${kind}-heading">${h(kind + '_title')}</h3><span id="${kind}-selected">${h('unselected')}</span></div><div class="sam-images">${config.sam[kind].map((src,i) => `<img src="${escapeHTML(src)}" alt="" data-sam="${kind}-${i+1}">`).join('')}</div><div class="ratings" role="radiogroup" aria-labelledby="${kind}-heading">${Array.from({length:9},(_,i) => `<button type="button" role="radio" aria-checked="false" aria-label="${i+1}" data-rating="${kind}" data-value="${i+1}" tabindex="${i === 0 ? 0 : -1}">${i+1}</button>`).join('')}</div><div class="scale-endpoints"><span>${h(low)}</span><span>${h(high)}</span></div></section>`;
  render(`<section class="survey"><h1>${h('feel_title')}</h1><p class="survey-intro">${h('survey_instructions')}</p>${scale('arousal','arousal_low','arousal_high')}${scale('pleasure','pleasure_low','pleasure_high')}<div class="survey-bottom"><button class="action primary" data-action="advance" disabled>${h('continue_button')}${arrow}</button></div></section>`);
  const choose = el => {
    ratings[el.dataset.rating] = Number(el.dataset.value);
    root.querySelectorAll(`[data-rating="${el.dataset.rating}"]`).forEach(button => {
      const selected = button === el; button.setAttribute('aria-checked',selected); button.tabIndex = selected ? 0 : -1;
    });
    document.querySelector('#' + el.dataset.rating + '-selected').textContent = String(el.dataset.value) + ' / 9';
    root.querySelector('[data-action=advance]').disabled = Object.values(ratings).some(value => value === null);
  };
  root.querySelectorAll('[data-rating]').forEach(el => {
    el.addEventListener('click', () => choose(el));
    el.addEventListener('keydown', e => {
      if (!['ArrowRight','ArrowLeft','ArrowUp','ArrowDown','Home','End'].includes(e.key)) return;
      e.preventDefault();
      const current = Number(el.dataset.value); const step = ['ArrowRight','ArrowDown'].includes(e.key) ? 1 : -1;
      const value = e.key === 'Home' ? 1 : e.key === 'End' ? 9 : Math.min(9,Math.max(1,current+step));
      const next = root.querySelector(`[data-rating="${el.dataset.rating}"][data-value="${value}"]`); choose(next); next.focus();
    });
  });
  currentActions = {advance:() => { if (Object.values(ratings).every(value => value !== null)) { append({section,...ratings}); complete(); } }};
}
function showVideo() {
  render(`<section class="video-screen"><h1>${h('video_title')}</h1><video id="study-video" playsinline preload="auto" src="${escapeHTML(config.video.path)}"></video><div class="video-actions">${button('play_video','play',true)}${button('pause_video','pause')}${button('replay_video','replay')}</div><p class="footnote">${h('video_hint')}</p><p class="notice" role="status"></p></section>`);
  const video = document.querySelector('#study-video');
  const play = () => video.play().then(() => {
    root.querySelector('[data-action=play]').hidden = true;
  }).catch(() => announce(t('video_failed')));
  const ended = () => { try { eventRecord('video-ended'); complete(); } catch { stop(true); } };
  video.addEventListener('ended',ended);
  video.addEventListener('error', () => announce(t('video_failed')));
  cleanup = () => { video.pause(); video.removeEventListener('ended',ended); video.removeAttribute('src'); video.load(); };
  currentActions = {play, pause:() => { eventRecord('video-pause',{paused:!video.paused}); if (video.paused) play(); else video.pause(); },replay:() => { eventRecord('video-replay'); video.currentTime = 0; play(); },skip:complete};
}
const cardMark = '<svg class="deck-mark" viewBox="0 0 120 120" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="60" cy="60" r="46"/><circle cx="60" cy="60" r="34"/><path d="M14 60h92M60 14v92M27.5 27.5l65 65m-65 0 65-65"/><circle cx="60" cy="60" r="13" fill="currentColor" stroke="none"/></svg>';
function showIgt() {
  render(`<section class="task"><div class="task-heading"><div><span class="progress">${h('igt_progress',{number:trialNumber,trials:config.igt.trials})}</span><h1>${h('igt_choose')}</h1><p>${h('igt_title')}</p></div><div class="balance"><span>${h('igt_balance')}</span>${money(balance)}</div></div><div class="deck-arena">${Array.from({length:4},(_,i) => `<div class="deck-slot"><button class="deck" data-deck="${i+1}" aria-label="${h('deck',{number:i+1})}"><span class="deck-turn"><span class="deck-back"><span class="deck-corner">${i+1}</span>${cardMark}<span class="deck-corner bottom">${i+1}</span></span><span class="deck-front" aria-hidden="true"></span></span></button><p class="deck-label">${h('deck',{number:i+1})}</p></div>`).join('')}</div><p class="card-hint" role="status">${h('igt_pick')}</p></section>`);
  let timeout;
  cleanup = () => clearTimeout(timeout);
  currentActions = {skip:() => skipTask('IGT')};
  startClock();
  root.querySelectorAll('[data-deck]').forEach(el => el.addEventListener('click', e => {
    if (busy || paused || onset === null || session.status !== 'active') return;
    busy = true;
    try {
      const choice = Number(el.dataset.deck); const outcome = deckDraw(choice);
      append({section:'IGT',trial:trialNumber,choice,...outcome,RT:rt()});
      eventRecord('igt-choice',{choice,input:e.detail ? 'pointer' : 'keyboard-button'});
      balance += outcome.gain - outcome.loss; total += outcome.gain - outcome.loss;
      root.querySelectorAll('[data-deck]').forEach(button => button.disabled = true);
      el.querySelector('.deck-front').innerHTML = `<span class="result-title">${h('igt_result')}</span><span class="result-row gain"><span>${h('igt_gain_label')}</span><strong>${h('igt_gain_amount',{amount:outcome.gain})}</strong></span><span class="result-row loss"><span>${h('igt_loss_label')}</span><strong>${h('igt_loss_amount',{amount:outcome.loss})}</strong></span>`;
      el.querySelector('.deck-front').setAttribute('aria-hidden','false'); el.querySelector('.deck-back').setAttribute('aria-hidden','true');
      el.classList.add('revealed');
      announce(t('igt_gain',{amount:outcome.gain}) + ' ' + t('igt_loss',{amount:outcome.loss}));
      // Flip motion is contained inside the existing feedback hold, never added to it.
      const feedbackEnd = performance.now() + config.igt.feedbackMs;
      const check = () => { if (paused) { timeout = setTimeout(check,100); return; } const remaining = feedbackEnd - performance.now(); if (remaining > 0) timeout = setTimeout(check,remaining); else complete(); };
      timeout = setTimeout(check,config.igt.feedbackMs);
    } catch (error) { console.error(error); stop(true); }
  }));
}
function balloonMarkup() {
  return `<svg class="balloon" aria-hidden="true"><defs>
    <radialGradient id="rubber" cx=".32" cy=".23" r=".78" gradientTransform="translate(0 .03) scale(1 1.08)">
      <stop offset="0" stop-color="#ffb9a5"/><stop offset=".4" stop-color="#f38a76"/><stop offset=".8" stop-color="#db6c60"/><stop offset="1" stop-color="#ac4b4b"/>
    </radialGradient>
    <radialGradient id="reflection"><stop stop-color="#fff0df" stop-opacity=".6"/><stop offset="1" stop-color="#fff0df" stop-opacity="0"/></radialGradient>
  </defs><path class="balloon-body" fill="url(#rubber)"/><ellipse class="balloon-reflection" fill="url(#reflection)"/>
    <path class="balloon-neck" fill="#c46458"/><path class="balloon-knot" fill="#d47b67"/>
    <path class="balloon-rope" fill="none" stroke="#aeb9cb" stroke-width="1.2" stroke-linecap="round"/>
  </svg>`;
}
function drawBalloon(field, count, capacity) {
  const size = balloonSize(count,capacity);
  const {width:fieldWidth,height:fieldHeight} = field.getBoundingClientRect();
  const svg = field.querySelector('.balloon');
  svg.setAttribute('viewBox',`0 0 ${fieldWidth} ${fieldHeight}`);
  const x = fieldWidth / 2, anchor = fieldHeight * .86;
  const w = fieldWidth * size.width, height = fieldHeight * size.height;
  const bottom = anchor - 8, top = bottom - height;
  // Only the body contour changes. Its neck joins a fixed knot in field coordinates.
  svg.querySelector('.balloon-body').setAttribute('d',`M ${x-4} ${bottom}
    C ${x-w*.16} ${bottom-height*.06} ${x-w*.5} ${bottom-height*.28} ${x-w*.5} ${top+height*.46}
    C ${x-w*.5} ${top+height*.2} ${x-w*.29} ${top} ${x} ${top}
    C ${x+w*.29} ${top} ${x+w*.5} ${top+height*.2} ${x+w*.5} ${top+height*.46}
    C ${x+w*.5} ${bottom-height*.28} ${x+w*.16} ${bottom-height*.06} ${x+4} ${bottom} Z`);
  const reflection = svg.querySelector('.balloon-reflection');
  reflection.setAttribute('cx',x-w*.22); reflection.setAttribute('cy',top+height*.27);
  reflection.setAttribute('rx',w*.08); reflection.setAttribute('ry',height*.17);
  reflection.setAttribute('transform',`rotate(20 ${x-w*.22} ${top+height*.27})`);
  svg.querySelector('.balloon-neck').setAttribute('d',`M ${x-4} ${anchor-8} L ${x-3} ${anchor} Q ${x} ${anchor+3} ${x+3} ${anchor} L ${x+4} ${anchor-8} Z`);
  svg.querySelector('.balloon-knot').setAttribute('d',`M ${x-2} ${anchor+1} Q ${x-5} ${anchor+7} ${x-7} ${anchor+11} Q ${x} ${anchor+8} ${x+7} ${anchor+11} Q ${x+5} ${anchor+6} ${x+2} ${anchor+1} Z`);
  const ropeLength = Math.min(69,fieldHeight-anchor-18), ropeY = anchor+9;
  svg.querySelector('.balloon-rope').setAttribute('d',`M ${x} ${ropeY} C ${x-9} ${ropeY+ropeLength*.23} ${x+10} ${ropeY+ropeLength*.38} ${x+1} ${ropeY+ropeLength*.57} S ${x-7} ${ropeY+ropeLength*.87} ${x-1} ${ropeY+ropeLength}`);
}
function updateBalloon() {
  drawBalloon(root.querySelector('.balloon-field'),pumps,config.bart.capacity);
  document.querySelector('#balloon-value').innerHTML = money(pumps * config.bart.reward);
  document.querySelector('#bank-value').innerHTML = money(bank);
}
function showBart() {
  pumps = 0;
  render(`<section class="balloon-layout"><div class="balloon-field">${balloonMarkup()}</div><div class="balloon-controls"><span class="progress">${h('bart_progress',{number:trialNumber,trials:config.bart.trials})}</span><h1>${h('bart_title')}</h1><div class="balloon-ledger"><div class="ledger-row"><span>${h('bart_value_label')}</span><span id="balloon-value">${money(0)}</span></div><div class="ledger-row"><span>${h('bart_bank_label')}</span><span id="bank-value">${money(bank)}</span></div></div><div class="balloon-actions"><button class="action" data-action="pump"><span>${h('bart_pump')}</span><kbd>${escapeHTML(keyName('pump'))}</kbd></button><button class="action" data-action="collect"><span>${h('bart_collect')}</span><kbd>${escapeHTML(keyName('collect'))}</kbd></button></div></div></section>`,'bart-shell');
  updateBalloon(); startClock();
  const resize = () => updateBalloon(); window.addEventListener('resize',resize);
  cleanup = () => window.removeEventListener('resize',resize);
  currentActions = {
    pump:details => {
      if (onset === null) return;
      pumps++;
      const exploded = burst(pumps,config.bart.capacity);
      eventRecord('bart-pump',{pumps,exploded,input:details.input});
      if (exploded) {
        busy = true; append({section:'BART',trial:trialNumber,pumps,gain:0,explosion:1,RT:rt()}); playSound('burst'); complete();
      } else { playSound('blow'); updateBalloon(); }
    },
    collect:details => {
      if (onset === null) return;
      busy = true; const gain = pumps * config.bart.reward;
      append({section:'BART',trial:trialNumber,pumps,gain,explosion:0,RT:rt()});
      eventRecord('bart-collect',{input:details.input}); bank += gain; total += gain; playSound('collect'); complete();
    },
    skip:() => skipTask('BART'),
  };
}
function showFinish(message = 'thanks', interrupted = false) {
  phase = 'finish';
  render(`<section class="finish"><div class="finish-copy"><h1>${h(interrupted ? 'interrupted' : 'finish_title')}</h1><p>${h(message)}</p><button class="text-button" id="new-session">${h('new_session')}</button></div><div class="finish-results">${interrupted ? '' : `<p class="muted">${h('winnings')}</p><div class="winnings">${money(total)}</div><p class="muted">${h('toman',{amount:Math.trunc(total * config.exchangeRate)})}</p>`}<div class="download-actions"><button class="action primary" id="csv">${h('download_csv')}${downloadIcon}</button><button class="action" id="journal">${h('download_journal')}${downloadIcon}</button><button class="action" id="detail">${h('download_detail')}${downloadIcon}</button></div><p class="footnote">${h('download_hint')}</p><p class="footnote" role="status">${h(message === 'storage_error' ? 'memory_only' : 'saved')}</p></div></section>`, '', true);
  for (const [id,type] of [['csv','csv'],['journal','jsonl'],['detail','json']]) safeClick('#' + id, () => { download(session,type); announce(t('download_success')); });
  safeClick('#new-session', () => { clearPhase(); jsPsych = null; showWelcome(); });
  root.querySelector('.operator')?.remove();
}
// Inputs are measured on activation/release; held keys never repeat or spill into a new trial.
const held = new Set(); let releaseAction = null;
document.addEventListener('keydown', e => {
  if (e.repeat || held.has(e.key)) {
    if (session?.status === 'active' && ['pump','collect','advance'].some(name => currentActions[name] && sameKey(e,name))) e.preventDefault();
    return;
  }
  held.add(e.key);
  if (!session || session.status !== 'active' || paused || /INPUT|SELECT|TEXTAREA/.test(e.target.tagName)) return;
  if (e.target.closest('button') && [' ', 'Enter'].includes(e.key)) return;
  for (const name of ['abort','skip','pump','collect','advance','pause','replay']) {
    if (!sameKey(e,name)) continue;
    if (!currentActions[name] && name !== 'abort') continue;
    e.preventDefault();
    if (['collect','advance'].includes(name)) releaseAction = {name,phase,trialNumber};
    else action(name,{input:'keyboard'});
    break;
  }
});
document.addEventListener('keyup', e => {
  held.delete(e.key);
  if (releaseAction && sameKey(e,releaseAction.name)) {
    const pending = releaseAction; releaseAction = null;
    if (pending.phase === phase && pending.trialNumber === trialNumber) action(pending.name,{input:'keyboard'});
  }
});
function interrupt() {
  held.clear(); releaseAction = null;
  if (!session || session.status !== 'active' || paused || phase === 'fixation') return;
  paused = true; interruptionStarted = performance.now();
  const video = document.querySelector('#study-video'); videoWasPlaying = video && !video.paused; video?.pause();
  try { eventRecord('focus-lost',{hidden:document.hidden}); } catch { stop(true); return; }
  root.inert = true;
  const overlay = document.createElement('div'); overlay.className = 'interruption'; overlay.setAttribute('role','dialog'); overlay.setAttribute('aria-modal','true');
  overlay.innerHTML = `<div><h2>${h('hidden_title')}</h2><p>${h('hidden_body')}</p><button class="action primary" id="resume">${h('resume')}</button></div>`; document.body.append(overlay);
  overlay.querySelector('button').addEventListener('click', () => {
    try { eventRecord('focus-restored',{durationMs:performance.now()-interruptionStarted}); } catch { stop(true); return; }
    paused = false; root.inert = false; overlay.remove(); root.focus();
    // RT includes the interruption; the separate event log identifies affected trials.
    if (videoWasPlaying) document.querySelector('#study-video')?.play().catch(() => announce(t('video_failed')));
  });
}
window.addEventListener('blur',interrupt);
document.addEventListener('visibilitychange', () => { if (document.hidden) interrupt(); });
window.addEventListener('beforeunload', e => { if (session?.status === 'active') { e.preventDefault(); e.returnValue = ''; } });
async function load() {
  config = validateConfig(await (await fetch('./study-config.json')).json());
  instructionLayouts = await (await fetch('./instruction-layouts.json')).json();
  catalogs = {};
  for (const code of ['en','fa']) {
    const [base, browser] = await Promise.all([fetch('../locales/' + code + '.json').then(r => r.json()),fetch('./locales/' + code + '.json').then(r => r.json())]);
    catalogs[code] = {...base.messages,...browser};
  }
  const keys = Object.keys(catalogs.en);
  if (keys.length !== Object.keys(catalogs.fa).length || keys.some(key => !(key in catalogs.fa))) throw Error('Incomplete translations');
  const query = new URLSearchParams(location.search).get('lang');
  language = ['en','fa'].includes(query) ? query : config.language;
  showWelcome();
}
load().catch(error => {
  console.error(error);
  root.innerHTML = '<div class="shell"><h1>BART / IGT</h1><p class="notice" role="alert">The experiment could not load. Serve the repository locally and check the study files, then reload.<br>آزمون بارگذاری نشد. مخزن را به‌صورت محلی اجرا و فایل‌ها را بررسی کنید.</p></div>';
});
