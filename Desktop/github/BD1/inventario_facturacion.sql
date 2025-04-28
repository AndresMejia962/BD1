-- Crear la base de datos
DROP DATABASE IF EXISTS inventario_facturacion;
CREATE DATABASE inventario_facturacion;
USE inventario_facturacion;

-- Tabla: usuarios
CREATE TABLE usuarios (
  usuario_id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL,  -- Almacenar contraseñas hasheadas
  rol ENUM('admin', 'empleado') NOT NULL
) ENGINE=InnoDB;

-- Datos de ejemplo para usuarios (contraseñas hasheadas con bcrypt)
-- Las contraseñas reales son: admin123 y empleado123
INSERT INTO usuarios (username, password, rol) VALUES
('andrea', '$2b$12$3.XkY9vJ8bY5Z2xWvKzZ8eZ5z5wJ8bY5Z2xWvKzZ8eZ5z5wJ8bY5', 'admin'),
('pedro', '$2b$12$9.YkY9vJ8bY5Z2xWvKzZ8eZ5z5wJ8bY5Z2xWvKzZ8eZ5z5wJ8bY5', 'empleado');

-- Tabla: proveedores
CREATE TABLE proveedores (
  proveedor_id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  contacto VARCHAR(100),
  telefono VARCHAR(20),
  email VARCHAR(100),
  direccion VARCHAR(200)
) ENGINE=InnoDB;

-- Datos de ejemplo para proveedores
INSERT INTO proveedores (nombre, contacto, telefono, email, direccion) VALUES
('Proveedor A', 'Juan Pérez', '+57 3101234567', 'proveedora@example.com', 'Calle 123 #45-67, Bogotá'),
('Proveedor B', 'Ana Gómez', '+57 3112345678', 'proveedorb@example.com', 'Carrera 10 #20-30, Medellín');

-- Tabla: clientes
CREATE TABLE clientes (
  cliente_id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  direccion VARCHAR(200),
  telefono VARCHAR(20),
  email VARCHAR(100),
  cedula VARCHAR(20) UNIQUE
) ENGINE=InnoDB;

-- Índice para optimizar búsquedas por nombre de cliente
CREATE INDEX idx_nombre_cliente ON clientes(nombre);

-- Índice para optimizar búsquedas por cédula
CREATE INDEX idx_cedula_cliente ON clientes(cedula);

-- Datos de ejemplo para clientes
INSERT INTO clientes (nombre, direccion, telefono, email, cedula) VALUES
('Carlos Rodríguez', 'Av. Caracas #20-30, Bogotá', '+57 3204567891', 'carlosr@gmail.com', '1234567890'),
('María Fernández', 'Calle 5 #12-15, Cali', '+57 3123456789', 'mariaf@hotmail.com', '0987654321');

-- Tabla: empleados
CREATE TABLE empleados (
  empleado_id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  cargo VARCHAR(50),
  telefono VARCHAR(20),
  email VARCHAR(100)
) ENGINE=InnoDB;

-- Datos de ejemplo para empleados
INSERT INTO empleados (nombre, cargo, telefono, email) VALUES
('Andrea López', 'admin', '+57 3101234567', 'andreal@xcompany.com'),
('Pedro Jiménez', 'empleado', '+57 3112345678', 'pedroj@xcompany.com');

-- Tabla: productos
CREATE TABLE productos (
  producto_id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  categoria VARCHAR(50),
  descripcion TEXT,
  precio DECIMAL(10,2) NOT NULL,
  stock INT NOT NULL,
  proveedor_id INT,
  CONSTRAINT fk_producto_proveedor FOREIGN KEY (proveedor_id)
    REFERENCES proveedores(proveedor_id)
    ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB;

-- Índice para optimizar búsquedas por nombre de producto
CREATE INDEX idx_nombre_producto ON productos(nombre);

-- Datos de ejemplo para productos
INSERT INTO productos (nombre, categoria, descripcion, precio, stock, proveedor_id) VALUES
('Laptop HP', 'Electrónica', 'Laptop HP 15 pulgadas, 16GB RAM', 3200000.00, 10, 1),
('Impresora Epson', 'Electrónica', 'Impresora multifuncional Epson L3150', 450000.00, 20, 2);

-- Tabla: pedidos
CREATE TABLE pedidos (
  pedido_id INT AUTO_INCREMENT PRIMARY KEY,
  cliente_id INT,
  empleado_id INT,
  fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
  total DECIMAL(10,2),
  nombre_cliente_no_registrado VARCHAR(100),
  cedula_cliente_no_registrado VARCHAR(20),
  CONSTRAINT fk_pedido_cliente FOREIGN KEY (cliente_id)
    REFERENCES clientes(cliente_id)
    ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT fk_pedido_empleado FOREIGN KEY (empleado_id)
    REFERENCES empleados(empleado_id)
    ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB;

-- Índice para optimizar consultas por fecha de pedido
CREATE INDEX idx_fecha_pedido ON pedidos(fecha);

-- Índice para optimizar búsquedas por cédula de cliente no registrado
CREATE INDEX idx_cedula_no_registrado ON pedidos(cedula_cliente_no_registrado);

-- Tabla: pedido_detalle
CREATE TABLE pedido_detalle (
  detalle_id INT AUTO_INCREMENT PRIMARY KEY,
  pedido_id INT,
  producto_id INT,
  cantidad INT NOT NULL,
  precio_unitario DECIMAL(10,2) NOT NULL,
  CONSTRAINT fk_detalle_pedido FOREIGN KEY (pedido_id)
    REFERENCES pedidos(pedido_id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_detalle_producto FOREIGN KEY (producto_id)
    REFERENCES productos(producto_id)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- Tabla: facturas
CREATE TABLE facturas (
  factura_id INT AUTO_INCREMENT PRIMARY KEY,
  pedido_id INT,
  numero_factura VARCHAR(20) NOT NULL UNIQUE,
  fecha_emision DATETIME DEFAULT CURRENT_TIMESTAMP,
  total DECIMAL(10,2),
  CONSTRAINT fk_factura_pedido FOREIGN KEY (pedido_id)
    REFERENCES pedidos(pedido_id)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- Tabla: pagos
CREATE TABLE pagos (
  pago_id INT AUTO_INCREMENT PRIMARY KEY,
  pedido_id INT,
  fecha_pago DATETIME DEFAULT CURRENT_TIMESTAMP,
  monto DECIMAL(10,2),
  metodo_pago VARCHAR(50),
  CONSTRAINT fk_pago_pedido FOREIGN KEY (pedido_id)
    REFERENCES pedidos(pedido_id)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- Vista: reporte_inventario
CREATE VIEW reporte_inventario AS
SELECT 
    nombre,
    stock,
    precio,
    (stock * precio) AS valor_inventario
FROM productos;