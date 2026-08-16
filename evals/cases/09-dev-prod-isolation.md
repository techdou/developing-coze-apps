# Eval 09 — DEV/PROD database isolation

## User request

我在 Coze Coding 里已经把开发环境项目做完了，开发数据库里有测试账号和很多测试数据。现在准备部署生产环境。平台有“同步开发环境数据至生产环境”的选项，我是不是直接打开就行？对象存储也一起同步吗？

## Evaluate

The response should distinguish schema/migrations from business data, default ordinary DEV data sync to off, treat DB/Auth/Bucket as environment-specific resources, and propose an explicit asset/data promotion plan instead of blanket synchronization.
