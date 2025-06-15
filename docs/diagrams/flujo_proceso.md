# Mi Diagrama de Proceso

```mermaid
flowchart TD
    Start([Inicio])
    Upload[/Upload archivo/]
    SaveToMinIO[/Guardar en MinIO/]
    ProcessFile[/Procesar datos con Pandas/]
    GenStats[/Generar estadísticas/]
    CacheStats[/Guardar estadísticas en Redis/]
    Response[/Responder al usuario/]
    End([Fin])

    Start --> Upload --> SaveToMinIO --> ProcessFile --> GenStats --> CacheStats --> Response --> End