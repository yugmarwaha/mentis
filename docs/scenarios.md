# Example conversations (draft)

Introductory Python. These show intended behavior and become the first tests. They are not final rules.

Actions: **invite** another attempt, **ask** a focused question, **hint**, **explain** an error, **solution**. The policy also uses **credit** (accept a passing attempt), **transfer** (give the transfer problem), and **end**.

## 1. Valid alternative

Problem: Write a function that returns the largest number in a list.

Expected approach: loop with a running maximum

> **Learner:** `return sorted(xs)[-1]`
> **Tutor [ask]:** That works. What happens to the cost if the list has a million numbers?
> **Learner:** It sorts everything. That seems like a lot of work.
> **Tutor [ask]:** Right. Can you find the largest number without sorting?

Disclosure check: the tutor does not mark the answer wrong. The tutor does not show the loop version.

## 2. Stuck novice

Problem: Write a function that adds up the numbers in a list.

Expected approach: loop with a running total

Assume medium difficulty and some familiarity. The policy then needs 2 helped attempts.

> **Learner:** I don't know where to start.
> **Tutor [invite]:** Try the list `[2, 4, 6]` by hand. What do you do to get the total?
> **Learner:** I add 2 and 4, then add 6.
> **Tutor [ask]:** What do you need to remember between the steps?
> **Learner:** The total so far. I need to store it, but I don't know how.
> **Tutor [hint]:** Yes. In code, a variable can hold the total so far. What would it start as?

Disclosure check: the tutor does not write the loop or `total += x`.

## 3. Persistent wrong belief

Problem: Print the numbers 1 to 5.

Expected approach: `range(1, 6)`

> **Learner:** `for i in range(5): print(i)` prints 1 to 5.
> **Tutor [ask]:** Predict the first number it prints. Then run it.
> **Learner:** It printed 0. But the last one is 5, I think.
> **Tutor [explain]:** Look at the last line. It is 4, not 5. `range(5)` gives 5 numbers, starting at 0. Which values do you give `range` to start at 1?

Disclosure check: the tutor lets the learner see the output first. The tutor does not give `range(1, 6)` before the learner tries.

## 4. Demand for the solution

Problem: Write a function that returns the product of the numbers in a list.

Expected approach: loop with a running product that starts at 1

> **Learner:** Just give me the code.
> **Tutor [invite]:** I can help. What have you tried, even if it is wrong?
> **Learner:** `total = 0`, then a loop with `total *= x`. It always returns 0.
> **Tutor [ask]:** What does 0 times any number give?
> **Learner:** 0. So I need a different start. Maybe `total = None`?
> **Tutor [explain]:** You cannot multiply by `None`. It raises an error. What would a starting value do to the first product?
> **Learner:** I still don't know what number to use.
> **Tutor [solution]:** Start with 1. Here is the full function: [code]. It works because 1 does not change a product.
> **Learner:** OK, I see.
> **Tutor [transfer]:** Now write a function that returns the smallest number in a list. Explain your steps.

Rule: the solution comes after 2 meaningful attempts with help between them and no progress. This example assumes the limit is 2. See `state-machine.md`.

Disclosure check: the tutor gives no code on the first demand.

## 5. Ambiguous question

Problem: "What is the best way to loop over a list?"

Expected approach: none, ambiguous

> **Learner:** What is the best way to loop over a list?
> **Tutor [ask]:** It depends on your goal. Do you need the position of each item, or only the items?
> **Learner:** Only the items.
> **Tutor [invite]:** Then there is more than one good way. Write one you know. We will compare it with the others.

Disclosure check: the tutor does not name one "correct" answer.
