FROM docker.io/eclipse-temurin:21-jdk-alpine AS build

WORKDIR /app

COPY build.gradle.kts settings.gradle.kts gradlew ./
COPY gradle ./gradle
COPY src ./src

RUN ./gradlew clean bootJar -x test --no-daemon
RUN cp build/libs/*.jar app.jar

# Stage 2: Create minimal runtime image
FROM docker.io/bellsoft/liberica-runtime-container:jdk-24-slim-musl

WORKDIR /app
COPY --from=build /app/app.jar app.jar

RUN addgroup -S spring && adduser -S springuser -G spring
USER springuser

ENTRYPOINT ["java", "-jar", "/app/app.jar"]