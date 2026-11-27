# قالب Redis الإنتاجي الشامل (قاعدة 80/20)

دليل مرجعي وعملي مصمم لبيئات الإنتاج (**Production**)، يغطي أهم **20% من أوامر Redis** التي تنجز **80% من المهام الفعلية** (Caching، Rate Limiting، Distributed Locks، Sessions، Queues، Leaderboards، وStreams)، مع شرح واضح بالعربية، وتعقيد الوقت (**Time Complexity**)، وأمثلة عملية، وتحذيرات الإنتاج الحرجة.

> **مرجع الأوامر الرسمي:** [Redis Commands Documentation](https://www.google.com/search?q=https%3A%2F%2Fredis.io%2Fdocs%2Flatest%2Fcommands%2F)

---

## 1. اتفاقية تسمية المفاتيح (Key Naming Convention)

قبل كتابة أي أمر في الإنتاج، اعتمد هيكلاً موحداً للمفاتيح لتسهيل المراقبة وتجنب تضارب البيانات:

```text
<service>:<entity>:<id>:<sub-entity>
```

* **أمثلة عملية:**
  * `auth:session:user_1042`
  * `ratelimit:api:192.168.1.10:/login`
  * `lock:order:98231`
  * `leaderboard:daily:2026-11-27`

---

## 2. الاتصال والفحص السريع (Connection & Health)

| الأمر | الصيغة | التعقيد | الشرح بالعربي |
| :--- | :--- | :--- | :--- |
| `PING` | `PING [message]` | `O(1)` | فحص جاهزية السيرفر؛ يرجع `PONG` أو الرسالة الممررة للتأكد من سلامة الاتصال. |
| `AUTH` | `AUTH [username] password` | `O(1)` | تسجيل الدخول باستخدام كلمة المرور الافتراضية أو مستخدم ACL محدد. |
| `SELECT` | `SELECT index` | `O(1)` | التبديل بين قواعد البيانات المنطقية (من `0` إلى `15`). في الإنتاج يُفضل استخدام قاعدة `0` فقط (وغير مدعوم غيرها في Redis Cluster). |
| `CLIENT LIST` | `CLIENT LIST [TYPE normal\|replica\|pubsub]` | `O(N)` | عرض كل الاتصالات النشطة حالياً لتتبع تسرب الاتصالات (Connection Leaks). |
| `QUIT` | `QUIT` | `O(1)` | إغلاق الاتصال الحالي بشكل نظيف. |

---

## 3. إدارة المفاتيح ووقت الانتهاء (Keys & TTL — أساسيات الإنتاج)

استخدام هذه المجموعة بشكل صحيح يحمي السيرفر من التوقف (**Blocking**) أو امتلاء الذاكرة (**OOM**).

| الأمر | الصيغة | التعقيد | الشرح بالعربي |
| :--- | :--- | :--- | :--- |
| [`SCAN`](https://redis.io/docs/latest/commands/scan/) | `SCAN cursor [MATCH pattern] [COUNT count]` | `O(1)` لكل خطوة | البحث التدريجي عن المفاتيح دون حظر السيرفر؛ **البديل الإنتاجي الآمن لأمر `KEYS *`**. |
| [`UNLINK`](https://redis.io/docs/latest/commands/unlink/) | `UNLINK key [key ...]` | `O(1)` للحذف الفوري | حذف مفتاح أو أكثر وإخلاء الذاكرة في خيط منفصل (**Non-blocking**). البديل الأفضل لـ `DEL` مع المفاتيح الكبيرة. |
| `DEL` | `DEL key [key ...]` | `O(1)` للـ String / `O(N)` للمجموعات | حذف مفتاح بشكل متزامن؛ مناسب للمفاتيح الصغيرة فقط. |
| `EXPIRE` | `EXPIRE key seconds [NX\|XX\|GT\|LT]` | `O(1)` | تحديد مدة صلاحية للمفتاح بالثواني (خيارات `NX/XX/GT/LT` تمنع الكتابة فوق TTL موجود بالخطأ). |
| `TTL` / `PTTL` | `TTL key` / `PTTL key` | `O(1)` | معرفة الوقت المتبقي لانتهاء المفتاح (بالثواني أو المللي ثانية). يرجع `-1` إذا لم يكن له TTL، و`-2` إذا لم يكن موجوداً. |
| `PERSIST` | `PERSIST key` | `O(1)` | إزالة وقت الانتهاء من المفتاح وجعله دائماً. |
| `EXISTS` | `EXISTS key [key ...]` | `O(N)` | التحقق من وجود مفتاح أو أكثر (يرجع عدد المفاتيح الموجودة). |
| `TYPE` | `TYPE key` | `O(1)` | معرفة نوع البيانات المخزنة في المفتاح (`string`, `hash`, `list`, `set`, `zset`, `stream`). |

```bash
# مثال إنتاجي: فحص مفاتيح الجلسات المنتهية أو البحث عنها بدون حظر السيرفر
SCAN 0 MATCH auth:session:* COUNT 100

# حذف مفتاح ضخم بأمان في الخلفية
UNLINK cache:products:all_catalog
```

---

## 4. النصوص والعدادات الذرية (Strings & Atomic Counters)

تُستخدم في الـ **Caching**، والعدادات، و**Distributed Locks**.

| الأمر | الصيغة | التعقيد | الشرح بالعربي |
| :--- | :--- | :--- | :--- |
| [`SET`](https://redis.io/docs/latest/commands/set/) | `SET key value [NX\|XX] [GET] [EX sec\|PX ms\|KEEPTTL]` | `O(1)` | تخزين قيمة نصية مع دعم كامل لانتهاء الصلاحية والكتابة الشرطية (يغني عن `SETEX` و`SETNX` القديمين). |
| `GET` | `GET key` | `O(1)` | قراءة قيمة المفتاح النصي (يرجع `nil` إذا لم يوجد). |
| `MGET` / `MSET` | `MGET key [key ...]` / `MSET k1 v1 k2 v2` | `O(N)` | قراءة أو كتابة عدة مفاتيح في طلب شبكة واحد لتقليل الـ Round-Trips. |
| `INCR` / `DECR` | `INCR key` / `DECR key` | `O(1)` | زيادة أو إنقاص رقم صحيح بمقدار `1` بشكل ذري (**Atomic**)، مثالي للعدادات والـ Rate Limiting. |
| `INCRBY` / `DECRBY` | `INCRBY key increment` | `O(1)` | زيادة أو إنقاص رقم صحيح بقيمة محددة. |
| `INCRBYFLOAT` | `INCRBYFLOAT key increment` | `O(1)` | زيادة قيمة عشرية (مثل الأرصدة أو النقاط العشرية). |

```bash
# تخزين كاش لمدة 10 دقائق
SET cache:user:42 '{"name":"Ahmed","role":"admin"}' EX 600

# محاولة حجز قفل موزع لمدة 30 ثانية فقط إذا لم يكن موجوداً (NX)
SET lock:invoice:5501 "worker-pod-7" NX PX 30000

# عداد زيارات يومي ذري
INCR metrics:visits:2026-11-27
```

---

## 5. الجداول المهيكلة (Hashes — مثالية للـ Objects والـ Sessions)

توفر ذاكرة أقل من تخزين JSON كنص كامل وتسمح بتعديل حقل واحد دون إعادة كتابة الكائن كله.

| الأمر | الصيغة | التعقيد | الشرح بالعربي |
| :--- | :--- | :--- | :--- |
| [`HSET`](https://redis.io/docs/latest/commands/hset/) | `HSET key field value [field value ...]` | `O(1)` لكل حقل | إضافة أو تحديث حقل أو أكثر داخل الـ Hash (البديل الحديث لـ `HMSET`). |
| `HGET` / `HMGET` | `HGET key field` / `HMGET key f1 f2` | `O(1)` / `O(N)` | قراءة حقل واحد أو عدة حقول محددة فقط دون جلب الكائن كاملاً. |
| `HGETALL` | `HGETALL key` | `O(N)` | جلب كل الحقول والقيم. **تحذير:** تجنبه على الـ Hashes الضخمة واستخدم `HSCAN`. |
| `HINCRBY` | `HINCRBY key field increment` | `O(1)` | زيادة عداد رقمي داخل حقل محدد في الـ Hash (مثل رصيد نقاط أو كمية مخزون). |
| `HDEL` | `HDEL key field [field ...]` | `O(N)` | حذف حقل أو أكثر من داخل الـ Hash. |
| `HEXISTS` | `HEXISTS key field` | `O(1)` | التحقق من وجود حقل معين داخل الـ Hash. |
| [`HSCAN`](https://redis.io/docs/latest/commands/hscan/) | `HSCAN key cursor [MATCH pattern] [COUNT count]` | `O(1)` لكل خطوة | المرور التدريجي على حقول Hash كبير دون تعطيل السيرفر. |
| [`HSETEX`](https://redis.io/docs/latest/commands/hsetex/) | `HSETEX key [FNX\|FXX] [EX sec] FIELDS n f1 v1 ...` | `O(N)` | (Redis 8+) تعيين حقول داخل الـ Hash مع مدة صلاحية (TTL) مستقلة للحقول نفسها. |

```bash
# حفظ وتحديث جلسة مستخدم
HSET auth:session:u901 user_id "901" ip "10.0.0.5" login_count 1
HINCRBY auth:session:u901 login_count 1
EXPIRE auth:session:u901 3600
```

---

## 6. القوائم (Lists — الطوابير البسيطة وآخر الأنشطة)

قوائم مرتبطة مزدوجة (**Doubly Linked Lists**) سريعة جداً في الإضافة والحذف من الأطراف.

| الأمر | الصيغة | التعقيد | الشرح بالعربي |
| :--- | :--- | :--- | :--- |
| `LPUSH` / `RPUSH` | `LPUSH key el [el ...]` | `O(1)` لكل عنصر | إضافة عنصر في بداية (`L`) أو نهاية (`R`) القائمة. |
| `LPOP` / `RPOP` | `LPOP key [count]` | `O(1)` | سحب وحذف عنصر (أو عدة عناصر) من بداية أو نهاية القائمة. |
| `BLPOP` / `BRPOP` | `BLPOP key [key ...] timeout` | `O(1)` | سحب عنصر مع الانتظار (**Blocking**) حتى يتوفر عنصر جديد؛ مثالي للـ Workers. |
| `LRANGE` | `LRANGE key start stop` | `O(S+N)` | قراءة شريحة من القائمة (`0 -1` لقراءة الكل؛ استخدم نطاقاً محدوداً في الإنتاج). |
| `LTRIM` | `LTRIM key start stop` | `O(N)` | قص القائمة للاحتفاظ بآخر N عناصر فقط (مثالي لسجل آخر 50 نشاطاً). |
| `LMOVE` | `LMOVE src dst LEFT\|RIGHT LEFT\|RIGHT` | `O(1)` | نقل عنصر بشكل ذري من قائمة لأخرى (لعمل طابور موثوق Reliable Queue). |

```bash
# الاحتفاظ بآخر 100 إشعار للمستخدم فقط
LPUSH user:101:notifications '{"msg":"تم شحن طلبك"}'
LTRIM user:101:notifications 0 99
```

---

## 7. المجموعات غير المرتبة (Sets — القيم الفريدة والتقاطعات)

تضمن عدم تكرار العناصر وتنفذ عمليات المجموعات الرياضية بسرعة فائقة.

| الأمر | الصيغة | التعقيد | الشرح بالعربي |
| :--- | :--- | :--- | :--- |
| `SADD` / `SREM` | `SADD key member [member ...]` | `O(1)` لكل عنصر | إضافة أو حذف عناصر فريدة من المجموعة. |
| `SISMEMBER` | `SISMEMBER key member` | `O(1)` | التحقق الفوري من وجود عنصر داخل المجموعة (مثل فحص الصلاحيات أو الـ Blacklist). |
| `SMISMEMBER` | `SMISMEMBER key m1 m2 ...` | `O(N)` | التحقق من عدة عناصر دفعة واحدة في طلب واحد. |
| `SCARD` | `SCARD key` | `O(1)` | معرفة عدد العناصر في المجموعة فوراً دون قراءتها. |
| `SINTER` / `SUNION` | `SINTER key1 key2` | `O(N*M)` | إيجاد العناصر المشتركة (تقاطع) أو المجمعة (اتحاد) بين مجموعتين (مثل الأصدقاء المشتركين). |
| [`SSCAN`](https://redis.io/docs/latest/commands/sscan/) | `SSCAN key cursor [MATCH p] [COUNT c]` | `O(1)` لكل خطوة | استعراض عناصر مجموعة كبيرة تدريجياً بدلاً من `SMEMBERS`. |

---

## 8. المجموعات المرتبة (Sorted Sets / ZSET — الترتيب والـ Rate Limiting)

كل عنصر له **Score** رقمي تترتب العناصر بناءً عليه تلقائياً.

| الأمر | الصيغة | التعقيد | الشرح بالعربي |
| :--- | :--- | :--- | :--- |
| `ZADD` | `ZADD key [NX\|XX] [GT\|LT] score member` | `O(log N)` | إضافة عنصر بدرجة معينة أو تحديث درجته. |
| `ZINCRBY` | `ZINCRBY key increment member` | `O(log N)` | زيادة أو إنقاص درجة عنصر (مثالي لزيادة نقاط اللاعبين). |
| `ZRANGE` | `ZRANGE key min max [BYSCORE\|BYLEX] [REV] [LIMIT off cnt] [WITHSCORES]` | `O(log N + M)` | استرجاع نطاق مرتب تصاعدياً أو تنازلياً (`REV`) بالترتيب أو بالدرجة (يغني عن `ZREVRANGE` القديم). |
| `ZRANK` / `ZREVRANK` | `ZREVRANK key member` | `O(log N)` | معرفة ترتيب العنصر تصاعدياً أو تنازلياً (يبدأ من `0`). |
| `ZSCORE` | `ZSCORE key member` | `O(1)` | معرفة درجة عنصر محدد. |
| `ZREMRANGEBYSCORE` | `ZREMRANGEBYSCORE key min max` | `O(log N + M)` | حذف العناصر التي تقع درجاتها في نطاق معين (أساسي لتنظيف نافذة الـ Rate Limiter). |
| `ZCARD` / `ZCOUNT` | `ZCARD key` / `ZCOUNT key min max` | `O(1)` / `O(log N)` | عدد كل العناصر أو العناصر داخل نطاق درجات محدد. |

```bash
# جلب أعلى 10 متصدرين مع نقاطهم
ZRANGE leaderboard:game1 0 9 REV WITHSCORES
```

---

## 9. التدفقات (Redis Streams — بديل Kafka الخفيف وطوابير المهام الموثوقة)

تدعم التخزين الدائم للأحداث، ومجموعات المستهلكين (**Consumer Groups**)، وتأكيد الاستلام (**ACK**).

| الأمر | الصيغة | التعقيد | الشرح بالعربي |
| :--- | :--- | :--- | :--- |
| [`XADD`](https://redis.io/docs/latest/commands/xadd/) | `XADD key [MAXLEN ~ count] * field val ...` | `O(1)` | إضافة حدث جديد للـ Stream مع توليد ID تلقائي (`*`) وتقليص تقريبي للحجم (`MAXLEN ~`) لحماية الذاكرة. |
| `XGROUP CREATE` | `XGROUP CREATE key group $ MKSTREAM` | `O(1)` | إنشاء مجموعة مستهلكين لتوزيع الرسائل على أكثر من Worker. |
| `XREADGROUP` | `XREADGROUP GROUP grp consumer [COUNT n] [BLOCK ms] STREAMS key >` | `O(M)` | قراءة الرسائل الجديدة (`>`) المخصصة لـ Consumer معين داخل المجموعة. |
| `XACK` | `XACK key group id [id ...]` | `O(1)` لكل ID | تأكيد معالجة الرسالة بنجاح لإزالتها من قائمة الانتظار (Pending). |
| `XPENDING` | `XPENDING key group [min max count]` | `O(N)` | فحص الرسائل التي سُحبت ولم يُؤكَّد تنفيذها بعد (لاكتشاف الـ Workers المتعطلة). |
| `XAUTOCLAIM` | `XAUTOCLAIM key group consumer min-idle-time start [COUNT n]` | `O(1)` لكل رسالة | سحب الرسائل العالقة عند Worker متعطل وإسنادها لـ Worker نشط تلقائياً. |

---

## 10. البث اللحظي (Pub/Sub — Fire-and-Forget)

مناسب للإشعارات الفورية التي لا يهم ضياعها إذا كان المستمع غير متصل لحظياً.

| الأمر | الصيغة | التعقيد | الشرح بالعربي |
| :--- | :--- | :--- | :--- |
| `PUBLISH` | `PUBLISH channel message` | `O(N+M)` | إرسال رسالة فورية لكل المشتركين في القناة حالياً. |
| `SUBSCRIBE` | `SUBSCRIBE channel [channel ...]` | `O(N)` | الاستماع لقناة أو أكثر بشكل لحظي. |
| `PSUBSCRIBE` | `PSUBSCRIBE pattern [pattern ...]` | `O(N)` | الاستماع لمجموعة قنوات تطابق نمطاً معيناً (مثل `notifications:*`). |

---

## 11. المعاملات، التجميع، والـ Lua Scripts (Atomicity & Performance)

| الأمر | الصيغة | الشرح بالعربي |
| :--- | :--- | :--- |
| `MULTI` / `EXEC` | `MULTI ... commands ... EXEC` | تجميع عدة أوامر لتنفذ بالتتابع كوحدة واحدة دون تداخل أوامر أخرى من عملاء آخرين (لا تدعم Rollback عند خطأ منطقي). |
| `WATCH` / `UNWATCH` | `WATCH key` | قفل تفاؤلي (**Optimistic Locking**)؛ يُلغي الـ `EXEC` إذا تغير المفتاح المراقَب قبل التنفيذ. |
| `EVAL` / `EVALSHA` | `EVAL "script" numkeys key... arg...` | تنفيذ كود **Lua** بالكامل داخل Redis كعملية ذرية واحدة؛ أسرع وأكثر أماناً للعمليات المعقدة. |
| **Pipelining** | *(ميزة في مكتبة العميل Client)* | إرسال عشرات الأوامر دفعة واحدة دون انتظار رد كل أمر على حدة؛ يضاعف الأداء عدة مرات. |

---

## 12. أنماط إنتاجية جاهزة (Production Patterns)

### أ) فك القفل الموزع بأمان (Safe Distributed Lock Release)
لا تحذف القفل بـ `DEL` مباشرة حتى لا تحذف قفل Worker آخر إذا انتهت مهلة قفلك؛ استخدم Lua للتحقق من الـ Token أولاً:

```lua
-- EVAL script 1 lock:order:98231 "worker-pod-7"
if redis.call("GET", KEYS[1]) == ARGV[1] then
    return redis.call("DEL", KEYS[1])
else
    return 0
end
```

### ب) محدد معدل الطلبات بالنافذة المنزلقة (Sliding Window Rate Limiter)
باستخدام `ZSET` داخل Lua Script أو Pipeline:
1. احذف الطلبات الأقدم من النافذة الزمنية: `ZREMRANGEBYSCORE key 0 (now - window_ms)`
2. أضف الطلب الحالي بدرجة الوقت الحالي: `ZADD key now unique_request_id`
3. احسب العدد: `ZCARD key` (إذا تجاوز الحد، ارفض الطلب).
4. حدّث الصلاحية: `EXPIRE key window_sec`

---

## 13. المراقبة، الذاكرة، والأمان (Production Ops & Guardrails)

| الأمر | الشرح بالعربي |
| :--- | :--- |
| `INFO [section]` | فحص صحة السيرفر: `INFO memory` (استهلاك الذاكرة والـ Fragmentation)، `INFO stats` (معدل الـ Cache Hit/Miss)، `INFO clients`. |
| `MEMORY USAGE key` | معرفة الحجم الفعلي للمفتاح في الرام بالبايت لاكتشاف **Big Keys**. |
| `SLOWLOG GET [count]` | عرض أبطأ الأوامر التي استغرقت وقتاً أطول من الحد المسموح (`slowlog-log-slower-than`). |
| `ACL LIST` / `ACL SETUSER` | إدارة المستخدمين وصلاحياتهم بدقة (تقييد الأوامر الخطيرة والمفاتيح المسموحة لكل خدمة). |
| `BGSAVE` | أخذ نسخة احتياطية (**RDB Snapshot**) في الخلفية دون إيقاف السيرفر. |
| `CONFIG GET maxmemory-policy` | التأكد من سياسة الإخلاء عند امتلاء الذاكرة (مثل `allkeys-lru` أو `volatile-lru` للـ Cache، و`noeviction` للـ Queues). |

### قائمة الممنوعات في بيئة الإنتاج (Production Don'ts)
* ❌ **تجنب `KEYS *` تماماً:** يعطل السيرفر (Single-threaded) حتى ينتهي من مسح كل المفاتيح؛ استخدم `SCAN` دائماً.
* ❌ **تجنب `FLUSHALL` / `FLUSHDB` بدون ACL:** امسحهما أو أعد تسميتهما في الإنتاج لمنع مسح البيانات بالخطأ.
* ❌ **تجنب `MONITOR` لفترات طويلة:** يستهلك الذاكرة ويخفض أداء السيرفر بأكثر من 50%.
* ❌ **تجنب قراءة المجموعات الضخمة دفعة واحدة:** لا تستخدم `HGETALL` أو `SMEMBERS` أو `LRANGE 0 -1` على مفاتيح تحتوي آلاف العناصر؛ استخدم `HSCAN` / `SSCAN` أو نطاقات محددة.
* ❌ **تجنب ترك المفاتيح بدون `TTL` في الكاش:** يؤدي حتماً إلى امتلاء الذاكرة (**OOM**).
