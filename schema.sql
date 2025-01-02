CREATE TABLE "balanca" (
	"id"	INTEGER NOT NULL,
	"usuario_id"	INTEGER NOT NULL,
	"numero_refeicoes"	INTEGER NOT NULL,
	"total_refeicoes"	FLOAT NOT NULL,
	"forma_pagamento"	VARCHAR(50),
	"data"	DATETIME NOT NULL,
	FOREIGN KEY("usuario_id") REFERENCES "usuario"("id")
);

CREATE TABLE "bebida" (
	"id"	INTEGER NOT NULL,
	"usuario_id"	INTEGER NOT NULL,
	"numero_bebidas"	INTEGER NOT NULL,
	"tipo_bebida"	VARCHAR(15) NOT NULL,
	"total_bebidas"	FLOAT NOT NULL,
	"forma_pagamento"	VARCHAR(15),
	"data"	DATETIME NOT NULL,
	FOREIGN KEY("id") REFERENCES "balanca"("id"),
	FOREIGN KEY("usuario_id") REFERENCES "usuarios"("id")
);

CREATE TABLE "usuario" (
	"id"	INTEGER NOT NULL,
	"nome"	VARCHAR(50) NOT NULL,
	"email"	VARCHAR(50) NOT NULL,
	"senha"	VARCHAR(50) NOT NULL,
	"permissao"	VARCHAR(15) NOT NULL,
	UNIQUE("email"),
	PRIMARY KEY("id" AUTOINCREMENT)
);