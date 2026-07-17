# CI/CD Pipeline Design Guide

Use this guide when executing Stage 6c — CI/CD Pipeline Design. It defines how to select a platform, structure pipeline stages, choose a branching strategy, and document the result.

---

## 1. Platform Selection

| Platform                     | Best for                                                              |
|------------------------------|-----------------------------------------------------------------------|
| GitHub Actions               | GitHub-hosted repos; large action marketplace; generous free tier     |
| GitLab CI/CD                 | GitLab-hosted repos; built-in registry; strong pipeline visualization |
| CircleCI                     | Complex parallel workflows; orb ecosystem                             |
| Jenkins                      | Existing Jenkins investment; self-hosted requirement                  |
| AWS CodePipeline + CodeBuild | AWS-native; integrates with ECR, ECS, CodeDeploy                      |
| Azure DevOps Pipelines       | Azure-native projects                                                 |
| Argo CD                      | GitOps pull-based CD for Kubernetes workloads (pair with any CI)      |
| Flux CD                      | GitOps pull-based CD; Kubernetes-native (pair with any CI)            |

**Decision rules — apply in order:**

1. Source code on GitHub → **GitHub Actions** (default)
2. Source code on GitLab → **GitLab CI/CD**
3. Kubernetes deployment target → consider **Argo CD or Flux CD** for the CD leg (any CI tool for the CI leg)
4. AWS-native with CodeDeploy → **AWS CodePipeline**
5. Azure-native → **Azure DevOps**
6. Strong existing Jenkins investment → **Jenkins** (with caution — high maintenance)

---

## 2. Standard Pipeline Stages

Template for a backend API service. Adapt to the actual tech stack — omit stages that don't apply (e.g., no integration test stage for a stateless function-only service).

| Stage                | Trigger                             | Tool examples                                                    | Gate / fail condition                             |
|----------------------|-------------------------------------|------------------------------------------------------------------|---------------------------------------------------|
| Lint & format        | Every push / PR                     | ESLint, Ruff, golangci-lint, Prettier                            | Any lint error                                    |
| Unit tests           | Every push / PR                     | Jest, pytest, go test, JUnit                                     | Any test failure or coverage drop below threshold |
| Build artifact       | Every push to main; every tag       | Docker build, `go build`, Maven                                  | Build error                                       |
| Integration tests    | After build, on PR and main         | Docker Compose test environment, Testcontainers                  | Any test failure                                  |
| Security scan        | After build                         | Trivy (images), Semgrep / Snyk (SAST), OWASP ZAP (DAST for APIs) | Critical CVE or high-severity SAST finding        |
| Push artifact        | After security scan passes, on main | ECR, GCR, GHCR, Docker Hub                                       | Registry push error                               |
| Deploy → dev         | Auto on main merge                  | ECS deploy, Helm upgrade, Terraform apply                        | Health check fails                                |
| Smoke test (dev)     | After deploy → dev                  | `curl` / Playwright / k6 smoke                                   | Key endpoint unreachable                          |
| Deploy → staging     | Auto after dev smoke passes         | Same as dev                                                      | Health check fails                                |
| Smoke test (staging) | After deploy → staging              | Same as dev                                                      | Key endpoint unreachable                          |
| Deploy → prod        | Manual approval gate or version tag | Same as dev                                                      | Health check fails                                |
| Smoke test (prod)    | After deploy → prod                 | Same as dev                                                      | Key endpoint unreachable                          |

---

## 3. Branching Strategy

| Strategy                | When to use                                                               | Branch model                                               |
|-------------------------|---------------------------------------------------------------------------|------------------------------------------------------------|
| Trunk-based development | Small team, high deployment frequency, feature flags available            | All devs commit to `main`; short-lived branches (<1 day)   |
| GitHub Flow             | Most teams — simple, effective, **default recommendation**                | `main` is always deployable; feature branches → PR → merge |
| GitFlow                 | Scheduled releases (weekly/monthly), hotfix discipline needed, large team | `main` + `develop` + `release/*` + `hotfix/*` branches     |

**Default recommendation:** GitHub Flow. Feature branch → PR with CI → merge to main → auto-deploy.

---

## 4. Environment Promotion

| Environment | Trigger                               | Gate                                 | Rollback                                                               |
|-------------|---------------------------------------|--------------------------------------|------------------------------------------------------------------------|
| dev         | Auto on every merge to main           | None                                 | Re-deploy previous image tag                                           |
| staging     | Auto after dev smoke tests pass       | Automated smoke tests must pass      | Re-deploy previous image tag                                           |
| prod        | Manual approval (or version tag `v*`) | Manual gate + post-deploy smoke test | Re-deploy previous image tag; use blue/green if zero-downtime required |

For blue/green or canary deployments in prod: document the traffic-shift percentage and observation window before full cutover.

---

## 5. Secret Injection

Never commit secrets to version control. Standard injection patterns:

| Platform               | Secret source                                   | How                                                   |
|------------------------|-------------------------------------------------|-------------------------------------------------------|
| GitHub Actions         | GitHub Encrypted Secrets                        | `${{ secrets.MY_SECRET }}` in workflow                |
| GitHub Actions (cloud) | OIDC → AWS Secrets Manager / GCP Secret Manager | `aws-actions/configure-aws-credentials` with role ARN |
| GitLab CI              | GitLab CI/CD Variables                          | Masked variables in group or project settings         |
| GitLab CI (cloud)      | OIDC → cloud provider                           | ID token with `aud` claim                             |
| AWS CodePipeline       | AWS Secrets Manager / Parameter Store           | IAM role for CodeBuild, `aws ssm get-parameter`       |
| Kubernetes / Argo CD   | External Secrets Operator                       | Syncs from AWS SM / GCP SM / Vault into K8s Secrets   |

**Prefer OIDC over long-lived credentials** wherever supported (GitHub Actions ↔ AWS, GCP, Azure). OIDC issues short-lived tokens — no key rotation required.

---

## 6. Artifact Management

| Artifact type | Store                               | Versioning                                            | Retention                                         |
|---------------|-------------------------------------|-------------------------------------------------------|---------------------------------------------------|
| Docker images | ECR / GCR / GHCR / Docker Hub       | `git-sha` tag for traceability; `latest` only for dev | Keep last 30 images; delete untagged after 7 days |
| Binary / JAR  | S3 / GCS / Azure Blob / Artifactory | `<version>-<git-sha>`                                 | Keep last 20 releases                             |
| Test reports  | CI platform artifact store          | Per run                                               | 90 days                                           |

Tag images with the full git SHA (`git rev-parse --short HEAD`) so any deployed container can be traced back to an exact commit.

---

## 7. What to include in the architecture document

CI/CD section (section 9) should contain:

1. **Platform selection** — CI platform + CD platform (if separate), with justification citing constraints from stages 3–5
2. **Pipeline stages table** — adapted from the standard template above; one row per stage, with tool, trigger, and gate
3. **Branching strategy** — strategy name and why it fits the team size and release cadence
4. **Environment promotion rules** — trigger and gate per environment; rollback procedure
5. **Secret injection approach** — what secrets are needed, where they are stored, how they reach the pipeline; confirm no long-lived credentials in code or CI config
6. **Artifact management** — registry choice, tag scheme, retention policy
