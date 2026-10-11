# Journal — one entry, one file

Every relevant piece of work is its own `YYYY-MM-DD-slug.md` file. Two concurrent sessions write to different files
and never collide (measured at the source: an append-only monolith conflicts at the head and the tail; one file per
entry merges cleanly). The date goes first so `ls` sorts: the file name **is** the index; there is no hand-kept index.

Content: `# YYYY-MM-DD — Title` · **Who** (name and role, from the profile) · **Intent** · **What was done** ·
**Verification** (real numbers) · **Declared debt**. Append-only: if a previous entry was wrong, add a dated inline
correction, don't rewrite. Anchors in `closed.md` point by date + title, never by line number.
