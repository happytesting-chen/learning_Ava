I want to build a simple learning web app for my child.

Update the OCR extraction pipeline using PaddleOCR (Chinese-optimized).

Goal:
- After OCR, only keep vocabulary items under these two categories:
  1) “口语表达词汇”
  2) “识读词语”

App behavior:
- Reading page/button MUST use ONLY “口语表达词汇”
- Practicing page/button MUST use ONLY “识读词语”
- Do NOT mix categories.

Implementation requirements:
1) Run PaddleOCR on the uploaded image and extract text with bounding boxes + confidence.
2) Parse the OCR output to detect the two headings “口语表达词汇” and “识读词语”.
3) Collect the vocabulary items that belong to each heading section.
4) Return a structured JSON like:
   {
     "spoken_vocab": [...],   // 口语表达词汇
     "practice_vocab": [...]  // 识读词语
   }
5) Update frontend routes/components so Reading uses spoken_vocab only, Practicing uses practice_vocab only.
Add basic filtering:
- keep only Chinese tokens
- drop low confidence text (e.g. < 0.85)
- remove duplicates


