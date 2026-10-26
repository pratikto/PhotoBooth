/** Run the actual Code.gs functions with a scoped, in-memory Drive service.
 * No Google account, credentials, network request, or customer photo is used.
 * Execute with: node --test tests/test_apps_script_retention.cjs
 */
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const crypto = require('node:crypto');
const source = fs.readFileSync(path.join(__dirname, '../apps_script/Code.gs'), 'utf8');
const NOW = Date.parse('2026-10-16T00:00:00Z');
const DAY = 86400000;
class ClockDate extends Date {
  constructor(value) { super(value === undefined ? NOW : value); }
  static now() { return NOW; }
}
function iterator(items) {
  let index = 0;
  return { hasNext: () => index < items.length, next: () => items[index++],
    getContinuationToken: () => String(index) };
}
function harness() {
  const clockTrigger = (handler = 'cleanupPhotoRetention') => ({
    getHandlerFunction: () => handler, getEventType: () => 'CLOCK',
  });
  const objects = new Map(), requests = [], triggers = [clockTrigger()], settings = {
    DRIVE_FOLDER_ID: 'booth-parent', UPLOAD_TOKEN: 'fixture-token', PHOTOBOOTH_RETENTION_ENABLED: 'true',
  };
  const properties = { getProperty: key => settings[key] || null,
    setProperty: (key, value) => { settings[key] = value; },
    deleteProperty: key => { delete settings[key]; }, getProperties: () => ({ ...settings }) };
  let deleteStatus = 204;
  function object(id, name, parent = 'booth-parent', imageAge = null) {
    const entry = { id, name, parent, description: '', deleted: false, children: [], files: [],
      getId() { return this.id; }, getName() { return this.name; },
      getUrl() { return 'https://drive.google.com/drive/folders/' + this.id; },
      getFoldersByName(name) { return iterator(this.children.filter(f => f.name === name && !f.deleted)); },
      getFilesByName(name) { return iterator(this.files.filter(f => f.name === name && !f.deleted)); },
      createFolder(name) { return folder('new-' + objects.size, name, this); },
      createFile(blob) { const f = file('new-' + objects.size, blob.name, 0, this); f.bytes = blob.getBytes(); return f; },
      setName(name) { this.name = name; },
      moveTo(parent) { const previous = objects.get(this.parent); previous.children = previous.children.filter(f => f !== this); this.parent = parent.id; parent.children.push(this); },
      getSharingPermission() { return 'view'; },
      setSharing() { this.shared = true; }, getSharingAccess() { return this.shared ? 'anyone' : 'private'; },
      getBlob() { return { getBytes: () => this.bytes || [] }; },
      getDescription() { return this.description; }, setDescription(value) { this.description = value; },
      isTrashed() { return false; },
      getDateCreated() { return new ClockDate(NOW - (imageAge === null ? 200 : imageAge) * DAY); },
      getParents() { return iterator(this.parent ? [objects.get(this.parent)] : []); },
      getFiles() { return iterator(this.files.filter(file => !file.deleted)); },
      getFolders() { return iterator(this.children.filter(folder => !folder.deleted)); },
      searchFolders(query) { assert.match(query, /trashed = false/); return this.getFolders(); },
      searchFiles(query) { assert.match(query, /trashed = false/); return this.getFiles(); },
    };
    objects.set(id, entry);
    return entry;
  }
  const root = object('booth-parent', 'PhotoBooth', null);
  function folder(id, name, parent = root) {
    const entry = object(id, name, parent.id);
    parent.children.push(entry);
    return entry;
  }
  function file(id, name, age, parent = root) {
    const entry = object(id, name, parent.id, age);
    parent.files.push(entry);
    return entry;
  }
  const context = vm.createContext({ Date: ClockDate, console: { log() {} },
    PropertiesService: { getScriptProperties: () => properties },
    LockService: { getScriptLock: () => ({ waitLock() {}, tryLock: () => true, releaseLock() {} }) },
    Utilities: { DigestAlgorithm: { MD5: 'md5' }, computeDigest: (_, bytes) => Array.from(crypto.createHash('md5').update(Buffer.from(bytes)).digest()),
      newBlob: (value, mime, name) => ({ name, getBytes: () => Array.from(typeof value === 'string' ? Buffer.from(value) : value) }),
      base64Decode: value => Array.from(Buffer.from(value, 'base64')), base64Encode: bytes => Buffer.from(bytes).toString('base64') },
    DriveApp: { Access: { ANYONE_WITH_LINK: 'anyone' }, Permission: { VIEW: 'view' }, getRootFolder: () => root, getFolderById(id) { if (!objects.has(id)) throw Error('Unknown folder'); return objects.get(id); },
      continueFolderIterator: () => iterator(root.children) },
    ScriptApp: { EventType: { CLOCK: 'CLOCK' }, getOAuthToken: () => 'fixture-oauth', getProjectTriggers: () => triggers,
      deleteTrigger(item) { triggers.splice(triggers.indexOf(item), 1); },
      newTrigger(handler) { return { timeBased() { return this; }, everyHours(hours) {
        assert.equal(hours, 1); return this;
      }, create() { const trigger = clockTrigger(handler); triggers.push(trigger); return trigger; } }; } },
    UrlFetchApp: { fetch(url, options) {
      const id = decodeURIComponent(new URL(url).pathname.split('/').pop());
      requests.push({ id, method: options.method });
      if (options.method === 'delete' && deleteStatus === 204) objects.get(id).deleted = true;
      return { getResponseCode: () => options.headers.Range ? 206 : options.method === 'get' ? 200 : deleteStatus,
        getBlob: () => ({ getBytes: () => {
          const entry = objects.get(id), match = /bytes=(\d+)-(\d+)/.exec(options.headers.Range);
          return entry.bytes.slice(Number(match[1]), Number(match[2]) + 1);
        } }),
        getContentText: () => { const entry = objects.get(id); return JSON.stringify(entry && entry.bytes ? {
          id, name: entry.name, size: String(entry.bytes.length), md5Checksum: crypto.createHash('md5').update(Buffer.from(entry.bytes)).digest('hex'),
          mimeType: 'application/octet-stream', parents: [entry.parent], trashed: false
        } : { id, mimeType: 'application/vnd.google-apps.folder' }); } };
    } },
    ContentService: { MimeType: { JSON: 'json' }, createTextOutput(value) {
      return { body: JSON.parse(value), setMimeType() { return this; } };
    } },
  });
  vm.runInContext(source, context);
  function mark(entry, age) {
    entry.description = JSON.stringify(context.photoRetention_(entry.name, new ClockDate(NOW - age * DAY)));
    return entry;
  }
  return { context, root, settings, properties, requests, triggers, folder, file, mark,
    setDeleteStatus: status => { deleteStatus = status; } };
}

