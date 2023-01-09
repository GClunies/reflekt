# PROJECT_NAME
A [Reflekt](https://github.com/GClunies/reflekt) to define and manage events schemas. Use the Reflekt CLI to:
- `reflekt pull` schemas from a schema registry to populate the Reflekt project `schemas/` directory with existing schemas.
- `reflekt lint` schemas to check they follow agreed-upon conventions (configurable in `reflekt_project.yml`). Perfect for a CI/CD pipeline.
- `reflekt push` schemas to a schema registry where they can be used for event data validation.
- `reflekt build` to build data artifacts (e.g., dbt packages) based on the schemas.

## Getting Started
- See the [Reflekt Github repo](https://github.com/GClunies/reflekt) for details on commands, schemas, registries, and project configuration.
- Event schemas are defined in the [`schemas/`](schemas/) directory.
- Data artifacts are defined in the [`artifacts/`](artifacts/) directory.

## Using Reflekt data artifacts

### dbt packages
To use a Reflekt dbt package in a dbt project, add it to the `packages.yml` of your dbt project.

#### dbt-core
```yaml
packages:
  - git: "https://github.com/<your_user_or_org>/<your_repo>"  # Replace with your repo URL
    subdirectory: "dbt-packages/<reflekt_dbt_package_name>"
    revision: v0.1.0__reflekt_dbt_package_name  # Example tag. Replace with branch, tag, or commit (full 40-character hash)
```

#### dbt-cloud
```yaml
packages:
  - git: ""https://{{env_var('DBT_ENV_SECRET_GITHUB_PAT')}}@github.com/<your_user_or_org>/<your_repo>.git""  # Replace with your repo URL
    subdirectory: "dbt-packages/<reflekt_dbt_package_name>"
    revision: v0.1.0__reflekt_dbt_package_name  # Example tag. Replace with branch, tag, or commit (full 40-character hash)
```
You will need to [create a Github personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token) (e.g., `DBT_ENV_SECRET_GITHUB_PAT`) and [configure it as an environment variable](https://docs.getdbt.com/docs/dbt-cloud/using-dbt-cloud/cloud-environment-variables) in your dbt-cloud account. For local dbt development, you will need to set the environment variable on your local machine. Like so:
```
# Add the following line to your .zshrc, .bash_profile, etc.
export DBT_ENV_SECRET_GITHUB_PAT=<DBT_ENV_SECRET_GITHUB_PAT FROM 1PASSWORD>
```
