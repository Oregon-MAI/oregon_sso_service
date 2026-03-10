# oregon-python-template

## Ci

### lint-test:

Линтеры и type checkrs:
- ruff
- ty

Для тестов используеться pytest. Проверяеться покрытие тестами. **Порого 80%**

### docker-push/docker-build

docker-push - просиходит после коммита в main. Просиходит сборка образа и отпрвка его в ghcr.io. **Обязательное условие этот public repo** инче не сможем все собрать в docker-compose. **Dockerfile ожидаем в /**

## Пакетный менеждер

Используеться uv. Все бибдиотеки нужные для ci лежат в группе dev.
