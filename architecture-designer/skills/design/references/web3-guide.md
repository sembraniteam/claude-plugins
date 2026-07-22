# Web3 / Decentralized Architecture Guide

Guidance for the optional Web3 track — activated when Stage 1–2 describes a decentralized, blockchain, or on-chain application, or Stage 5 names a distributed-ledger platform of any kind. This guide is **network-agnostic by design**: it teaches the invariant dimensions every decentralized system must resolve and the questions to ask about the *target network*, not the answers for any one network.

## Core rule: dimensions here, facts from the network

**This document names what to ask; it never supplies a particular network's facts.** Consensus model, finality time, address format, token standards, fee mechanics, available primitives, tooling — all of these differ per network and change over time. Never state any of them from memory. When the architecture needs one, record it as a verification placeholder that names its source:

> `<VERIFY against {target network}'s official docs: finality model and typical time-to-finality>`

An LLM will confidently produce a plausible, precise, and wrong value for every one of these — and in Web3 a wrong value can mean permanent, irreversible loss of funds. A placeholder the user must fill from the network's own current documentation is always correct; a remembered fact is a liability. This is the same discipline as the address rule below and the `agentTools` availability rule: never fabricate, always ground.

## Why this domain punishes hallucination hardest

Two properties make decentralized systems the least forgiving domain this plugin covers, and both belong in the document that results:

- **Immutability.** Deployed on-chain code and confirmed transactions typically cannot be reverted. There is no `git revert`, no hotfix, no rollback. Every claim that survives into deployed code must have been verified *before* deployment — the entire security posture is front-loaded.
- **Value at stake.** The system holds assets directly. A subtle logic error is not a bug ticket; it is a loss. This raises the bar on independent verification from "recommended" to "mandatory in proportion to value held."

The document must never describe generated output as "secure" or "safe." The plugin produces *a skeleton that must be independently audited*, and the wording must say exactly that — the same way the security-auditor never claims "no vulnerabilities" from an LLM pass alone.

## Addresses, hashes, ABIs, chain identifiers: tool-or-placeholder only

The Web3 analogue of the security-auditor's "a CVE only appears if a tool returned it." Contract addresses, transaction hashes, interface definitions, chain identifiers, and token contract references must never be written from memory. They come only from: a document the user supplied, a block explorer or registry fetched via a tool, or the user stating them directly. Otherwise, a named placeholder — never an invented value. Where the target network uses a checksummed address format, that checksum is deterministically verifiable and should be validated by a script rather than trusted by eye.

## The invariant dimensions

For each dimension: the stable principle (safe to state), the question to resolve about the target network (never answered from here), and what verifies it. Present these as conditional additions to the design session; the user's answers become grounded facts in `session.json` (owner: user), flowing into the document and diagrams.

### 1. Trust and consensus model
- **Principle**: every decentralized system rests on an explicit answer to "who validates, and under what assumption does security hold?" The application's threat model inherits directly from this and cannot be reasoned about without it.
- **Ask about the target**: what is the network's validation/consensus model, and what is its security assumption (e.g. stake, work, authority set, committee)? What breaks that assumption?
- **Verifies**: the network's own protocol documentation, stated as `<VERIFY>` until supplied.

### 2. Immutability and pre-deployment verification
- **Principle**: irreversibility means the verification budget is spent before deploy, not after. Upgrade mechanisms, if any, are themselves a trust and attack surface, not an undo button.
- **Ask about the target**: is deployed code upgradeable on this network, and if so by whom and through what mechanism? What is the deployment/finality path that cannot be reversed?
- **Verifies**: static analysis, comprehensive test/fuzz/invariant suites, and independent audit — as hard requirements sized to value at stake, not options.

### 3. On-chain vs off-chain boundary
- **Principle**: on-chain is expensive, public forever, and constrained; off-chain (indexers, RPC access, compute, storage) is where anything not requiring consensus belongs. Mis-placing this boundary is one of the most common decentralized-architecture design errors.
- **Ask about the target**: which operations genuinely require consensus, and which are being put on-chain only by habit? Where do reads come from (direct node, indexer, third-party RPC) and what is the availability/trust of that path?
- **Verifies**: the boundary drawn explicitly in the architecture diagram, on-chain and off-chain components visually separated.

