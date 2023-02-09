# PROJECT_NAME
A [Reflekt](https://github.com/GClunies/reflekt) project to:
- Define event schemas
- Pull schema(s) from a schema registry in [JSONschema](https://json-schema.org/) format.
- Push schema(s) to a schema registry for use in event validation.
- Lint schemas to enforce conventions and required metadata.
- Build data artifacts (e.g., dbt packages) based on schemas that model and document event data.


## Getting Started
- See the [Reflekt Github repo](https://github.com/GClunies/reflekt) for details on commands, schemas, registries, and project configuration.
- Event schemas are defined in the [`schemas/`](schemas/) directory.
- Data artifacts (e.g., dbt packages) are built in the [`artifacts/`](artifacts/) directory.

## Using Reflekt data artifacts

### dbt packages
To use a Reflekt dbt package in a downstream dbt project, add it to the `packages.yml` of the dbt project.

#### dbt-core
```yaml
packages:
  - git: "https://github.com/<your_user_or_org>/<your_repo>"  # Replace with Github repo URL for your Reflekt project
    subdirectory: "dbt-packages/<reflekt_dbt_package_name>"
    revision: v0.1.0__reflekt_dbt_package_name  # Example tag. Replace with branch, tag, or commit (full 40-character hash)
```

#### dbt-cloud
```yaml
packages:
  - git: ""https://{{env_var('DBT_ENV_SECRET_GITHUB_PAT')}}@github.com/<your_user_or_org>/<your_repo>.git""  # Replace with your PAT and Github repo URL for your Reflekt project
    subdirectory: "dbt-packages/<reflekt_dbt_package_name>"
    revision: v0.1.0__reflekt_dbt_package_name  # Example tag. Replace with branch, tag, or commit (full 40-character hash)
```

To use with dbt-cloud, you will need to [create a Github personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token) (e.g., `DBT_ENV_SECRET_GITHUB_PAT`) and [configure it as an environment variable](https://docs.getdbt.com/docs/dbt-cloud/using-dbt-cloud/cloud-environment-variables) in your dbt-cloud account.

For local dbt development, you will need to set the environment variable on your local machine.
```bash
# Add the following line to your .zshrc, .bash_profile, etc.
export DBT_ENV_SECRET_GITHUB_PAT=YOUR_TOKEN
```
