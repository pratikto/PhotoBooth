// PhotoBooth source file
// Apps Script backend for Drive folder preparation, assignment, and retry-safe uploads.

/**
 * Meongs Photo Booth Drive Web App.
 *
 * Keep the existing Script Properties:
 *   UPLOAD_TOKEN    - must match photobooth/local_settings.py
 *   DRIVE_FOLDER_ID - parent folder for booth transaction folders
 *
 * Deploy this project as a Web App (execute as the deploying account, access
 * available to anyone). The old upload-only request remains supported when
 * `action` is omitted. New booth clients use ensure_folder_pool, assign_slot,
 * and upload_file actions. Layout 2 adds reserve_transactions/bind_transaction
 * and asset_manifest/asset_chunk after manual setupBoothStorage; keep the same
 * token/deployment. PHOTOBOOTH_ROOT_ID and GLOBAL_ADVERTISEMENT_ID/
 * GLOBAL_TEMPLATE_ID identify named siblings, never an archive parent.
 */

const PHOTO_RETENTION_DAYS = 30;
const PHOTO_RETENTION_MARKER = "meongs-photobooth-retention-v1";
const PHOTO_RETENTION_TRIGGER = "cleanupPhotoRetention";
const PHOTO_RETENTION_ENABLED = "PHOTOBOOTH_RETENTION_ENABLED";
const LEGACY_PHOTO_NAME = /^photo_[0-9]{8}_[0-9]{6}_[0-9]{6}\.jpg$/;

/**
 * Provide a lightweight health check so an operator can confirm the deployed Web App
 * responds at its /exec URL.
 */
function doGet() {
  return jsonResponse_({ ok: true, service: "meongs-photobooth-drive" });
}

/**
 * Parse one JSON request, authenticate it with the shared upload token, dispatch the
 * requested action, and return a consistent JSON success or error response.
 */
function doPost(event) {
  try {
    const body = JSON.parse(event && event.postData && event.postData.contents || "{}");
    let properties = PropertiesService.getScriptProperties();
    const expectedToken = properties.getProperty("UPLOAD_TOKEN") || "";
    // Authenticate every action before it can create or modify Drive content.
    if (!body.token || !expectedToken || body.token !== expectedToken) {
      throw apiError_("Invalid upload token.", 401);
    }

    // Requests without an action keep using the original one-file upload behavior.
    const action = body.action || "legacy_upload";
    if (body.storage_layout === 2 && ["upload_file", "register_retention", "retention_status"].includes(action)) {
      const boothId = validateStorageBooth_(body.booth_id || String(body.transaction_id || "").split("_")[0]);
      properties = storageProperties_(properties, storagePhotoFolder_(properties, boothId, false), boothId);
    }
    let result;
    if (action === "reserve_transactions") {
      result = withPhotoLock_(function () { return reserveStorageTransactions_(body, properties); });
    } else if (action === "bind_transaction") {
      result = withPhotoLock_(function () { return bindStorageTransaction_(body, properties); });
    } else if (action === "asset_manifest") {
      result = storageAssetManifest_(body, properties);
    } else if (action === "asset_chunk") {
      result = storageAssetChunk_(body, properties);
    } else if (action === "ensure_folder_pool") {
      result = ensureFolderPool_(body, properties);
    } else if (action === "assign_slot") {
      result = assignSlot_(body, properties);
    } else if (action === "upload_file") {
      result = withPhotoLock_(function () { return uploadTransactionFile_(body, properties); });
    } else if (action === "register_retention") {
      result = withPhotoLock_(function () { return registerRetention_(body, properties); });
    } else if (action === "retention_status") {
      result = { retention_status: inspectPhotoRetention_(properties) };
    } else if (action === "cleanup_retention") {
      result = cleanupPhotoRetention();
    } else if (action === "legacy_upload") {
      result = legacyUpload_(body, properties);
    } else {
      throw apiError_("Unsupported action: " + action, 400);
    }
    return jsonResponse_(Object.assign({ ok: true }, result));
  } catch (error) {
    return jsonResponse_({
      ok: false,
      code: error && error.code || 400,
      error: error && error.message || String(error),
    });
  }
}

