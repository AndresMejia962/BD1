USE inventario_facturacion;

-- Agregar columna de email a la tabla usuarios permitiendo NULL inicialmente
ALTER TABLE usuarios
ADD COLUMN email VARCHAR(100) NULL AFTER username;

-- Actualizar los usuarios existentes con correos de ejemplo
UPDATE usuarios 
SET email = 'andrea@admin.com' 
WHERE username = 'andrea';

UPDATE usuarios 
SET email = 'pedro@empleado.com' 
WHERE username = 'pedro';

-- Ahora que todos los registros tienen email, hacer la columna NOT NULL
ALTER TABLE usuarios
MODIFY COLUMN email VARCHAR(100) NOT NULL UNIQUE; 