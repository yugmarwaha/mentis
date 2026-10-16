# Writing style: ASD-STE100

Use ASD-STE100 Simplified Technical English for all explanations in this project. This applies to chat replies, docs, ADRs, comments, commit messages, and PR text.

## Documentation
- Use the `clear-writing` skill (`.claude/skills/clear-writing/`) each time you write or revise documentation. This includes README, `CLAUDE.md`, ADRs, and files in `docs/`.

## Sentences
- Write 20 words or fewer in instructions. Write 25 words or fewer in descriptions.
- Put one idea in each sentence.
- Use 6 sentences or fewer in a paragraph.
- Use the active voice.
- Use the imperative for instructions: "Run the tests."
- Use the simple present for descriptions. Use the simple past or future only when needed.

## Words
- Use one word for one meaning. Do not swap synonyms for variety.
- Use the same name for the same thing. Use the terms in `docs/glossary.md` when that file exists.
- Use simple words: "use", not "utilize"; "start", not "initiate".
- Do not use idioms, slang, or figurative language.
- Keep articles ("the", "a"). Do not drop them.
- Do not use more than 3 nouns in a row. Rewrite long noun strings.
- Spell out each abbreviation on first use. Then use the short form.

## Form
- Put the most important point first.
- Use a list for steps or items. Do not hide them in a long sentence.
- Use a number for each step in a procedure.
- Give one action in each step.
- Start a warning or caution before the step it applies to.

## Exceptions
- Code, commands, and quoted text stay as they are.
- Use the words that the domain needs. Define each one at first use.