// Layout 2 deliberately uses the existing upload/retention engine with a scoped
// parent. Folder descriptions hold ownership, not an unbounded Script Property.
const STORAGE_SLOT_MARKER = "meong-empty-slot-v2";
function validateStorageBooth_(value) {
  const id = String(value || "");
  if (!/^PB[0-9]+(?:V2(?:S2)?)?$/.test(id)) throw apiError_("Invalid booth identity.", 400);
  return id;
}
function physicalBooth_(value) { return validateStorageBooth_(value).replace(/V2(?:S2)?$/, ""); }
function storageFolder_(id) {
  if (!id) throw apiError_("Run setupBoothStorage in the Apps Script editor first.", 409);
  const folder = DriveApp.getFolderById(String(id));
  // Check every ancestor's name before accessing its parent. Never enter old.
  let current = folder, depth = 0;
  while (current) {
    if (current.getName().toLowerCase() === "old" || current.isTrashed() || depth++ > 20)
      throw apiError_("Archive or invalid storage root is excluded.", 409);
    const parents = current.getParents();
    current = parents.hasNext() ? parents.next() : null;
    if (parents.hasNext()) throw apiError_("Ambiguous storage ancestry.", 409);
  }
  return folder;
}
function uniqueStorageChild_(parent, name, create) {
  const found = parent.getFoldersByName(name);
  let child = found.hasNext() ? found.next() : null;
  if (found.hasNext()) throw apiError_("Duplicate managed folder names; operator review required.", 409);
  if (!child && create) child = parent.createFolder(name);
  return child;
}
/** Manual setup only. Does not scan/migrate old or alter the legacy upload root. */
function setupBoothStorage() {
  const p = PropertiesService.getScriptProperties();
  const root = p.getProperty("CONTENT_ROOT_ID") ? storageFolder_(p.getProperty("CONTENT_ROOT_ID")) : DriveApp.getRootFolder();
  [["PHOTOBOOTH_ROOT_ID", "Photobooth"], ["GLOBAL_ADVERTISEMENT_ID", "Global_Advertisement"],
    ["GLOBAL_TEMPLATE_ID", "Global_Template"]].forEach(function (entry) {
    const folder = p.getProperty(entry[0]) ? storageFolder_(p.getProperty(entry[0])) : uniqueStorageChild_(root, entry[1], true);
    if (folder.getName() !== entry[1] || !hasParent_(folder, root)) throw apiError_("Storage roots must be named siblings.", 409);
    p.setProperty(entry[0], folder.getId());
  });
  return { storage_layout: 2, configured: true };
}
function storageBoothFolder_(p, booth, create) {
  const physical = physicalBooth_(booth), root = storageFolder_(p.getProperty("PHOTOBOOTH_ROOT_ID"));
  if (root.getName() !== "Photobooth") throw apiError_("The active booth root must be Photobooth.", 409);
  const folder = uniqueStorageChild_(root, physical, create);
  if (!folder) throw apiError_("This booth is not prepared yet.", 409);
  if (create) {
    const local = uniqueStorageChild_(folder, "Local", true);
    uniqueStorageChild_(local, "Advertisement", true); uniqueStorageChild_(local, "Template", true);
    p.setProperty("PHOTOBOOTH_ROOT_" + physical, folder.getId());
  }
  return folder;
}
// Customer photos are numbered directly beneath the physical booth's Photo.
function storagePhotoFolder_(p, booth, create) {
  const parent = storageBoothFolder_(p, booth, create);
  const photo = uniqueStorageChild_(parent, "Photo", create);
  if (!photo) throw apiError_("Photo storage has not been prepared.", 409);
  return photo;
}
function storageLinkReady_(folder) {
  folder.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);
  if (folder.getSharingAccess() !== DriveApp.Access.ANYONE_WITH_LINK
      || folder.getSharingPermission() !== DriveApp.Permission.VIEW)
    throw apiError_("Download link must be Anyone with the link / Viewer.", 409);
}
function storageProperties_(p, parent, booth) {
  const cursor = "PHOTOBOOTH_RETENTION_CURSOR_" + physicalBooth_(booth);
  return { getProperty: function (key) { return key === "STORAGE_LAYOUT" ? "2" : key === "DRIVE_FOLDER_ID" ? parent.getId() : p.getProperty(key === "PHOTOBOOTH_RETENTION_CURSOR" ? cursor : key); },
    setProperty: function (key, value) { p.setProperty(key === "PHOTOBOOTH_RETENTION_CURSOR" ? cursor : key, value); },
    deleteProperty: function (key) { p.deleteProperty(key === "PHOTOBOOTH_RETENTION_CURSOR" ? cursor : key); },
    getProperties: function () { return p.getProperties(); } };
}
function storageClaim_(body, booth) {
  const tx = validateTransactionId_(body.transaction_id, booth);
  if (!/^[a-f0-9]{32}$/.test(String(body.claim_token || ""))) throw apiError_("Invalid transaction claim.", 400);
  return { transaction_id: tx, claim_key: md5Hex_(Utilities.newBlob(body.claim_token).getBytes()) };
}
function storageTransaction_(parent, claim, create) {
  const number = claim.transaction_id.split("_").pop();
  let folder = uniqueStorageChild_(parent, number, false) || uniqueStorageChild_(parent, claim.transaction_id, false);
  if (!folder) {
    // Recover only this exact authenticated empty reserve, preserving printed URLs.
    const parents = parent.getParents();
    const booth = parents.hasNext() ? parents.next() : null;
    const prior = booth && uniqueStorageChild_(booth, claim.transaction_id, false);
    if (prior) {
      let owner;
      try { owner = JSON.parse(prior.getDescription()); } catch (_) { owner = {}; }
      if (owner.transaction_id !== claim.transaction_id || owner.claim_key !== claim.claim_key
          || owner.managed_slot !== STORAGE_SLOT_MARKER || prior.getFiles().hasNext()
          || prior.getFolders().hasNext())
        throw apiError_("Existing transaction needs operator review; no data was moved.", 409);
      prior.moveTo(parent); folder = prior;
    }
  }
  if (!folder && create) {
    folder = parent.createFolder(number);
    folder.setDescription(JSON.stringify({ managed_slot: STORAGE_SLOT_MARKER, transaction_id: claim.transaction_id, claim_key: claim.claim_key }));
  }
  if (!folder) throw apiError_("Transaction folder is missing.", 409);
  let owner;
  try { owner = JSON.parse(folder.getDescription()); } catch (_) { owner = {}; }
  if (owner.transaction_id !== claim.transaction_id || owner.claim_key !== claim.claim_key
      || (owner.managed_slot !== STORAGE_SLOT_MARKER && owner.storage_layout !== 2))
    throw apiError_("Transaction ownership conflict; folder was not reused.", 409);
  if (folder.getName() !== number) folder.setName(number);
  return folder;
}
function reserveStorageTransactions_(body, p) {
  const booth = validateStorageBooth_(body.booth_id);
  if (!Array.isArray(body.slots) || body.slots.length > 100) throw apiError_("Invalid reserve list.", 400);
  const claims = body.slots.map(function (slot) { return storageClaim_(slot, booth); });
  const parent = storagePhotoFolder_(p, booth, true);
  const slots = claims.map(function (claim) {
    const folder = storageTransaction_(parent, claim, true);
    if (folder.getFiles().hasNext() || folder.getFolders().hasNext()
        || JSON.parse(folder.getDescription()).managed_slot !== STORAGE_SLOT_MARKER)
      throw apiError_("A reserve must be genuinely empty and unclaimed.", 409);
    storageLinkReady_(folder);
    return {transaction_id: claim.transaction_id, folder_id: folder.getId(), folder_url: folder.getUrl(), status: "READY", photo_number_layout: 1, link_verified: true};
  });
  return {storage_layout: 2, slots: slots};
}
function bindStorageTransaction_(body, p) {
  const booth = validateStorageBooth_(body.booth_id), claim = storageClaim_(body, booth);
  const started = new Date(body.started_at), count = Number(body.session_count);
  if (!Number.isFinite(started.getTime()) || started.getTime() > Date.now() + 300000
      || !Number.isInteger(count) || count < 1 || count > 99) throw apiError_("Invalid original transaction metadata.", 400);
  const parent = storagePhotoFolder_(p, booth, true), folder = storageTransaction_(parent, claim, true);
  const existing = readPhotoRetention_(folder.getDescription(), claim.transaction_id);
  const policy = Object.assign({}, existing || {}, photoRetention_(claim.transaction_id,
    existing && new Date(existing.started_at) < started ? existing.started_at : started),
    {storage_layout: 2, claim_key: claim.claim_key});
  folder.setDescription(JSON.stringify(policy));
  if (new Date(policy.expires_at).getTime() <= Date.now()) throw apiError_("Photo delivery has expired.", 410);
  if (new Date(policy.expires_at).getTime() > Date.now()) {
    storageLinkReady_(folder);
    ["raw", "color", "bw"].forEach(function (kind) { uniqueStorageChild_(folder, kind, true); });
    // Write once, without the private claim token. Retry never overwrites photos.
    if (!folder.getFilesByName("manifest.json").hasNext()) folder.createFile(Utilities.newBlob(JSON.stringify({
      storage_layout: 2, transaction_id: claim.transaction_id, booth_id: physicalBooth_(booth),
      started_at: policy.started_at, session_count: count }), "application/json", "manifest.json"));
  }
  return {storage_layout: 2, photo_number_layout: 1, link_verified: true, transaction_id: claim.transaction_id, folder_id: folder.getId(), folder_url: folder.getUrl()};
}

