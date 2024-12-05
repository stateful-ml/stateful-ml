# Stateful ML
This is the central monorepo of the example project. Please look at the [infra](https://github.com/stateful-ml/infra) repo to see the setup in practice, but the main idea is:
- This repo contains the code for the services and pipelines of the project
- Dedicated ml repos do nasty ml things without polluting this repo's history and having complete freedom in mlflow-style modeling lifecycle
- A dedicated deployment manager repo turns mlflow-style into actually-safe-for-production-style by recording the combination of versions deployed at any given moment in any environment (e.g. code version 1.2.3, this model version 42, that model version 15, the other model version 301)
- The state here is a set of tables per release, it is kept in a dedicated database schema, allowing point in time operations and instant recovery to a working state even if it takes massive amount of time to build it the first time.

## Overengineered?
Yes, on purpose. This is preparation for the worst case scenario, it coordinates the deployment of a single system with many models that cant or shouldnt have their own tiny deployment code. Imagine a stateful LLM agent with a lot of LORAs that are deployed together and all contribute to a shared state of a conversation with a user. Or a recommender where serving code must be aware of the embedder specifics but also has a reranker strapped to it.
I expect that, in reality, this setup can be collapsed into one of its simpler special cases:

### Special case 1: Model-centric monorepo
The most obvious option:
- absorb modelling into a `models/` directory in the same repo
- version models in mlflow
- version only code in git
- during ci, pull the latest model(s) version(s) and create a tag of the form `<code-version>-<model1-version>-<modeln-version>`
- suffix with rc for staging or have multistage ci
- tolerate having slightly confusing identical code version tags on different (!) commits when serving code doesnt change but models are iterated on.
This removes the deployment manager by tracking working system states directly in tags. And it removes separate repos, which leaves us with a bulky but working thing with hopefully low cognitive overhead

### Special case 2: Just ditch the deployment manager
If we really dont like stray modelling commits ticking the serving history forward (i actually want to puke a little bit when i see that), we can keep the separate model repos.
- version models in mlflow in their respective training repos
- version serving code in its own repo
- during ci, pull the latest model(s) version(s) and create a tag of the form `<code-version>-<model1-version>-<modeln-version>`
- suffix with rc for staging or have multistage ci
- A single serving repo commit will have potentially multiple model version tags, e.g. `v1.2.3-model1v42-model2v45`, `v1.2.3-model1v43-model2v52`, `v1.2.3-model1v44-model2v77`
This removes the deployment manager by tracking working system states directly in tags. It saves people from confusion of many commits representing identical serving code tag

### Special case 3: Code-centric monorepo
Alternatively, we could commit the mlops crime of coupling model versions to code, and call modelling efforts a minor change. This will simplify all kinds of things and, in cases when modelling is minimal but business sways and pivots are substantial, seems like a very clean option.
- absorb modelling into a models/ directory in the same repo
- version only code in git
- version models in mlflow for convenience but couple the versions to code
- during ci, pull the latest model(s) version(s), just log them / pass them around in env variables but keeps tags simply `<joint-version>`. (Since models changes cause a bump, remember?)
- suffix with rc for staging or have multistage ci. Here deployment flexibility is maximised since the complete state of the system is in front of you yet no sub-version tracking is required.
- tolerate breaking the oath of keeping code version and model version separate.


## Setup

### Env setup: secrets, links and data

To set everything up, use a terminal (jump in with `make term`). It will use in-cluster env config for proper prefect blocks creation. This is a workaround since i got frustrated at prefect kubernetes worker job setup, which would allow for the proper solution that works in all cases by prepopulating all the connectivity-critial values right from the k8s configmap. TODO: actually do that
For now:
1. `make term`
2. `python create_secrets.py`
3. `python create_data.py`

## Plan

### Pipelines
- Currently, services are stuck together through prefect blocks, which creates a second source of truth along with env variables. Some code uses env vars, some uses blocks, and i just got lucky to have the concers separable for now - bad idea, it will break. I should unify that by moving to env vars for everything that is env-dependent. Whats env-dependent? The source of truth for the infra setup is the configmap from the infra repo, but that truth must be overriden when im port-forwarding onto the host (UI only works on the host and some buggy-looking hardcodes inside prefect orion force me to keep port-forwarding). Thus, the urls must be managed by an env var that comes from a configmap in the cluster and a .env file on the host

- Mess around and find out: fix bugs and run the pipelines - that will reveal versioning problems and will open the way to buttoning up the service releases
