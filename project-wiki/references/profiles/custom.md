# Custom profile

Start with the user's recurring questions, then infer concrete recurring objects, concepts and relationships. Reuse supplied details. Ask about scope or source selection only if missing information would materially change the Wiki.

Suggest a minimal page model; do not require a fixed number of entity types or force software vocabulary. Map chosen types to page_dirs in project config and describe their boundaries in schema.md. Create local templates for added types with the shared metadata contract. The same query/sync helpers operate on all configured directories.

When changing an existing schema, inspect affected pages and show the actual rename/type/link implications. Additive changes may proceed within the request; destructive migration is separate from initializing a new Wiki. Avoid empty category forests.