test('30-day boundary uses permanent scoped deletion, without Trash', () => {
  const h = harness();
  const expired = h.mark(h.folder('expired', 'PB001_00000001'), 30);
  const recent = h.mark(h.folder('recent', 'PB001_00000002'), 29.999);
  h.context.cleanupPhotoRetention();
  assert.equal(expired.deleted, true);
  assert.equal(recent.deleted, false);
  assert.deepEqual(h.requests, [{ id: 'expired', method: 'delete' }]);
});

test('unused pre-created READY slots remain, even with an old or forged deadline', () => {
  const h = harness();
  const ready = h.mark(h.folder('ready', 'PB001_00000001'), 200);
  const empty = h.folder('empty', 'PB001_00000002');
  h.settings.PHOTOBOOTH_POOL_PB001 = JSON.stringify({ slots: [{ folder_id: 'ready', status: 'READY' }] });
  h.context.cleanupPhotoRetention();
  assert.equal(ready.deleted, false);
  assert.equal(empty.deleted, false);
  assert.equal(empty.description, '');
  assert.equal(h.requests.length, 0);
});

test('original transaction registration is immutable across retries and removes the READY slot', () => {
  const h = harness();
  const folder = h.folder('claimed', 'PB001_00000001');
  h.settings.PHOTOBOOTH_POOL_PB001 = JSON.stringify({ slots: [{ folder_id: 'claimed', status: 'READY' }] });
  const body = { folder_id: 'claimed', transaction_id: folder.name, started_at: new ClockDate(NOW - 14 * DAY).toISOString() };
  const first = h.context.registerRetention_(body, h.properties).retention;
  const retry = h.context.registerRetention_({ ...body, started_at: new ClockDate().toISOString() }, h.properties).retention;
  assert.equal(first.expires_at, retry.expires_at);
  assert.equal(Date.parse(first.expires_at), NOW + 16 * DAY);
  assert.equal(JSON.parse(h.settings.PHOTOBOOTH_POOL_PB001).slots.length, 0);
});

