# ==========================================
# The Builder
# ==========================================
FROM gcc:13-bookworm AS builder

WORKDIR /build

COPY inc/ ./inc/

COPY src/ ./src/

RUN gcc -Wall -pedantic -Werror -Wextra -std=gnu89 -O3 \
    -I./inc \
    src/*.c -o /build/core_binary

# ==========================================
# The Runtime
# ==========================================
FROM debian:bookworm-slim

WORKDIR /app

RUN apt-get update && apt-get upgrade -y && \
    apt-get clean && rm -rf /var/lib/apt/lists/* && \
    useradd --user-group --system --no-create-home --shell /bin/false sysuser

COPY --from=builder --chown=sysuser:sysuser /build/core_binary /app/core_binary

USER sysuser
ENTRYPOINT ["/app/core_binary"]
# CMD ["--config", "default.conf"]
