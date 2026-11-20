import asyncio
import uuid
from collections.abc import AsyncIterable, AsyncIterator

import grpc
from google.protobuf import empty_pb2, timestamp_pb2

import task_manager_pb2 as pb2
import task_manager_pb2_grpc as pb2_grpc


class TaskManagerService(pb2_grpc.TaskManagerServicer):
    """تنفيذ العقد البرمجي المولّد من ملف task_manager.proto"""

    def __init__(self) -> None:
        # مخزن مؤقت في الذاكرة لتجربة المثال عملياً
        self._tasks: dict[str, pb2.Task] = {}

    # ------------------------------------------------------------------
    # 1. دالة لا تستقبل قيماً ولا تُرجع قيماً (Empty -> Empty)
    # ------------------------------------------------------------------
    async def Ping(
        self,
        request: empty_pb2.Empty,
        context: grpc.aio.ServicerContext,
    ) -> empty_pb2.Empty:
        # إرجاع كائن Empty فارغ يدل على نجاح الاستدعاء (StatusCode.OK)
        return empty_pb2.Empty()

    # ------------------------------------------------------------------
    # 2. دالة تستقبل قيمة ولا تُرجع قيماً (TaskIdRequest -> Empty)
    # ------------------------------------------------------------------
    async def DeleteTask(
        self,
        request: pb2.TaskIdRequest,
        context: grpc.aio.ServicerContext,
    ) -> empty_pb2.Empty:
        if request.id not in self._tasks:
            # إنهاء الطلب فوراً بكود خطأ قياسي من gRPC (يناظر 404 في HTTP)
            await context.abort(
                grpc.StatusCode.NOT_FOUND,
                f"Task with id '{request.id}' does not exist.",
            )

        del self._tasks[request.id]
        return empty_pb2.Empty()

    # ------------------------------------------------------------------
    # 3. دالة أحادية (Unary): استقبال طلب معقد وإرجاع كائن
    # ------------------------------------------------------------------
    async def CreateTask(
        self,
        request: pb2.CreateTaskRequest,
        context: grpc.aio.ServicerContext,
    ) -> pb2.Task:
        # قراءة البيانات الوصفية (Metadata) المرسلة في ترويسات HTTP/2
        # المفاتيح تكون دائماً بأحرف صغيرة (lowercase)
        metadata = dict(context.invocation_metadata())
        auth_token = metadata.get("authorization")
        if auth_token != "Bearer secret-token":
            await context.abort(
                grpc.StatusCode.UNAUTHENTICATED,
                "Missing or invalid authorization token.",
            )

        # التحقق من صحة المدخلات وإرجاع INVALID_ARGUMENT عند وجود خلل
        if not request.title.strip():
            await context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                "Field 'title' cannot be empty.",
            )

        # التحقق الصريح من الحقل الاختياري (يعمل فقط لأننا حددنا optional في proto3)
        notes_value = request.notes if request.HasField("notes") else None

        # إنشاء الطابع الزمني الحالي بتوقيت UTC
        now = timestamp_pb2.Timestamp()
        now.GetCurrentTime()

        task_id = str(uuid.uuid4())[:8]
        task = pb2.Task(
            id=task_id,
            title=request.title,
            priority=request.priority,
            tags=list(request.tags),
            labels=dict(request.labels),
            created_at=now,
        )

        if notes_value is not None:
            task.notes = notes_value

        # فحص أي حقل تم تعيينه داخل مجموعة oneof
        source_kind = request.WhichOneof("source")
        if source_kind == "url_source":
            task.url_source = request.url_source
        elif source_kind == "raw_payload":
            task.raw_payload = request.raw_payload

        self._tasks[task_id] = task
        return task

    # ------------------------------------------------------------------
    # 4. دفق من الخادم (Server Streaming): استخدام yield لإرسال عدة رسائل
    # ------------------------------------------------------------------
    async def StreamTasks(
        self,
        request: pb2.StreamTasksRequest,
        context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[pb2.Task]:
        for task in self._tasks.values():
            # التحقق مما إذا كان العميل قد ألغى الطلب أو انتهى الموعد النهائي (Deadline)
            if context.cancelled():
                break

            if request.min_priority != pb2.PRIORITY_UNSPECIFIED:
                if task.priority < request.min_priority:
                    continue

            # إرسال رسالة واحدة عبر نفس اتصال HTTP/2 دون إغلاقه
            yield task
            await asyncio.sleep(0.2)  # محاكاة تدفق تدريجي للبيانات

    # ------------------------------------------------------------------
    # 5. دفق من العميل (Client Streaming): استقبال مكرر لاتزامني وإرجاع رد واحد
    # ------------------------------------------------------------------
    async def BulkUploadTasks(
        self,
        request_iterator: AsyncIterable[pb2.CreateTaskRequest],
        context: grpc.aio.ServicerContext,
    ) -> pb2.BulkUploadSummary:
        created_ids: list[str] = []

        # استهلاك تيار الرسائل القادم من العميل حتى يُغلق العميل جهة الإرسال
        async for req in request_iterator:
            now = timestamp_pb2.Timestamp()
            now.GetCurrentTime()

            task_id = str(uuid.uuid4())[:8]
            self._tasks[task_id] = pb2.Task(
                id=task_id,
                title=req.title,
                priority=req.priority,
                created_at=now,
            )
            created_ids.append(task_id)

        # إرجاع النتيجة المجمعة بعد اكتمال دفق العميل
        return pb2.BulkUploadSummary(
            created_count=len(created_ids),
            created_ids=created_ids,
        )

    # ------------------------------------------------------------------
    # 6. دفق مزدوج (Bidirectional Streaming): استقبال وإرسال متزامن
    # ------------------------------------------------------------------
    async def SyncTasks(
        self,
        request_iterator: AsyncIterable[pb2.SyncEvent],
        context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[pb2.SyncAck]:
        # لكل حدث يصل من العميل، نعالج الحالة ونرسل تأكيداً فورياً عبر نفس الدفق
        async for event in request_iterator:
            exists = event.task_id in self._tasks
            if exists:
                yield pb2.SyncAck(
                    task_id=event.task_id,
                    accepted=True,
                    detail=f"Action '{event.action}' applied.",
                )
            else:
                yield pb2.SyncAck(
                    task_id=event.task_id,
                    accepted=False,
                    detail="Task ID not found.",
                )


async def serve() -> None:
    server = grpc.aio.server()
    # ربط تنفيذ الخدمة بالخادم
    pb2_grpc.add_TaskManagerServicer_to_server(TaskManagerService(), server)

    # الاستماع على المنفذ 50051 بدون تشفير TLS (لبيئة التطوير المحلية فقط)
    # في بيئة الإنتاج يُستخدم server.add_secure_port مع شهادات SSL/TLS
    listen_addr = "[::]:50051"
    server.add_insecure_port(listen_addr)

    print(f"gRPC async server listening on {listen_addr}")
    await server.start()
    try:
        await server.wait_for_termination()
    except asyncio.CancelledError:
        # إغلاق سلس يمنح الطلبات الجارية 5 ثوانٍ للانتهاء قبل قطع الاتصال
        await server.stop(grace=5)


if __name__ == "__main__":
    asyncio.run(serve())