test('adoption uses the oldest photo date, never the old empty-folder creation date', () => {
  const h = harness();
  const recent = h.folder('recent', 'PB001_00000001');
  const raw = h.folder('raw', 'raw', recent);
  const session = h.folder('session', 'session_001', raw);
  h.file('photo', 'capture_01.jpg', 3, session);
  h.context.cleanupPhotoRetention();
  assert.equal(recent.deleted, false);
  assert.equal(Date.parse(JSON.parse(recent.description).expires_at), NOW + 27 * DAY);
});

test('unrelated/foreign folders, malformed metadata, and unknown nested content are preserved', () => {
  const h = harness();
  const foreignParent = h.folder('foreign-parent', 'Other');
  const foreign = h.mark(h.folder('foreign', 'PB001_00000001', foreignParent), 40);
  const unknown = h.folder('unknown', 'PB001_00000002');
  unknown.description = 'Personal folder notes';
  const malformed = h.folder('malformed', 'PB001_00000003');
  malformed.description = '{not-json';
  const nested = h.folder('nested', 'PB001_00000004');
  const raw = h.folder('raw', 'raw', nested);
  h.folder('notes', 'personal-notes', raw);
  const output = h.folder('output', 'output', nested);
  const session = h.folder('session', 'session_001', output);
  h.file('result', 'template_a.png', 40, session);
  h.context.cleanupPhotoRetention();
  for (const entry of [foreignParent, foreign, unknown, malformed, nested]) assert.equal(entry.deleted, false);
  assert.equal(h.requests.length, 0);
});

test('legacy root photo pattern expires, arbitrary root images remain untouched', () => {
  const h = harness();
  const legacy = h.file('legacy', 'photo_20260901_120000_123456.jpg', 31);
  const unrelated = h.file('unrelated', 'reference.jpg', 100);
  const marked = h.mark(h.file('owned-legacy', 'portrait.jpg', 31), 31);
  h.context.cleanupPhotoRetention();
  assert.equal(legacy.deleted, true);
  assert.equal(unrelated.deleted, false);
  assert.equal(marked.deleted, true);
});

test('Drive permission failures are reported and retried; successful deletion is idempotent', () => {
  const h = harness();
  const folder = h.mark(h.folder('old', 'PB001_00000001'), 31);
  h.setDeleteStatus(403);
  assert.equal(h.context.cleanupPhotoRetention().errors.length, 1);
  assert.equal(folder.deleted, false);
  h.setDeleteStatus(204);
  h.context.cleanupPhotoRetention();
  h.context.cleanupPhotoRetention();
  assert.equal(folder.deleted, true);
  assert.equal(h.requests.filter(r => r.method === 'delete').length, 2);
});

test('preview is read-only before activation and reports only candidates', () => {
  const h = harness();
  delete h.settings.PHOTOBOOTH_RETENTION_ENABLED;
  const old = h.folder('old', 'PB001_00000001');
  const raw = h.folder('raw', 'raw', old);
  const session = h.folder('session', 'session_001', raw);
  h.file('photo', 'capture_01.jpg', 31, session);
  const result = h.context.previewPhotoRetention();
  assert.equal(result.candidates.length, 1);
  assert.equal(old.description, '');
  assert.equal(old.deleted, false);
  assert.equal(h.requests.length, 0);
});

