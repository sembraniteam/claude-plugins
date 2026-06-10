# Observability Guide

A reference for designing the observability stack in a software architecture. Use when filling out the "Observability Strategy" section of each architecture option.

---

## The Three Pillars of Observability

Every production system needs all three:

| Pillar      | What it answers                                   | Tooling layer               |
|-------------|---------------------------------------------------|-----------------------------|
| **Logs**    | What happened? What was the event context?        | Loki, ELK, ClickHouse       |
| **Metrics** | How is the system performing over time?           | Prometheus, VictoriaMetrics |
| **Traces**  | How did a single request flow through the system? | Jaeger, Tempo, Zipkin       |

A fourth dimension increasingly added:

| Pillar        | What it answers                       | Tooling          |
|---------------|---------------------------------------|------------------|
| **Profiling** | Where is CPU/memory time being spent? | Pyroscope, Parca |

---

## Instrumentation Standard: OpenTelemetry

**OpenTelemetry (OTel)** is the CNCF standard for instrumenting code to produce logs, metrics, and traces. It is vendor-neutral — instrument once, export to any backend.

**Why OpenTelemetry over vendor SDKs**:
- Switch backends without re-instrumenting code (avoid vendor lock-in)
- Single SDK for all three signals (logs, metrics, traces)
- Wide language support: Go, Java, Python, Node.js, .NET, Rust, PHP, Ruby
- Auto-instrumentation for most frameworks (HTTP, gRPC, databases) with zero code changes
- CNCF-graduated project — long-term stability guaranteed

**Architecture**:
```
Application → OTel SDK → OTel Collector → Backend (SigNoz / Grafana / Datadog / etc.)
```

**OTel Collector roles**:
- Receives telemetry from SDKs (OTLP protocol)
- Processes/enriches data (add k8s labels, filter noise, sample traces)
- Exports to one or many backends simultaneously
- Acts as a buffer during backend outages

**Sampling strategies** (critical for high-traffic systems):
- **Head-based**: Decision made at trace start (random %, fast but may miss errors)
- **Tail-based**: Decision made after trace completes (can always keep error traces, more memory-intensive)
- Recommended: Head-based for >1k req/s, tail-based for systems where errors must never be dropped

---

## Logging

### Grafana Loki
**Best for**: Log aggregation alongside Grafana metrics dashboards; Kubernetes-native environments.

**Strengths**: Lightweight (indexes labels, not full text), integrates tightly with Grafana and Tempo, cost-effective at scale, works with Promtail/Vector/Fluentbit for log shipping.

**Weaknesses**: Full-text search is slower than Elasticsearch (requires streaming search over chunks), not suitable as primary search engine for log analytics.

**When to choose**: Kubernetes environments with Grafana stack; cost-sensitive deployments; full-text log search is not required.

---

### Elasticsearch / OpenSearch (ELK Stack)
**Best for**: Full-text search on logs, complex log analytics, existing Elastic infrastructure.

**Strengths**: Powerful full-text search, rich aggregation/analytics, Kibana visualization.

**Weaknesses**: Operationally heavy (JVM, cluster management), expensive at petabyte scale.

**When to choose**: Compliance-heavy environments needing advanced log search; teams already running Elasticsearch.

---

### ClickHouse for Logs
**Best for**: High-volume log ingestion with fast analytics queries; cost-effective alternative to Elasticsearch at scale.

**Strengths**: Excellent compression (logs compress 10–20×), extremely fast aggregation queries, SQL interface, scales to hundreds of TB affordably.

**When to choose**: When log volume is large and full-text search is less important than analytics (e.g., "how many 5xx errors in the last hour by service?"). SigNoz uses ClickHouse for this reason.

---

## Metrics

### Prometheus
**Best for**: Time-series metrics for services, infrastructure, and Kubernetes.

**Strengths**: Pull-based scraping, powerful PromQL query language, huge ecosystem of exporters, de-facto standard for Kubernetes metrics.

**Weaknesses**: Local storage only (single-node by default), not designed for long-term storage at scale without Thanos/Cortex/Mimir.

**When to choose**: All architectures where Kubernetes or Docker is used. Prometheus is the default metrics layer — add Thanos or Mimir for long-term remote storage.

---

### VictoriaMetrics
**Best for**: Drop-in Prometheus replacement with better performance and long-term storage built-in.

**Strengths**: PromQL compatible, 10× better compression than Prometheus, single binary, built-in long-term storage, handles millions of time series efficiently.

**When to choose**: When long-term storage is needed without the operational complexity of Thanos, and PromQL compatibility is required. Excellent cost/performance ratio.

---

### Grafana Mimir
**Best for**: Horizontally scalable, multi-tenant Prometheus-compatible metrics storage.

**When to choose**: Very large scale (billions of active time series), multi-tenant SaaS platforms.

---

## Distributed Tracing

### Jaeger
**Best for**: Distributed tracing in microservices, request flow visualization.

**Strengths**: CNCF-graduated, OpenTelemetry-native, mature, supports Cassandra/Elasticsearch/ClickHouse backends.

**Weaknesses**: UI is functional but not as polished as commercial tools.

**When to choose**: Self-hosted distributed tracing when Grafana Tempo is not the stack.

---

### Grafana Tempo
**Best for**: Distributed tracing tightly integrated with Grafana + Loki + Prometheus (the Grafana stack).

**Strengths**: Cost-effective (stores traces as objects in S3/GCS/MinIO, no indexing), integrates trace→log correlation in Grafana, scales well.

**When to choose**: Grafana stack environments. Tempo + Loki + Prometheus + Grafana = complete self-hosted observability.

---

### Zipkin
**Best for**: Simpler microservices environments needing distributed tracing.

**Weaknesses**: Less feature-rich than Jaeger/Tempo; less active development.

