# Stateful ML
This is the central monorepo of the example project. Please look at the [infra](https://github.com/stateful-ml/infra) repo to see the setup in practice, but the main idea is:
- This repo contains the code for the services and pipelines of the project
- Dedicated ml repos do nasty ml things without polluting this repo's history and having complete freedom in mlflow-style modeling lifecycle
- A dedicated deployment manager repo turns mlflow-style into actually-safe-for-production-style by recording the combination of versions deployed at any given moment in any environment (e.g. code version 1.2.3, this model version 42, that model version 15, the other model version 301)
- The state here is a set of tables per release, it is kept in a dedicated database schema, allowing point in time operations and instant recovery to a working state even if it takes massive amount of time to build it the first time.

## Overengineered?
Yes, on purpose. This is preparation for the worst case scenario, it coordinates the deployment of a single system with many models that cant or shouldnt have their own tiny deployment code. Imagine a stateful LLM agent with a lot of LORAs that are deployed together and all contribute to a shared state of a conversation with a user. Or a recommender where serving code must be aware of the embedder specifics but also has a reranker strapped to it.
I expect that, in reality, this setup can be collapsed into one of its simpler special cases:

### Special case 1: Treating models as dependencies
The cleanest option, but requires courage to ditch some minor mlflow suggestions:
- version models in mlflow and their code in respective model repos
- version service code in the main repo in git
- version models you want to use in your code in a config and disregard mlflow model lifecycle management
- absorb modelling into a `models/` directory as submodules if you plan on changing model apis and you need to import them at static analysis time
- treat model bumps as minor change and have a single semver code repo version
- suffix that verion with rc for staging
- remove the deployment manager, it is now the main repo itself
- tolerate the fact that you cant initiate deployment from a model repo, now the main code repo is deciding everything

### Special case 1.1: Just ditch the deployment manager
If we really dont like stray modelling commits ticking the deployment history forward (i actually want to puke a little bit when i see that), we can keep the separate model repos.
- version models in mlflow in their respective model repos
- version serving code in its own repo
- during ci, pull the latest model(s) version(s) and create a tag of the form `<code-version>-<model1-version>-<modeln-version>`
- suffix with rc for staging
- A single serving repo commit will have potentially multiple model version tags, e.g. `v1.2.3-model1v42-model2v45`, `v1.2.3-model1v43-model2v52`, `v1.2.3-model1v44-model2v77`
This removes the deployment manager by tracking working system states directly in tags (instead of the config, like in the first approach). It saves people from confusion of many commits representing identical serving code tag, and keeps ml engineers screaming MLFlow at bay. However, visually parsing the tags will be literally impossible.

### Special case 2: Model-centric monorepo
The most head-on approach and a direct extension of mlflow philosophy:
- version models in mlflow
- version service code in git
- absorb modelling into a `models/` directory in the same repo
- during ci, pull the latest model(s) version(s) and create a tag of the form `<code-version>-<model1-version>-<modeln-version>`
- suffix with rc for staging
- tolerate having slightly confusing identical code version tags on different (!) or the same (!!!) commits when serving code doesnt change but models are iterated on.
This removes the deployment manager by tracking working system states directly in tags. And it removes separate repos, which leaves us with an unwieldy but working thing (since usually you dont redeploy after retraining with zero new commits, you wouldnt even notice)

### Special case 2.1: Code-centric monorepo
Alternatively, we could commit the mlops crime of coupling model versions to code, and call modelling efforts a minor change. This will simplify all kinds of things and, in cases when modelling is minimal but business sways and pivots are substantial, seems like a reasonably clean option.
- absorb modelling into a `models/` directory in the same repo
- version service code in git
- version models in mlflow for convenience but couple the versions to code (meaning you are only allowed to have one model version per commit)
- any modelling causes a minor version bump
- during ci, pull the latest model(s) version(s), just log them / pass them around in env variables but keeps tags simply `<joint-version>`. (Since model changes cause a bump)
- suffix with rc for staging. Here deployment flexibility is maximised since the complete state of the system is in front of you yet no sub-version tracking is required.
- tolerate breaking the oath of keeping code version and model version separate (which is a way worse crime than disregarding mlflow model lifecycle tooling).
Id only attempt this versioning method if modelling is truly almost non-existent

## Setup

Try the thing out! Mostly to see it wörks

### Source Database

This repo assumes theres larger infra around, and just for fun i decided to use zoomer tech supabase. Ever thoughtful, they dont provide (afaik) a way to programmatically create tables in the underlying postgres db, so while im searching for the internal db password to connect to it directly, just create the table on the UI (sorry)

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
