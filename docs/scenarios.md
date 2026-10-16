# Example conversations (draft)

Domain: introductory Python. See ADR 0001.

Status: drafted, not reviewed. The tutor actions come from the brief, section 4. We have not decided when each action applies. These examples show the intended behavior, not final rules.

Actions: **invite** another attempt, **ask** a focused question, **hint**, **explain** an error, **solution**.

## 1. Valid alternative

Problem: Write a function that returns the largest number in a list.

> **Learner:** `return sorted(xs)[-1]`
> **Tutor [ask]:** That works. What happens to the cost if the list has a million numbers?
> **Learner:** It sorts everything. That seems like a lot of work.
> **Tutor [invite]:** Right. Can you find the largest number without sorting?

Disclosure check: the tutor does not mark the answer wrong. The tutor does not show the loop version.

## 2. Stuck novice

Problem: Write a function that adds up the numbers in a list.

> **Learner:** I don't know where to start.
> **Tutor [invite]:** Try the list `[2, 4, 6]` by hand. What do you do to get the total?
> **Learner:** I add 2 and 4, then add 6.
> **Tutor [ask]:** What do you need to remember between the steps?
> **Learner:** The total so far?
> **Tutor [hint]:** Yes. In code, a variable can hold the total so far. What would it start as?

Disclosure check: the tutor does not write the loop or `total += x`.

## 3. Persistent wrong belief

Problem: Print the numbers 1 to 5.

> **Learner:** `for i in range(5): print(i)` prints 1 to 5.
> **Tutor [ask]:** Predict the first number it prints. Then run it.
> **Learner:** It printed 0. But the last one is 5, I think.
> **Tutor [invite]:** Look at the last line it printed. What is it?
> **Learner:** 4. So range(5) is 0 to 4?
> **Tutor [explain]:** Yes. `range(5)` gives 5 numbers, starting at 0. Which values do you give `range` to start at 1?

Disclosure check: the tutor lets the learner see the output first. The tutor does not give `range(1, 6)` before the learner tries.

## 4. Demand for the solution

Problem: Write a function that returns the product of the numbers in a list.

> **Learner:** Just give me the code.
> **Tutor [invite]:** I can help. What have you tried, even if it is wrong?
> **Learner:** `total = 0`, then a loop with `total *= x`. It always returns 0.
> **Tutor [ask]:** What does 0 times any number give?
> **Learner:** 0. Oh. But what do I start with? I'm stuck, this is taking long.
> **Tutor [solution]:** Start with 1. Here is the full function: [code]. It works because 1 does not change a product.
> **Tutor [transfer]:** Now write a function that returns the smallest number in a list. Explain your steps.

Open question: when is the solution justified? We have not decided this. The example shows a learner who made a real attempt, found the error with help, and is still stuck.

Disclosure check: the tutor gives no code on the first demand.

## 5. Ambiguous question

Problem: "What is the best way to loop over a list?"

> **Learner:** What is the best way to loop over a list?
> **Tutor [ask]:** It depends on your goal. Do you need the position of each item, or only the items?
> **Learner:** Only the items.
> **Tutor [invite]:** Then there is more than one good way. Write one you know. We will compare it with the others.

Disclosure check: the tutor does not name one "correct" answer.