---

## All-in-One Observability Backends

### SigNoz (Open-Source)
**What it is**: Full-stack observability platform — logs, metrics, traces in one UI. Built on ClickHouse (storage) + OpenTelemetry (instrumentation).

**Strengths**:
- Single platform for all three pillars (replace Datadog/New Relic with self-hosted open-source)
- OpenTelemetry-native (designed around OTel from the start)
- ClickHouse backend → excellent performance and cost at scale
- Actively developed, strong community

**Self-hosted**: Yes (Docker Compose or Kubernetes). Also offers SigNoz Cloud.

**When to choose**: Teams wanting a self-hosted, open-source Datadog alternative. Best choice for new projects that want all three signals in one place without vendor lock-in.

**Future impact**: Low vendor risk (open-source, self-hosted). ClickHouse backend means growing log/trace volumes are cost-effective.

---

### Uptrace (Open-Source)
**What it is**: OpenTelemetry-based observability backend with logs, metrics, traces, and exceptions.

**Strengths**: OpenTelemetry-native, built on ClickHouse, supports Prometheus metrics (compatible with existing Prometheus exporters), clean UI.

**Self-hosted**: Yes (single Docker image, very easy to set up).

**When to choose**: Smaller teams wanting a lightweight all-in-one with minimal ops overhead. Simpler to operate than SigNoz.

---

### Grafana Stack (Loki + Tempo + Mimir + Grafana)
**What it is**: Composable open-source observability stack: Loki (logs) + Tempo (traces) + Prometheus/Mimir (metrics) + Grafana (visualization).

**Strengths**: Each component is best-in-class for its pillar; highly composable; Grafana is the most widely used dashboard tool; large ecosystem.

**Weaknesses**: More components to operate vs. SigNoz/Uptrace; trace-log correlation requires configuration; more complex setup.

**Self-hosted**: Yes. Also, Grafana Cloud (managed).

**When to choose**: Teams already using Grafana for metrics who want to add logs (Loki) and traces (Tempo) to the same platform. Good for Kubernetes-native environments. Best for maximum flexibility and composability.

---

### Datadog (Commercial)
**Strengths**: Best-in-class APM, log analytics, infrastructure monitoring, anomaly detection, 500+ integrations, excellent UX.

**Weaknesses**: Very expensive at scale (pricing based on hosts + log volume + trace volume), significant vendor lock-in.

**When to choose**: Teams with budget and need for best-in-class tooling without ops overhead. Common in enterprise.

---

### New Relic (Commercial)
**Strengths**: Full-stack observability, generous free tier (100GB/month), OpenTelemetry support.

**When to choose**: Teams wanting a managed platform with a usable free tier for smaller systems.

---

### Honeycomb (Commercial)
**Best for**: High-cardinality distributed tracing and event-driven observability.

**When to choose**: Complex distributed systems where trace cardinality is extremely high (millions of unique attribute combinations).

---

## Recommended Stacks by Architecture Tier

| Tier                 | Instrumentation      | Logs                       | Metrics                       | Traces              | Unified Dashboard       |
|----------------------|----------------------|----------------------------|-------------------------------|---------------------|-------------------------|
| **Lean**             | OTel SDK (basic)     | Loki + Promtail            | Prometheus + Grafana          | Tempo               | Grafana                 |
| **Standard**         | OTel SDK             | Loki                       | Prometheus + VictoriaMetrics  | Tempo               | Grafana or SigNoz       |
| **Advanced**         | OTel SDK + Collector | Loki / ClickHouse          | VictoriaMetrics / Mimir       | Tempo / Jaeger      | SigNoz or Grafana Stack |
| **Budget-first**     | OTel SDK             | Uptrace (built-in)         | Uptrace (built-in)            | Uptrace (built-in)  | Uptrace                 |
| **Enterprise**       | OTel SDK             | Datadog                    | Datadog                       | Datadog APM         | Datadog                 |
| **Serverless/Cloud** | OTel SDK             | CloudWatch / Cloud Logging | CloudWatch / Cloud Monitoring | X-Ray / Cloud Trace | Managed                 |

---

## Observability Stack Components Summary

```
Instrumentation (code level)
  └── OpenTelemetry SDK (Go / Node / Python / Java / Rust / ...)
       └── OTel Collector (pipeline, sampling, routing)
            ├── Logs → Loki / Elasticsearch / ClickHouse
            ├── Metrics → Prometheus / VictoriaMetrics / Mimir
            └── Traces → Jaeger / Tempo / Zipkin

Unified backends (logs + metrics + traces together):
  ├── Self-hosted open-source: SigNoz, Uptrace, Grafana Stack
  └── Managed/commercial:      Datadog, New Relic, Honeycomb
```

---

## Alerting

| Tool                        | Use Case                                        |
|-----------------------------|-------------------------------------------------|
| **Prometheus Alertmanager** | Metric-based alerts → Slack, PagerDuty, email   |
| **Grafana Alerting**        | Multi-signal alerts (metrics + logs) in Grafana |
| **SigNoz Alerts**           | Built-in alerts on logs, metrics, traces        |
| **PagerDuty / OpsGenie**    | Incident management and on-call routing         |
| **Uptime Kuma**             | Lightweight self-hosted uptime monitoring       |

---

## Minimum Viable Observability (for MVP / Lean)

Even simple monoliths should have at minimum:

1. **Structured logging** (JSON to stdout) → collected by Promtail → stored in Loki
2. **Prometheus metrics** endpoint (`/metrics`) → scraped by Prometheus
3. **Grafana dashboard** — request rate, error rate, latency (RED method)
4. **One alert**: error rate > 1% for 5 minutes → Slack notification

This requires no code changes for most frameworks — just configuration.