function storageAssetRoots_(body, p) {
  const booth = validateStorageBooth_(body.booth_id), parent = storageBoothFolder_(p, booth, false);
  const local = uniqueStorageChild_(parent, "Local", false);
  const roots = { Global_Advertisement: storageFolder_(p.getProperty("GLOBAL_ADVERTISEMENT_ID")),
    Global_Template: storageFolder_(p.getProperty("GLOBAL_TEMPLATE_ID")),
    "Local/Advertisement": local && uniqueStorageChild_(local, "Advertisement", false),
    "Local/Template": local && uniqueStorageChild_(local, "Template", false) };
  const parents = storageFolder_(p.getProperty("PHOTOBOOTH_ROOT_ID")).getParents();
  if (!parents.hasNext()) throw apiError_("Managed roots require one common parent.", 409);
  const common = parents.next();
  ["Global_Advertisement", "Global_Template"].forEach(function (key) {
    if (roots[key].getName() !== key || !hasParent_(roots[key], common))
      throw apiError_("Global content roots must be named siblings of Photobooth.", 409);
  });
  return roots;
}
function storageFileMeta_(id) {
  const response = driveRetentionRequest_("get", id, "fields=id,name,size,md5Checksum,mimeType,modifiedTime,parents,trashed");
  if (response.getResponseCode() !== 200) throw apiError_("Content metadata is unavailable.", 503);
  return JSON.parse(response.getContentText());
}
function storageAssetManifest_(body, p) {
  const roots = storageAssetRoots_(body, p), files = [], deadline = Date.now() + 40000;
  function visit(folder, prefix, depth) {
    if (depth > 6 || Date.now() > deadline) throw apiError_("Content inventory exceeds this request budget.", 413);
    const items = folder.getFiles();
    while (items.hasNext()) {
      const file = items.next(), name = file.getName();
      if (name.toLowerCase() === "old") continue;
      validateRelativePath_(prefix + "/" + name, name);
      if (files.length >= 500) throw apiError_("Content inventory exceeds 500 files.", 413);
      const meta = storageFileMeta_(file.getId());
      if (!/^[a-f0-9]{32}$/i.test(meta.md5Checksum || "") || !Number.isSafeInteger(Number(meta.size)))
        throw apiError_("Only ordinary downloadable content files are supported.", 409);
      files.push({id: meta.id, path: prefix + "/" + name, size: Number(meta.size), md5: meta.md5Checksum, mime_type: meta.mimeType});
    }
    const children = folder.getFolders();
    while (children.hasNext()) {
      const child = children.next(), name = child.getName();
      if (name.toLowerCase() === "old") continue; // Prune BEFORE any descendant access.
      validateRelativePath_(prefix + "/" + name, name);
      visit(child, prefix + "/" + name, depth + 1);
    }
  }
  Object.keys(roots).forEach(function (key) { if (roots[key]) visit(roots[key], key, 0); });
  files.sort(function (a, b) { return a.path.localeCompare(b.path); });
  if (new Set(files.map(function (f) { return f.path.toLowerCase(); })).size !== files.length)
    throw apiError_("Duplicate content paths are not supported on Windows.", 409);
  return {storage_layout: 2, files: files, version: md5Hex_(Utilities.newBlob(JSON.stringify(files)).getBytes())};
}
function storageAssetChunk_(body, p) {
  const roots = storageAssetRoots_(body, p), namespace = String(body.namespace || ""), root = roots[namespace];
  if (!root) throw apiError_("Unknown content namespace.", 400);
  const meta = storageFileMeta_(String(body.file_id || ""));
  if (meta.trashed || !meta.parents || meta.parents.length !== 1 || meta.name.toLowerCase() === "old") throw apiError_("Invalid content file.", 409);
  let parent = storageFolder_(meta.parents[0]), found = false;
  for (let depth = 0; depth <= 6; depth++) {
    if (parent.getId() === root.getId()) { found = true; break; }
    const ancestors = parent.getParents();
    if (!ancestors.hasNext()) break;
    parent = ancestors.next();
    if (parent.getName().toLowerCase() === "old") break;
  }
  if (!found) throw apiError_("Content file is outside the allowed source.", 403);
  const offset = Number(body.offset), length = Math.min(Number(body.length), 512 * 1024), size = Number(meta.size);
  if (!Number.isSafeInteger(offset) || !Number.isSafeInteger(length) || offset < 0 || offset >= size || length < 1
      || body.md5 !== meta.md5Checksum) throw apiError_("Invalid or changed content chunk.", 409);
  const last = Math.min(size - 1, offset + length - 1);
  const response = UrlFetchApp.fetch("https://www.googleapis.com/drive/v3/files/" + encodeURIComponent(meta.id) + "?alt=media&supportsAllDrives=true", {
    headers: {Authorization: "Bearer " + ScriptApp.getOAuthToken(), Range: "bytes=" + offset + "-" + last}, muteHttpExceptions: true });
  const bytes = response.getBlob().getBytes();
  if (![200, 206].includes(response.getResponseCode()) || bytes.length !== last - offset + 1)
    throw apiError_("Content range could not be verified.", 503);
  return {offset: offset, size: size, md5: meta.md5Checksum, data: Utilities.base64Encode(bytes)};
}

/**
 * Validate existing ready slots and create enough empty, link-shareable transaction
 * folders to reach the requested pool size. A script lock protects sequence allocation
 * from simultaneous booth requests.
 */
