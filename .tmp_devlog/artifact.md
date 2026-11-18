# Template distillation contract

- Reference: `C:\Users\xavie\Downloads\Format_Devlog_SMK_MART.docx`
- SHA-256: `24724afe687f6c55eb7f8ace66b52d5fe28f4da99c9633d9d6a0d68208e858cc`; source size 27,167 bytes.
- Reference render: `.tmp_devlog/template-render-word/page-1.png` through `page-5.png`, exported read-only through Microsoft Word because the packaged DOCX renderer could not locate Windows `soffice.exe`.
- Page system: five pages, one A4 portrait section (8.27 x 11.69 in), margins L/R/T 1.00 in, bottom 0.90 in. Header text `SAS Kelas X RPL | Format Devlog`; footer contains a PAGE field.
- Typography and components: centered large bold serif title and subtitle; Heading 1 17 pt bold, Heading 2 13.5 pt bold; Normal Table style with gray bold header rows, thin gray gridlines, repeated template table geometry. Main text and tables use the source styles.
- Content flow: identity table; devlog instructions; daily entry template; filled-example slot; daily summary table; group weekly recap; peer assessment; teacher scoring sheet.
- Slot map: Table 0 personal details intentionally blank. Tables 1 and 2 are repurposed for cashier work and bug fixing/profit work; a page break before entry 2 keeps the second table together. Table 3 first two body rows summarize those entries. Weekly/group and teacher-only tables remain blank.
- Package preservation: edit only `word/document.xml`; preserve all other package parts, including headers, footer PAGE field, styles, numbering, theme, settings, font table, endnotes and footnotes.
- Fidelity gates: verify the source hash unchanged, compare package inventories and all preserve-only part bytes, render every final page via Word to PDF and inspect PNGs. Preserve the A4 section, source table styles, header and page-number field.
