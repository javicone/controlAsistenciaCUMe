-- ==============================================
-- MIGRACIÓN: Añadir clase_id a tabla asistencias
-- ==============================================
-- Ejecutar este script para habilitar el seguimiento
-- de la clase asociada a cada fichaje
-- ==============================================

-- Añadir columna clase_id (nullable para registros existentes)
ALTER TABLE asistencias 
ADD COLUMN clase_id INT(11) NULL AFTER aula_id;

-- Añadir foreign key hacia la tabla clases
ALTER TABLE asistencias 
ADD CONSTRAINT asistencias_ibfk_3 
FOREIGN KEY (clase_id) REFERENCES clases(id) 
ON DELETE SET NULL;

-- Crear índice para mejorar rendimiento de consultas
CREATE INDEX idx_asistencias_clase ON asistencias(clase_id);

-- ==============================================
-- OPCIONAL: Intentar vincular asistencias existentes con clases
-- Esto asigna clase_id a registros antiguos basándose en 
-- fecha_hora y aula_id
-- ==============================================
UPDATE asistencias a
SET a.clase_id = (
    SELECT c.id 
    FROM clases c 
    WHERE c.aula_id = a.aula_id 
      AND a.fecha_hora BETWEEN c.hora_inicio AND c.hora_fin
    LIMIT 1
)
WHERE a.clase_id IS NULL;

-- Verificar resultado
SELECT 
    COUNT(*) AS total_asistencias,
    SUM(CASE WHEN clase_id IS NOT NULL THEN 1 ELSE 0 END) AS con_clase,
    SUM(CASE WHEN clase_id IS NULL THEN 1 ELSE 0 END) AS sin_clase
FROM asistencias;
