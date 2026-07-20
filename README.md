# Real-Time Market Data Platform

A Python-based real-time market data pipeline with anomaly detection,
lineage tracking, and agentic incident enrichment.

## Why staging tables are separate

**Cadence:** Ticks arrive thousands per second, reference data once or twice daily, 
corporate actions irregularly. A shared table's three write patterns are completely different.

**Retention:** All three need history, but different kinds — ticks are an append-only 
event log retained for days/weeks for debugging, constituents are versioned snapshots 
retained indefinitely for point-in-time lookups, corporate actions are an ordered 
log kept permanently for audit. One retention policy cannot serve all three.

**Access patterns:** Ticks are queried by ticker + time range, reference data by 
index_id + effective_date. 
Different query shapes need different indexes and partitioning strategies.

**Correctness:** Ticks can arrive late or out of order — you take the latest. 
Corporate actions must be applied in exact sequence. One table cannot enforce 
both "order doesn't matter" and "order is critical."

**Schema:** Ticks are flat, reference data is a nested snapshot 
(one-to-many with constituents), corporate actions have conditional fields 
(ratio only for splits, index_id only for additions/removals). A shared table 
means nullable columns everywhere, destroying validation guarantees.