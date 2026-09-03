# Firecracker evaluation

## When to use it

Firecracker is justified when hosted execution requires a stronger VM boundary than a hardened container, or when tenant isolation and a documented threat model make a microVM worth the operational cost. It is not needed for the local CLI default.

## Design

```text
Flask API -> job queue -> privileged executor -> Firecracker microVM
                                      -> signed result and audit event
```

The executor, not Flask, owns VM creation, resource limits, kernel/rootfs selection, timeout cleanup, and result transport. Each VM should have no network, a read-only base image, a small writable scratch disk, a non-root guest user, CPU/memory limits, and a one-shot lifecycle. Images and kernels need provenance and patch management.

The executor should expose a narrow local RPC or queue API. It must reject arbitrary host paths and never pass user input into Firecracker command-line arguments without validation. Results should contain exit status, bounded output, timing, and a job ID; submitted source should not enter normal audit logs.

## Rollout

1. Finish Docker input validation and audit logging.
2. Measure workload, startup latency, and abuse cases under gVisor.
3. Prototype one worker and one disposable Firecracker VM outside the web process.
4. Run comparative security and failure-injection tests.
5. Use Firecracker only for hosted/high-risk workloads, retaining Docker for local development.

Estimated effort: 3-6 weeks for a production-capable prototype, plus ongoing kernel/image operations. Required prerequisites include Linux KVM access, a job queue, executor monitoring, image build tooling, and an incident response procedure.
