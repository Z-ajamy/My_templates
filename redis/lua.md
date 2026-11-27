# قالب أوامر Lua في Redis (المهم فقط — قاعدة 80/20)

ملخص عملي ومباشر لأهم أساسيات **Lua** و**Redis Lua API** التي تحتاجها فعلياً في بيئة الإنتاج لتنفيذ عمليات ذرية (**Atomic**) على السيرفر.

> **المراجع الرسمية:** [Scripting with Lua](https://redis.io/docs/latest/develop/programmability/eval-intro/) | [Redis Lua API Reference](https://redis.io/docs/latest/develop/programmability/lua-api/) | [Redis Functions](https://redis.io/docs/latest/develop/programmability/functions-intro/)

---

## 1. تشغيل السكربتات (Execution & Caching)

| الأمر | الصيغة | الشرح بالعربي |
| :--- | :--- | :--- |
| `EVAL` | `EVAL "script" numkeys key1 ... arg1 ...` | تنفيذ كود Lua مباشرة بتمرير عدد المفاتيح (`numkeys`) ثم أسماء المفاتيح ثم المعاملات. |
| `SCRIPT LOAD` | `SCRIPT LOAD "script"` | تحميل السكربت في ذاكرة Redis وإرجاع بصمته (**SHA1**) دون تنفيذه فوراً. |
| `EVALSHA` | `EVALSHA sha1 numkeys key1 ... arg1 ...` | تشغيل السكربت المحمَّل عبر بصمته لتوفير الباندويث في الإنتاج (يعيد `NOSCRIPT` إذا أُعيد تشغيل السيرفر). |
| `SCRIPT EXISTS` | `SCRIPT EXISTS sha1 [sha1 ...]` | التأكد من وجود السكربت في الـ Cache (`1` موجود، `0` غير موجود). |
| `SCRIPT KILL` | `SCRIPT KILL` | إيقاف سكربت عالق طال تنفيذه (يعمل فقط إذا لم يكتب السكربت بيانات بعد). |

```bash
# تشغيل ملف .lua من الطرفية (لاحظ الفاصلة بين المفاتيح والمعاملات مع مسافات حولها)
redis-cli --eval my_script.lua key1 key2 , arg1 arg2
```

---

## 2. أساسيات لغة Lua داخل Redis (ما تحتاجه فقط)

* **الترقيم يبدأ من `1` وليس `0`:** أول مفتاح هو `KEYS[1]` وأول معامل هو `ARGV[1]`.
* **المتغيرات المحلية إلزامية (`local`):** استخدم `local x = 10` دائماً؛ المتغيرات العامة (**Global**) محظورة في بيئة Redis لحماية التزامن.
* **انتبه لقيمة الفراغ (`nil` مقابل `false`):** عندما يرجع Redis قيمة فارغة (`nil` في البروتوكول)، تتحول داخل Lua (مع RESP2 الافتراضي) إلى `false` وليس `nil`!

```lua
-- التحويل والشرط الصحيح لقيمة غير موجودة من Redis
local val = redis.call("GET", KEYS[1])
if not val then
    return nil
end
local num = tonumber(val) -- تحويل النص إلى رقم للحسابات
```

| العنصر | الصيغة في Lua | الشرح بالعربي |
| :--- | :--- | :--- |
| `KEYS` / `ARGV` | `KEYS[1]`, `ARGV[1]` | مصفوفات جاهزة تحتوي على أسماء المفاتيح والمعاملات الممررة للسكربت. |
| `local` | `local count = 0` | تعريف متغير محلي داخل السكربت (إلزامي في Redis). |
| `if ... end` | `if a == b then ... elseif ... else ... end` | الجملة الشرطية (`~=` تعني لا يساوي). |
| `for` | `for i = 1, #KEYS do ... end` | حلقة تكرار على المفاتيح (`#KEYS` يعطي طول المصفوفة). |
| `tonumber` / `tostring` | `tonumber(ARGV[1])` | التحويل بين النصوص والأرقام (كل قيم `ARGV` ونتائج Redis تصل كنصوص). |

---

## 3. أهم دوال Redis Lua API

| الدالة | الاستخدام | الشرح بالعربي |
| :--- | :--- | :--- |
| `redis.call(...)` | `redis.call("SET", KEYS[1], ARGV[1])` | تنفيذ أمر Redis؛ إذا فشل الأمر يتوقف السكربت فوراً ويرجع الخطأ للعميل (الأكثر استخداماً). |
| `redis.pcall(...)` | `local res = redis.pcall("GET", KEYS[1])` | تنفيذ أمر Redis بأمان؛ إذا فشل يرجع جدولاً يحتوي على حقل `err` لتعالجه داخل السكربت دون توقفه. |
| `redis.error_reply(msg)` | `return redis.error_reply("ERR no_balance")` | إرجاع رسالة خطأ مخصصة للعميل بصيغة Redis القياسية. |
| `redis.status_reply(msg)` | `return redis.status_reply("OK")` | إرجاع رد حالة قياسي للعميل. |
| `cjson.decode` / `encode` | `local obj = cjson.decode(val)` | مكتبة مدمجة لتحويل نصوص JSON إلى جداول Lua والعكس بسرعة فائقة. |

---

## 4. أهم 3 قوالب Lua إنتاجية جاهزة

### أ) فك القفل الموزع بأمان (Safe Lock Release)
يتأكد أن العميل الذي يحذف القفل هو نفس صاحبه عبر مطابقة الـ `token`:

```lua
-- KEYS[1] = lock_key | ARGV[1] = lock_token
if redis.call("GET", KEYS[1]) == ARGV[1] then
    return redis.call("DEL", KEYS[1])
else
    return 0
end
```

### ب) خصم رصيد أو مخزون ذري (Atomic Conditional Decrement)
يمنع السحب على المكشوف (**Race Condition**) في خطوة واحدة:

```lua
-- KEYS[1] = stock:product_10 | ARGV[1] = quantity
local current = tonumber(redis.call("GET", KEYS[1]) or "0")
local qty = tonumber(ARGV[1])

if current < qty then
    return redis.error_reply("ERR insufficient_stock")
end

return redis.call("DECRBY", KEYS[1], qty)
```

### ج) محدد معدل الطلبات بالنافذة المنزلقة (Sliding Window Rate Limiter)
```lua
-- KEYS[1] = ratelimit:user_1 | ARGV[1] = now_ms | ARGV[2] = window_ms | ARGV[3] = limit | ARGV[4] = req_id
local now = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local limit = tonumber(ARGV[3])

redis.call("ZREMRANGEBYSCORE", KEYS[1], 0, now - window)
local count = redis.call("ZCARD", KEYS[1])

if count >= limit then
    return 0 -- مرفوض (تجاوز الحد)
end

redis.call("ZADD", KEYS[1], now, ARGV[4])
redis.call("PEXPIRE", KEYS[1], window)
return 1 -- مسموح
```

---

## 5. البديل الحديث: Redis Functions (إصدار 7.0+)

بدلاً من إعادة إرسال السكربتات من التطبيق، يمكنك حفظها كدوال دائمة على السيرفر تُنسخ تلقائياً للـ Replicas والـ AOF:

```bash
# تحميل مكتبة دوال باسم mylib
FUNCTION LOAD "#!lua name=mylib\nredis.register_function('ping_ok', function() return 'OK' end)"

# استدعاء الدالة بالاسم (0 = عدد المفاتيح)
FCALL ping_ok 0
```

---

## 6. قواعد الإنتاج الذهبية (Production Rules)

* **مرر كل المفاتيح عبر `KEYS`:** لا تكتب اسم مفتاح ثابت أو مركب بالدمج داخل السكربت (`"user:" .. id`)؛ مرره في `KEYS` لكي يعمل السكربت في **Redis Cluster**.
* **لا تكتب سكربتات بطيئة:** Redis ينفذ السكربت ككتلة واحدة (**Atomic & Blocking**)، فأي حلقة طويلة توقف جميع العملاء الآخرين.
* **استخدم `EVALSHA` في الكود:** المكتبات الحديثة (مثل `redis-py` و`ioredis`) تدير `SCRIPT LOAD` و`EVALSHA` تلقائياً عبر كائنات مثل `register_script`.