### 4. External data and oracles
- **Principle**: any value entering the system from outside is an attack surface. Prices, randomness, and cross-system state are manipulable unless sourced with explicit resistance.
- **Ask about the target**: what external data does the system depend on, how is it sourced, and what is the manipulation cost? Is a single point (e.g. one venue's spot value) being trusted where a manipulation-resistant source is required?
- **Verifies**: the data source and its manipulation-resistance stated per input; adversarial cases in the test plan.

### 5. Finality as a spectrum
- **Principle**: "confirmed" is not binary. Different networks offer different finality guarantees and reorg possibilities; application logic that assumes instant irreversibility where the network offers only probabilistic settlement is unsafe.
- **Ask about the target**: what finality does the network guarantee, and after what conditions is a transaction safe to act on for this application's value level?
- **Verifies**: `<VERIFY>` against network docs; the chosen confirmation threshold recorded as a design decision with its rationale.

### 6. Key management and signing
- **Principle**: control of keys is control of assets. Key custody, signing flow, and recovery are first-class architecture, not an afterthought, and span the off-chain side too.
- **Ask about the target**: who holds which keys, how are they stored and signed with, and what is the recovery/rotation story? Are any privileged keys a centralization risk that undermines the trust model in dimension 1?
- **Verifies**: the key-custody model documented; privileged roles enumerated with their blast radius.

### 7. Economic and value-at-risk verification
- **Principle**: the level of independent scrutiny scales with the value the system can hold or move. This is the "verify first" principle moved into the user's hands, and in this domain it is the primary backstop — it lives in the ecosystem's tools and auditors, not in this plugin. Exposure should also be staged, not switched on all at once: a deployment that goes straight from development to holding full value skips the chance to catch what audit and testing missed while the cost of being wrong is still small.
- **Ask about the target**: what is the maximum value at risk, and therefore what tier of audit is mandatory before any deployment holding real value? Does the rollout plan stage that exposure — testnet, then a mainnet deployment with a capped value ceiling, then full mainnet — so problems surface before maximum value is at stake, rather than a single big-bang deployment straight to full value?
- **Verifies**: a required audit step in the document, sized to value; never implied to be satisfied by generation alone. A staged rollout plan (testnet → value-capped mainnet → full mainnet) recorded as part of the same audit-tier discussion, not treated as optional polish.

### 8. Cross-chain and bridge risk
- **Principle**: value or state crossing between chains — bridges, cross-chain messaging, wrapped/synthetic assets — introduces a trust boundary distinct from any single chain's own consensus (dimension 1): the destination chain cannot independently verify what happened on the source chain, so security rests entirely on whatever validates the message (a validator set, a light client, a fraud-proof window, a multisig). Bridge and cross-chain-messaging exploits are historically among the largest single losses in the ecosystem, and their failure mechanisms — forged or replayed messages, a compromised validator/relayer set, a bypassed verification step — are distinct from oracle/price manipulation (dimension 4), which is why this is its own dimension rather than folded into that one.
- **Ask about the target**: does the system move value or state across chains? If so, what bridge or messaging protocol is used, what is its message-verification mechanism, and what is its audit history and track record? What happens to user funds if that bridge is paused, exploited, or its message queue is compromised — is the application's logic exposed to that failure, or isolated from it?
- **Verifies**: the bridge/messaging protocol and its verification mechanism stated per crossing point — never assumed trustworthy by default, and never named from memory (use the `<VERIFY>` placeholder for anything not confirmed by the user or the protocol's own docs); adversarial bridge-failure cases included in the test plan whenever a cross-chain flow exists.

## Confirmed vs needs-review for security claims

Apply the same discipline as the plugin's other grounding rules (the Stage 2 compliance-grounding tag, the Stage 5 version-grounding tag, and the `<VERIFY>` placeholder above): never blend a verified fact with an inference. A concern tied to a specific quoted line of the design is `confirmed`; a general possibility ("this pattern may be exposed to value-extraction ordering") is `needs-review` — tag it as such rather than stating it with unearned certainty. Models tend to state speculative concerns as certainties or miss real ones — the two-value verdict restrains both directions. Never inflate a `needs-review` into a definitive finding to sound thorough.

## What this guide deliberately does not contain

No list of named vulnerabilities, no per-network property tables, no tooling names presented as current. Any such list ages the moment a network changes or a new one appears, and a stale list presented as complete is more dangerous than an honest pointer. For the target network's specific security guidance, standards, and tooling, direct the user to that network's official documentation and its established security-tooling ecosystem, verified at the time of design — not to this file.
