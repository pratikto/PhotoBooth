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
 * and upload_file actions.
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
    const properties = PropertiesService.getScriptProperties();
    const expectedToken = properties.getProperty("UPLOAD_TOKEN") || "";
    // Authenticate every action before it can create or modify Drive content.
    if (!body.token || !expectedToken || body.token !== expectedToken) {
      throw apiError_("Invalid upload token.", 401);
    }

    // Requests without an action keep using the original one-file upload behavior.
    const action = body.action || "legacy_upload";
    let result;
    if (action === "ensure_folder_pool") {
      result = ensureFolderPool_(body, properties);
    } else if (action === "assign_slot") {
      result = assignSlot_(body, properties);
    } else if (action === "upload_file") {
      result = withPhotoLock_(function () { return uploadTransactionFile_(body, properties); });
    } else if (action === "register_retention") {
      result = withPhotoLock_(function () { return registerRetention_(body, properties); });
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
  if (rootFolder.getName() !== transactionId || !hasParent_(rootFolder, DriveApp.getFolderById(parentId))) {
    throw apiError_("Transaction folder name does not match its ID.", 409);
  }
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
    return !part || part === "." || part === ".." || /[<>:"|?*]/.test(part);
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
  const parentId = properties.getProperty("DRIVE_FOLDER_ID");
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
  if (!triggers.length) {
    ScriptApp.newTrigger(PHOTO_RETENTION_TRIGGER).timeBased().everyHours(1).create();
  } else {
    triggers.slice(1).forEach(function (trigger) { ScriptApp.deleteTrigger(trigger); });
  }
  properties.setProperty(PHOTO_RETENTION_ENABLED, "true");
  return { enabled: true, retention_days: PHOTO_RETENTION_DAYS, interval_hours: 1 };
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
  if (folder.isTrashed() || folder.getName() !== transactionId || !hasParent_(folder, parent)) {
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
  return { retention: policy, retention_enabled: properties.getProperty(PHOTO_RETENTION_ENABLED) === "true" };
}

/** A timestamp retry can shorten a known clock but must never extend it. */
function ensureFolderRetention_(folder, identity, started) {
  const description = folder.getDescription() || "";
  const existing = readPhotoRetention_(description, identity);
  if (description && !existing) {
    throw apiError_("Unknown folder description; retention was not overwritten.", 409);
  }
  if (existing && new Date(existing.started_at).getTime() <= new Date(started).getTime()) return existing;
  const policy = photoRetention_(identity, started);
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
function oldestTransactionPhoto_(folder, depth) {
  if (depth > 3) throw apiError_("Unknown transaction photo hierarchy; adoption skipped.", 409);
  let oldest = null;
  const files = folder.getFiles();
  while (files.hasNext()) {
    const file = files.next();
    if (!/\.(jpg|jpeg|png)$/i.test(file.getName())) throw apiError_("Unknown transaction file; adoption skipped.", 409);
    const stamp = file.getDateCreated();
    if (!oldest || stamp.getTime() < oldest.getTime()) oldest = stamp;
  }
  const folders = folder.getFolders();
  while (folders.hasNext()) {
    const child = folders.next();
    if (!(depth === 0 ? /^(raw|output)$/ : /^session_[0-9]{3}$/).test(child.getName())) {
      throw apiError_("Unknown transaction subfolder; adoption skipped.", 409);
    }
    const stamp = oldestTransactionPhoto_(child, depth + 1);
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
  // Installable clock events are objects too: only an explicit true value can
  // select preview mode. Preview never changes markers, cursors, or image bytes.
  const dryRun = options && options.dryRun === true;
  const properties = PropertiesService.getScriptProperties();
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
    const ageQuery = "trashed = false and createdDate <= '"
      + new Date(Date.now() - PHOTO_RETENTION_DAYS * 86400000).toISOString() + "'";
    let folders;
    try {
      const token = properties.getProperty("PHOTOBOOTH_RETENTION_CURSOR");
      folders = token && !dryRun ? DriveApp.continueFolderIterator(token) : parent.searchFolders(ageQuery);
    } catch (_) { folders = parent.searchFolders(ageQuery); }
    while (folders.hasNext() && Date.now() < deadline && report.candidates.length < 100) {
      const folder = folders.next();
      const name = folder.getName();
      if (ready.has(folder.getId()) || !/^[A-Za-z0-9]+_[0-9]{8}$/.test(name)
          || folder.isTrashed() || !hasParent_(folder, parent)) continue;
      try {
        let policy = readPhotoRetention_(folder.getDescription(), name);
        if (!policy && !folder.getDescription()) {
          const oldest = oldestTransactionPhoto_(folder, 0);
          if (oldest) {
            policy = dryRun ? photoRetention_(name, oldest) : ensureFolderRetention_(folder, name, oldest);
            report.adopted.push(name);
          }
        }
        if (policy && new Date(policy.expires_at).getTime() <= Date.now()) {
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