test('setup installs one hourly trigger, does not delete content, and refuses to sweep before activation', () => {
  const h = harness();
  delete h.settings.PHOTOBOOTH_RETENTION_ENABLED;
  h.mark(h.folder('old', 'PB001_00000001'), 40);
  assert.equal(h.context.cleanupPhotoRetention().enabled, false);
  h.context.setupPhotoRetention();
  h.context.setupPhotoRetention();
  assert.equal(h.triggers.length, 1);
  assert.equal(h.settings.PHOTOBOOTH_RETENTION_ENABLED, 'true');
  assert.equal(h.requests.filter(r => r.method === 'delete').length, 0);
});

test('expired folders reject uploads and invalid tokens never reach cleanup', () => {
  const h = harness();
  h.mark(h.folder('expired', 'PB001_00000001'), 31);
  assert.throws(() => h.context.uploadTransactionFile_({ folder_id: 'expired', transaction_id: 'PB001_00000001',
    relative_path: 'raw/session_001/capture_01.jpg', filename: 'capture_01.jpg', size_bytes: 1,
    md5_checksum: 'a'.repeat(32) }, h.properties), /retention has expired/);
  const response = h.context.doPost({ postData: { contents: JSON.stringify({ action: 'cleanup_retention', token: 'wrong' }) } });
  assert.equal(response.body.code, 401);
  assert.equal(h.requests.length, 0);
});

test('corrupt slot ledgers fail closed before any deletion', () => {
  const h = harness();
  h.mark(h.folder('old', 'PB001_00000001'), 40);
  h.settings.PHOTOBOOTH_POOL_PB001 = '{not-json';
  assert.throws(() => h.context.cleanupPhotoRetention(), /ledger is corrupt/);
  assert.equal(h.requests.length, 0);
});

test('large backlogs are bounded and retain an iterator cursor for the next hourly pass', () => {
  const h = harness();
  for (let number = 1; number <= 105; number += 1) {
    h.mark(h.folder('old-' + number, 'PB001_' + String(number).padStart(8, '0')), 31);
  }
  const result = h.context.cleanupPhotoRetention();
  assert.equal(result.deleted.length, 100);
  assert.equal(h.settings.PHOTOBOOTH_RETENTION_CURSOR, '100');
});

test('a stale enabled flag without an owning-account clock never acknowledges active retention', () => {
  const h = harness();
  h.triggers.length = 0;
  const folder = h.folder('claimed', 'PB001_00000001');
  const result = h.context.registerRetention_({folder_id: folder.id,
    transaction_id: folder.name, started_at: new ClockDate().toISOString()}, h.properties);
  assert.equal(result.retention_enabled, false);
  assert.equal(result.retention_state, 'TRIGGER_MISSING');
  assert.equal(h.requests.length, 0);
});

test('setup repairs a same-name non-clock trigger without touching unrelated triggers or photos', () => {
  const h = harness();
  h.triggers.length = 0;
  h.triggers.push({getHandlerFunction: () => 'cleanupPhotoRetention', getEventType: () => 'ON_OPEN'});
  const unrelated = {getHandlerFunction: () => 'otherJob', getEventType: () => 'CLOCK'};
  h.triggers.push(unrelated);
  h.context.setupPhotoRetention();
  h.context.setupPhotoRetention();
  const own = h.triggers.filter(t => t.getHandlerFunction() === 'cleanupPhotoRetention');
  assert.equal(own.length, 1);
  assert.equal(own[0].getEventType(), 'CLOCK');
  assert.ok(h.triggers.includes(unrelated));
  assert.equal(h.requests.filter(r => r.method === 'delete').length, 0);
});

test('authenticated retention status only reads activation and Drive metadata, never content or configuration', () => {
  const h = harness();
  const before = JSON.stringify(h.settings);
  const result = h.context.doPost({postData: {contents: JSON.stringify({
    action: 'retention_status', token: 'fixture-token'})}}).body;
  assert.equal(result.ok, true);
  assert.equal(result.retention_status.state, 'READY');
  assert.equal(result.retention_status.clock_trigger_count, 1);
  assert.equal(result.retention_status.drive_api_accessible, true);
  assert.equal(JSON.stringify(h.settings), before);
  assert.deepEqual(h.requests, [{id: 'booth-parent', method: 'get'}]);
  assert.equal(h.triggers.length, 1);
  assert.doesNotMatch(JSON.stringify(result), /fixture-token|booth-parent|fixture-oauth/);
});

