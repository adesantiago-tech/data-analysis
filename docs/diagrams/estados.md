```mermaid
stateDiagram-v2
    [*] --> "Subido"
    "Subido" --> "Procesando"
    "Procesando" --> "Procesado"
    "Procesando" --> "Error"
    "Procesado" --> "Listo_para_descarga"
    "Error" --> [*]
    "Listo_para_descarga" --> [*]
```
