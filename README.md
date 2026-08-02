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

## Why event-driven, not cron

**latency**
Since producers are random events, consumers also has to event driven, to avoid any kind of latency between producer and consumer.
Tick data particularly is very time sensitive and it has to processed as soon as it is created.

**ordering** 
Another advantage of kafka here is to control the ordering alongside running parallelism.
so we definately know for every type of event what ordering is expected.
for example, for corporate actions, its very important that they are applied/stored in the order they come
so every index/ticker can be act as a key for kafka so that ordering will be preserved while multiple tickers can be consumed in parallel.

**back-pressure**
Kafka naturally provides backpressure here.
In case of cron job, we have to do entire mechanism of saving the data first in DB and then processing it as per downstream's capability.

**correctness**
As mentioned earlier, these are random events occuring throughout the day.
A cron job polling every 5 minutes could miss a stock split announced and effective within that window, or process a removal before an addition that was announced first, breaking the index composition
