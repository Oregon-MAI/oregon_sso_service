# oregon-sso-service

### Эндпоинты:

1.  POST /api/v1/auth/login
    Тело: {login, password}
    Ответ: {id, login, name, surname, email, roles[], access_token, refresh_token}
2.  POST /api/v1/auth/validate
    Заголовок: Authorization: Bearer <token>
    Ответ: {is_valid: "True"} или {is_valid: "False"} при ошибке
3.  POST /api/v1/auth/refresh
    Заголовок: Authorization: Bearer <refresh_token>  (не тело!)
    Ответ: {access_token, refresh_token}
4.  POST /api/v1/auth/register
    Тело: {login, password, name, surname, email}
    Ответ: {access_token, refresh_token}
5.  GET /api/v1/roles/roles
    Заголовок: Authorization: Bearer <access_token>
    Ответ: [RoleDto]  (каждый: {id, name, description})
6.  GET /api/v1/roles/role?id={uuid}
    Заголовок: Authorization: Bearer <access_token>
    Ответ: RoleDto
7.  POST /api/v1/roles/create_role
    Тело: {name, description}  (оба обязательные)
    Заголовок: Authorization + права админа
    Ответ: {"Info": "Success"}
8.  PATCH /api/v1/roles/update_role
    Тело: {id, name, description}  (все обязательные)
    Заголовок: Authorization + права админа
    Ответ: {"Info": "Success"}
9.  DELETE /api/v1/roles/delete_role
    Тело: {id}
    Заголовок: Authorization + права админа
    Ответ: {"Info": "Success"}
10.  GET /api/v1/user/users
     Заголовок: Authorization: Bearer <access_token>
     Ответ: [UserDto]  (каждый: {id, login, name, surname, email, roles[]})
11.  GET /api/v1/user/user?id={uuid}
     Заголовок: Authorization: Bearer <access_token>
     Ответ: UserDto
12.  POST /api/v1/user/change_role
     Тело: {user_id, role_id}
     Заголовок: Authorization + права админа
     Ответ: {"Info": "Success"} или {"error": "you not have permission"}
13.  DELETE /api/v1/user/delete_user
     Тело: {id}
     Заголовок: Authorization + права админа
     Ответ: {"Info": "Success"} или {"error": "you not have permission"}

Более подробное описание эндроинтов можно получит обратившись по ручке /docs.

### Структура

<pre>
    ├── api/
    │   └── routers/
            ├── notification_router.py 
    ├── consumers/
            ├── consumer.py 
    ├── data/
    │   └── models/   
            ├── message.py 
    ├── repositories/
            ├── message_repository.py 
    ├── services/
    │   ├── background_service.py  
    │   ├── connection_service.py  
    │   └── messages_service.py   
    ├── constants.py 
    └── main.py 

    oregon_sso_service/
    ├── src/                                
    │   ├── alembic.ini                     
    │   ├── constants.py                    
    │   ├── log.py                          
    │   ├── main.py                         
    │   ├── trace.py                        
    │   ├── __init__.py
    │   ├── api/
    │   │   └── routers/
    │   │       ├── auth_router.py          
    │   │       ├── role_router.py          
    │   │       └── user_router.py          
    │   ├── data/
    │   │   ├── models/                     
    │   │   │   ├── base.py
    │   │   │   ├── role.py
    │   │   │   ├── token.py
    │   │   │   ├── user.py
    │   │   │   └── user_role.py
    │   │   ├── repositories/               
    │   │   │   ├── auth_repository.py
    │   │   │   ├── role_repository.py
    │   │   │   └── user_repository.py
    │   │   └── schemas/                    
    │   │       ├── role.py
    │   │       └── user.py
    │   ├── migrations/                     
    │   │   ├── env.py
    │   │   ├── script.py.mako
    │   │   └── versions/
    │   └── services/                       
    │       ├── role_service.py
    │       ├── security_service.py
    │       └── user_service.py
    ├── tests/                              
    │   ├── conftest.py                     
    │   ├── test_auth_router.py
    │   ├── test_repository.py
    │   ├── test_role.py
    │   ├── test_role_router.py
    │   ├── test_security.py
    │   ├── test_user_router.py
    │   └── test_user_service.py
    ├── docker-compose.yaml                 
    ├── Dockerfile                          
    ├── entrypoint.sh                       
    ├── pyproject.toml                      
    ├── uv.lock                             
    ├── .dockerignore
    ├── .gitignore
    ├── .python-version
    └── README.md
</pre>

Также в репозитории находятся юнит тесты, обеспечивающие покрытие >80%.

## Что требуется для запуска

1. Необходимо собрать образ приложения при помощи команды docker build.
2. Написать docker-compose.yaml или запустить compose файл, лежащий в репозитории, содержащий  PostgreSQL с портом  порт 5433.
3. Наслаждаться SSO сервисом.