test('status distinguishes setup, missing and duplicate clocks without installing or sweeping', () => {
  for (const [enabled, count, state] of [[false, 1, 'SETUP_REQUIRED'], [true, 0, 'TRIGGER_MISSING'],
    [true, 2, 'DUPLICATE_TRIGGERS']]) {
    const h = harness();
    h.settings.PHOTOBOOTH_RETENTION_ENABLED = String(enabled);
    const trigger = h.triggers[0]; h.triggers.length = 0;
    for (let n = 0; n < count; n++) h.triggers.push(trigger);
    const before = JSON.stringify(h.settings);
    const result = h.context.inspectPhotoRetention_(h.properties);
    assert.equal(result.state, state);
    assert.equal(result.clock_trigger_count, count);
    assert.equal(h.triggers.length, count);
    assert.equal(JSON.stringify(h.settings), before);
    assert.ok(h.requests.every(r => r.method === 'get'));
  }
});

test('status rejects invalid tokens before even a Drive metadata read', () => {
  const h = harness();
  const result = h.context.doPost({postData: {contents: JSON.stringify({
    action: 'retention_status', token: 'wrong'})}}).body;
  assert.equal(result.ok, false);
  assert.equal(result.code, 401);
  assert.equal(h.requests.length, 0);
});

test('status reports Drive and trigger permission failures without echoing raw account errors', () => {
  const h = harness();
  h.context.UrlFetchApp.fetch = () => { throw Error('fixture-private-url-token'); };
  assert.equal(h.context.inspectPhotoRetention_(h.properties).state, 'DRIVE_API_UNAVAILABLE');
  h.context.ScriptApp.getProjectTriggers = () => { throw Error('fixture-private-owner'); };
  const result = h.context.inspectPhotoRetention_(h.properties);
  assert.equal(result.state, 'TRIGGER_ACCESS_REQUIRED');
  assert.equal(result.clock_trigger_count, null);
  assert.doesNotMatch(JSON.stringify(result), /fixture-private/);
});

test('setup repairs duplicate own clocks, leaves other tasks alone and never deletes photos', () => {
  const h = harness();
  h.triggers.push(h.triggers[0]);
  // Distinct trigger instances, as returned by Apps Script.
  h.triggers[1] = {getHandlerFunction: () => 'cleanupPhotoRetention', getEventType: () => 'CLOCK'};
  h.triggers.push({getHandlerFunction: () => 'otherJob', getEventType: () => 'CLOCK'});
  h.context.setupPhotoRetention();
  assert.equal(h.triggers.filter(t => t.getHandlerFunction() === 'cleanupPhotoRetention').length, 1);
  assert.equal(h.triggers.filter(t => t.getHandlerFunction() === 'otherJob').length, 1);
  assert.ok(h.requests.every(r => r.method === 'get'));
});

