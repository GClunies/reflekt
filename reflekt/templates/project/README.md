# reflekt-PROJECT_NAME
A [Reflekt](https://github.com/GClunies/reflekt) project representing tracking plans as `code`. Tracking plans are defined in the [`tracking-plans/`](tracking-plans/) directory. dbt packages templated by Reflekt that model and document the events found in the tracking plans, are defined in the [`dbt-packages/`](dbt-packages/) directory.

To use a Reflekt dbt package in your dbt project, reference it in the `packages.yml` of your dbt project. Like so:
```yaml
  # Example packages.yml in dbt project
  packages:
  - package: dbt-labs/dbt_utils
    version: 0.8.5

  # Can reference multiple Reflekt dbt packages in a dbt project
  - git: "https://github.com/your/reflekt-project-repo"
    subdirectory: "dbt-packages/reflekt_dbt_package_one"
    revision: v0.1.0__reflekt_dbt_package_one  # Git branch, tag, or specific commit (full 40-character hash)

  - git: "https://github.com/your/reflekt-project-repo"
    subdirectory: "dbt-packages/reflekt_dbt_package_two"
    revision: v0.3.0__reflekt_dbt_package_two  # Git branch, tag, or specific commit (full 40-character hash)
  ```

### Reflekt resources:
- [GitHub repo](https://github.com/GClunies/reflekt)
- [Reflekt Docs](https://github.com/GClunies/reflekt/blob/main/docs/DOCUMENTATION.md/#reflekt-docs)

### dbt resources:
- dbt [docs](https://docs.getdbt.com/docs/introduction)
- Docs on dbt [packages](https://docs.getdbt.com/docs/building-a-dbt-project/package-management/)
- dbt [slack & discourse communities](https://community.getdbt.com/)
- dbt [blog](https://blog.getdbt.com/)
