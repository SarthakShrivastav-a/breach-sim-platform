# Release Process

1. Work from `dev`.
2. Create a focused feature branch.
3. Run local checks.
4. Push branch and open a PR into `dev`.
5. Merge with GitHub CLI after CI passes.
6. Open a release PR from `dev` into `main`.
7. Tag the release and create GitHub Release notes.

Docker Hub publishing remains disabled until:

- `config/app.yaml` has `docker.image_repository` set.
- `ENABLE_DOCKER_PUBLISH=true` is configured for the workflow.
- `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` secrets exist.