function storageHarness() {
  const h = harness(); h.context.setupBoothStorage();
  h.post = (action, body = {}) => h.context.doPost({ postData: { contents: JSON.stringify({action,
    storage_layout: 2, booth_id: 'PB001V2S2', token: 'fixture-token', ...body}) } }).body;
  h.claim = {transaction_id: 'PB001V2S2_00000001', claim_token: 'a'.repeat(32)};
  h.bind = () => h.post('bind_transaction', {...h.claim, started_at: new ClockDate(NOW-2*DAY).toISOString(), session_count: 2});
  return h;
}
test('layout 2 creates named siblings, separate booths, 25 truly empty reserves; retry is idempotent', () => {
  const h = storageHarness(), slots = Array.from({length:25}, (_, i) => ({transaction_id:'PB001V2S2_'+String(i+1).padStart(8,'0'), claim_token:'a'.repeat(32)}));
  const first = h.post('reserve_transactions', {slots}); assert.equal(first.ok, true); assert.equal(first.slots.length,25);
  const again = h.post('reserve_transactions', {slots}); assert.equal(again.slots[0].folder_id,first.slots[0].folder_id);
  const p1 = h.context.storagePhotoFolder_(h.properties,'PB001V2S2',false);
  for (const tx of p1.children.filter(f => /^[0-9]{8}$/.test(f.name))) { assert.equal(tx.children.length,0); assert.equal(tx.files.length,0); }
  const second = h.post('reserve_transactions',{booth_id:'PB002V2S2', slots:[{...h.claim,transaction_id:'PB002V2S2_00000001'}]});
  assert.equal(second.ok,true); assert.notEqual(second.slots[0].folder_id,first.slots[0].folder_id);
  assert.equal(h.settings.DRIVE_FOLDER_ID,'booth-parent');
});
test('offline bind uses original deadline, session hierarchy and safe manifest; conflicts never reuse a folder', () => {
  const h = storageHarness(), first = h.bind(); assert.equal(first.ok,true);
  const parent = h.context.storagePhotoFolder_(h.properties,'PB001V2S2',false), tx = parent.children.find(f => f.name === '00000001');
  assert.deepEqual(tx.children.map(f => f.name),['raw','color','bw']);
  assert.equal(parent.name,'Photo');
  assert.equal(parent.getParents().next().name,'PB001');
  assert.equal(tx.shared,true);
  assert.equal(tx.files[0].name,'manifest.json'); assert.doesNotMatch(Buffer.from(tx.files[0].bytes).toString(),/claim_token|claim_key/);
  const expiry = JSON.parse(tx.description).expires_at;
  assert.equal(h.post('bind_transaction',{...h.claim,session_count:2,started_at:new ClockDate().toISOString()}).folder_id,first.folder_id);
  assert.equal(JSON.parse(tx.description).expires_at,expiry);
  assert.equal(h.post('bind_transaction',{...h.claim,claim_token:'b'.repeat(32),session_count:2,started_at:new ClockDate().toISOString()}).code,409);
  assert.equal(h.post('reserve_transactions',{slots:[h.claim]}).code,409);
});
test('layout 2 scoped upload verifies bytes and cannot upload through old or legacy paths', () => {
  const h = storageHarness(), bound=h.bind(), bytes=Buffer.from('fixture image'), md5=crypto.createHash('md5').update(bytes).digest('hex');
  const payload={folder_id:bound.folder_id,transaction_id:h.claim.transaction_id,relative_path:'raw/session_001_capture.jpg',filename:'session_001_capture.jpg',size_bytes:bytes.length,md5_checksum:md5,image_base64:bytes.toString('base64')};
  assert.equal(h.post('upload_file',payload).ok,true); assert.equal(h.post('upload_file',payload).ok,true);
  assert.equal(h.post('upload_file',{...payload,relative_path:'Photo/01/old/capture.jpg'}).code,400);
  assert.equal(h.post('upload_file',{...payload,relative_path:'raw/session_001/capture.jpg'}).code,400);
  assert.equal(h.post('upload_file',{...payload,booth_id:'PB002V2S2'}).ok,false);
});
test('new-root cleanup keeps unused reserves, all assets and old untouched; legacy parent is excluded', () => {
  const h=storageHarness(); h.bind();
  const p=h.context.storagePhotoFolder_(h.properties,'PB001V2S2',false), tx=p.children.find(f=>f.name==='00000001');
  tx.description=JSON.stringify({...JSON.parse(tx.description), ...h.context.photoRetention_(h.claim.transaction_id,new ClockDate(NOW-31*DAY))}); tx.getDateCreated=()=>new ClockDate();
  p.searchFolders=query=>iterator(p.children.filter(f=>!f.deleted && (!query.includes('createdDate') || f.getDateCreated()<new ClockDate(NOW-30*DAY))));
  const archive=h.folder('excluded','old',tx);
  archive.getFiles=archive.getFolders=()=>{throw Error('Archive was entered');};
  h.mark(h.folder('legacy-expired','PB001_00009999'),40);
  assert.equal(h.context.cleanupPhotoRetention().deleted.length,0); assert.equal(archive.deleted,false);
  tx.children=tx.children.filter(f=>f!==archive);
  assert.deepEqual(Array.from(h.context.cleanupPhotoRetention().deleted),['00000001']);
  assert.equal(h.root.children.find(f=>f.id==='legacy-expired').deleted,false);
});
test('content inventory prunes old before access, chunks are scoped and checksum/version verified', () => {
  const h=storageHarness(); h.bind();
  const globals=h.root.children.find(f=>f.name==='Global_Advertisement'), media=h.file('ad','demo.png',0,globals); media.bytes=Array.from(Buffer.from('hello content'));
  const archive=h.folder('excluded','old',globals); archive.getFiles=archive.getFolders=()=>{throw Error('Archive was entered');};
  const manifest=h.post('asset_manifest'); assert.equal(manifest.ok,true); assert.equal(manifest.files.length,1);
  const f=manifest.files[0], chunk=h.post('asset_chunk',{file_id:f.id,namespace:'Global_Advertisement',offset:2,length:5,md5:f.md5});
  assert.equal(Buffer.from(chunk.data,'base64').toString(),'llo c');
  assert.equal(h.post('asset_chunk',{file_id:f.id,namespace:'Global_Template',offset:0,length:2,md5:f.md5}).code,403);
  assert.equal(h.post('asset_chunk',{file_id:f.id,namespace:'Global_Advertisement',offset:0,length:2,md5:'b'.repeat(32)}).code,409);
  assert.equal(h.post('asset_manifest',{token:'wrong'}).code,401);
});


