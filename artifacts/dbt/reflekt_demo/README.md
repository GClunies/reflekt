# reflekt_demo
A private dbt package built by [Reflekt](https://github.com/GClunies/reflekt) defining sources, models, and documentation based on events schemas defined in Reflekt project `reflekt_demo`.

To use this package, add it to the `packages.yml` of your dbt project.

```yaml
  # Example packages.yml in dbt project
  packages:
  - package: dbt-labs/dbt_utils
    version: 0.8.5

  - git: "https://github.com/path/to/your/reflekt/project/repo"  # Replace with your repo URL
    subdirectory: "dbt-packages/reflekt_demo"
    revision: v0.1.0__reflekt_demo  # Example tag. Replace with your branch, tag, or commit (full 40-character hash)
  ```

### Reflekt resources:
- [GitHub repo](https://github.com/GClunies/Reflekt)
- [Reflekt Docs](https://reflekt-ci.notion.site/reflekt-ci/Reflekt-Docs-a27c2dd7006b4584b6a451819b09cdb7)

### dbt resources:
- dbt [docs](https://docs.getdbt.com/docs/introduction)
- Docs on dbt [packages](https://docs.getdbt.com/docs/building-a-dbt-project/package-management/)
- dbt [slack & discourse communities](https://community.getdbt.com/)
- dbt [blog](https://blog.getdbt.com/)
