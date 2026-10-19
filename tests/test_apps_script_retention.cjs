/** Run the actual Code.gs functions with a scoped, in-memory Drive service.
 * No Google account, credentials, network request, or customer photo is used.
 * Execute with: node --test tests/test_apps_script_retention.cjs
 */
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
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
  const objects = new Map(), requests = [], triggers = [], settings = {
    DRIVE_FOLDER_ID: 'booth-parent', UPLOAD_TOKEN: 'fixture-token', PHOTOBOOTH_RETENTION_ENABLED: 'true',
  };
  const properties = { getProperty: key => settings[key] || null,
    setProperty: (key, value) => { settings[key] = value; },
    deleteProperty: key => { delete settings[key]; }, getProperties: () => ({ ...settings }) };
  let deleteStatus = 204;
  function object(id, name, parent = 'booth-parent', imageAge = null) {
    const entry = { id, name, parent, description: '', deleted: false, children: [], files: [],
      getId() { return this.id; }, getName() { return this.name; },
      getDescription() { return this.description; }, setDescription(value) { this.description = value; },
      isTrashed() { return false; },
      getDateCreated() { return new ClockDate(NOW - (imageAge === null ? 200 : imageAge) * DAY); },
      getParents() { return iterator(this.parent ? [objects.get(this.parent)] : []); },
      getFiles() { return iterator(this.files.filter(file => !file.deleted)); },
      getFolders() { return iterator(this.children.filter(folder => !folder.deleted)); },
      searchFolders(query) { assert.match(query, /createdDate <=/); return this.getFolders(); },
      searchFiles(query) { assert.match(query, /createdDate <=/); return this.getFiles(); },
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
    DriveApp: { getFolderById(id) { if (!objects.has(id)) throw Error('Unknown folder'); return objects.get(id); },
      continueFolderIterator: () => iterator(root.children) },
    ScriptApp: { getOAuthToken: () => 'fixture-oauth', getProjectTriggers: () => triggers,
      deleteTrigger(item) { triggers.splice(triggers.indexOf(item), 1); },
      newTrigger(handler) { return { timeBased() { return this; }, everyHours(hours) {
        assert.equal(hours, 1); return this;
      }, create() { const trigger = { getHandlerFunction: () => handler }; triggers.push(trigger); return trigger; } }; } },
    UrlFetchApp: { fetch(url, options) {
      const id = decodeURIComponent(new URL(url).pathname.split('/').pop());
      requests.push({ id, method: options.method });
      if (options.method === 'delete' && deleteStatus === 204) objects.get(id).deleted = true;
      return { getResponseCode: () => options.method === 'get' ? 200 : deleteStatus,
        getContentText: () => JSON.stringify({ id, mimeType: 'application/vnd.google-apps.folder' }) };
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
