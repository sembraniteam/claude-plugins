# Infrastructure as Code Guide

Use this guide when executing Stage 6b — IaC Design. It defines how to select a tool, structure the codebase, manage state, and decide what to document in the architecture document.

---

## 1. Tool Selection

| Tool                            | Best for                                                                                                                                    | Language                     | State backend                                                                                                                   |
|---------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------|------------------------------|---------------------------------------------------------------------------------------------------------------------------------|
| Terraform                       | Multi-cloud, largest ecosystem, most examples                                                                                               | HCL                          | S3 + DynamoDB (AWS), GCS (GCP), Azure Blob (Azure), Terraform Cloud                                                             |
| OpenTofu                        | Terraform OSS fork — BSL-free, drop-in replacement                                                                                          | HCL                          | Same as Terraform                                                                                                               |
| Pulumi                          | Developer-centric teams who prefer code over config                                                                                         | TypeScript, Python, Go, .NET | Pulumi Cloud, S3, GCS, Azure Blob                                                                                               |
| AWS CDK                         | AWS-only projects with TypeScript or Python teams                                                                                           | TypeScript, Python, Java, Go | CloudFormation (managed by AWS)                                                                                                 |
| CloudFormation                  | AWS-only with no extra tooling requirement                                                                                                  | YAML / JSON                  | Managed by AWS                                                                                                                  |
| Bicep                           | Azure-only projects                                                                                                                         | DSL                          | ARM (managed by Azure)                                                                                                          |
| Ansible (+ Terraform if hybrid) | On-premise / self-hosted / bare metal — Stage 3's "on-premise or bare metal" answer, or `tech-stacks.md`'s self-hosted stack recommendation | YAML                         | Git-tracked playbooks/inventory (no cloud state backend); add Terraform's own backend only for the hybrid-cloud portion, if any |

**Decision rules — apply in order:**

1. If Stage 3's infrastructure constraint is on-premise, bare metal, or self-hosted with no cloud component → **Ansible** (configuration management, not provisioning — there's no cloud API to provision against). If a portion is hybrid-cloud, add Terraform for that portion only per rule 6 below.
2. If the requirements include multi-cloud or cloud-agnostic as a constraint → **Terraform / OpenTofu**
3. If the team is developer-first and dislikes HCL syntax → **Pulumi**
4. If AWS-only and the team has strong TypeScript or Python → **AWS CDK**
5. If AWS-only and the team wants no extra tooling → **CloudFormation**
6. If Azure-only → **Bicep**
7. Default for all other cases → **Terraform** (largest community, most provider coverage, most hiring pool)

---

## 2. State Backend

Always use a remote state backend. Never commit state files to version control.

| Tool                            | Recommended backend                               | Locking                    |
|---------------------------------|---------------------------------------------------|----------------------------|
| Terraform / OpenTofu (AWS)      | S3 bucket + DynamoDB table                        | DynamoDB conditional write |
| Terraform / OpenTofu (GCP)      | GCS bucket                                        | GCS object locking         |
| Terraform / OpenTofu (Azure)    | Azure Blob Storage + Azure Table Storage          | Blob lease                 |
| Terraform Cloud / HCP Terraform | Built-in                                          | Built-in                   |
| Pulumi                          | Pulumi Cloud (default) or S3/GCS/Azure Blob       | Platform-managed           |
| AWS CDK                         | CloudFormation (managed by AWS, no config needed) | CloudFormation stack lock  |

---

## 3. Module / Stack Structure

**This structure is for cloud deployments.** For an Ansible-based on-premise/self-hosted setup (tool selection rule 1 above), organize by `roles/` (one per service — e.g. `roles/database/`, `roles/app-server/`) and `inventory/` (per-environment host lists) instead of the `modules/`/`environments/` split below; state/locking concerns don't apply since there's no remote backend to manage.

Organize by infrastructure concern, not by resource type. Standard layer split:

```
infra/
├── modules/
│   ├── network/        VPC · subnets · security groups · NAT gateway · peering
│   ├── compute/        ECS/EKS cluster · autoscaling group · load balancer · target groups
│   ├── database/       RDS/Cloud SQL · parameter group · subnet group · backup config
│   ├── cache/          ElastiCache / Redis · replication group
│   ├── storage/        S3 buckets · lifecycle rules · bucket policies
│   ├── messaging/      SQS · SNS · EventBridge rules (if async)
│   └── monitoring/     CloudWatch dashboards · alarms · Grafana agent · Datadog integration
├── environments/
│   ├── dev/            tfvars or config overrides for dev
│   ├── staging/
│   └── prod/
└── backend.tf          remote state config (Terraform) or Pulumi.<stack>.yaml
```

Tailor this to the actual infrastructure from Stage 5 — omit modules for services not in scope (e.g., no `messaging/` for a monolith with no async).

---

## 4. Environment Strategy

| Approach                  | When to use                                                     | Trade-offs                                                                 |
|---------------------------|-----------------------------------------------------------------|----------------------------------------------------------------------------|
| Terraform workspaces      | Identical infra shape per env, single state backend, small team | Simple; risky if envs diverge (same module code, just different vars)      |
| Directory-per-environment | Different infra sizing per env (prod is HA, dev is single-node) | Explicit, safe for destructive ops, easy to diff — **recommended default** |
| Separate repos            | Strict access control, separate blast radius per env            | Maximum isolation; highest maintenance overhead                            |

**Default recommendation:** directory-per-environment. It makes env differences explicit and prevents accidental `terraform destroy` on prod when targeting dev.

---

## 5. Drift Detection

Infrastructure drifts when someone changes a resource manually (console, CLI) outside IaC. Detect it:

- **CI plan runs**: on every PR, run `terraform plan` (or equivalent) against the current state. A non-empty plan on a no-change branch means drift.
- **Scheduled scans**: run `terraform plan` on a cron (nightly) in CI and alert on unexpected diffs.
- **Terraform Cloud / HCP Terraform**: built-in drift detection dashboard.
- **Pulumi Drift**: `pulumi refresh` followed by `pulumi preview`; automate in CI.

---

## 6. What to include in the architecture document

IaC section (section 8) should contain:

1. **Tool selection** — tool name and version, why it was chosen (cite constraints from stages 3–5)
2. **State backend** — backend type, bucket/container name convention, locking mechanism
3. **Module breakdown table** — one row per module:

   | Module   | Provisions                                       | Dev variation           | Prod variation               |
   |----------|--------------------------------------------------|-------------------------|------------------------------|
   | network  | VPC, 2 public + 2 private subnets, NAT gateway   | Single AZ               | Multi-AZ                     |
   | compute  | ECS Fargate cluster, ALB, target group           | 1 task, no autoscaling  | 2–10 tasks, autoscaling      |
   | database | RDS PostgreSQL 16, subnet group, parameter group | db.t3.micro, no replica | db.r7g.large, 1 read replica |

4. **Environment strategy** — which approach and why
5. **Drift detection** — how and how often
