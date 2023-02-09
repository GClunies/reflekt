# _DBT_PKG_NAME_
A private dbt package built by [Reflekt](https://github.com/GClunies/reflekt) defining sources, models, and documentation based on events schemas defined in Reflekt project `_DBT_PKG_NAME_`.

## Using this package
To use a Reflekt dbt package in a downstream dbt project, add it to the `packages.yml` of the dbt project.

#### dbt-core
```yaml
packages:
  - git: "https://github.com/<your_user_or_org>/<your_repo>"  # Replace with Github repo URL for your Reflekt project
    subdirectory: "dbt-packages/<reflekt_dbt_package_name>"
    revision: v0.1.0___DBT_PKG_NAME_  # Example tag. Replace with branch, tag, or commit (full 40-character hash)
```

#### dbt-cloud
```yaml
packages:
  - git: ""https://{{env_var('DBT_ENV_SECRET_GITHUB_PAT')}}@github.com/<your_user_or_org>/<your_repo>.git""  # Replace with your PAT and Github repo URL for your Reflekt project
    subdirectory: "dbt-packages/<reflekt_dbt_package_name>"
    revision: v0.1.0___DBT_PKG_NAME_  # Example tag. Replace with branch, tag, or commit (full 40-character hash)
```
To use with dbt-cloud, you will need to [create a Github personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token) (e.g., `DBT_ENV_SECRET_GITHUB_PAT`) and [configure it as an environment variable](https://docs.getdbt.com/docs/dbt-cloud/using-dbt-cloud/cloud-environment-variables) in your dbt-cloud account.

For local dbt development, you will need to set the environment variable on your local machine.
```bash
# Add the following line to your .zshrc, .bash_profile, etc.
export DBT_ENV_SECRET_GITHUB_PAT=YOUR_TOKEN
```

### Reflekt resources:
- [GitHub repo](https://github.com/GClunies/Reflekt)

### dbt resources:
- dbt [docs](https://docs.getdbt.com/docs/introduction)
- Docs on dbt [packages](https://docs.getdbt.com/docs/building-a-dbt-project/package-management/)
