import asyncio
from collections.abc import AsyncIterator

import grpc
from google.protobuf import empty_pb2

import task_manager_pb2 as pb2
import task_manager_pb2_grpc as pb2_grpc


async def main() -> None:
    # فتح قناة اتصال (Channel) غير مشفرة؛ يُنصح بإعادة استخدام نفس القناة عبر التطبيق
    # لأن HTTP/2 يمرر كافة الطلبات المتوازية عبر اتصال TCP واحد (Multiplexing)
    async with grpc.aio.insecure_channel("localhost:50051") as channel:
        # إنشاء الـ Stub (الكائن الوكيل الذي يحمل نفس دوال الخادم)
        stub = pb2_grpc.TaskManagerStub(channel)

        # إعداد بيانات التوثيق لإرسالها ضمن ترويسات الطلب
        auth_metadata = (("authorization", "Bearer secret-token"),)

        # --------------------------------------------------------------
        # 1. استدعاء دالة لا تستقبل ولا تُرجع قيماً (Ping)
        # --------------------------------------------------------------
        await stub.Ping(empty_pb2.Empty(), timeout=2.0)
        print("[1] Ping succeeded (Empty -> Empty)")

        # --------------------------------------------------------------
        # 2. استدعاء دالة أحادية (CreateTask) مع كافة الحقول و Deadline
        # --------------------------------------------------------------
        create_req = pb2.CreateTaskRequest(
            title="Build gRPC Gateway",
            priority=pb2.PRIORITY_HIGH,
            notes="Must support HTTP/2 multiplexing",
            tags=["backend", "rpc"],
            labels={"env": "staging", "owner": "core"},
            url_source="https://grpc.io/docs/",  # تعيين أحد خيارات oneof
        )
        created_task = await stub.CreateTask(
            create_req,
            metadata=auth_metadata,
            timeout=5.0,  # Deadline: يُلغى الطلب تلقائياً بعد 5 ثوانٍ
        )
        print(
            f"[2] Created Task -> id={created_task.id}, "
            f"source={created_task.WhichOneof('source')}"
        )

        # --------------------------------------------------------------
        # 3. استدعاء دفق من العميل (BulkUploadTasks)
        # --------------------------------------------------------------
        async def generate_bulk_requests() -> AsyncIterator[pb2.CreateTaskRequest]:
            batch = [
                ("Configure Envoy L7 LB", pb2.PRIORITY_HIGH),
                ("Write Protobuf Lint Rules", pb2.PRIORITY_LOW),
                ("Benchmark Serialization", pb2.PRIORITY_MEDIUM),
            ]
            for title, priority in batch:
                yield pb2.CreateTaskRequest(title=title, priority=priority)
                await asyncio.sleep(0.1)

        summary = await stub.BulkUploadTasks(generate_bulk_requests(), timeout=10.0)
        print(
            f"[3] BulkUpload Summary -> count={summary.created_count}, "
            f"ids={list(summary.created_ids)}"
        )

        # --------------------------------------------------------------
        # 4. استدعاء دفق من الخادم (StreamTasks)
        # --------------------------------------------------------------
        print("[4] Server Streaming (priority >= MEDIUM):")
        stream_req = pb2.StreamTasksRequest(min_priority=pb2.PRIORITY_MEDIUM)
        async for task in stub.StreamTasks(stream_req, timeout=10.0):
            print(f"    -> Received: {task.id} | {task.title} | priority={task.priority}")

        # --------------------------------------------------------------
        # 5. استدعاء دفق مزدوج (SyncTasks)
        # --------------------------------------------------------------
        print("[5] Bidirectional Streaming:")

        async def generate_sync_events() -> AsyncIterator[pb2.SyncEvent]:
            # إرسال معرّف موجود وآخر وهمي لاختبار استجابة الخادم الفورية
            events = [
                pb2.SyncEvent(task_id=created_task.id, action="CHECK"),
                pb2.SyncEvent(task_id="invalid-id", action="ARCHIVE"),
            ]
            for ev in events:
                yield ev
                await asyncio.sleep(0.2)

        async for ack in stub.SyncTasks(generate_sync_events(), timeout=10.0):
            print(f"    -> Ack for {ack.task_id}: accepted={ack.accepted} ({ack.detail})")

        # --------------------------------------------------------------
        # 6. استدعاء دالة تستقبل قيمة ولا تُرجع قيماً (DeleteTask)
        # --------------------------------------------------------------
        await stub.DeleteTask(pb2.TaskIdRequest(id=created_task.id), timeout=3.0)
        print(f"[6] Deleted Task {created_task.id} (Request -> Empty)")

        # --------------------------------------------------------------
        # 7. اختبار معالجة الأخطاء القياسية (محاولة حذف نفس المهمة مجدداً)
        # --------------------------------------------------------------
        try:
            await stub.DeleteTask(pb2.TaskIdRequest(id=created_task.id), timeout=3.0)
        except grpc.aio.AioRpcError as err:
            # استخراج كود الخطأ القياسي ورسالة التفاصيل القادمة من الخادم
            print(f"[7] Expected Error Caught -> code={err.code().name}, details='{err.details()}'")


if __name__ == "__main__":
    asyncio.run(main())
