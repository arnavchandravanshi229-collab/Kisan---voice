# Kisan---voice
# Kisan Vani 🌾
A Hindi voice assistant that gives farmers advice on crop residue and farming, by voice.

**Live demo:** https://kisan-voice.onrender.com/
**Built for:** The Great Indian AI Internship Challenge by Gnani.ai
**Author:** Arnav Chandravanshi, B.Tech student, Ganga Institute of Technology and Management

## Problem
Many farmers burn crop stubble (parali) because trusted, simple advice is hard to reach in their own language. The smoke harms air quality, soil and family health. Most farming apps need reading, typing or English.

## Solution
Kisan Vani lets a farmer ask a question by voice in Hindi and hear the answer spoken back. No typing or reading is needed. There are also tap-to-ask example questions and a text box for those who prefer to type.

It covers 14 topics: stubble alternatives, Happy Seeder, composting with decomposer, selling stubble, soil testing, fertiliser use, pesticide safety, crop insurance, pollution safety, seeds, irrigation, mandi prices, government schemes, and the Kisan call centre.

## How it works
1. Phone microphone records the question.
2. **Gnani Prisma v2.5 (speech-to-text)** converts Hindi speech to text.
3. The app matches the question to a hand-written, reviewable answer.
4. **Gnani Timbre v2.5 (text-to-speech)** speaks the answer in Hindi.

Stack: Python/Flask, a single-page web app, hosted on Render.

## Impact
- Reaches farmers who cannot easily read or type.
- Encourages alternatives to stubble burning, which can improve local air quality.
- Works on any phone with a browser, with no app install.

## Limits and next steps
- Answers are general guidance; farmers should confirm with their local Krishi Vigyan Kendra.
- Next: more languages (Bhojpuri, Punjabi), more topics, and testing with farmers.