function ensureFolderPool_(body, properties) {
  const boothId = validateBoothId_(body.booth_id);
  const targetReady = Math.max(1, Math.min(100, Number(body.target_ready) || 25));
  const parentId = properties.getProperty("DRIVE_FOLDER_ID") || "";
  if (!parentId) throw apiError_("Set DRIVE_FOLDER_ID in Script Properties.", 400);

  const lock = LockService.getScriptLock();
  lock.waitLock(30000);
  try {
    const key = poolPropertyKey_(boothId);
    const pool = readPool_(properties, key);
    const parent = DriveApp.getFolderById(parentId);
    let readyCount = 0;

    pool.slots.forEach(function (slot) {
      if (slot.status !== "READY") return;
      const validation = validateReadyFolder_(slot, parent);
      slot.verified = validation.verified;
      slot.issue = validation.issue || null;
      if (validation.verified) {
        readyCount += 1;
      } else {
        slot.status = "ACTION_REQUIRED";
      }
    });

    // Persist the next sequence before another request can allocate the same ID.
    while (readyCount < targetReady) {
      const sequence = Number(pool.next_sequence) || 1;
      pool.next_sequence = sequence + 1;
      // Folder names are final transaction IDs from creation; assignment never renames them.
      const transactionId = boothId + "_" + String(sequence).padStart(8, "0");
      // Never reuse a name that may belong to a transaction outside this ledger.
      if (parent.getFoldersByName(transactionId).hasNext()) {
        writePool_(properties, key, pool);
        continue;
      }

      const folder = parent.createFolder(transactionId);
      // The customer opens this folder from a QR code, so its link must be viewable without sign-in.
      folder.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);
      const slot = {
        folder_id: folder.getId(),
        folder_url: folder.getUrl(),
        slot_key: transactionId,
        status: "READY",
        folder_name: transactionId,
        transaction_id: transactionId,
        verified: folder.getSharingAccess() === DriveApp.Access.ANYONE_WITH_LINK,
        issue: null,
      };
      if (!slot.verified) {
        slot.status = "ACTION_REQUIRED";
        slot.issue = "Folder sharing could not be verified as Anyone with the link.";
      } else {
        readyCount += 1;
      }
      pool.slots.push(slot);
      writePool_(properties, key, pool);
    }

    return { slots: pool.slots };
  } finally {
    lock.releaseLock();
  }
}

/**
 * Remove a ready slot from the available pool after a transaction claims it. The Drive
 * folder already has its final ID, so this action deliberately does not rename it.
 */
function assignSlot_(body, properties) {
  const boothId = validateBoothId_(body.booth_id);
  const transactionId = validateTransactionId_(body.transaction_id, boothId);
  const lock = LockService.getScriptLock();
  lock.waitLock(30000);
  try {
    const key = poolPropertyKey_(boothId);
    const pool = readPool_(properties, key);
    const slot = pool.slots.find(function (item) {
      return item.folder_id === body.folder_id;
    });
    if (!slot) {
      // A retry can arrive after the slot was already removed from the ready pool.
      // Accept it only if the folder already has this final ID under the configured parent.
      const assignedFolder = DriveApp.getFolderById(String(body.folder_id || ""));
      if (assignedFolder.getName() === transactionId && hasParent_(assignedFolder, DriveApp.getFolderById(properties.getProperty("DRIVE_FOLDER_ID")))) {
        return { slot: { folder_id: assignedFolder.getId(), transaction_id: transactionId, status: "ASSIGNED" } };
      }
      throw apiError_("Drive slot does not match the assigned transaction.", 409);
    }
    if (slot.transaction_id !== transactionId || slot.slot_key !== body.slot_key) {
      throw apiError_("Drive slot does not match the assigned transaction.", 409);
    }
    if (slot.status !== "READY") throw apiError_("Drive slot is not ready.", 409);
    // Removing the slot makes it unavailable to another transaction; its Drive name is unchanged.
    pool.slots = pool.slots.filter(function (item) { return item.folder_id !== slot.folder_id; });
    writePool_(properties, key, pool);
    return { slot: Object.assign({}, slot, { status: "ASSIGNED" }) };
  } finally {
    lock.releaseLock();
  }
}

/**
 * Validate the transaction folder, relative path, file size, and MD5 before creating or
 * verifying the file. Repeated identical requests are safe and do not create duplicate
 * files.
 */
function uploadTransactionFile_(body, properties) {
  const boothId = validateBoothId_(body.transaction_id && body.transaction_id.split("_")[0]);
  const transactionId = validateTransactionId_(body.transaction_id, boothId);
  const folderId = String(body.folder_id || "");
  const relativePath = validateRelativePath_(body.relative_path, body.filename);
  if (body.storage_layout === 2 && !/^(raw|color|bw)\/session_[0-9]{3}_[^/]+\.(jpg|jpeg|png)$/i.test(relativePath))
    throw apiError_("Layout 2 uploads must use raw,color,bw/session_NNN_filename.", 400);
  const expectedSize = Number(body.size_bytes);
  const expectedMd5 = String(body.md5_checksum || "").toLowerCase();
  if (!Number.isInteger(expectedSize) || expectedSize < 0 || !/^[a-f0-9]{32}$/.test(expectedMd5)) {
    throw apiError_("Upload size or checksum is invalid.", 400);
  }

  const parentId = properties.getProperty("DRIVE_FOLDER_ID") || "";
  if (!parentId) throw apiError_("Set DRIVE_FOLDER_ID in Script Properties.", 400);
  const poolKey = poolPropertyKey_(boothId);
  const pool = readPool_(properties, poolKey);
  const slot = pool.slots.find(function (item) {
    return item.folder_id === folderId && item.transaction_id === transactionId;
  });

  const rootFolder = DriveApp.getFolderById(folderId);
  if (rootFolder.getName() !== (body.storage_layout === 2 ? transactionId.split("_").pop() : transactionId) || !hasParent_(rootFolder, DriveApp.getFolderById(parentId))) {
    throw apiError_("Transaction folder name does not match its ID.", 409);
  }
  if (body.storage_layout === 2 && !(readPhotoRetention_(rootFolder.getDescription(), transactionId) || {}).storage_layout)
    throw apiError_("Bind the transaction before uploading images.", 409);
  // New Python clients register the transaction's original time first. Older
  // clients are adopted from their oldest photo, never an empty slot's age.
  const retention = readPhotoRetention_(rootFolder.getDescription(), transactionId)
    || ensureFolderRetention_(rootFolder, transactionId, oldestTransactionPhoto_(rootFolder, 0) || new Date());
  if (new Date(retention.expires_at).getTime() <= Date.now()) {
    throw apiError_("This transaction's 30-day Drive retention has expired.", 410);
  }
  if (slot) {
    if (slot.status !== "READY") throw apiError_("Transaction folder is not a ready slot.", 409);
    pool.slots = pool.slots.filter(function (item) { return item.folder_id !== folderId; });
    writePool_(properties, poolKey, pool);
  }

  const pathParts = relativePath.split("/");
  const fileName = pathParts.pop();
  let targetFolder = rootFolder;
  // Re-create the same subfolder hierarchy recorded in the local transaction-relative path.
  pathParts.forEach(function (name) {
    targetFolder = getOrCreateChildFolder_(targetFolder, name);
  });

  // Check the actual decoded bytes, not only the metadata supplied by the Python client.
  const bytes = Utilities.base64Decode(String(body.image_base64 || ""));
  const actualMd5 = md5Hex_(bytes);
  if (bytes.length !== expectedSize || actualMd5 !== expectedMd5) {
    throw apiError_("Uploaded bytes do not match the supplied size or checksum.", 400);
  }

  const existing = targetFolder.getFilesByName(fileName);
  if (existing.hasNext()) {
    // An identical retry returns the existing file; a different file at the same path is a conflict.
    const file = existing.next();
    if (existing.hasNext()) {
      throw apiError_("Multiple files with this path already exist; staff review is required.", 409);
    }
    const existingBytes = file.getBlob().getBytes();
    const existingMd5 = md5Hex_(existingBytes);
    if (existingBytes.length !== expectedSize || existingMd5 !== expectedMd5) {
      throw apiError_("A different file already exists at this transaction path.", 409);
    }
    file.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);
    return { file: fileResponse_(file, existingBytes.length, existingMd5) };
  }

  const mimeType = String(body.mime_type || "application/octet-stream");
  const blob = Utilities.newBlob(bytes, mimeType, fileName);
  const file = targetFolder.createFile(blob);
  // Match the link-sharing behavior used by the QR-based result flow.
  file.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);
  return { file: fileResponse_(file, bytes.length, actualMd5) };
}

