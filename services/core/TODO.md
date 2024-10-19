# TODO
- Prop up database and RabbitMQ server in Docker containers
- Prop up web server
    - Establish connections to database and message queue server upon server initialisation
    - Create endpoints for:
        - Task submission (from the client-side)
            - This will involve asynchronous task subdivision and distribution
        - Work submission (from the worker-side)
