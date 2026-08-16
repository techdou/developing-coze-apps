# Expected — Eval 12

Must include:

- Database migration/copy of an object key does not copy the binary object into the production bucket.
- The same key string can refer to no object or a different object in another environment.
- Persist canonical object keys/IDs, not expiring signed URLs.
- Required curated media should be promoted with an allowlist/manifest.
- Verify target object key, content type, size/checksum/read behavior in production before updating references.
- Do not bulk-copy the entire DEV bucket unless explicitly required and reviewed.