test('reserved photo numbers are genuinely empty and link-readable; denied sharing never returns READY', () => {
  const h = storageHarness();
  const result = h.post('reserve_transactions', {slots:[h.claim]});
  assert.equal(result.ok,true); assert.equal(result.slots[0].link_verified,true);
  const folder = h.context.DriveApp.getFolderById(result.slots[0].folder_id);
  assert.equal(folder.name,'00000001'); assert.equal(folder.children.length,0); assert.equal(folder.files.length,0);
  folder.getSharingPermission = () => 'edit';
  assert.equal(h.post('reserve_transactions',{slots:[h.claim]}).ok,false);
});
test('repair authenticates an empty legacy reserve and keeps its exact QR folder ID', () => {
  const h=storageHarness(), booth=h.context.storageBoothFolder_(h.properties,'PB001V2S2',true);
  const prior=h.folder('printed-qr','PB001V2S2_00000001',booth);
  prior.description=JSON.stringify({managed_slot:'meong-empty-slot-v2',transaction_id:h.claim.transaction_id,
    claim_key:crypto.createHash('md5').update(h.claim.claim_token).digest('hex')});
  const result=h.bind(); assert.equal(result.ok,true); assert.equal(result.folder_id,'printed-qr');
  assert.equal(prior.name,'00000001'); assert.equal(prior.getParents().next().name,'Photo');
  assert.equal(h.bind().folder_id,'printed-qr');
});
test('interrupted empty-reserve rename retries with the original folder ID', () => {
  const h=storageHarness(), booth=h.context.storageBoothFolder_(h.properties,'PB001V2S2',true);
  const prior=h.folder('interrupted-qr',h.claim.transaction_id,booth);
  prior.description=JSON.stringify({managed_slot:'meong-empty-slot-v2',transaction_id:h.claim.transaction_id,
    claim_key:crypto.createHash('md5').update(h.claim.claim_token).digest('hex')});
  let fail=true;prior.setName=function(name){if(fail){fail=false;throw Error('transient rename');}this.name=name;};
  assert.equal(h.bind().ok,false);assert.equal(prior.getParents().next().name,'Photo');
  const result=h.bind();assert.equal(result.ok,true);assert.equal(result.folder_id,'interrupted-qr');
  assert.equal(prior.name,'00000001');
});
test('an unrelated numbered folder is neither overwritten nor link-shared', () => {
  const h=storageHarness(), photo=h.context.storagePhotoFolder_(h.properties,'PB001V2S2',true);
  const foreign=h.folder('foreign-number','00000001',photo);
  assert.equal(h.bind().ok,false);assert.equal(foreign.description,'');assert.equal(foreign.shared,undefined);
  assert.equal(foreign.children.length,0);
});
