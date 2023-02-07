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

`DBT_ENV_SECRET_GITHUB_PAT` is a Github personal access token (PAT) stored as an environment variable in dbt Cloud. This is required to access private Github repos. To create a PAT and configure it with dbt-cloud, see the [dbt](https://docs.getdbt.com/docs/build/packages#git-token-method) and [GitHub](https://docs.github.com/en/enterprise-server@3.1/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token) docs.

### Reflekt resources:
- [GitHub repo](https://github.com/GClunies/Reflekt)

### dbt resources:
- dbt [docs](https://docs.getdbt.com/docs/introduction)
- Docs on dbt [packages](https://docs.getdbt.com/docs/building-a-dbt-project/package-management/)
