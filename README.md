# happy-terraform
Repository for Happy Path terraform modules.

## Naming & Namespacing
This repository assumes AWS infrastructure. There are some types of resources (task definitions, ECR names, and more) that are created in an account-wide namespace, and others like ECS service names only need to be unique within a given ECS cluster.

Resource names need take their namespace level into account. Stack-level resources in the account-level namespace, our standard naming format is:

```
${stack_resource_prefix}-${deployment_stage}-${custom_stack_name}-${resource_name}
```

As an example, for a `frontend` task definition in a `jennifer` stack, in the `dev` environment, for the `widgetstore` application, we'd have the following name:

```
widgetstore-dev-jennifer-frontend
```

