# RAG Architecture Notes

## The RAG Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│  INDEXING (one-time)                                            │
│  ┌──────────┐    ┌────────────────┐    ┌──────────────────┐    │
│  │ PDF docs │ → │ Embedding Model │ → │ Vectors in Qdrant │    │
│  └──────────┘    └────────────────┘    └──────────────────┘    │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  QUERYING                                                       │
│  ┌───────┐    ┌────────────────┐    ┌─────────────────────┐    │
│  │ Query │ → │ Embedding Model │ → │ Find similar vectors │    │
│  └───────┘    └────────────────┘    └──────────┬──────────┘    │
│                                                 ↓               │
│                                      ┌──────────────────┐       │
│                                      │ Retrieved chunks │       │
│                                      └────────┬─────────┘       │
│                                               ↓                 │
│                               ┌───────────────────────────────┐ │
│                               │ LLM generates answer from     │ │
│                               │ query + retrieved chunks      │ │
│                               └───────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Key Insight: Embeddings and LLM Are Independent

| Step | Purpose | Constraint |
|------|---------|------------|
| Embedding | Convert text → vector for similarity search | Must use **same** embedding model for indexing AND querying |
| LLM | Read retrieved text, generate answer | Can be **anything** - doesn't care how you found the text |

The LLM just sees: "Here's a question and some relevant text chunks, write an answer."
It has no idea what embedding model found those chunks.

You can mix providers (e.g., Ollama embeddings + Claude LLM).

---

## What Does the LLM Actually Do?

### Without LLM (just embeddings)

**Query:** "What happens if I steal from a sept?"

**Result:** Raw text chunks ranked by similarity:
```
1. "Those who steal from a sept can be considered to have stolen from
   the gods, and thus receive a harsher punishment."
2. "It is customary for a thief to be punished by losing a finger or a hand."
3. "Pickpockets can likewise be punished by cutting off a hand."
```

That's it. Just search results. You read them yourself.

### With LLM

**Query:** "What happens if I steal from a sept?"

**Result:**
```
Stealing from a sept is considered stealing from the gods themselves,
which carries a harsher punishment than ordinary theft. While regular
theft typically results in losing a finger or hand, theft from a sept
would likely result in more severe consequences.

[Citations: Section 6.1, 6.3]
```

### The LLM's job:
- **Synthesize** multiple chunks into a coherent answer
- **Reason** - "harsher than X" requires knowing what X is
- **Answer the actual question** rather than just showing matches
- **Say "I don't know"** if the chunks don't contain the answer

**Embeddings = search engine**
**LLM = the person who reads the search results and writes you a summary**

---

## Why Not Just Feed the Whole Document to the LLM?

For a tiny 2-page PDF, you could! But RAG exists for scale.

| Approach | Pros | Cons |
|----------|------|------|
| **Just feed doc to LLM** | Simple, no pipeline | Context limits, cost, speed |
| **RAG (embed + retrieve + LLM)** | Scales to huge docs | More complex |

### The real constraints:

**1. Context window limits**
- Claude: ~200K tokens (~150K words)
- GPT-4: ~128K tokens
- laws.pdf: ~800 words - fits easily
- Real regulatory docs: thousands of pages - doesn't fit

**2. Cost**
- LLMs charge per token
- Feeding 500 pages per query = expensive
- RAG: feed only the 3 relevant paragraphs = cheap

**3. "Lost in the middle" problem**
- LLMs get worse at finding info buried in long contexts
- RAG puts the relevant stuff front and center

**4. Speed**
- Processing 3 paragraphs: fast
- Processing 500 pages: slow

---

## TL;DR

RAG is overkill for 2 pages, essential for 2000 pages.

For this exercise, the point is to learn the RAG pipeline because that's what
production legal/compliance systems actually need.