/**
 * Preserve the original one-file upload request format for older booth clients that do not
 * send an action field.
 */
function legacyUpload_(body, properties) {
  if (!body.filename || !body.image_base64) {
    throw apiError_("Legacy upload requires filename and image_base64.", 400);
  }
  const parentId = properties.getProperty("DRIVE_FOLDER_ID") || "";
  if (!parentId) throw apiError_("Set DRIVE_FOLDER_ID in Script Properties.", 400);
  const bytes = Utilities.base64Decode(String(body.image_base64));
  const blob = Utilities.newBlob(
    bytes,
    String(body.mime_type || "image/jpeg"),
    String(body.filename),
  );
  const file = DriveApp.getFolderById(parentId).createFile(blob);
  // Every new legacy API upload is owned by this photo backend, even if an old
  // client chose a different filename. Unmarked historical files are adopted
  // only when they match the repository's exact generated filename pattern.
  file.setDescription(JSON.stringify(photoRetention_(String(body.filename), new Date())));
  file.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);
  return {
    file_id: file.getId(),
    file_url: file.getUrl(),
    file_name: file.getName(),
  };
}

/**
 * Check that a candidate slot exists, is not trashed, has the expected final name and
 * parent, is empty, and has the required link-sharing permission.
 */
function validateReadyFolder_(slot, parent) {
  try {
    // A slot is reusable only when it is empty and still has the final ID recorded in the ledger.
    const folder = DriveApp.getFolderById(slot.folder_id);
    if (folder.isTrashed() || folder.getName() !== slot.transaction_id) {
      return { verified: false, issue: "Folder is missing, trashed, or has the wrong name." };
    }
    if (!hasParent_(folder, parent)) return { verified: false, issue: "Folder is outside the configured Drive parent." };
    if (folder.getFiles().hasNext() || folder.getFolders().hasNext()) {
      return { verified: false, issue: "Ready folder is not empty." };
    }
    if (folder.getSharingAccess() !== DriveApp.Access.ANYONE_WITH_LINK) {
      folder.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);
    }
    if (folder.getSharingAccess() !== DriveApp.Access.ANYONE_WITH_LINK) {
      return { verified: false, issue: "Folder sharing could not be verified." };
    }
    slot.folder_url = folder.getUrl();
    slot.folder_name = folder.getName();
    return { verified: true, issue: null };
  } catch (error) {
    return { verified: false, issue: error && error.message || String(error) };
  }
}

/**
 * Check that the configured Drive parent is an immediate parent of this folder. The booth
 * creates transaction folders directly under that parent.
 */
function hasParent_(folder, expectedParent) {
  const parents = folder.getParents();
  // Compare IDs instead of names because Drive folder names are not globally unique.
  while (parents.hasNext()) {
    if (parents.next().getId() === expectedParent.getId()) return true;
  }
  return false;
}

/**
 * Find or create one child folder while walking the transaction-relative path structure.
 */
function getOrCreateChildFolder_(parent, name) {
  const matches = parent.getFoldersByName(name);
  if (matches.hasNext()) {
    const folder = matches.next();
    if (matches.hasNext()) throw apiError_("Duplicate subfolder exists: " + name, 409);
    return folder;
  }
  return parent.createFolder(name);
}

/**
 * Reject absolute paths, traversal segments, and unsafe file names before creating nested
 * Drive folders or files.
 */
