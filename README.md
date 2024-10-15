## Setup

explain all the previous stuff


### Env setup: secrets, links and data

To set everything up, use a terminal (jump in with `make term`). It will use in-cluster env config for proper prefect blocks creation. This is a workaround since i got frustrated at prefect kubernetes worker job setup, which would allow for the proper solution that works in all cases by prepopulating all the connectivity-critial values right from the k8s configmap. TODO: actually do that
For now:
1. `make term`
2. `python create_secrets.py`
3. `python create_data.py`

## Plan

- Currently, services are stuck together through prefect blocks, which creates a second source of truth along with env variables. Some code uses env vars, some uses blocks, and i just got lucky to have the concers separable for now - bad idea, it will break. I should unify that by moving to env vars for everything that is env-dependent. Whats env-dependent? The source of truth for the infra setup is the configmap from the infra repo, but that truth must be overriden when im port-forwarding onto the host (UI only works on the host and some buggy-looking hardcodes inside prefect orion force me to keep port-forwarding). Thus, the urls must be managed by an env var that comes from a configmap in the cluster and a .env file on the host

- Mess around and find out: fix bugs and run the pipelines - that will reveal versioning problems and will open the way to buttoning up the service releases
