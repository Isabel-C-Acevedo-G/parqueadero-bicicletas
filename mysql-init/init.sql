SET NAMES utf8mb4;
SET foreign_key_checks = 0;

DROP DATABASE IF EXISTS ParqueaderoBicicletas;
CREATE DATABASE ParqueaderoBicicletas
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
USE ParqueaderoBicicletas;

SET foreign_key_checks = 0;

CREATE TABLE IF NOT EXISTS Roles (
    IdRol INT AUTO_INCREMENT PRIMARY KEY,
    NombreRol VARCHAR(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS Usuarios (
    IdUsuario INT AUTO_INCREMENT PRIMARY KEY,
    Documento VARCHAR(20) NOT NULL UNIQUE,
    Nombres VARCHAR(100) NOT NULL,
    Apellidos VARCHAR(100) NOT NULL,
    Correo VARCHAR(100) UNIQUE,
    Telefono VARCHAR(20),
    PasswordHash VARCHAR(255) NOT NULL,
    Estado VARCHAR(20) DEFAULT 'Activo',
    FechaRegistro DATETIME DEFAULT CURRENT_TIMESTAMP,
    IdRol INT NOT NULL,
    FOREIGN KEY (IdRol) REFERENCES Roles(IdRol)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS Bicicletas (
    IdBicicleta INT AUTO_INCREMENT PRIMARY KEY,
    IdUsuario INT NOT NULL,
    Marca VARCHAR(50),
    Modelo VARCHAR(50),
    Color VARCHAR(30),
    NumeroSerie VARCHAR(100) UNIQUE,
    Foto VARCHAR(255),
    Estado VARCHAR(20) DEFAULT 'Activa',
    FOREIGN KEY (IdUsuario) REFERENCES Usuarios(IdUsuario)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS Espacios (
    IdEspacio INT AUTO_INCREMENT PRIMARY KEY,
    CodigoEspacio VARCHAR(20) UNIQUE,
    Estado VARCHAR(20) DEFAULT 'Disponible'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS Reservas (
    IdReserva INT AUTO_INCREMENT PRIMARY KEY,
    IdUsuario INT NOT NULL,
    IdBicicleta INT NOT NULL,
    IdEspacio INT NOT NULL,
    FechaReserva DATETIME DEFAULT CURRENT_TIMESTAMP,
    FechaExpiracion DATETIME,
    Estado VARCHAR(20) DEFAULT 'Activa',
    FOREIGN KEY (IdUsuario) REFERENCES Usuarios(IdUsuario),
    FOREIGN KEY (IdBicicleta) REFERENCES Bicicletas(IdBicicleta),
    FOREIGN KEY (IdEspacio) REFERENCES Espacios(IdEspacio)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS Ingresos (
    IdIngreso INT AUTO_INCREMENT PRIMARY KEY,
    IdBicicleta INT NOT NULL,
    IdUsuario INT NOT NULL,
    IdEspacio INT NOT NULL,
    FechaIngreso DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (IdBicicleta) REFERENCES Bicicletas(IdBicicleta),
    FOREIGN KEY (IdUsuario) REFERENCES Usuarios(IdUsuario),
    FOREIGN KEY (IdEspacio) REFERENCES Espacios(IdEspacio)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS Salidas (
    IdSalida INT AUTO_INCREMENT PRIMARY KEY,
    IdIngreso INT NOT NULL,
    FechaSalida DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (IdIngreso) REFERENCES Ingresos(IdIngreso)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS Incidentes (
    IdIncidente INT AUTO_INCREMENT PRIMARY KEY,
    IdUsuario INT,
    IdBicicleta INT,
    TipoIncidente VARCHAR(100),
    Descripcion TEXT,
    FechaIncidente DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (IdUsuario) REFERENCES Usuarios(IdUsuario),
    FOREIGN KEY (IdBicicleta) REFERENCES Bicicletas(IdBicicleta)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

SET foreign_key_checks = 1;

INSERT IGNORE INTO Roles (NombreRol) VALUES
('Administrador'),
('Vigilante'),
('Ciclista');

INSERT IGNORE INTO Usuarios (Documento, Nombres, Apellidos, Correo, Telefono, PasswordHash, IdRol)
VALUES
('12345678', 'Isabel Cristina', 'Acevedo Guirales', 'isabel@gmail.com', '3226753558', '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4', 1);

INSERT IGNORE INTO Bicicletas (IdUsuario, Marca, Modelo, Color, NumeroSerie)
VALUES (1, 'GW', 'Hawk', 'Negro', 'SERIE001');

INSERT IGNORE INTO Espacios (CodigoEspacio)
VALUES ('A01'), ('A02'), ('A03'), ('A04'), ('A05');

INSERT IGNORE INTO Ingresos (IdBicicleta, IdUsuario, IdEspacio)
VALUES (1, 1, 1);

UPDATE Espacios SET Estado='Ocupado' WHERE IdEspacio=1;

INSERT IGNORE INTO Salidas (IdIngreso) VALUES (1);
