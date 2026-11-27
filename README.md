# Monty Playground — Web Builder Upgrade
if you want to open Monty online visit: https://ariomoshfeqi-cell.github.io/monty/

**Monty is made with Python. Created by Ario Moshfeghi.**

## Run it

1. Install Python 3 if it is not already installed.
2. Open this folder in VS Code.
3. Open Terminal → New Terminal.
4. Run:

   ```bash
   python app.py
   ```

5. Open `https://ariomoshfeqi-cell.github.io/monty/` in Chrome.

No third-party Python packages are required.

## Monty website commands

```python
web = website("My Website")
web.heading("Hello!", 1)
web.text("A paragraph")
web.button("Click", "You clicked!")
web.image("https://example.com/image.png", "Example")
web.link("Visit site", "https://example.com")
web.card("Card title", "Card description")
web.navbar("Brand", [("Home", "#home")])
web.footer("Created with Monty")
web.input("Name", "Your name")
web.form(["Name", "Email"], "Submit")
web.columns("First", "Second", "Third")
web.divider()
web.spacer(30)
web.background_color("#ffffff")
web.color("#222222")
web.accent_color("#7957e8")
web.font("Arial, sans-serif")
web.animate("Hello", "fade")
web.custom_css("h1 { letter-spacing: 2px; }")
web.run()
```

Animations supported: `fade`, `slide`, `pop`.

## Important safety note

This is an early local development build. The Monty interpreter currently executes Python code using `exec`, so it is **not a secure sandbox**. Only run code you trust. The server binds to `127.0.0.1` so it is intended for local use on your own computer. Do not expose it to a public network.

Generated websites are previewed inside the app. This is not yet a production website hosting or publishing system.
# Monty Programming Language

**Monty is a programming language project created by Ario Moshfeghi and built using Python.**

Monty is designed to become a general-purpose programming language, with the goal of supporting website development, game development, software creation, and more.

## ✨ Features

- **Custom Commands:** Alternative names for familiar programming commands, such as `pt` for `print` and `inp` for `input`.
- **Variable Renaming:** The `vachange()` command renames variables while preserving their values.
- **Python-Based Interpreter:** Python currently powers Monty's interpreter.
- **Website Builder:** A basic website-building prototype is part of the project.

## 💻 Example

```monty
# A simple Monty program

pt("Hello, World!")

score = 100
pt(score)

pt("Monty is running!")
```

## 🚀 Future Goals

Monty aims to grow into a general-purpose programming language with:

- Frontend and backend development.
- Website creation and previewing.
- Game development.
- Desktop application development.
- A dedicated VS Code extension.
- More built-in commands and language features.
- Multiline comments using `#\` to start and `#/` to end.

## 👨‍💻 Creator

**Created by Ario Moshfeghi.**

**Made with Python.**

Monty is an evolving project, and its features and capabilities are still under development.

---

# 📚 Monty Commands & Syntax

Monty uses its own command names for some familiar Python functions.

| Monty command | Python equivalent | Explanation |
|---|---|---|
| `pt()` | `print()` | Displays text or values. |
| `inp()` | `input()` | Asks the user for input. |
| `spam()` | `sum()` | Adds numbers in a collection. |
| `egg` | `True` | Represents a true value. |
| `chicken` | `False` | Represents a false value. |
| `every()` | `all()` | Checks whether every item is true. |
| `mword()` | `str()` | Converts a value into text. |
| `number()` | `int()` | Converts a value into an integer. |
| `properties()` | `property()` | Creates a property. |
| `mass()` | `object()` | Creates a basic object. |
| `pows()` | `pow()` | Calculates a number raised to a power. |
| `giveup()` | `quit()` | Exits the program. |
| `Unicodeserror` | `UnicodeError` | Represents a Unicode-related error. |
| `end()` | `max()` | Finds the largest value. |
| `sort()` | `sorted()` | Sorts a collection. |
| `getatr()` | `getattr()` | Gets an object's attribute by name. |
| `length()` | `len()` | Returns the number of items or characters. |
| `minimum()` | `min()` | Finds the smallest value. |
| `maximum()` | `max()` | Finds the largest value. |
| `average()` | Custom function | Calculates the average of numbers. |
| `absolute()` | `abs()` | Returns the absolute value. |
| `roundnum()` | `round()` | Rounds a number. |
| `sequence()` | `range()` | Creates a sequence of numbers. |
| `random_number()` | `random.randint()` | Generates a random integer. |
| `vachange()` | Custom Monty command | Renames a variable while keeping its value. |

*Note: This command reference describes the intended command mappings. Check that each command is implemented in the current interpreter before treating it as available.*

## 🔄 Variable Renaming

Monty introduces `vachange()` to rename an existing variable.

```monty
score = 100

vachange(score, points)

pt(points)
```

Output:

```text
100
```

After renaming, `points` contains the original value, and `score` is no longer available.

## 🧮 More Examples

**Displaying information:**

```monty
pt("Welcome to Monty!")
```

**Getting user input:**

```monty
name = inp("What is your name? ")
pt("Hello", name)
```

**Working with numbers:**

```monty
numbers = [10, 20, 30]

pt(spam(numbers))
pt(average(numbers))
pt(maximum(numbers))
pt(minimum(numbers))
```

Output:

```text
60
20.0
30
10
```

---

**Monty — Created by Ario Moshfeghi. Made with Python.**
Copyright © 2026 Ario Moshfeghi. All rights reserved.