function validateRelativePath_(relativePath, filename) {
  // Normalize Windows separators before checking path segments and matching the leaf filename.
  const path = String(relativePath || "").replace(/\\/g, "/");
  const parts = path.split("/");
  if (!path || parts.length > 12 || parts.some(function (part) {
    return !part || part === "." || part === ".." || part.toLowerCase() === "old" || /[<>:"|?*\u0000-\u001f]/.test(part);
  })) {
    throw apiError_("Upload path is invalid.", 400);
  }
  if (parts[parts.length - 1] !== String(filename || "")) {
    throw apiError_("Upload filename does not match its relative path.", 400);
  }
  return parts.join("/");
}

/**
 * Accept only a safe booth identifier that can be used in folder names and Script Properties
 * keys.
 */
function validateBoothId_(boothId) {
  const value = String(boothId || "");
  if (!/^[A-Za-z0-9]+$/.test(value)) throw apiError_("Booth ID is invalid.", 400);
  return value;
}

/**
 * Ensure a transaction ID uses the expected booth prefix and fixed-width incrementing
 * numeric suffix.
 */
function validateTransactionId_(transactionId, boothId) {
  const value = String(transactionId || "");
  if (!new RegExp("^" + boothId + "_[0-9]{8}$").test(value)) {
    throw apiError_("Transaction ID is invalid.", 400);
  }
  return value;
}

/**
 * Load the booth's slot ledger from Script Properties, returning an empty ledger when none
 * exists and reporting malformed saved data.
 */
function readPool_(properties, key) {
  // The pool ledger is JSON stored in a Script Property because each Web App request is stateless.
  const raw = properties.getProperty(key);
  if (!raw) return { next_sequence: 1, slots: [] };
  try {
    const pool = JSON.parse(raw);
    return {
      next_sequence: Number(pool.next_sequence) || 1,
      slots: Array.isArray(pool.slots) ? pool.slots : [],
    };
  } catch (error) {
    throw apiError_("Drive slot ledger is corrupt; staff review is required.", 409);
  }
}

/**
 * Save the updated slot ledger as JSON in Script Properties so sequence and ready-slot
 * state survive Web App calls.
 */
function writePool_(properties, key, pool) {
  properties.setProperty(key, JSON.stringify(pool));
}

/**
 * Build a namespaced Script Properties key for one booth's Drive slot ledger.
 */
function poolPropertyKey_(boothId) {
  return "PHOTOBOOTH_POOL_" + boothId;
}

/**
 * Calculate a stable lowercase MD5 digest from Google Apps Script byte values for upload
 * verification.
 */
function md5Hex_(bytes) {
  return Utilities.computeDigest(Utilities.DigestAlgorithm.MD5, bytes)
    .map(function (value) { return ("0" + (value & 255).toString(16)).slice(-2); })
    .join("");
}

/**
 * Return the Drive file identifiers, link, name, byte count, and checksum in the shape
 * expected by the Python client.
 */
function fileResponse_(file, size, checksum) {
  return {
    id: file.getId(),
    name: file.getName(),
    size_bytes: size,
    md5_checksum: checksum,
  };
}

/**
 * Create an error object with an HTTP-style code that doPost can return as JSON.
 */
function apiError_(message, code) {
  const error = new Error(message);
  error.code = code || 400;
  return error;
}

/**
 * Serialize a JavaScript value as a JSON TextOutput from the Web App.
 */
function jsonResponse_(value) {
  return ContentService.createTextOutput(JSON.stringify(value))
    .setMimeType(ContentService.MimeType.JSON);
}

/**
 * Run ONCE from the Apps Script editor after updating Code.gs. Authorize Drive,
 * external requests and clock triggers when Google asks, then redeploy the Web
 * App's existing deployment as a new version. This installs exactly one hourly
 * trigger for this account; it does not delete photos during setup.
 *
 * The deletion uses Drive v3 files.delete, not Trash. Enable Google Drive API
 * in the project's Cloud settings (adding Drive API in Services also enables it
 * for the default Apps Script Cloud project). A metadata request verifies access
 * before any retention job is enabled.
 */
function setupPhotoRetention() {
  const properties = PropertiesService.getScriptProperties();
  const parentId = properties.getProperty("PHOTOBOOTH_ROOT_ID") || properties.getProperty("DRIVE_FOLDER_ID");
  if (!parentId) throw apiError_("Set DRIVE_FOLDER_ID first.", 400);
  const response = driveRetentionRequest_("get", parentId, "fields=id,mimeType");
  if (response.getResponseCode() !== 200) {
    throw apiError_("Enable Drive API and authorize the script before retention setup.", 403);
  }
  const parent = JSON.parse(response.getContentText());
  if (parent.mimeType !== "application/vnd.google-apps.folder") {
    throw apiError_("DRIVE_FOLDER_ID must identify the dedicated booth parent folder.", 400);
  }
  const triggers = ScriptApp.getProjectTriggers().filter(function (trigger) {
    return trigger.getHandlerFunction() === PHOTO_RETENTION_TRIGGER;
  });
  const clocks = triggers.filter(function (trigger) {
    return trigger.getEventType() === ScriptApp.EventType.CLOCK;
  });
  const keep = clocks.length ? clocks[0]
    : ScriptApp.newTrigger(PHOTO_RETENTION_TRIGGER).timeBased().everyHours(1).create();
  triggers.filter(function (trigger) { return trigger !== keep; })
    .forEach(function (trigger) { ScriptApp.deleteTrigger(trigger); });
  properties.setProperty(PHOTO_RETENTION_ENABLED, "true");
  return { enabled: true, retention_days: PHOTO_RETENTION_DAYS, interval_hours: 1 };
}

/** A saved enable flag is insufficient if its owning-account timer has gone. */
function photoRetentionActivation_(properties) {
  const configured = !!properties.getProperty("DRIVE_FOLDER_ID");
  const enabled = properties.getProperty(PHOTO_RETENTION_ENABLED) === "true";
  const status = { protocol_version: 1, managed_by: PHOTO_RETENTION_MARKER,
    retention_days: PHOTO_RETENTION_DAYS, enabled: enabled,
    clock_trigger_count: null, drive_api_accessible: null, state: "TRIGGER_ACCESS_REQUIRED" };
  try {
    status.clock_trigger_count = ScriptApp.getProjectTriggers().filter(function (trigger) {
      return trigger.getHandlerFunction() === PHOTO_RETENTION_TRIGGER
        && trigger.getEventType() === ScriptApp.EventType.CLOCK;
    }).length;
    status.state = !configured ? "CONFIGURATION_REQUIRED" : !enabled ? "SETUP_REQUIRED"
      : status.clock_trigger_count === 0 ? "TRIGGER_MISSING"
      : status.clock_trigger_count > 1 ? "DUPLICATE_TRIGGERS" : "READY";
  } catch (_) { /* Only an allowlisted state leaves the Web App. */ }
  return status;
}

/** Authenticated diagnosis: read one parent's metadata; no sweep, marker or trigger writes. */
function inspectPhotoRetention_(properties) {
  const status = photoRetentionActivation_(properties);
  const parentId = properties.getProperty("DRIVE_FOLDER_ID");
  if (!parentId) return status;
  try {
    const response = driveRetentionRequest_("get", parentId, "fields=id,mimeType");
    status.drive_api_accessible = response.getResponseCode() === 200;
    if (!status.drive_api_accessible) {
      if (status.state === "READY") status.state = "DRIVE_API_UNAVAILABLE";
    } else if (JSON.parse(response.getContentText()).mimeType !== "application/vnd.google-apps.folder") {
      status.state = "DRIVE_PARENT_INVALID";
    }
  } catch (_) {
    status.drive_api_accessible = false;
    if (status.state === "READY") status.state = "DRIVE_API_UNAVAILABLE";
  }
  return status;
}

/** Serialize photo uploads, deadline registration and cleanup, without nesting existing locks. */
function withPhotoLock_(work) {
  const lock = LockService.getScriptLock();
  lock.waitLock(30000);
  try { return work(); } finally { lock.releaseLock(); }
}

/** The Python manifest supplies the actual transaction time, including offline claims. */
function registerRetention_(body, properties) {
  const boothId = validateBoothId_(String(body.transaction_id || "").split("_")[0]);
  const transactionId = validateTransactionId_(body.transaction_id, boothId);
  const folder = DriveApp.getFolderById(String(body.folder_id || ""));
  const parent = DriveApp.getFolderById(properties.getProperty("DRIVE_FOLDER_ID"));
  if (folder.isTrashed() || folder.getName() !== (properties.getProperty("STORAGE_LAYOUT") === "2" ? transactionId.split("_").pop() : transactionId) || !hasParent_(folder, parent)) {
    throw apiError_("Retention folder is outside this booth transaction.", 409);
  }
  const started = new Date(body.started_at);
  if (!Number.isFinite(started.getTime()) || started.getTime() > Date.now() + 300000) {
    throw apiError_("Retention requires the transaction's valid original timestamp.", 400);
  }
  const policy = ensureFolderRetention_(folder, transactionId, started);
  // Registration is also proof that a preallocated slot has been claimed. It
  // cannot remain READY if an upload worker's assignment acknowledgement lags.
  const key = poolPropertyKey_(boothId);
  const pool = readPool_(properties, key);
  pool.slots = pool.slots.filter(function (slot) { return slot.folder_id !== folder.getId(); });
  writePool_(properties, key, pool);
  const activation = photoRetentionActivation_(properties);
  return { retention: policy, retention_enabled: activation.state === "READY",
    retention_state: activation.state };
}

/** A timestamp retry can shorten a known clock but must never extend it. */
function ensureFolderRetention_(folder, identity, started) {
  const description = folder.getDescription() || "";
  const existing = readPhotoRetention_(description, identity);
  if (description && !existing) {
    throw apiError_("Unknown folder description; retention was not overwritten.", 409);
  }
  if (existing && new Date(existing.started_at).getTime() <= new Date(started).getTime()) return existing;
  const policy = Object.assign({}, existing || {}, photoRetention_(identity, started));
  folder.setDescription(JSON.stringify(policy));
  return policy;
}

/** Use exactly 30 elapsed days in UTC, independent of Script/local time zones. */
function photoRetention_(identity, started) {
  const stamp = new Date(started);
  if (!Number.isFinite(stamp.getTime())) throw apiError_("Invalid retention timestamp.", 400);
  return { managed_by: PHOTO_RETENTION_MARKER, transaction_id: identity,
    started_at: stamp.toISOString(),
    expires_at: new Date(stamp.getTime() + PHOTO_RETENTION_DAYS * 86400000).toISOString() };
}

/** Malformed or foreign metadata never authorizes deletion. */
function readPhotoRetention_(description, identity) {
  try {
    const policy = JSON.parse(description || "{}");
    if (policy.managed_by !== PHOTO_RETENTION_MARKER || policy.transaction_id !== identity) return null;
    if (new Date(policy.expires_at).getTime() - new Date(policy.started_at).getTime()
        !== PHOTO_RETENTION_DAYS * 86400000) return null;
    return policy;
  } catch (_) { return null; }
}

/**
 * Adopt the known raw/output/session hierarchy used before retention existed.
 * An unused empty folder has no image date and is never adopted or deleted.
 * Unknown child folders stop adoption, so unrelated content is not guessed.
 */
function oldestTransactionPhoto_(folder, depth, layout) {
  if (depth > 3) throw apiError_("Unknown transaction photo hierarchy; adoption skipped.", 409);
  let oldest = null;
  const files = folder.getFiles();
  while (files.hasNext()) {
    const file = files.next();
    if (depth === 0 && file.getName() === "manifest.json") continue;
    if (!/\.(jpg|jpeg|png)$/i.test(file.getName()) || depth === 0)
      throw apiError_("Unknown transaction file; adoption skipped.", 409);
    const stamp = file.getDateCreated();
    if (!oldest || stamp.getTime() < oldest.getTime()) oldest = stamp;
  }
  const folders = folder.getFolders();
  while (folders.hasNext()) {
    const child = folders.next();
    const name = child.getName();
    const allowed = depth === 0 ? /^(raw|output|Photo|color|bw)$/ : layout === 2
      ? (depth === 1 ? /^[0-9]{2}$/ : depth === 2 ? /^(raw|color|bw)$/ : /(?!)^/)
      : depth === 1 ? /^session_[0-9]{3}$/ : /(?!)^/;
    if (!allowed.test(name)) {
      throw apiError_("Unknown transaction subfolder; adoption skipped.", 409);
    }
    const stamp = oldestTransactionPhoto_(child, depth + 1, depth === 0 && name === "Photo" ? 2 : layout);
    if (stamp && (!oldest || stamp.getTime() < oldest.getTime())) oldest = stamp;
  }
  return oldest;
}

/** Drive API permanent deletion leaves no extra 30-day Trash copy. */
function driveRetentionRequest_(method, id, query) {
  return UrlFetchApp.fetch("https://www.googleapis.com/drive/v3/files/" + encodeURIComponent(id)
    + "?supportsAllDrives=true" + (query ? "&" + query : ""), {
      method: method, headers: { Authorization: "Bearer " + ScriptApp.getOAuthToken() },
      muteHttpExceptions: true,
    });
}

/**
 * The hourly cloud job works without an online booth. Only our marked transaction
 * folders immediately under DRIVE_FOLDER_ID (and legacy photo_TIMESTAMP.jpg files
 * produced by this repository) can expire. Never delete READY slots, the parent,
 * or unrelated Drive content. Bound each pass so upload requests are not held
 * behind a long lock; a saved iterator resumes the next hourly pass.
 */
function previewPhotoRetention() {
  return cleanupPhotoRetention({ dryRun: true });
}

function cleanupPhotoRetention(options) {
  const properties = PropertiesService.getScriptProperties();
  if (!properties.getProperty("PHOTOBOOTH_ROOT_ID")) return cleanupPhotoParent_(options, properties);
  const root = storageFolder_(properties.getProperty("PHOTOBOOTH_ROOT_ID"));
  const saved = properties.getProperties();
  const keys = Object.keys(saved).filter(function (key) { return /^PHOTOBOOTH_ROOT_PB[0-9]+$/.test(key); }).sort();
  const report = { enabled: properties.getProperty(PHOTO_RETENTION_ENABLED) === "true", deleted: [], candidates: [], errors: [] };
  const dryRun = options && options.dryRun === true;
  let cursor = dryRun ? 0 : Number(properties.getProperty("PHOTOBOOTH_CLEANUP_BOOTH_CURSOR") || 0);
  const end = Date.now() + 40000;
  for (let count = 0; count < keys.length && Date.now() < end; count++, cursor++) {
    const key = keys[cursor % keys.length], physical = key.slice("PHOTOBOOTH_ROOT_".length);
    try {
      const folder = storageFolder_(saved[key]);
      if (folder.getName() !== physical || !hasParent_(folder, root)) throw apiError_("Invalid booth retention parent.", 409);
      const result = cleanupPhotoParent_(options, storageProperties_(properties, storagePhotoFolder_(properties, physical, false), physical));
      ["deleted", "candidates", "errors"].forEach(function (field) { report[field].push.apply(report[field], result[field] || []); });
    } catch (_) { report.errors.push({booth: physical, error: "Booth cleanup requires operator attention."}); }
  }
  if (!dryRun && keys.length) properties.setProperty("PHOTOBOOTH_CLEANUP_BOOTH_CURSOR", String(cursor % keys.length));
  return report;
}

function cleanupPhotoParent_(options, properties) {
  // Installable clock events are objects too: only an explicit true value can
  // select preview mode. Preview never changes markers, cursors, or image bytes.
  const dryRun = options && options.dryRun === true;
  if (!dryRun && properties.getProperty(PHOTO_RETENTION_ENABLED) !== "true") return { enabled: false, deleted: [] };
  const lock = LockService.getScriptLock();
  if (!lock.tryLock(1000)) return { enabled: true, skipped_busy: true, deleted: [] };
  try {
    const parent = DriveApp.getFolderById(properties.getProperty("DRIVE_FOLDER_ID"));
    const ready = new Set();
    const saved = properties.getProperties();
    Object.keys(saved).filter(function (key) { return key.indexOf("PHOTOBOOTH_POOL_") === 0; })
      .forEach(function (key) {
        // Corrupt pool ledgers fail closed before any deletion is attempted.
        readPool_(properties, key).slots.forEach(function (slot) { ready.add(slot.folder_id); });
      });
    const report = { enabled: properties.getProperty(PHOTO_RETENTION_ENABLED) === "true",
      dry_run: !!dryRun, deleted: [], candidates: [], adopted: [], errors: [] };
    const deadline = Date.now() + 20000;
    // A slot is always created before its real transaction. This coarse age
    // filter avoids scanning a month of recent customer folders every hour;
    // the actual deletion decision still uses the transaction marker below.
    // DriveApp queries use Drive API v2's createdDate (REST v3 uses createdTime).
    // Offline transactions may bind into a newly created folder weeks later.
    // Its creation date must never delay the original 30-day photo deadline.
    const ageQuery = properties.getProperty("STORAGE_LAYOUT") === "2" ? "trashed = false"
      : "trashed = false and createdDate <= '"
      + new Date(Date.now() - PHOTO_RETENTION_DAYS * 86400000).toISOString() + "'";
    let folders;
    try {
      const token = properties.getProperty("PHOTOBOOTH_RETENTION_CURSOR");
      folders = token && !dryRun ? DriveApp.continueFolderIterator(token) : parent.searchFolders(ageQuery);
    } catch (_) { folders = parent.searchFolders(ageQuery); }
    while (folders.hasNext() && Date.now() < deadline && report.candidates.length < 100) {
      const folder = folders.next();
      const name = folder.getName();
      if (ready.has(folder.getId()) || !(properties.getProperty("STORAGE_LAYOUT") === "2" ? /^[0-9]{8}$/ : /^[A-Za-z0-9]+_[0-9]{8}$/).test(name)
          || folder.isTrashed() || !hasParent_(folder, parent)) continue;
      try {
        let identity = name;
        if (properties.getProperty("STORAGE_LAYOUT") === "2") {
          let metadata;
          try { metadata = JSON.parse(folder.getDescription()); } catch (_) { continue; }
          identity = metadata.transaction_id;
          if (!/^PB[0-9]+V2S2_[0-9]{8}$/.test(identity || "")
              || identity.split("_").pop() !== name
              || physicalBooth_(identity.split("_")[0]) !== parent.getParents().next().getName()) continue;
        }
        let policy = readPhotoRetention_(folder.getDescription(), identity);
        if (!policy && !folder.getDescription()) {
          const oldest = oldestTransactionPhoto_(folder, 0);
          if (oldest) {
            policy = dryRun ? photoRetention_(name, oldest) : ensureFolderRetention_(folder, name, oldest);
            report.adopted.push(name);
          }
        }
        if (policy && new Date(policy.expires_at).getTime() <= Date.now()) {
          // Validate known descendants before deleting a marked directory too;
          // unknown/old children are never read or indirectly removed.
          oldestTransactionPhoto_(folder, 0);
          report.candidates.push(name);
          if (dryRun) continue;
          const response = driveRetentionRequest_("delete", folder.getId());
          if (![200, 204, 404, 410].includes(response.getResponseCode())) {
            throw apiError_("Drive refused retention deletion: " + response.getResponseCode(), 503);
          }
          report.deleted.push(name);
        }
      } catch (error) { report.errors.push({ transaction_id: name, error: String(error) }); }
    }
    if (!dryRun) {
      if (folders.hasNext()) properties.setProperty("PHOTOBOOTH_RETENTION_CURSOR", folders.getContinuationToken());
      else properties.deleteProperty("PHOTOBOOTH_RETENTION_CURSOR");
    }
    // Early prototypes stored single photos directly in the configured parent.
    // Match their exact generated filename; never sweep arbitrary root files.
    const files = parent.searchFiles(ageQuery);
    while (files.hasNext() && Date.now() < deadline && report.candidates.length < 100) {
      const file = files.next();
      if (file.isTrashed()) continue;
      try {
        let policy = readPhotoRetention_(file.getDescription(), file.getName());
        if (!policy && !LEGACY_PHOTO_NAME.test(file.getName())) continue;
        if (!policy && !file.getDescription()) {
          policy = photoRetention_(file.getName(), file.getDateCreated());
          if (!dryRun) file.setDescription(JSON.stringify(policy));
        }
        if (policy && new Date(policy.expires_at).getTime() <= Date.now()) {
          report.candidates.push(file.getName());
          if (dryRun) continue;
          const response = driveRetentionRequest_("delete", file.getId());
          if (![200, 204, 404, 410].includes(response.getResponseCode())) throw apiError_("Legacy photo deletion failed.", 503);
          report.deleted.push(file.getName());
        }
      } catch (error) { report.errors.push({ file: file.getName(), error: String(error) }); }
    }
    console.log(JSON.stringify(report));
    return report;
  } finally { lock.releaseLock(); }
}

