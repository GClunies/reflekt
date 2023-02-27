# PROJECT_NAME
A [Reflekt](https://github.com/GClunies/reflekt) project to manage product analytics event schemas and build corresponding data artifacts.

## Getting Started
- See the [Reflekt Github repo](https://github.com/GClunies/reflekt) for details on commands, schemas, registries, and project configuration.
- Event schemas are defined in the [`schemas/`](schemas/) directory.
- Data artifacts are built in the [`artifacts/`](artifacts/) directory.
  - dbt packages are built in the [`artifacts/dbt/`](artifacts/dbt/) directory.

## Using dbt artifacts
To use a Reflekt dbt package in a downstream dbt project, add it to dbt project's `packages.yml`.

#### dbt-core
```yaml
packages:
  - git: "https://github.com/<your_user_or_org>/<your_repo>"  # Reflekt project Github repo URL
    subdirectory: "dbt-packages/<reflekt_dbt_package_name>"
    revision: v0.1.0__reflekt_demo  # Branch, tag, or commit (40-character hash). For latest, use 'main' branch.
```

#### dbt-cloud
```yaml
packages:
  - git: ""https://{{env_var('DBT_ENV_SECRET_GITHUB_PAT')}}@github.com/<your_user_or_org>/<your_repo>.git""  # Reflekt project Github repo URL with GitHub PAT
    subdirectory: "dbt-packages/<reflekt_dbt_package_name>"
    revision: v0.1.0__reflekt_demo  # Branch, tag, or commit (40-character hash). For latest, use 'main' branch.
```
To use with dbt-cloud, you will need to create a [Github personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token) (e.g., `DBT_ENV_SECRET_GITHUB_PAT`) and [configure it as an environment variable](https://docs.getdbt.com/docs/dbt-cloud/using-dbt-cloud/cloud-environment-variables) in your dbt-cloud account.

For local dbt development, set the environment variable on your local machine.
```bash
# Add the following line to your .zshrc, .bash_profile, etc.
export DBT_ENV_SECRET_GITHUB_PAT=YOUR_TOKEN
```

