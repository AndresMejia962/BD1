-- Crear la base de datos (opcional, si no tienes una creada)
CREATE DATABASE IF NOT EXISTS empresa;
USE empresa;

-- Crear la tabla CLIENTES
CREATE TABLE CLIENTES (
    Nº_Cliente INT PRIMARY KEY,
    Nombre VARCHAR(100),
    Dirección VARCHAR(200),
    Teléfono VARCHAR(15),
    Poblacion VARCHAR(50)
);

-- Crear la tabla PRODUCTO
CREATE TABLE PRODUCTO (
    Cod_Producto VARCHAR(10) PRIMARY KEY,
    Descripción VARCHAR(100),
    Precio DECIMAL(10, 2)
);

-- Crear la tabla VENTA
CREATE TABLE VENTA (
    Id_Venta INT PRIMARY KEY AUTO_INCREMENT,
    Cod_Producto VARCHAR(10),
    Nº_Cliente INT,
    Cantidad INT,
    FOREIGN KEY (Cod_Producto) REFERENCES PRODUCTO(Cod_Producto),
    FOREIGN KEY (Nº_Cliente) REFERENCES CLIENTES(Nº_Cliente)
);

-- Insertar datos en la tabla CLIENTES
INSERT INTO CLIENTES (Nº_Cliente, Nombre, Dirección, Teléfono, Poblacion) VALUES
(1, 'Juan Pérez', 'Calle 123', '123456789', 'Palermo'),
(2, 'María Gómez', 'Avenida 456', '987654321', 'Valldupar'),
(3, 'Carlos López', 'Calle 789', '456123789', 'Palermo'),
(4, 'Ana Martínez', 'Avenida 101', '321654987', 'Bogotá'),
(5, 'Pedro Sánchez', 'Calle 202', '654987321', 'Valldupar');

-- Insertar datos en la tabla PRODUCTO
INSERT INTO PRODUCTO (Cod_Producto, Descripción, Precio) VALUES
('P1', 'Laptop', 1200.00),
('P2', 'Mouse', 25.00),
('P3', 'Teclado', 45.00),
('P4', 'Monitor', 300.00);

-- Insertar datos en la tabla VENTA
INSERT INTO VENTA (Cod_Producto, Nº_Cliente, Cantidad) VALUES
('P1', 1, 600),  -- Id_Venta: 1 (Juan Pérez, Palermo)
('P2', 1, 300),  -- Id_Venta: 2 (Juan Pérez, Palermo)
('P3', 2, 700),  -- Id_Venta: 3 (María Gómez, Valldupar)
('P4', 2, 200),  -- Id_Venta: 4 (María Gómez, Valldupar)
('P1', 3, 100),  -- Id_Venta: 5 (Carlos López, Palermo)
('P3', 5, 800),  -- Id_Venta: 6 (Pedro Sánchez, Valldupar)
('P2', 5, 400),  -- Id_Venta: 7 (Pedro Sánchez, Valldupar)
('P1', 2, 550);  -- Id_Venta: 8 (María Gómez, Valldupar)
-- Para el ejercicio 6, necesitamos una venta con Id_Venta = 18
INSERT INTO VENTA (Id_Venta, Cod_Producto, Nº_Cliente, Cantidad) VALUES
(18, 'P4', 4, 500); -- (Ana Martínez, Bogotá)