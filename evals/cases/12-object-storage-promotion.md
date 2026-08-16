# Eval 12 — Object-storage promotion

## User request

开发环境对象存储里已经生成了课程封面、视频和参考图，数据库里也保存了这些文件的 key。上线生产后是不是数据库迁移过去就能直接显示这些文件？

## Evaluate

The response should explain that an object key is scoped to the storage resource/bucket, database rows alone do not copy objects, temporary signed URLs should not be persisted, and curated assets require explicit production promotion + verification.
