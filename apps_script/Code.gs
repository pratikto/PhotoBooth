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

function doGet() {
  return jsonResponse_({ ok: true, service: "meongs-photobooth-drive" });
}

function doPost(event) {
  try {
    const body = JSON.parse(event && event.postData && event.postData.contents || "{}");
    const properties = PropertiesService.getScriptProperties();
    const expectedToken = properties.getProperty("UPLOAD_TOKEN") || "";
    if (!body.token || !expectedToken || body.token !== expectedToken) {
      throw apiError_("Invalid upload token.", 401);
    }

    const action = body.action || "legacy_upload";
    let result;
    if (action === "ensure_folder_pool") {
      result = ensureFolderPool_(body, properties);
    } else if (action === "assign_slot") {
      result = assignSlot_(body, properties);
    } else if (action === "upload_file") {
      result = uploadTransactionFile_(body, properties);
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

    while (readyCount < targetReady) {
      const sequence = Number(pool.next_sequence) || 1;
      pool.next_sequence = sequence + 1;
      const transactionId = boothId + "_" + String(sequence).padStart(8, "0");
      // Never reuse a name that may belong to a transaction outside this ledger.
      if (parent.getFoldersByName(transactionId).hasNext()) {
        writePool_(properties, key, pool);
        continue;
      }

      const folder = parent.createFolder(transactionId);
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
    pool.slots = pool.slots.filter(function (item) { return item.folder_id !== slot.folder_id; });
    writePool_(properties, key, pool);
    return { slot: Object.assign({}, slot, { status: "ASSIGNED" }) };
  } finally {
    lock.releaseLock();
  }
}

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
  if (slot) {
    if (slot.status !== "READY") throw apiError_("Transaction folder is not a ready slot.", 409);
    pool.slots = pool.slots.filter(function (item) { return item.folder_id !== folderId; });
    writePool_(properties, poolKey, pool);
  }

  const pathParts = relativePath.split("/");
  const fileName = pathParts.pop();
  let targetFolder = rootFolder;
  pathParts.forEach(function (name) {
    targetFolder = getOrCreateChildFolder_(targetFolder, name);
  });

  const bytes = Utilities.base64Decode(String(body.image_base64 || ""));
  const actualMd5 = md5Hex_(bytes);
  if (bytes.length !== expectedSize || actualMd5 !== expectedMd5) {
    throw apiError_("Uploaded bytes do not match the supplied size or checksum.", 400);
  }

  const existing = targetFolder.getFilesByName(fileName);
  if (existing.hasNext()) {
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
  file.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);
  return { file: fileResponse_(file, bytes.length, actualMd5) };
}

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
  file.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);
  return {
    file_id: file.getId(),
    file_url: file.getUrl(),
    file_name: file.getName(),
  };
}

function validateReadyFolder_(slot, parent) {
  try {
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

function hasParent_(folder, expectedParent) {
  const parents = folder.getParents();
  while (parents.hasNext()) {
    if (parents.next().getId() === expectedParent.getId()) return true;
  }
  return false;
}

function getOrCreateChildFolder_(parent, name) {
  const matches = parent.getFoldersByName(name);
  if (matches.hasNext()) {
    const folder = matches.next();
    if (matches.hasNext()) throw apiError_("Duplicate subfolder exists: " + name, 409);
    return folder;
  }
  return parent.createFolder(name);
}

function validateRelativePath_(relativePath, filename) {
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

function validateBoothId_(boothId) {
  const value = String(boothId || "");
  if (!/^[A-Za-z0-9]+$/.test(value)) throw apiError_("Booth ID is invalid.", 400);
  return value;
}

function validateTransactionId_(transactionId, boothId) {
  const value = String(transactionId || "");
  if (!new RegExp("^" + boothId + "_[0-9]{8}$").test(value)) {
    throw apiError_("Transaction ID is invalid.", 400);
  }
  return value;
}

function readPool_(properties, key) {
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

function writePool_(properties, key, pool) {
  properties.setProperty(key, JSON.stringify(pool));
}

function poolPropertyKey_(boothId) {
  return "PHOTOBOOTH_POOL_" + boothId;
}

function md5Hex_(bytes) {
  return Utilities.computeDigest(Utilities.DigestAlgorithm.MD5, bytes)
    .map(function (value) { return ("0" + (value & 255).toString(16)).slice(-2); })
    .join("");
}

function fileResponse_(file, size, checksum) {
  return {
    id: file.getId(),
    name: file.getName(),
    size_bytes: size,
    md5_checksum: checksum,
  };
}

function apiError_(message, code) {
  const error = new Error(message);
  error.code = code || 400;
  return error;
}

function jsonResponse_(value) {
  return ContentService.createTextOutput(JSON.stringify(value))
    .setMimeType(ContentService.MimeType.JSON);
}
