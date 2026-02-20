# Brewin# Interpreter (Python)

A multi-stage interpreter for a progressively extended programming language, implemented in Python.  
This project evolved across four major iterations, culminating in support for static typing, objects, interfaces, first-class functions, and closures.

The goal was to design and implement a correct execution model on top of a provided parser/AST framework, focusing on runtime semantics, scoping rules, type enforcement, and higher-order behavior.

---

## Overview

This interpreter executes a custom language with:

- Lexical scoping
- Static type enforcement via name suffix conventions
- Structured control flow
- User-defined functions and recursion
- Objects with dynamic fields
- Interface conformance checks
- First-class functions
- Lambda expressions with closure capture
- Method dispatch with implicit receiver injection

The implementation emphasizes:

- Clear environment modeling
- Correct stack discipline
- Deterministic runtime error behavior
- Precise semantic handling of closures and reference parameters

---

## Language Capabilities

### 1. Core Execution Model
- Program entry via `main`
- Expression evaluation (arithmetic, boolean, comparison, logical ops)
- Structured control flow: `if`, `while`
- Recursive function calls
- Return propagation via explicit call frames

### 2. Static Typing via Suffix System
Type is encoded in identifier suffix:
- `i` → int
- `b` → bool
- `s` → string
- `o` → object
- `f` → function
- `InterfaceName` (capitalized) → interface type

The interpreter enforces:
- Assignment compatibility
- Parameter compatibility
- Return type correctness
- Interface structural conformance

This required building a runtime type validation layer on top of dynamic Python values.

### 3. Environment & Scope Model
- Function scope
- Block scope (`bvar`)
- Shadowing rules (required in final version)
- Separate lexical environments captured for closures

Internally implemented via:
- Stack of activation records
- Nested environment chains
- Explicit lookup resolution strategy

### 4. Objects
- Object construction
- Dynamic field creation
- Dotted access and assignment
- Field-stored functions

Objects are implemented as runtime dictionaries with metadata enforcing typing and interface constraints.

### 5. Pass-by-Reference Parameters
Supports reference parameters:
- Alias binding between caller and callee
- Correct mutation semantics
- Scope-aware resolution

This required explicit reference wrappers rather than raw Python primitives.

### 6. First-Class Functions
Functions can:
- Be stored in variables
- Be returned from functions
- Be passed as parameters
- Be stored inside objects

Function values internally store:
- Parameter list
- Return type
- AST body
- Captured environment snapshot

### 7. Lambdas & Closures
Lambda expressions support:
- Environment capture
- Value capture for primitives
- Reference capture for objects
- Nested closure chains

Correct closure implementation required:
- Free variable detection
- Environment freezing at creation time
- Correct resolution order during invocation

### 8. Method Dispatch & Implicit Receiver
When invoking a function via object field:

```brewin
obj.method()
```


## Licensing and Attribution

This is an unlicensed repository; even though the source code is public, it is **not** governed by an open-source license.

This code was primarily written by [Carey Nachenberg](http://careynachenberg.weebly.com/) with support from his TAs.

As a studend in CS 131, I've implemented the interpreter files in this repository. 



## Interpreter Implementation:

The implementation of the interpreter is over the provided baseclass. I developed this incrementally over different projects. 