# ADR 0001 — Model sovereignty

Status: accepted as the engineering premise. Not a legal opinion.

## Context

"Build our own model and call no external model" cannot mean training a frontier model from random weights. That needs tens of thousands of GPUs, trillions of tokens, and a budget Coopreta does not have. "Ten times better than ChatGPT" cannot mean a higher score on general knowledge.

## Decision

- Dhara is sovereign when Coopreta hosts the weights, fine-tunes them, and serves them, with zero runtime calls to a third-party inference API.
- Starting weights come from a permissively licensed open-weight family (Llama, Mistral, or Qwen class).
- Rented GPU time is allowed. Data and weights do not leave Coopreta's control.
- The 10x claim is Dhara-Bench against a general chatbot on held-out Coopreta documents only.

## Consequences

- vLLM (or the same class) runs inside Coopreta's network.
- Product copy and investor language use this definition. They do not claim a general-benchmark win.
- Any pull request that adds an outbound inference API is SECURITY GATE BLOCKED.
