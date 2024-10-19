# the core workers

## architecturally

this directory stores scripts for two kinds of workers that perform asynchronous work 
as "part" of the centralised server in that they do not perform the model finetuning 
subtasks. some work done by the core server is long-lived and needs to take place out of
the request's band, so they're delegated to these workers

## note for contributors

for some reason, scripts in this module can't import from `server` or `utils` modules,
so required dependencies are just redefined in this module (connection establishment utilities, 
message schema definitions, etc.)
